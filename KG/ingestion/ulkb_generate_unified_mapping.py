#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 15:51:15 2021

@author: rosariouceda-sosa
"""
###########################################
# Extraction of Propbank, Verbnet and mappings 
# It requires verbnet3.4, verbnet3.3 and verbnet3.2 in nltk_data directory, 
#      as well as the latest version of propbank
#
# In particular, it does require the last 
###########################################
import json
import re
from nltk.corpus import treebank
from nltk.corpus.util import LazyCorpusLoader
from VerbnetCorpusReaderEx import VerbnetCorpusReaderEx
from nltk.corpus import PropbankCorpusReader
from semlinkEx import query_pb_vn_mapping, query_pb_vn_mapping_1_2
from xml.etree import ElementTree
from propbank_readerEx import PropbankCorpusReaderEx

#from nltk.corpus import propbank
propbank = LazyCorpusLoader(
    "propbank-latest",
    PropbankCorpusReaderEx,
    "prop.txt",
    r"frames/.*\.xml",
    "verbs.txt",
    lambda filename: re.sub(r"^wsj/\d\d/", "", filename),
    treebank,
)  # Must be defined *after* treebank corpus.


vn_dict = {
    "verbnet3.2": LazyCorpusLoader("verbnet3.2", VerbnetCorpusReaderEx, r"(?!\.).*\.xml"),
    "verbnet3.3": LazyCorpusLoader("verbnet3.3", VerbnetCorpusReaderEx, r"(?!\.).*\.xml"),
    "verbnet3.4": LazyCorpusLoader("verbnet3.4", VerbnetCorpusReaderEx, r"(?!\.).*\.xml")
}

#The default is 3.4
current_vn = vn_dict["verbnet3.4"]

VN_FILES = "/Users/rosariouceda-sosa/Documents/usr/SemanticsSvces/verbnet/verbnet-master/verbnet3.4"
VN_DIR = "/Users/rosariouceda-sosa/Documents/usr/SemanticsSvces/verbnet/"
PB_DIR = "/Users/rosariouceda-sosa/Documents/usr/SemanticsSvces/propbank/"
outputFile = ""
logFile = ""

processedGroupingsVN = {}
processedMaps = []

#key is entity and the list of mappings they have. Keys for Verbnet, Propbank and WN are their id's
memberToMap = {}
#inverse of memberToMap
mapToMember = {}

#Each propbank has: [roleSet] : name, arguments, lemmas, provenance
pb_index = {}

#Each verbnet has: [CODE] :  name, [arguments] variableName, variableType, lemmas, provenance,
vn_index = {}

#{roleset} admire-31.2': {'provenance': 'verbnet3.4', 'arguments' : {'ARG0' : {'description' : "XXX" , 'vnArg' : Agent}}]
map_index = {}

extended_semnlink_index = []

# 
#vnCodeToLemma = {}



###### LOG
outLog = open("/Users/rosariouceda-sosa/Downloads/OutLog_ULKB_Clean.txt", "w")


###########################################################
# AUXILIARY FUNCTIONS 
###########################################################
#IMPORTANT: To standardize both verbnet names and codes, 
def vn_standard(_verb: str) -> str:   
    # return _verb.replace(".", "-")
    #do nothing
    return _verb
    
def count_dict() -> int : 
    
    highest = 0
    for thisMap in mapToMember : 
        if len(mapToMember[thisMap]) > highest: 
            highest = len(mapToMember[thisMap])
    return highest
def compare_strs(_first : str, _second : str) -> bool :
    if (_first.lower() ==  _second.lower()):
        return 1
    return 0


def checkKeyStr(_dict : {}, _key: str) ->  str : 
      
    if _key in _dict.keys(): 
       return  _dict[_key] 
    else: 
        return ""
    
    
def toRDFStr(_in :str) -> str : 
    
  #somewhat sloppy, but gets the data 
  _in = _in.replace("/", "_") 
  _in = _in.replace(":", "-")
  _in = _in.replace(" ", "")
  _in = _in.replace("(", "_")
  _in = _in.replace(")", "_")
  _in = _in.replace("'", "") 
  _in = _in.replace(".", "-")
  _in = _in.replace(",", "_")
  _in = _in.replace("__", "_")
  _in = _in.replace(">", "")
  _in = _in.replace("<", "")
  _in = _in.replace("#", "-")
  _in = _in.replace("%", "_")
  _in = _in.replace("?", "_")
  #ADD THIS FOR THE INCONSISTENT VERBNET NAMING IN SEMLINK AND NLTK
  _in = _in.replace("-", "_")
  return _in


def checkArray(_dict : {}, _name : str) -> [] :
    
    if (_name) in _dict.keys() :
        return _dict.get(_name)
    else:
        return []
    
# Whether the mapping points to 'nothing'
def wrong_mapping(_term :str) -> bool :
    
    _term = _term.strip()
    if len(_term) == 0 :
        return True
    
    if _term == 'NP' or _term == 'np' or _term == 'NP>' or _term == 'np>':
        return  True
    if _term == 'NM' or _term == 'nm' or _term == 'NM>' or _term == 'nm>':
        return  True
    return False 
    
def clean_text(_text :str, _oneLine : bool) -> str : 
    
     _text = _text.replace("\"", "\\\"")
         
     _text = _text.replace("'", "\\'")
     _text = _text.replace("\/", "-") 
     _text = _text.replace("`", " ")  
                 
     if _oneLine : 
         _text = _text.replace("\n", "")
         
     return _text
 
def chunk(mappings: str) -> []:
    
    rList = mappings.split(',')
    
    for item in rList : 
        item = item.strip()
    return rList

# from admire-31.2 to admire
def get_vn_lemma(_verb : str) -> str : 
    
    return _verb.split('-', 1)[0]

# from admire-31.2 to 31.2 -- The first hyphen is the one that counts
def get_vn_code(_verb: str) -> str : 
    stVerb = vn_standard(_verb)
    return stVerb.split('-',1)[1]
    
#from admire.01 to admire
def get_pb_lemma(_verb : str) -> str : 
    return _verb.split('.', 1)[0]

def get_vn_varName(_var : str) -> str : 
    
    if _var.startswith('?') : 
        _var = _var[1:]
        
    return _var


def match_vn_codes(_first:str , _second: str) -> bool :
    
    if toRDFStr(_first) == toRDFStr(_second):
        return True
    return False

def matchRDF(_item, _dict: {}) -> str : 
    
    toMatch = toRDFStr(_item)
    for keyItem in _dict: 
        if  toMatch == toRDFStr(keyItem):
            return keyItem
    return ""

# Also consider one start with another
def vn_in_dict(_item:str, _dict: {}, _name: str) -> bool :
    for keyItem in _dict: 
       if len (_name ) == 0 :
           compareTo = keyItem
       else :     
           compareTo = _dict[keyItem][_name]
       if compareTo == _item :          
           return True
       if compareTo.startswith(_item) or compareTo.startswith(_name) :
           return True
    return False


def vn_to_swap(_item:str, _dict: {}, _name:str) -> str : 
    
    _itemCode = get_vn_code(_item)
    if _itemCode not in vn_index : 
        return ""
    _itemProvenance = vn_index[_itemCode]['provenance']
    _itemVersion = _itemProvenance.split('.',1)[1]
    for keyItem in _dict: 
        if len(_name) == 0 : 
            compareTo = keyItem 
        else : 
            compareTo = _dict[keyItem][_name]
        compareToCode = get_vn_code(compareTo)
        if _itemCode == compareToCode or compareToCode.startswith(_itemCode) or _itemCode.startswith(compareToCode) : 
            if compareToCode in vn_index : 
                compareToProvenance = vn_index[compareToCode]['provenance']
                compareToVersion = compareToProvenance.split('.', 1)[1]
                if compareToVersion < _itemVersion :
                    return compareTo
    return ""

def unmatched_roles(_have : [], _want: []) -> [] : 
    result = []
    for haveEntry in _have : 
        haveEntry = haveEntry.lower()
        found = False
        for wantEntry in _want :
            if wantEntry.lower() == haveEntry : 
                found = True
        if not found : 
             result.append(haveEntry)
    return result


def wrongly_matched_roles(_have : [], _want: []) -> [] : 
    result = []
    for haveEntry in _have : 
        haveEntry = haveEntry.lower()
        found = False
        for wantEntry in _want :
            if wantEntry.lower() == haveEntry : 
                found = True
        if not found : 
             result.append(haveEntry)
    return result


def getRoleStrFrom(_list : []) -> str : 
    resultStr = ""
    
    noDupList = []
    for item in _list :
        if item.startswith("?") : 
            item = item[1:]
        if item not in noDupList : 
            noDupList.append(item)
            
    for item in noDupList : 
        if len(resultStr) == 0 : 
            resultStr += item
        else : 
            resultStr += ", " + item
    return resultStr    

def getRoleListFrom(_list : []) -> [[str]] : 
    resultStr = ""
    
    noDupList = []
    for item in _list :
        if item.startswith("?") : 
            item = item[1:]
        if item not in noDupList : 
            noDupList.append(item)
    return noDupList
######################################################################
# SEMLINK INGESTION
######################################################################
#maps from  verbnet class + argument a URL 
#Check the variables that have been already mapped through Verbnet
def map_to_url(_class: str, _param : str) -> []: 
    global vnClassToVars, framesToVars
    resultList = []
    if _class not in vnClassToVars : 
        return resultList   
    
    argList = vnClassToVars[_class]
    for argKey in argList : 
        if argKey.lower() == _param.lower(): 
            resultList.append(argList[argKey])               
  #  elif _class in framesToVars : #try the frames
  #      argList = framesToVars[_class] 
  #      for frameKey in argList : 
  #          for argKey in argList[frameKey] : 
  #              if argKey.lower() == _param.lower() : 
  #                  resultList.append(argList[frameKey][argKey])
    return resultList

def process_semlink_1_2() :    
    global provenance, pbToMap_params, pbToMap, semLinkFromPB
    
    # from {'mapping': '51.2', 'source': 'verbnet3.4', 'arguments': {'ARG0': 'Theme'}}
    # TO map_index
    #[{'vnVerb': 'admire-31.2', 'provenance': 'verbnet3.4', 'arguments' : {'ARG0' : {'description' : "XXX" , 'vnArg' : Agent}}]   
    oldProvenance = provenance
    provenance  = "semlink 1.2.2"
    
    for roleset in pb_index : 
               
        if "abound.01" in roleset:
            print("DEBUG " + roleset)
        semLinkmappingList = query_pb_vn_mapping_1_2(roleset)
        #If there is no mapping, ignore. 
        if not semLinkmappingList or len(semLinkmappingList) == 0 : 
        #        if outLog is not None : 
        #            outLog.write("PROPBANK NO_SEMLINK_1_2," + roleset + "\n")
        #            outLog.flush()
               continue 
        #If there is a mapping BUT we don't have the roleset, it's an issue.  
        if roleset not in  map_index : 
            if outLog is not None : 
                    outLog.write("NO_PROPBANK SEMLINK_1_2," + roleset + "\n")
                    outLog.flush()
            map_index[roleset] = {}
        
        #Grab the current map_index entry. We know it's there
        ourMappings = map_index[roleset]
        
        for mapping in semLinkmappingList :   
           vnRawCode = mapping['mapping']  
           vnRawCode = vn_standard(vnRawCode)
           vnRawName = ""
           if vnRawCode in vn_index : 
               vnRawName = vn_index[vnRawCode]['name']
           else : # use a hack to substitute the first hyphen by a dot. Oh brother...
             if outLog is not None : 
                    outLog.write("NO VERBNET SEMLINK_1_2," + vnRawName + "," + vnRawCode +  "\n")
                    outLog.flush()
             continue #go to the next mapping
           #If the verbnet class is already mapped, we ignore it.
           arguments = mapping["arguments"] 
           toSwapVerb = vn_to_swap(vnRawName, ourMappings, "")
           #we swao the new verbs but ONLY if we can get arguments in the new verb
           if len(toSwapVerb) > 0 and len(arguments) > 0 : 
                ourMappings.pop(toSwapVerb, None)
           if not vn_in_dict(vnRawName, ourMappings, "") :               
               print("SEMLINK1.2 Process " + roleset)                        
               newMapping = {}
               newMapping['provenance'] = 'Semlink 1.2.2'
               ourMappings[vnRawName] =  newMapping
               newArguments = {}
               newMapping['arguments'] = newArguments
               if len(arguments) > 0 :                                           
                   for pbArg in arguments : 
                       vnArg = arguments[pbArg]
                       newArguments[pbArg] = {'description': "", "vnArg" : vnArg}
           
            
    provenance = oldProvenance
    
def process_semlink_2() : 
    global provenance, pbToMap_params, pbToMap, semLinkFromPB
    oldProvenance = provenance
    provenance = "semlink 2"
    foundMap = False
    
    # FROM [{'mapping': 'admire-31.2', 'source': 'verbnet3.4', 'arguments' : {'ARG0' : Agent}}]
    # TO map_index
    #[{'vnVerb': 'admire-31.2', 'provenance': 'verbnet3.4', 'arguments' : {'ARG0' : {'description' : "XXX" , 'vnArg' : Agent}}]
    for roleset in pb_index : 
        if "abound.01" in roleset : 
            print("DEBUG  " + roleset)
        if roleset not in map_index :   #shouldn't happen       
            if outLog is not None : 
                outLog.write("NO_PROPBANK SEMLINK_2," + roleset + "\n")
                outLog.flush()
            map_index[roleset] = {}
        semLinkmappingList = query_pb_vn_mapping(roleset)        
        if not semLinkmappingList or len(semLinkmappingList) == 0 : 
                if outLog is not None : 
                    outLog.write("PROPBANK NO_SEMLINK_2," + roleset + "\n")
                    outLog.flush()
                continue         
        print("SEMLINK2 Process " + roleset)
        ourMappings = map_index[roleset]     
        for mapping in semLinkmappingList : 
            vnName = mapping['mapping']
            #Favor verbs in higher versions of Verbnet ONLYthey 
            toSwapVerb = vn_to_swap(vnName, ourMappings, "")
            semLinkArgs = {}
            if 'arguments' in mapping :
                 semLinkArgs = mapping['arguments'] 
            #Substitute for new-er versions of Verbnet but only if they have arguments
            if len(toSwapVerb) > 0 and len(semLinkArgs) > 0: 
                ourMappings.pop(toSwapVerb, None)
            if not vn_in_dict(vnName, ourMappings, "") : 
                    newMapping = {}
                    ourMappings[vnName] = newMapping
                    newMapping['provenance'] = "Semlink 2.0"
                    newMapping['arguments'] = {}
                    arguments = newMapping['arguments']                    
                    for pbArg in  semLinkArgs : 
                            arguments[pbArg] = {'description': "", "vnArg" : semLinkArgs[pbArg]}
            
    provenance = oldProvenance
        
######################################################################
# PROPBANK INGESTION
######################################################################
def query_propbank_roles(propbank_id):
    print("\nquery_propbank_roles for propbank_id {}".format(propbank_id))
    try:
        role_set = propbank.roleset(propbank_id)
    except Exception as e:
        print(e)
        return None

    role_mappings = dict()
    # print("role_set:", ElementTree.tostring(role_set, encoding='unicode'))
    for role in role_set.findall("roles/role"):
        # print("role:", ElementTree.tostring(role, encoding='unicode'))
        for vn_role in role.findall('vnrole'):
            # print("vn_role:", ElementTree.tostring(vn_role, encoding='unicode'))
            arg_key = "ARG{}".format(role.attrib['n'])
            if arg_key not in role_mappings:
                role_mappings[arg_key] = []
            role_mappings[arg_key].append({
                "vncls": vn_role.attrib["vncls"],
                "vntheta": vn_role.attrib["vntheta"],
                "description": role.attrib['descr']
            })
    #print("query_propbank_roles role_mappings:", role_mappings)
    return role_mappings

#########################################
# TRANSFORM MAPPINGS IN PROPBANK TO SEMLINK
# "abash.01": {
#    "31.1": {
#      "ARG0": "stimulus",
#      "ARG1": "experiencer"
#    }
#  },
#  #[{'mapping': 'admire-31.2', 'source': 'verbnet3.4', 'arguments' : {'ARG0' : Agent}}]
def propbank_to_semlink(_roleset : str) : 
    global map_index
    
    #The mappings, [roleSet] : vn_name, [[arguments] : [pb_arg] : vn_arg, provenances
    raw = query_propbank_roles(_roleset)
    
    if len(raw) == 0 :
        return
    
    # vn_mapping
    #[{'vnVerb': 'admire-31.2', 'provenance': 'verbnet3.4', 'arguments' : {'ARG0' : {'description' : "XXX" , 'vnArg' : Agent}}]
    rolesetMap = {}
    if _roleset in map_index : 
        rolesetMap = map_index[_roleset]
    else : 
        map_index[_roleset] = rolesetMap
       
    for argX in raw: 
        argXMappings = raw[argX]
        for argXMapsTo in argXMappings : 
            vnTheta = argXMapsTo['vntheta']
            vnDescription = argXMapsTo['description']
            vncls = argXMapsTo["vncls"]
            # We need to match on underscores because Propbank's verbs 
            # sometimes don't use the right VN code!!
            vnCode = matchRDF(vncls, vn_index)
            if len(vnCode) == 0 :
                print (vncls + " NOT FOUND IN PROPBANK MAPPING")
                if outLog is not None : 
                    outLog.write("NO_PROPBANK," + _roleset + "\n")
                    outLog.flush()
                continue
            vnMapping = vn_index[vnCode]
            vnName = vnMapping['name']
            if len(vnName) == 0 :
                print (vncls + " NOT FOUND")
                if outLog is not None : 
                    outLog.write("NO_PROPBANK," + _roleset + "\n")
                    outLog.flush()
                continue
            
            if outLog is not None : 
                outLog.write("MAP PB," + _roleset + "," + vnName + "\n")
                outLog.flush()
            
            if vnName not in rolesetMap : 
                verbMapping = {}
                rolesetMap[vnName] = verbMapping
                verbMapping['provenance'] = "Propbank"
                verbMapping['arguments'] = {}
                
            thisMapping = rolesetMap[vnName]
                       
            thisMapping['arguments'][argX] = {'description' : vnDescription, 'vnArg' : vnTheta }
    
def process_propbank( _namespace : str) : 
    global outputFile, idCounter, provenance, outLog
    
    #Each propbank has: [roleSet] : name, arguments, lemmas, provenance
    provenance = "Propbank NLTK"
    for rolesetData  in propbank.rolesets():  
            roleset = rolesetData.attrib["id"]
            if outLog is not None : 
                outLog.write("PB," + roleset + "\n")
                outLog.flush()
                
            #outFile.write(fileID + "#" + tagger + "#" + roleset + "#")
            rRoleSet = "UL_PB:" + toRDFStr(roleset) 
  
            if roleset in pb_index : 
                continue
                        
            pb_index[roleset] = {}
            pb_index[roleset]['name'] = roleset
            pb_index[roleset]['provenance'] = 'Propbank'
            pb_index[roleset]['arguments'] = {}
            argumentDict = pb_index[roleset]['arguments']
            
            for role in rolesetData.findall("roles/role"):
                argID = "ARG" + role.attrib['n']
                argDesc = role.attrib['descr']
                argumentDict[argID] = argDesc
                
            propbank_to_semlink(roleset)
            #Whether it has data or not, it has been added to map_index
               
    provenance = "automatic generation"
######################################################################
# VERBNET INGESTION
######################################################################

def process_mappings() : 
    global idCounter, provenance, mapToMember, memberToMap
    provenance = "clustered mappings"
    for mapEntity in mapToMember : 
        if "UL_WN:" in mapEntity or "UL_PB:" in mapEntity or "UL_VN:" in mapEntity : 
            temp2 = mapEntity.split(":")[1]
            temp1 = mapEntity.split(":")[0]
            rMapName = temp1 + ":" + toRDFStr(temp2)
        #else if "UL_WN-" in mapEntity or "UL_PB-" in mapEntity or "UL_VN-" in mapEntity :
         #   temp2 = mapEntity[6:]
         #   temp1 = mapEntity[0:5]
         #   rMapName = temp1 + ":" + toRDFStr(temp2)
        else : 
            rMapName = toRDFStr(mapEntity)
        if mapEntity not in processedMaps: 
            print("MAP NOT PROCESSED " + rMapName)
        memberList = mapToMember[mapEntity]  #maybe we added more
        for member in memberList: 
            if "UL_WN:" in member or "UL_PB:" in member or "UL_VN:" in member :
                temp1 = member.split(":")[0]
                temp2 = member.split(":")[1]
                rMember = temp1 + ":" + toRDFStr(temp2)
           # else if "UL_WN-" in member or "UL_PB-" in member or "UL_VN-" in member:
           #     temp2 = mapEntity[6:]
            #    temp1 = mapEntity[0:5]
            #    rMember = temp1 + ":" + toRDFStr(temp2)
            else : 
                rMember = toRDFStr(member)
            #if len(rMember) == 1 :
             #   print("DEBUG: rMember ")
           
    provenance = "automatic reasoning"

#Returns the name of the map with all the entities there
def unify_maps(_mapList : {}) -> str : 
    
    global memberToMap, mapToMember
    if len(_mapList) == 0 :
        return None
    
    theMapName = ""
    theMap = []
    counter = 0 
    for entity in _mapList:
        if counter == 0 :
            theMapName = entity 
            theMap = _mapList[entity]
            counter += 1
            continue
        mapMembers = _mapList[entity]
        for member in mapMembers : 
            if not member in theMap : 
                theMap.append(member)
                memberToMap[member] = theMapName
    mapToMember[theMapName] = theMap
    return theMapName
        
        
def get_vn_classes_for(term :str ) -> [] :
    
    return vn.classids(term)

#def get_all_vn_classes() -> [] : 
#    return vn.classids()
    
def process_vn_frames(_className: str,  _classKey:str)  -> str:
    #Each verbnet has: [CODE] :  name, [arguments] variableName, variableType, lemmas, provenance
    global idCounter, current_vn, framesToVars, vnClassToVars, provenance
    
    theClass = current_vn.vnclass(_className)
    vnframes = theClass.findall("FRAMES/FRAME")
    if 'put' in _className : 
        print("DEBUG " + _className)
    
    stClassKey = vn_standard(_classKey)
    stClassName = vn_standard(_className)
    vnIndexClass = vn_index[stClassKey] # it better work
    if 'arguments' not in vnIndexClass : 
        vnIndexClass['arguments'] = {}
    variables = vnIndexClass['arguments']
    classRolesList = []
    for frame in vnframes :       
        #DESCRIPTIOPN
        descF = frame.find("DESCRIPTION")
        numberF = descF.get("descriptionNumber")       
       
        #PROCESS SEMANTICS         
        semList = current_vn._get_semantics_within_frame(frame)
        predCounter = 1
        #Predicates per frame
        for semPre in semList : 
            txt = ""
            roleList = ""
            predValue = semPre['predicate_value']
            arguments = semPre['arguments']
            is_negated = semPre["is_negated"]           
            
            if is_negated : 
               txt += "NOT "
           
            txt += predValue + "("
            argOrder = 1
            for argument in arguments : 
                argValue = argument["value"]
                argType = argument["type"]
                argText = argType + "(" + argValue + ")"
                if argType != 'Event' : 
                    if argValue not in classRolesList : 
                        classRolesList.append(argValue)
                     
                # argText = argument["type"] + "(" + argument["value"] + ")"
                
                #writeStmt_toStr(rPredName, rdf_param_text, str(argOrder) + ", " + argText)
                argOrder += 1
                #if argValue not in framesToVars : 
                #    framesToVars[argValue] = {}
                #frameIndex = framesToVars[argValue] 
                #if rName not in frameIndex : 
                #    frameIndex[rName] = {}
                #paramIndex = frameIndex[rName]
                #if argValue not in paramIndex : 
                #    paramIndex[argValue] = argName
                txt += argText + ","
                
            txt = txt.rstrip(txt[-1]) + ")"
            
            #The variable name must have the context of the frame so it can be 
            #identified. The text form can also be used. 
            
            #This is the whole text of the predicate
            predCounter += 1
            #print(_className + " --Sem--> " + txt + "\n\n")
        #if len(txt)> 0 : 
        #   writeStmt_toStr(name, vn_semantics, txt)
        
    
    return getRoleListFrom(classRolesList)
    
def process_vn_thematic_roles(_className: str, _classCode:str) :
    global idCounter, current_vn , vnClassToVars
    
    theClass = current_vn.vnclass(_className)
    vnthemRoles = theClass.findall("THEMROLES/THEMROLE")
    mapping = vn_index[_classCode]
    if 'arguments' not in mapping : 
        mapping['arguments'] = []
    if 'caused_calibratable_cos' in _className : 
        print("DEBUG " + _className)
    for themRole in vnthemRoles : 
        tType = themRole.get('type')
        roleName = tType.strip()
        if roleName not in mapping['arguments'] : 
            mapping['arguments'].append(roleName)
        
  
def process_vn_lemmas(_className: str, _classKey: str) : 
    #Each verbnet has: [CODE] :  name, [arguments] variableName, variableType, lemmas, provenance
    global current_vn, vn_index
    
    theClass = current_vn.vnclass(_className)
    stKey = vn_standard(_classKey)
    stClassName = vn_standard(_className)
    vnIndexClass = vn_index[stKey] # it better work
    if 'lemmas' not in vnIndexClass : 
        vnIndexClass['lemmas'] = []
    vnLemmas = vnIndexClass['lemmas']
    for member in theClass.findall("MEMBERS/MEMBER") : 
        vnKey = member.get("name")       
        if vnKey in vnLemmas : 
            continue        
        vnLemmas.append(vnKey)
          

def read_verbnet_index( _namespace :str,  _vn, _version) : 
  
    global logFile, vnClassToRDF, provenance, current_vn, vnCodeToVerb
    
    #fill all the indexes
    current_vn = _vn
    allClasses = current_vn.classids()
    
    for className in allClasses : 
        cCode = get_vn_code(className)
        stCode = vn_standard(cCode)
        stClassName = vn_standard(className)
        if stCode not in vn_index: 
            print(_version + " , " + stClassName)
            vn_index[stCode] = {}
            vn_index[stCode]['name'] = stClassName
            vn_index[stCode]['provenance'] = _version
            if outLog is not None : 
                outLog.write(_version + "," + stClassName + "," + stCode + "\n")
                outLog.flush()
            process_vn_lemmas(className, cCode)
            process_vn_thematic_roles(className, cCode)
            roleList = process_vn_frames(className, cCode)
            if 'arguments' not in vn_index[cCode] : 
                vn_index[cCode]['arguments']
            args = vn_index[cCode]['arguments']
            if len(roleList) > 0 : 
                for item in roleList : 
                    if '?' in item: 
                        item = item[1:]
                    if item not in args : 
                        args.append(item)
            
        subClasses = current_vn.subclasses(className)       
        for subClassName in subClasses : 
            cCode = get_vn_code(subClassName)
            stCode = vn_standard(cCode)
            stSubClassName = vn_standard(subClassName)
            if stCode not in vn_index : 
               print(_version + " , " + stSubClassName)
               vn_index[stCode] = {} 
               vn_index[stCode]['name'] = stSubClassName
               vn_index[stCode]['provenance'] = _version
               if outLog is not None : 
                    outLog.write(_version + "," + stSubClassName+ "," + stCode + "\n")
                    outLog.flush()
               process_vn_lemmas(subClassName, cCode)
               process_vn_thematic_roles(subClassName, cCode)
               roleList = process_vn_frames(subClassName, cCode)
               if 'arguments' not in vn_index[cCode] : 
                   vn_index[cCode]['arguments']
               args = vn_index[stCode]['arguments']
               if len(roleList) > 0 : 
                   for item in roleList : 
                       if '?' in item: 
                           item = item[1:]
                       if item not in args : 
                           args.append(item)


# Ingests Verbnet and Propbank
#  (1) Verbnet (3.4, 3.3 and 3.2)   
#  (2) Propbank (from NLTK)
#  (3) Mappings from PB to VN from Semlink
def process_ulkb_mappings(_output: str,  _namespace = "ULKB" ,  _log = True) : 
    
    global outputFile, outLog, processedClasses, vn, provenance
    
    outLog= open("/Users/rosariouceda-sosa/Downloads/UL_KB_LOG.txt", "w")   
    
    #STEP 1  -- READ THE VERBNET NAMES AND ROLES
    print("-----> PROCESSING VERBNET 3.4 ")
    read_verbnet_index( _namespace, vn_dict["verbnet3.4"], "verbnet3.4") 
    print("-----> PROCESSING VERBNET 3.3")
    read_verbnet_index( _namespace, vn_dict["verbnet3.3"], "verbnet3.3")
    print("-----> PROCESSING VERBNET 3.2")
    read_verbnet_index( _namespace, vn_dict["verbnet3.2"], "verbnet3.2") 
       
    #STEP 2 -- BRING PROPBANK 
    #_namespace = "UL_PB"
    print("-----> PROCESSING PROPBANK")
    process_propbank(_namespace)
    
    #STEP 3 -- From Semlink, depends on Propbank to fill pbIndex
    print("-----> PROCESSING SEMLINK 2")
    process_semlink_2()
    print("-----> PROCESSING SEMLINK 1.2")
    process_semlink_1_2()
    
    #Process all mappings at this time if there are any left
    print("-----> PROCESSING MAPPINGS")
    process_mappings()
   
    outputFile = open(_output, "w")
    
    for pb_verb in map_index : 
        mapping = map_index[pb_verb]
        for key in mapping: 
            vn_code = get_vn_code(key) 
            vn_args = vn_index[vn_code]['arguments']
            mapping_args = mapping[key]['arguments']
            mapping_vn_args = []
            for arg in mapping_args : 
                mapping_vn_args.append(mapping_args[arg]['vnArg'])
            not_matched = unmatched_roles(vn_args, mapping_vn_args)
            wrongly_matched = unmatched_roles(mapping_vn_args, vn_args)
            outputFile.write(pb_verb + "," + 
                             key  +"," + 
                             mapping[key]['provenance'] + "," +
                             vn_index[vn_code]['provenance'] +  "," + 
                             str(mapping_args).replace(",", ";") + "," + 
                             str(not_matched).replace(",", ";") + "," + 
                             str(wrongly_matched).replace(",", ";") +  "," + 
                             str(vn_args).replace(",", ";") + 
                             "\n")   
    outputFile.close()
    
    #Writie to json fileto be ingested in the graph
    jsonFile = _output.replace(".txt", ".json")
    with open(jsonFile, 'w') as outfile:
        json.dump(map_index, outfile)    
    outfile.close()    
    
    print("-----> DONE")
    
if __name__ == '__main__':
       
    workDir = "/Users/rosariouceda-sosa/Downloads/cleanULKB/"
    outFileName = "/Users/rosariouceda-sosa/Downloads/ULKB_UNIFIED.txt"
    namespace = "UL_KB" # THE GENERAL NAMESPACE 
     
    inputGroupings = VN_DIR + "otherdata/all_verbnet_grouping.json"


    # INGESTION PROCESS 
    process_ulkb_mappings(outFileName)
    
    #INDIVIDUAL TESTS
    #print(query_propbank_roles("make_up.08"))
    
       
    if outLog is not None : 
         outLog.close()
       
#    for vn_Class in  vnClassToRDF : 
#       if  vn_Class not in processedGroupingsVN : 
#            listFile.write(vn_Class + "," + "NO GROUP MAPPING" + "\n")
#   listFile.close()
    

    
    #SIMPLE TEST -- GET ALL CLASSES 
    #all_verb_classes = get_all_classes()    
    #for verbClass in all_verb_classes:
    #    print(verbClass) 
    
    #SIMPLE TEST - GET INFO FOR A LEMMA
    #sampleClasses = get_classes_for('leave')
    #for className in sampleClasses  :
    #    v = vn.vnclass(className)
    #    print("CLASS = " + className)
    #    print('\t' + vn.pprint_themroles(className))
    #    for t in v.findall('THEMROLES/THEMROLE/SELRESTRS/SELRESTR') : 
    #        print('\t' + str(t))
        
    #export_verbnet_instances(workDir + "verbnet_output.txt")
    
    
    