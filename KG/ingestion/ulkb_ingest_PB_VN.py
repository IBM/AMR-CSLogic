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
import csv
import re
#from importlib.machinery import SourceFileLoader


from nltk.corpus import treebank
from nltk.corpus.util import LazyCorpusLoader
from VerbnetCorpusReaderEx import VerbnetCorpusReaderEx
from nltk.corpus import PropbankCorpusReader

#from  semlink import query_pb_vn_mapping, query_pb_vn_mapping_1_2
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

entityToRDF = {}

#Simple lemmas to be used. Original names only
lemmasIndex = []
pbIndex = []
vnIndex = []
wnIndex = []
vnCodeToVerb = {}
pb_to_params = {} #roleset to mappings (LIST) name with params
vn_to_params = {}
pbToMap = {} #roleset to mappings (LIST) w/o params
semLinkFromPB = {}

# From verbnet name to verbnet URL
vnClassToRDF = {}

vnClass_to_rolelist = {} 

# keep the code and the lemma
vnCodeToLemma = {}

# class name to { name, [uri]}
vnClassToVars = {}

#class, { frame, { name, uri}
framesToVars = {}

##### ERROR LOG
# Verbnet 3.3, performance26

###### LOG
outLog = open("/Users/rosariouceda-sosa/Downloads/OutLog_UL_KB.txt", "w")

##############################################################
# The RDF/OWL vocabulary
##############################################################
mapping  = "rrp:Mapping"
provenance = "automatic generation"
mappingClass = "rrp:Mapping"
mappingGroup = "rrp:MappingGroup"
kbOverlay = "rrp:KBOverlay"
KB = "rrp:KB"
kbProxy = "rrp:KBProxy"

rdf_kbElement = "rrp:KBElement"
rdf_linClass = "rrp:LinguisticClass"
rdf_frame = "rrp:Frame" 
rdf_semantic_pred = "rrp:SemanticPredicate"
rdf_semantic_role = "rrp:SemanticRole"
rdf_lemma = "rrp:Lemma"
rdf_variable = "rrp:Variable"
rdf_syn_form = "rrp:SyntacticForm"
rdf_sel_restriction = "rrp:SelectionalRestriction"
rdf_sel_restriction_list = "rrp:ConstraintList"
rdf_mapping = "rrp:Mapping"
rdf_mapping_group = "rrp:MappingGroup"
rdf_logic_operator = "rrp:logicOperatorName"
rdf_maps_to = "rrp:mapsTo"
rdf_lemma_txt = "rrp:lemmaText"
rdf_role_list = "rrp:roleList"

rdf_has_component = "rrp:hasComponent"
rdf_has_lemma = "rrp:hasLemma"
rdf_has_parameter = "rrp:hasParameter"
rdf_bound_by = "rrp:boundBy"
rdf_has_mapping = "rrp:hasMapping"
rdf_in_kb = "rrp:inKB"

rdf_value = "rrp:varExpression"
rdf_type = "rrp:varType"
rdf_varName = "rrp:varName"
rdf_text_info = "rrp:textInfo"
rdf_param_text = "rrp:paramText"
rdf_syn_expr = "rrp:syntacticExpression"
rdf_description = "rrp:description"
rdf_sentiment_polarity = "rrp:sentimentPolarity"
rdf_example = "rrp:example"

WordNet = "rrp:WordNet"
PropBank = "rrp:PropBank"
VerbNet = "rrp:VerbNet"

idCounter = 1

##############################################################
# RDF/OWL PROLOGUE
##############################################################
prologue = """# baseURI: http://www.ibm.com/{}
# imports: http://www.ibm.com/RRP
# prefix: <http://www.ibm.com/{}#> 

@prefix : <http://www.ibm.com/UL_KB#> .
@prefix Chronos: <http://www.ibm.com/Chronos#> .
@prefix Chronos_Schema: <http://www.ibm.com/Chronos_Schema#> .
@prefix glo: <http://www.ibm.com/GLO_V2#> . 
@prefix rrp: <http://www.ibm.com/RRP#> . 
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix time: <http://www.w3.org/2006/time#> . 
@prefix kairosTagset: <http://www.kairos.com/kairosTagset#> . 
@prefix kairosG: <http://www.ibm.com/kairosG#> . 
@prefix UL_KB: <http://www.ibm.com/UL_KB#> . 
@prefix UL_VN: <http://www.ibm.com/UL_VN#> . 
@prefix UL_PB: <http://www.ibm.com/UL_PB#> . 
@prefix UL_WN: <http://www.ibm.com/UL_WN#> .
<http://www.ibm.com/{}>
  a owl:Ontology ;
  owl:imports <http://www.ibm.com/RRP>  ;
.

 """

###########################################################
# AUXILIARY FUNCTIONS 
###########################################################

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
  _in = _in.replace(".", "_")
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

# from admire-31.2 to 31.2
def get_vn_code(_verb: str) -> str : 
    return _verb.split('-',1)[1]
    
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

def getRoleStrFrom(_list : []) -> str : 
    resultStr = ""
    tempList = []
    for item in _list : 
        if item.startswith("?") : 
            item = item[1:]
        if item not in tempList : 
            tempList.append(item)
            
    for item in tempList :
        if len(resultStr) == 0 : 
            resultStr += item
        else : 
            resultStr += ", " + item
        
    return resultStr    
###########################################################
# INITIALIZATION
###########################################################

def init(_namespace) : 
    
    outputFile.write(prologue.format(_namespace, _namespace, _namespace))
    #Wortnet
    #outputFile.write(WordNet + "\n" )
    #outputFile.write("    a " + kbOverlay + ";\n")
    #outputFile.write("    rdfs:label \"" + "WordNet" + "\";\n")
    #outputFile.write("    rrp:provenance \"" + provenance + "\";\n")
    #outputFile.write("    rrp:identifier \"" + "WordNet_KBProxy" + "\";\n")
    #outputFile.write(". \n\n")
       
    #PropBank
    #outputFile.write(PropBank + "\n" )
    #outputFile.write("    a " + kbOverlay + ";\n")
    #outputFile.write("    rdfs:label \"" + "PropBank" + "\";\n")
    #outputFile.write("    rrp:provenance \"" + provenance + "\";\n")
    #outputFile.write("    rrp:identifier \"" + "PropBank_KBProxy" + "\";\n")
    #outputFile.write(". \n\n")
    
    #Verbnet -- A KB, not a proxy
    #outputFile.write(VerbNet + "\n" )
    #outputFile.write("    a " + KB + ";\n")
    #outputFile.write("    rdfs:label \"" + "VerbNet" + "\";\n")
    #outputFile.write("    rrp:provenance \"" + provenance + "\";\n")
    #outputFile.write("    rrp:identifier \"" + "VerbNet_KBProxy" + "\";\n")
    #outputFile.write(". \n\n")
    outputFile.flush()
 
###########################################################
# RDF/OWL writing functions
###########################################################
    
def writeObj_noLabel(_entityName : str, _class : str, _id : str) :

    global outputFile 
    global provenance
    if ":" in _entityName : 
        outputFile.write(_entityName + "\n" )
    else :
        outputFile.write(":" + _entityName + "\n" )
    outputFile.write("    a " + _class + ";\n")
    outputFile.write("    rrp:provenance \"" + provenance + "\";\n")
    outputFile.write("    rdfs:label \"" + _entityName + "\";\n")
    if len(_id) > 0 :
        outputFile.write("    rrp:identifier \"" + (_id) + "\";\n")
    outputFile.write(". \n\n")
    outputFile.flush()

def writeObj(_entityName : str, _class : str, _id : str, _label: bool) :

    global outputFile , provenance

    if "http://" in _class and not '<' in _class: 
        _class = "<" + _class + ">"
    if ":" not in _entityName  :
        outputFile.write(":" + _entityName + "\n" )
    else : 
        outputFile.write(_entityName + "\n" )
    outputFile.write("    a " + _class + ";\n")
    if _label  :
        outputFile.write("    rdfs:label \"" + _label + "\";\n")
    outputFile.write("    rrp:provenance \"" + provenance + "\";\n")
    if len(_id) > 0 :
        outputFile.write("    rrp:identifier \"" + (_id) + "\";\n")
    outputFile.write(". \n\n")
    outputFile.flush()
    
# subject predicate literal
def writeStmt_toStr(_subj : str, _pred: str, _obj: str) : 
    global outputFile
    startStr = ":"
    if not startStr in _subj :
        _subj = ":" + _subj
    outputFile.write(_subj + " " + _pred + " \"" + _obj + "\" . \n")
    outputFile.flush()
    
# subject predicate literal
def writeStmt_toFloat(_subj : str, _pred: str, _obj: float) : 
    global outputFile
    startStr = ":"
    if not startStr in _subj :
        _subj = ":" + _subj
    outputFile.write(_subj + " " + _pred + " " + str(_obj) + ". \n")
    outputFile.flush()
    
#subject predicate true/false
def writeStmt_toBool(_subj : str, _pred: str, _obj: bool) : 
    global outputFile
    startStr = ":"
    if not startStr in _subj :
        _subj = ":" + _subj
    if _obj : 
        outputFile.write(_subj + " " + _pred + " true . \n")
    else: 
        outputFile.write(_subj + " " + _pred + " false . \n")
    outputFile.flush()
 
# subject predicate object (not literal)
def writeStmt_toObj(_subj : str, _pred: str, _obj: str) : 
    global outputFile
    startStr = ":"
    if not startStr in _subj :
        _subj = ":" + _subj
    if not startStr in _obj :
        _obj = ":" + _obj
    outputFile.write(_subj + " " + _pred + " " + _obj + ". \n")
    outputFile.flush()
    
def clean_vn_param(_param : str) -> str : 
    
    _param = _param.replace('?', '')
    return _param
    
    
######################################################################
# GROUPINGS (From Web file) -- Deprecated by Semlink processing
######################################################################

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



######################################################################
# PROPBANK INGESTION
######################################################################
#### FROM JASON
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


def process_propbank( _namespace : str) : 
    global outputFile, idCounter, provenance, outLog
    global pb_to_params
    
    provenance = "Propbank NLTK"
    for rolesetData  in propbank.rolesets():  
            roleset = rolesetData.attrib["id"]
            if outLog is not None : 
                outLog.write("PB  " + roleset)
            if "make" in roleset : 
                print("PROCESS --> " + roleset)
                
            #outFile.write(fileID + "#" + tagger + "#" + roleset + "#")
            rRoleSet = "UL_PB:" + toRDFStr(roleset) 
  
            if roleset in pbIndex : 
                continue
            
            writeObj(rRoleSet,rdf_kbElement, roleset, roleset)
            writeStmt_toStr(rRoleSet, rdf_lemma_txt, get_pb_lemma(roleset))
            writeStmt_toObj(rRoleSet, rdf_in_kb, PropBank)
            writeStmt_toObj(rRoleSet, "rdf:type", rdf_linClass)
            
            pbIndex.append(roleset)
            pb_to_params[roleset] = {}
            
           
            for role in rolesetData.findall("roles/role"):
                argID = "ARG" + role.attrib['n']
                argDesc = role.attrib['descr']
                name = "UL_PB:" + toRDFStr(roleset.upper()) + "_"  + argID
                if name not in pb_to_params[roleset] : 
                    pb_to_params[roleset][argID] = name
                writeObj(name, rdf_semantic_role, argID, argID)
                writeStmt_toObj(name, rdf_in_kb, PropBank)
                writeStmt_toStr(name, rdf_description, clean_text(argDesc, True))
                writeStmt_toObj(rRoleSet, rdf_has_parameter, name) 
                
            #Process examples
            for example in rolesetData.findall("example") : 
                for textElt in example.findall('text') :  
                    textRaw = textElt.text
                    if textRaw is not None:
                        writeStmt_toStr(rRoleSet, rdf_example, clean_text(textRaw, True))
    provenance = "automatic generation"
######################################################################
# VERBNET INGESTION
######################################################################

        
def get_vn_classes_for(term :str ) -> [] :
    
    return vn.classids(term)

#def get_all_vn_classes() -> [] : 
#    return vn.classids()

def process_wn_proxy( _verbName: str):
    
    #vName_chopped = _verbName.split('%')[0]
    #vName = "WN__" + toRDFStr(vName_chopped )
    if _verbName in wnIndex : 
        return
    rVerbName = "UL_WN:" + toRDFStr(_verbName)
    writeObj(rVerbName, kbProxy, _verbName, _verbName)
    writeStmt_toObj(rVerbName, rdf_in_kb, WordNet)
    wnIndex.append(_verbName)
    
    
def process_pb_proxy(_verbName: str):

   #vName_chopped = _verbName  
   rVerbName = toRDFStr(_verbName)
   #vName = "PB__" + rVerbName
   if rVerbName in pbIndex: 
       return 
   rVerbName = "UL_PB:" + toRDFStr(_verbName)
   writeObj(rVerbName, kbProxy, _verbName, _verbName)
   writeStmt_toObj(rVerbName, rdf_in_kb, PropBank)
   pbIndex.append(_verbName)
    

def process_vn_thematic_roles(_className: str, _rClassName:str) :
    global idCounter, current_vn , vnClassToVars
    
    theClass = current_vn.vnclass(_className)
    vnthemRoles = theClass.findall("THEMROLES/THEMROLE")
    allRoles = ""
    if 'caused_calibratable_cos' in _className : 
        print("DEBUG  " + _className)
    for themRole in vnthemRoles : 
        tType = themRole.get('type')
        rsrName = _rClassName + "_" + tType.strip()
        srNameText = tType.strip()
        writeObj(rsrName, rdf_semantic_role, srNameText, srNameText)
        writeStmt_toObj(_rClassName, rdf_has_parameter,rsrName)
        if len(allRoles) == 0 : 
            allRoles += tType
        else : 
            allRoles += "," + tType
        selRestrs = themRole.findall("SELRESTRS")
        logicPred = "" 
        for srList in selRestrs :           
          logicPred = srList.get('logic') #for the time being we ignore, as all are 'OR'
        themRoleList = themRole.findall("SELRESTRS/SELRESTR")
        if len(themRoleList) > 0 :
            rlName = _rClassName + "_cnsL_" + str(idCounter)            
            lNameText  = _className + " cns list " + str(idCounter)
            idCounter +=1
            writeObj(rlName, rdf_sel_restriction_list, lNameText, lNameText)
            writeStmt_toObj(rsrName, rdf_bound_by , rlName)
        hasLogic = False
        if logicPred and len(logicPred)> 0 : 
            hasLogic = True
            writeStmt_toStr(rlName, rdf_logic_operator, logicPred) 
            logicPred += " ("
        else:  logicPred = ""
        for restr in themRoleList :
              srValue = restr.get('Value') 
              srType = restr.get('type')
              logicPred += " " + srValue + srType + ","
              rName = _rClassName + "_cns_" +  str(idCounter)
              nameText = _className + " constraint " + str(idCounter)
              idCounter +=1
              writeObj(rName, rdf_sel_restriction, nameText, nameText)
              writeStmt_toObj(rlName, rdf_has_component , rName)
              writeStmt_toStr(rName, rdf_type, srType)
              writeStmt_toStr(rName, rdf_value, srValue) 
              writeStmt_toStr(rName, rdf_varName, srValue)
        if logicPred and len(logicPred) > 0 :
            if logicPred[-1] == ',':
                logicPred = logicPred.rstrip(logicPred[-1])
            if hasLogic : 
                logicPred += ")"
            writeStmt_toStr(rsrName, rdf_syn_expr, logicPred)
    # We use the rolelist by computing it directly from the frames. This is more exact
    # writeStmt_toStr(_rClassName, rdf_role_list, allRoles)
    
def process_vn_frames(_className: str, _rClassName:str) :
    
    global idCounter, current_vn, framesToVars, vnClassToVars, provenance
    global vn_to_params
    
    theClass = current_vn.vnclass(_className)
    vnframes = theClass.findall("FRAMES/FRAME")
    
    if _className not in vn_to_params : 
        vn_to_params[_className] = {}

    if 'acquiesce-95.1-1' in _className : 
        print("DEBUG " + _className)
        
    # {Type(Class) : node}
    classPreds = {} 
    classRoleList = []
    for frame in vnframes :  
        #DESCRIPTIOPN
        descF = frame.find("DESCRIPTION")
        numberF = descF.get("descriptionNumber")       
        name = _className + " " +  numberF
        rName = _rClassName + "_" + toRDFStr(numberF)+ "_fr_" + str(idCounter)
        idCounter += 1
        primary = descF.get("primary")
        secondary = descF.get('secondary')
        
        nameTxt = _className + " " + str(numberF)
        writeObj(rName, rdf_frame, numberF, name)
        writeStmt_toObj(_rClassName, rdf_has_component, rName)
        if primary : 
            writeStmt_toStr(rName, rdf_syn_expr , primary)
        if secondary: 
            writeStmt_toStr(rName, rdf_text_info , clean_text(secondary, True))
        #writeStmt_toStr(name, 'rrp:identifier', name)
        #EXAMPLES
        for example in frame.findall('EXAMPLES/EXAMPLE') : 
            writeStmt_toStr(rName, 'rrp:example', clean_text(example.text, True))
            #print(_className + " --> " + clean_text(example.text, True) + "\n")
        #SYNTAX
        synList = current_vn._get_syntactic_list_within_frame(frame)
        txt = ""
        roleList = "" #Incude a list of roles for Jason's service
        for synStr in synList : 
            txt += synStr['pos_tag']
            modifiers = synStr['modifiers']
            if len(modifiers) > 0 : 
                txt += "("
                if 'value' in modifiers and len(modifiers['value']) > 0 :
                    txt += modifiers['value']
                if 'selrestrs' in modifiers and len(modifiers['selrestrs']) > 0 :
                    if txt[-1] == "(" : 
                        txt += " SelRestrs("
                    else : 
                        txt += ", SelRestrs("
                    for synR in modifiers["selrestrs"] :  
                        txt += " [" + synR['type'] + ", " + synR['value'] + "] "                
                    txt += ") "
                if 'synrestrs' in modifiers and len(modifiers['synrestrs']) > 0 :
                    if txt[-1] == "(" :
                        txt += " SynRestrs("
                    else : 
                        txt += ", SynRestrs("
                    for selR in modifiers['synrestrs'] : 
                        txt += " [" + selR['type'] + ", " + selR['value'] + "] "
                    txt += ") "
                txt +=  ") "
        if len(txt)> 0 :
            sfName = rName + "_sf"
            writeObj(sfName , rdf_syn_form, nameTxt + "_syf", nameTxt + "syntactic form")
            writeStmt_toObj(rName, rdf_has_component, sfName)
            writeStmt_toStr(sfName, rdf_text_info, txt)
            #Add the role list for the predicate. 
        #print(_className + " --Syn-> " + txt + "\n")
        #print(_className + " --Syn-> " + str(synStr) + "\n\n")
            
        #PROCESS SEMANTICS         
        semList = current_vn._get_semantics_within_frame(frame)
        predCounter = 1
        #variables = []
        #Predicates per frame
        allRolesList = []
        for semPre in semList : 
            txt = ""
            roleList = ""
            predValue = semPre['predicate_value']
            arguments = semPre['arguments']
            is_negated = semPre["is_negated"]           
            rPredName = rName + "_pred_" + str(predCounter)
            labelPredName = name + " pred " + str(predCounter)
            writeObj(rPredName, rdf_semantic_pred, labelPredName , predValue )
            writeStmt_toObj(rName, rdf_has_component, rPredName)
            if is_negated : 
                writeStmt_toStr(rPredName, rdf_logic_operator , "NOT")
                txt += "NOT "
            #else : 
            #    writeStmt_toBool(predName, rdf_not_operator , False)
            txt += predValue + "("

            for argument in arguments : 
                argValue = argument["value"]
                argType = argument["type"]
                argSimpleValue =  get_vn_varName(argValue)
                argText = argType+ "(" + argValue + ")"
                argCode = argType+ "(" + argSimpleValue + ")"
                if argCode not in classPreds : 
                    classPreds[argCode] = _rClassName + "_" + toRDFStr(argType) + "_" + toRDFStr(argSimpleValue)
                    writeObj(classPreds[argCode], rdf_variable, 
                             argType + "_" + argSimpleValue, 
                             argType + "_" + argSimpleValue)
                    writeStmt_toStr(classPreds[argCode], rdf_value, argSimpleValue)
                    writeStmt_toStr(classPreds[argCode], rdf_type, argType)
                    writeStmt_toStr(classPreds[argCode], rdf_varName, argCode)
                    vn_to_params[_className][argType + "_" + argSimpleValue] = classPreds[argCode]
                
                argNode = classPreds[argCode]
                
                
                if argType != 'Event' : 
                    if argValue not in allRolesList : 
                        allRolesList.append(argValue)
                    if argValue not in classRoleList : 
                        classRoleList.append(argValue) 
                    if len(roleList) == 0 : 
                        roleList = argValue
                    else : 
                        roleList += "," + argValue
                        
                writeStmt_toObj(rPredName, rdf_has_parameter , argNode)    
                argText = argument["type"] + "(" + argument["value"] + ")"
                txt += argText + ","
                
            txt = txt.rstrip(txt[-1]) + ")"
            
            #The variable name must have the context of the frame so it can be 
            #identified. The text form can also be used.             
            #This is the whole text of the predicate
            writeStmt_toStr(rPredName, rdf_text_info, str(predCounter) + "   " + txt)
            writeStmt_toStr(rPredName, rdf_role_list, roleList)
            predCounter += 1
            #print(_className + " --Sem--> " + txt + "\n\n")
        roleListStr = getRoleStrFrom(allRolesList)
        writeStmt_toStr(rName, rdf_role_list, roleListStr) 
        
    roleListStr = getRoleStrFrom(classRoleList)
    writeStmt_toStr(_rClassName, rdf_role_list, roleListStr)         
            
        #   writeStmt_toStr(name, vn_semantics, txt)
  
def process_vn_lemmas(_className: str, _rClassName :str) : 
    
    global current_vn
    
    theClass = current_vn.vnclass(_className)
    for member in theClass.findall("MEMBERS/MEMBER") : 
        vnKey = member.get("name")
        
        if vnKey in lemmasIndex : 
            continue
        
        lemmasIndex.append(vnKey)
        rVnkey = _rClassName + "_lemma_" + toRDFStr(vnKey)
        wn_term = member.get("wn")
        features = member.get("features")
        sentimentPolarity = ""
        
        if features is not None : 
            if "pos_feeling" in features : 
                sentimentPolarity = "positive"
            elif "neg_feeling" in features : 
                sentimentPolarity = "negative"
        
        writeObj(rVnkey, rdf_lemma, vnKey, vnKey)
        writeStmt_toObj(_rClassName, 'rrp:hasComponent', rVnkey)
        writeStmt_toStr(rVnkey,rdf_lemma_txt, vnKey )
        if len(sentimentPolarity) > 0 : 
            writeStmt_toStr(rVnkey, rdf_sentiment_polarity, sentimentPolarity)
            
        #WORDNET For the time being 
        wn_grouping = member.get("wn")
        if wn_grouping and len(wn_grouping) > 0:
           wnList = wn_grouping.split()
           for wn_term in wnList : 
               if len(wn_term) > 0 : 
                   continue
               process_wn_proxy(wn_term)
               rwn_term = "UL_WN:" + toRDFStr(wn_term)
               writeStmt_toObj(rVnkey, 'rrp:hasComponent', rwn_term)    


def process_verbnet( _namespace : str, _provenance : str, _vn, _log: True) : 
  
    global logFile, vnClassToRDF, provenance, current_vn
    
    current_vn = _vn
    provenance = _provenance
    #depends on the reader
    allClasses = current_vn.classids()
    for className in allClasses : 
        subClasses = current_vn.subclasses(className)
        rClassName = "UL_VN:" + toRDFStr(className)
        if "help" in className : 
            print("DEBUG " + className)
        # We need to check for the rClassName because of Verbnet3.4 moving 
        # 3.2 classes to subclasses with different names
        if rClassName not in vnClassToRDF.values() : 
            vnCodeToLemma[className.split('-', 1)[1]] = className.split('-', 1)[0]
            vnClassToRDF[className] = rClassName
            vId = className 
            if ('-') in className : 
                vId = className.split('-')[1]
            writeObj(rClassName, rdf_kbElement , vId, className)
            writeStmt_toObj(rClassName, 'rdf:type', rdf_linClass)
            writeStmt_toObj(rClassName,rdf_in_kb, VerbNet)
            writeStmt_toStr(rClassName, rdf_lemma_txt, get_vn_lemma(className))
            if className in processedGroupingsVN : 
                processedGroupingsVN[className] = "IN VN"
            
            entityToRDF[className] = rClassName
            process_vn_thematic_roles(className, rClassName)
            process_vn_lemmas(className, rClassName)
            process_vn_frames(className, rClassName)
            if _log : 
                logFile.write(className + " , " + str(count_dict()) + ", " + provenance + "\n")
        for subClassName in subClasses : 
            rSubClassName = "UL_VN:" + toRDFStr(subClassName)
            if rSubClassName not in vnClassToRDF.values() : 
                vnCodeToLemma[subClassName.split('-', 1)[1]] = subClassName.split('-', 1)[0]
                vnClassToRDF[subClassName] = rSubClassName
                vId = subClassName 
                if ('-') in subClassName : 
                     vId = subClassName.split('-')[1]
                writeObj(rSubClassName, rdf_kbElement, vId, subClassName)
                writeStmt_toObj(rSubClassName, 'rdf:type', rdf_linClass)
                writeStmt_toObj(rSubClassName,rdf_in_kb, VerbNet)
                writeStmt_toObj(rSubClassName, 'rrp:subConceptOf', rClassName)
                entityToRDF[subClassName] = rSubClassName
                if subClassName in processedGroupingsVN : 
                    processedGroupingsVN[subClassName] = "IN VN"            
               
                process_vn_thematic_roles(subClassName, rSubClassName)
                process_vn_lemmas(subClassName, rSubClassName)
                process_vn_frames(subClassName, rSubClassName)
                if _log : 
                    logFile.write(subClassName + " , " + str(count_dict()) + ", " + provenance + "\n")
    provenance = "automatic extraction"   
    


############################################################
# UNIFIED MAPPING
############################################################ 

def vn_to_node(_class: str, _arg: str) -> str : 
    
    global vn_to_params
    args = vn_to_params[_class]
    
    for argKey in args : 
        label= argKey
        label = label.split("_", -1)[1]
        if label.lower() == _arg.lower() :
            return args[argKey]
    return ""
 
def pb_to_node(_roleset: str, _arg: str) -> str : 
    
    global pb_to_params
    args = pb_to_params[_roleset]
    
    for argKey in args : 
        label= argKey
        
        if label.lower() == _arg.lower() :
            return args[argKey]
    return ""
 
   
    
    
def process_um_v1(_input: str) : 
    global provenance, pbToMap_params, pbToMap, semLinkFromPB 
    global vn_to_params, pb_to_params
    
    oldProvenance = provenance
    provenance = "Unified mapping "
    with open(_input) as iFile:
       mReader = csv.reader(iFile, delimiter=',')
       for row in mReader:
           mappingSource = row[0].strip()
           roleset = row[1].strip()
           verbnetVersion = row[2].strip()
           verbnetClass = row[3].strip()
           mapping = row[4]
           mapping = mapping.replace(";", ",") #Should be 
           # get rid of the internal quotes first...
           mapping = mapping.replace ("\"", "-")
           mapping = mapping.replace("\'", "\"")
           print("----> " + mapping + "\n\n")
           mappingDict = json.loads(mapping)
           
           pb_params = pb_to_params[roleset]
           vn_params = vn_to_params[verbnetClass]
           
           rolesetLemma = roleset.split(".", -1)[0]
           vnLemma = verbnetClass.split("-", 1)[0]
           
           pbName = toRDFStr(roleset)
           mappingRawName = toRDFStr(roleset + "_" + verbnetClass)
           mappingName = "UL_KB:" + mappingRawName
           vnName = toRDFStr(verbnetClass)
           writeObj(mappingName, mappingClass , mappingRawName, mappingRawName)  
           writeStmt_toStr(mappingName, "rrp:provenance" , mappingSource + " " + verbnetVersion)                                         
           writeStmt_toObj("UL_VN:" +  vnName, rdf_has_mapping, mappingName)
           writeStmt_toObj("UL_PB:" + pbName, rdf_has_mapping, mappingName)
           writeStmt_toStr(mappingName, rdf_lemma_txt, rolesetLemma)
           writeStmt_toStr(mappingName, rdf_lemma_txt, vnLemma)
           
           for PBArg in mappingDict : 
               VNArg = mappingDict[PBArg]['vnArg']
               vnNode = vn_to_node(verbnetClass, VNArg)
               pbNode = pb_to_node(roleset, PBArg)               
               writeStmt_toObj(pbNode, rdf_maps_to ,vnNode)
               writeStmt_toObj(vnNode, rdf_maps_to ,pbNode)
    provenance = oldProvenance 
    

# Ingests Verbnet and Propbank
#  (1) Verbnet (3.4, 3.3 and 3.2)   
#  (2) Propbank (from NLTK)
#  (3) Mappings from PB to VN from Semlink
def process_UL_KB_V5(_input:str, _output: str, _namespace :str, _log : bool) : 
    
    global outputFile, logFile, processedClasses, vn, provenance
    
    logFile= open("/Users/rosariouceda-sosa/Downloads/UL_KB_LOG.txt", "w")
    outputFile = open(_output, "w")
    #.ttl file prolog
    init(_namespace)
    
    #PROPBANK uses NLTK to process propbank. No mappings are used. 
    #_namespace = "UL_PB"
    print("-----> PROCESSING PROPBANK")
    process_propbank(_namespace)
    
   
    #VERBNET -- Uses NLTK    
    _namespace = "UL_VN"
    print("-----> PROCESSING VERBNET 3.4")
    process_verbnet(_namespace, "verbnet3.4", vn_dict["verbnet3.4"],_log )
    print("-----> PROCESSING VERBNET 3.3")
    process_verbnet(_namespace, "verbnet3.3", vn_dict["verbnet3.3"],_log )
    print("-----> PROCESSING VERBNET 3.2")
    process_verbnet(_namespace, "verbnet3.2", vn_dict["verbnet3.2"],_log )


    #PROCESS THE MAPPINGS FROM EXCEL
    process_um_v1("/Users/rosariouceda-sosa/Downloads/UM_V1_MAPPINGS.csv")
    
    print("-----> DONE")
    outputFile.close()
    
if __name__ == '__main__':
       
    workDir = "/Users/rosariouceda-sosa/Downloads/"
    outFileName = "/Users/rosariouceda-sosa/Downloads/UL_KB_V5.ttl"
    namespace = "UL_KB" # THE GENERAL NAMESPACE
    
    workDir = "/Users/rosariouceda-sosa/Downloads/verbnet/"
    inputGroupings = VN_DIR + "otherdata/all_verbnet_grouping.json"


    # INGESTION PROCESS 
    process_UL_KB_V5(inputGroupings, outFileName, namespace, False)
    
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
    
    
    