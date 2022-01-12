#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 21:07:04 2021

@author: rosariouceda-sosa

Access to the RDF/OWL UL_KB_V4 graph
The differences with the previous version is that the 
function ulkb_sem_predicates_LONG and ulkb_sem_predicates_SHORT now returns the rolesets
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from nltk.stem import PorterStemmer
import requests
import operator
import json

try:
    from . import config
except ImportError:
    import config

# from csv import reader
# GLOBALS
schemaLibrary = {}
schemaIndex = {}  # qNode, label

# UL_KB ##################################################################

query_prefix = ("prefix rrp: <http://www.ibm.com/RRP#> \n"
                "prefix glo: <http://www.ibm.com/GLO_V2#> \n"
                "prefix ulvn: <http://www.ibm.com/UL_VN#> \n"
                "prefix ulwn: <http://www.ibm.com/UL_WN#> \n"
                "prefix ulpb: <http://www.ibm.com/UL_PB#> \n"
                "prefix ulkb: <http://www.ibm.com/UL_KB#> \n")

# THIS IS THE SERVER, which is taken from config
sparql = SPARQLWrapper(config.SPARQL_ENDPOINT)
# THIS IS A LOCAL VERSION (ROSARIO'S)
# sparql = SPARQLWrapper("http://127.0.0.1:9999/blazegraph/namespace/UL_KB_V0")

query_roles_for_pb_str = """SELECT DISTINCT ?verb ?pbSemRole ?pbSemRoleDesc ?vnVerbLabel ?vnVarType ?vnVarName WHERE {{
  ?verb rdfs:label "{}" . 
  #?verb rrp:inKB rrp:PropBank .
  ?verb rrp:hasParameter ?pbParam .
  ?pbParam rrp:description ?pbSemRoleDesc .  
  ?pbParam rdfs:label ?pbSemRole . 
  OPTIONAL {{
  ?vnVerb rrp:inKB rrp:VerbNet . 
  ?vnVerb rdfs:label ?vnVerbLabel . 
  ?vnVerb rrp:hasComponent ?vnFrame . 
  ?vnFrame rrp:hasComponent ?semPred . 
  ?semPred rrp:hasParameter ?vnParam . 
  ?pbParam rrp:mapsTo ?vnParam . 
  ?vnParam rrp:varType ?vnVarType . 
  ?vnParam rrp:varName ?vnVarName . 
  }}
  }}
"""

query_roles_for_lemma_str = """SELECT DISTINCT ?pbSemRole ?vnVerbLabel ?pbVerbLabel ?vnVarType ?vnVarName WHERE {{  
  ?entity rdfs:label "{}" . 
  ?entity a rrp:Lemma . 
  ?vnVerb rrp:hasComponent ?entity .
  ?vnVerb rrp:inKB rrp:VerbNet . 
  ?vnVerb rdfs:label ?vnVerbLabel . 
  ?verb rrp:hasParameter ?pbParam . 
  ?verb rrp:inKB rrp:PropBank. 
  ?verb rdfs:label ?pbVerbLabel . 
  ?pbParam rdfs:label ?pbSemRole . 
  ?vnVerb rrp:hasComponent ?vnFrame . 
  ?vnFrame rrp:hasComponent ?semPred . 
  ?semPred rrp:hasParameter ?vnParam . 
  ?pbParam rrp:mapsTo ?vnParam . 
  ?vnParam rrp:varType ?vnVarType . 
  ?vnParam rrp:varName ?vnVarName . 
  }} """

query_all_parents_str = """SELECT DISTINCT ?entity ?entityLabel {{  
     <{}> wdt:P31* ?entityClass . 
     ?entityClass wdt:P279* ?entity . 
     ?entity rdfs:label ?entityLabel .  
     FILTER (lang(?entityLabel) = 'en')
     }}  """

query_label_str = """SELECT DISTINCT ?entityLabel {{
     <{}>  rdfs:label ?entityLabel .  
     FILTER (lang(?entityLabel) = 'en') 
  }}
"""

query_map_classes = """SELECT DISTINCT  ?otherEntityLabel ?provenance ?KB  WHERE {{
                  <{}> rrp:hasMapping ?mapping . 
                  ?otherEntity rrp:hasMapping ?mapping .
                  ?otherEntity rrp:provenance ?provenance . 
                  ?otherEntity rrp:inKB ?KB .               
                  ?otherEntity rdfs:label ?otherEntityLabel. 
                }} ORDER BY ?otherEntity
                  """

query_sem_predicates_vn_str = """SELECT DISTINCT ?example ?roleList ?operator ?semanticPredicate ?semanticPredicateLabel ?param ?type ?value  WHERE {{
                  {} rrp:hasComponent ?frame . 
                  ?frame rrp:example ?example . 
                  OPTIONAL {{ ?frame rrp:roleList ?roleList }} . 
                  ?frame rrp:hasComponent ?semanticPredicate . 
                  ?semanticPredicate a rrp:SemanticPredicate .
                  ?semanticPredicate rdfs:label ?semanticPredicateLabel. 
                  ?semanticPredicate rrp:hasParameter ?param . 
                  OPTIONAL {{
                    ?semanticPredicate rrp:logicOperatorName ?operator .  
                   }}
                  ?param rrp:varType ?type . 
                  ?param rrp:varName ?value . 
                }} ORDER BY ?semanticPredicate
                  """

#If you want the more exact result, use   FILTER (?label = "{}")  instead of regex 
query_sem_predicates_str = """SELECT DISTINCT ?example ?roleList ?operator ?semanticPredicate ?semanticPredicateLabel ?param ?type ?vnVarName  WHERE {{
                  ?entity rdfs:label ?label . 
                  FILTER regex(?label, "{}", "i") . 
                  ?entity rrp:hasComponent ?frame . 
                  ?frame rrp:example ?example . 
                  OPTIONAL {{ ?frame rrp:roleList ?roleList }} . 
                  ?frame rrp:hasComponent ?semanticPredicate . 
                  ?semanticPredicate a rrp:SemanticPredicate .
                  ?semanticPredicate rdfs:label ?semanticPredicateLabel. 
                  ?semanticPredicate rrp:hasParameter ?param . 
                  OPTIONAL {{
                    ?semanticPredicate rrp:logicOperatorName ?operator .  
                   }}
                  ?param rrp:varType ?type . 
                  ?param rrp:varName ?vnVarName .
                }} ORDER BY ?semanticPredicate
                  """

query_check_verb_name_str = """SELECT DISTINCT ?entity ?provenance  WHERE {{
  {{ ?entity a rrp:Lemma }} UNION {{ ?entity a rrp:LinguisticClass }} 
  ?entity rdfs:label ?name . 
  FILTER regex(?name, "{}", "i")
  ?entity rrp:provenance ?provenance. 
}} ORDER BY ?mapping"""


query_pb_lemma_str = """SELECT DISTINCT ?propbankVerb ?lemma  WHERE {{
  ?propbankVerbNode rdfs:label ?propbankVerb . 
  ?propbankVerbNode rrp:lemmaText ?lemma . 
   ?propbankVerbNode a rrp:LinguisticClass . 
  ?propbankVerbNode rrp:inKB rrp:PropBank . 
  
  }} ORDER BY ?propbankVerb
"""

query_vn_lemma_str = """SELECT DISTINCT ?verbnetVerb ?lemma  WHERE {
  ?verbnetNode rdfs:label ?verbnetVerb . 
  ?verbnetNode rrp:hasComponent ?lemmaNode . 
  ?lemmaNode rrp:lemmaText ?lemma . 
  ?verbnetNode a rrp:LinguisticClass . 
  ?verbnetNode rrp:inKB rrp:VerbNet . 
  
} ORDER BY ?verbnetVerb
"""

query_lemma_for_pbverb_str = """SELECT DISTINCT ?lemma ?argument  WHERE {{
  ?propbankVerbNode rdfs:label "{}" . 
  ?propbankVerbNode rrp:lemmaText ?lemma . 
  ?propbankVerbNode a rrp:LinguisticClass . 
  ?propbankVerbNode rrp:inKB rrp:PropBank . 
  ?propbankVerbNode rrp:hasParameter ?param . 
  ?param rdfs:label ?argument . 
  }} ORDER BY ?propbankVerb
"""

query_lemma_for_vnverb_str = """SELECT DISTINCT ?verbnetNode ?verbnetVerb ?roleList WHERE {{
  ?verbnetNode rdfs:label ?verbnetVerb . 
  ?verbnetNode rrp:hasComponent ?lemmaNode . 
  ?lemmaNode rrp:lemmaText ?lemmaText . 
  FILTER regex(?lemmaText, "^{}$", "i")
  ?verbnetNode rrp:hasComponent ?frame . 
  ?frame rrp:roleList ?roleList . 
}} ORDER BY ?verbnetVerb
"""

query_args_for_vnverb_str = """SELECT DISTINCT ?vnVerbLabel ?arg WHERE {{ 
  ?vnVerb a rrp:LinguisticClass . 
  ?vnVerb rrp:inKB rrp:VerbNet . 
  ?vnVerb rdfs:label "{}" . 
  ?vnVerb rrp:hasComponent ?frame . 
  ?frame rrp:hasComponent ?pred . 
  ?pred rrp:hasParameter ?param . 
  ?param rdfs:label ?arg . 
  
  }} ORDER BY ?vnVerbLabel

"""

query_pb_roles_by_lemma_str = """SELECT DISTINCT ?verb ?pbSemRole ?pbSemRoleDesc ?vnVerbLabel ?vnVarType ?vnVarName WHERE {{
  ?verb a rrp:LinguisticClass . 
  ?verb rrp:inKB rrp:PropBank . 
  ?verb rrp:lemmaText "^{}$" .  
  
  ?verb rrp:hasParameter ?pbParam .
  ?pbParam rrp:description ?pbSemRoleDesc .  
  ?pbParam rdfs:label ?pbSemRole . 
  ?vnVerb rrp:inKB rrp:VerbNet . 
  ?vnVerb rdfs:label ?vnVerbLabel . 
  ?vnVerb rrp:hasComponent ?vnFrame . 
  ?vnFrame rrp:hasComponent ?semPred . 
  ?semPred rrp:hasParameter ?vnParam . 
  ?pbParam rrp:mapsTo ?vnParam . 
  ?vnParam rrp:varType ?vnVarType . 
  ?vnParam rrp:varName ?vnVarName . 
  }}"""


###############################################################################
# AUXILIARY FUNCTIONS
###############################################################################

# Retrieves the equivalence classes for all entities.

def analyze_coverage_text(_entries: {}, _output: str):
    max = -1
    counter = 0
    outDict = {}
    for entry in _entries:
        if "COVID-19 pandemic in" in entry:
            continue
        verbList = _entries[entry]
        for rawVerb in verbList:
            verb = stem_verb(rawVerb)
            counter += 1
            if len(verb) == 0:
                continue
            if verb in outDict:
                continue
            listItems = check_verb_name(verb)
            if len(listItems) > 0:
                outDict[verb] = "YES"
                print("process " + verb + ", YES")
            else:
                outDict[verb] = "NO"
                print("process " + verb + ", NO")
        if max > 0 and counter > max:
            break

    with open(_output, 'w') as f:
        for key, value in outDict.items():
            f.write('%s:%s\n' % (key, value))
        # if verbList in ourDict:
        #    continue

    f.close()


def link_to_terms_list(_list: []) -> []:
    resultList = []
    for link in _list:
        resultList.append(link.split['/'])


def check_verb_name(_name: str) -> {}:
    query_text = query_check_verb_name_str.format(_name)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    returnResults = {}
    for result in results["results"]["bindings"]:
        verb = result["entity"]["value"]
        provenance = result["provenance"]["value"]
        returnResults[verb] = provenance
    return returnResults


def stem_verb(_inputVerb: str) -> str:
    ps = PorterStemmer()
    return ps.stem(_inputVerb)

#####################################################################
# ANALYSIS  -- ACCESS THROUGH VERBNET LEMMAS 
# 
#####################################################################

def analyze_pb_vn_lemmas(_outFile : str) : 

    #pb {vn verbs}
    pb_index = {}
    query_text = query_pb_lemma_str
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()    
    for result in results["results"]["bindings"]:
        name = result["propbankVerb"]["value"]
        lemma = result["lemma"]["value"]
        pb_index[name] = {}
        pb_index[name]["lemma"] = lemma
        
    
    for pbVerb in pb_index : 
        pbDict = pb_index[pbVerb]
        query_text = query_roles_for_pb_str.format(pbVerb)
        sparql.setQuery(query_prefix + query_text)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
      
        for result in results["results"]["bindings"]:
            vnVerbLabel = result["vnVerbLabel"]["value"]
            if 'vnVerbs' not in pbDict : 
                pbDict["vnVerbs"] = []
            pbDict["vnVerbs"].append(vnVerbLabel)
    
        
    
    #Try the maps ?verbnetNode ?verbnetVerb ?roleList
    query_text = query_vn_lemma_str
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()    
    for result in results["results"]["bindings"]:
        verbnetVerb = result["verbnetVerb"]["value"]
        roleList = result["roleList"]["value"]
        
    
    query_text = query_vn_lemma_str
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()    
    for result in results["results"]["bindings"]:
        name = result["verbnetVerb"]["value"]
        lemma = result["lemma"]["value"]
        for pbVerb in pb_index: 
            pbDict = pb_index[pbVerb]
            if lemma == pbDict["lemma"]: 
                if "vnVerbs" not in pbDict : 
                    pbDict["vnVerbs"] = []             
                pbDict["vnVerbs"].append(name)
                
    
    with open(_outFile, 'w') as f: 
       for pbVerb in pb_index : 
           vList = [] 
           if "vnVerbs" in pb_index[pbVerb]: 
               vList = pb_index[pbVerb]["vnVerbs"]
           if len(vList) == 0 :
               f.write(pbVerb + "," + pb_index[pbVerb]["lemma"] + "\n")
           else : 
               for verb in vList : 
                    f.write(pbVerb + "," + pb_index[pbVerb]["lemma"] + "," + verb + "\n")
    
    f.close()
    

#####################################################################
# API  -- ulkb_pb_vn_mappings("enter.01")
# Usage : from a propbank verb, it gives the mappings for it. Right 
#         now it gets 
#####################################################################
def ulkb_pb_vn_mappings(_pbName: str, _lemmaMatching = True, _oneLemma = False) -> {}:
    returnResults = []
    query_text = query_roles_for_pb_str.format(_pbName)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    returnResults = {}
    # ?verb ?pbSemRole ?vnVerbLabel ?vnParamLabel
    verbResults = {}

    returnResults["info"] = "semantic roles for " + _pbName
    returnResults["provenance"] = "Unified Mapping"
    
    vnMapsFound = False
    
    pbTRoles = {}
    
    # ?verb ?pbSemRole ?pbSemRoleDesc ?vnVerbLabel ?vnVarType ?vnVarName
    
    for result in results["results"]["bindings"]:
        pbSemRole = result["pbSemRole"]["value"]
        pbSemRoleDesc = result["pbSemRoleDesc"]["value"]
        if pbSemRole not in pbTRoles : 
            pbTRoles[pbSemRole] = pbSemRoleDesc
        if "vnVerbLabel" in result :  
            vnVerbLabel = result["vnVerbLabel"]["value"]
            vnMapsFound = True
            vnVarType = result["vnVarType"]["value"]
            vnVarExpression = result["vnVarName"]["value"]
            if vnVerbLabel not in verbResults:
                verbResults[vnVerbLabel] = {}
            curVerb = verbResults[vnVerbLabel]
            if pbSemRole not in curVerb:
                curVerb[pbSemRole] = vnVarType + "(" + vnVarExpression + ")"
        # print(pbSemRole + "\t(" + vnVerbLabel + ", " + vnParamLabel + ")")

    if  _lemmaMatching and len(verbResults) == 0 :
        lemma = _pbName 
        if "." in _pbName: 
            lemma = _pbName.split(".", -1)[0]
        return ulkb_lemma_mappings(lemma, pbTRoles, _pbName)
    returnResults[_pbName] = verbResults
    return returnResults

#####################################################################
# API  -- ulkb_lemma_mappings("put")
# Usage: from a lemma, get a list of mappings from pb to vn that 
#           correspond to that lemma
#####################################################################

def ulkb_lemma_mappings(_lemma: str, _pbRoles = [],  _roleset = "") -> {}:
    returnResults = []
    query_text = query_roles_for_lemma_str.format(_lemma)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    returnResults = {}
    # pbVerb [?vnVerbLabel : pbVerbArg ?vnVarType ?vnVarExpression
    verbResults = {}

    for result in results["results"]["bindings"]:
        pbSemRole = result["pbSemRole"]["value"]
        vnVerbLabel = result["vnVerbLabel"]["value"]
        pbVerbLabel = result["pbVerbLabel"]["value"]
        vnVarType = result["vnVarType"]["value"]
        vnVarName = result["vnVarName"]["value"]
        # The vnVerb
        if pbVerbLabel not in verbResults:
            verbResults[pbVerbLabel] = {}
        curpbVerb = verbResults[pbVerbLabel]
        
        if vnVerbLabel not in curpbVerb : 
            curpbVerb[vnVerbLabel] = {}
        curvnVerb = curpbVerb[vnVerbLabel]
            
        if pbSemRole not in curvnVerb:
            curvnVerb[pbSemRole] = vnVarType + "(" + vnVarName + ")"
        # print(pbSemRole + "\t(" + vnVerbLabel + ", " + vnParamLabel + ")")
    if len(_roleset) > 0 : 
        returnResults["info"] = "NO semantic mapping for " + _roleset + ", use lemma " + _lemma
    else : 
        returnResults["info"] = "semantic roles for lemma " + _lemma
    returnResults[_lemma] = verbResults
    
    if len(_pbRoles) > 0 : 
       return one_mappingResult(_lemma, _roleset, _pbRoles, verbResults) 
        
    return returnResults


#INTERNAL, SELECTS ANY ONE MATCHING PAIR 
def one_mappingResult(_lemma: str, _roleset: str, _pbRoles: {}, _returnResults : {}) :
    
    #iterated through the results and see (1) which results are more common: 
        
    tempResults = []
    mostMatched = 0 
    bestResult = {}
    toDelete = []
    for pbVerb in _returnResults: 
        vnVerbDict = _returnResults[pbVerb]
        for vnVerb in vnVerbDict : 
            args = vnVerbDict[vnVerb]
            matched = 0 
            for role in _pbRoles : 
                if role in  args : 
                    matched +=1
                else : 
                   toDelete.append(role) 
            if matched > mostMatched : 
                mostMatched = matched
                bestResult = vnVerbDict
            else : 
                toDelete = []
    
    if len(bestResult) == 0 :
        return {"info": "NO semantic mappings for " + _roleset + ", or its lemma",
    _lemma: {}}
    
    #Let's make sure all the mappings are right. 
    for item in toDelete:  
        for vnVerb in bestResult : 
            args = vnVerbDict[vnVerb]
            args.pop(item, None)
            
    returnResults = {}
    returnResults[_roleset] = bestResult
    returnResults["information"] = "Map lemma " + _lemma + ", as " + _roleset
    returnResults["provenance"] = "Unified Mapping"
                    
    return returnResults                
    
   
#####################################################################
# API  -- ulkb_sem_roles_for_pb_by_role("enter.01") to be deprecated
# Usage : from a propbank verb, it gives the semantic role mappings
#         for it and returns results after arranging by roles
#####################################################################
def ulkb_sem_roles_for_pb_by_role(_pbName: str) -> {}:
    query_text = query_roles_for_pb_str.format(_pbName)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # ?verb ?pbSemRole ?vnVerbLabel ?vnParamLabel
    verbResults = {}
    for result in results["results"]["bindings"]:
        pbSemRole = result["pbSemRole"]["value"]
        pbSemRoleDesc = result["pbSemRoleDesc"]["value"]
        vnVerbLabel = result["vnVerbLabel"]["value"]
        vnVarExpression = result["vnVarName"]["value"]
        if pbSemRole not in verbResults:
            verbResults[pbSemRole] = []
        verbResults[pbSemRole].append({
            "vncls": "-".join(vnVerbLabel.split("-")[1:]),
            "vntheta": vnVarExpression.lower(),
            "description": pbSemRoleDesc
        })
    return verbResults



#####################################################################
# API  -- ulkb_sem_predicates_SHORT("escape-51.1-2")
# Usage: from a VN verb, get a list of its semantic predicates. The 
#       predicate expressions are strings 
#####################################################################
def ulkb_sem_predicates_SHORT(_verb: str) -> []:
    global query_prefix

    query_text = query_sem_predicates_str.format(_verb)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    output = []
    thisFrame = {}
    output.append(thisFrame)
    curPredicateID = ""
    thisPredicate = {}
    for result in results["results"]["bindings"]:
        example = result["example"]["value"]

        if 'example' not in thisFrame:
            thisFrame['example'] = example
            
        if 'roleList' in result and 'roleList' not in thisFrame:
            thisFrame['roleList'] = result['roleList']['value'].split(',')

        if example != thisFrame['example']:
            thisFrame = {}
            output.append(thisFrame)
            thisFrame['example'] = example
            curPredicateID = ""
        thisPredicateID = result["semanticPredicate"]["value"]

        if 'predicates' not in thisFrame:
            thisFrame['predicates'] = []
        predicates = thisFrame['predicates']
        
       
        if thisPredicateID != curPredicateID:
            thisPredicate = {}
            predicates.append(thisPredicate)
            curPredicateID = thisPredicateID

        # predicateText = result["predicateText"]["value"]
        predLabel = result["semanticPredicateLabel"]["value"]

        thisPredicate['label_predicate'] = predLabel
        if "operator" in result:
            thisPredicate['operator'] = result["operator"]["value"]

        if 'params' not in thisPredicate:
            thisPredicate['params'] = []
        params = thisPredicate['params']
        params.append(result["type"]["value"] + "(" + result["vnVarName"]["value"] + ")")
        # thisPredicate['type'] = result["type"]["value"]
        # thisPredicate['value'] = result["value"]["value"]
        # print(example + " " + " " +  thisPredicateID + " " +  predLabel + " " +
        #      result["type"]["value"] + " " + result["value"]["value"] )
    return output


#####################################################################
# API  -- ulkb_sem_predicates_SHORT("escape-51.1-2")
# Usage: from a VN verb, get a list of its semantic predicates. The 
#       predicate expressions are independent json elements 
#####################################################################
def ulkb_sem_predicates_LONG(_verb: str) -> []:
    global query_prefix

    query_text = query_sem_predicates_str.format(_verb)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    output = []
    thisFrame = {}
    output.append(thisFrame)
    curPredicateID = ""
    thisPredicate = {}

    for result in results["results"]["bindings"]:
        example = result["example"]["value"]

        if 'example' not in thisFrame:
            thisFrame['example'] = example
        if 'roleList' in result and 'roleList' not in thisFrame:
            thisFrame['roleList'] = result['roleList']['value'].split(',')
            
        if example != thisFrame['example']:
            thisFrame = {}
            output.append(thisFrame)
            thisFrame['example'] = example
            curPredicateID = ""
        thisPredicateID = result["semanticPredicate"]["value"]

        if 'predicates' not in thisFrame:
            thisFrame['predicates'] = []
        predicates = thisFrame['predicates']

        if thisPredicateID != curPredicateID:
            thisPredicate = {}
            predicates.append(thisPredicate)
            curPredicateID = thisPredicateID

        # predicateText = result["predicateText"]["value"]
        predLabel = result["semanticPredicateLabel"]["value"]

        thisPredicate['label_predicate'] = predLabel
        thisPredicate['id_predicate'] = curPredicateID
        if "operator" in result:
            thisPredicate['operator'] = result["operator"]["value"]

        if 'params' not in thisPredicate:
            thisPredicate['params'] = []
        params = thisPredicate['params']
        params.append({'type': result["type"]["value"], 'value': result["vnVarName"]["value"]})
        # thisPredicate['type'] = result["type"]["value"]
        # thisPredicate['value'] = result["value"]["value"]
        # print(example + " " + " " +  thisPredicateID + " " +  predLabel + " " +
        #      result["type"]["value"] + " " + result["value"]["value"] )
    return output


def ulkb_sem_predicates_for_lemma_SHORT(_verb: str) -> []:
    global query_prefix

    query_text = query_sem_predicates_str.format(_verb)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    output = []
    thisFrame = {}
    output.append(thisFrame)
    curPredicateID = ""
    thisPredicate = {}
    for result in results["results"]["bindings"]:
        example = result["example"]["value"]

        if 'example' not in thisFrame:
            thisFrame['example'] = example
        if example != thisFrame['example']:
            thisFrame = {}
            output.append(thisFrame)
            thisFrame['example'] = example
            curPredicateID = ""
        thisPredicateID = result["semanticPredicate"]["value"]
        
        if 'roleList' in result and 'roleList' not in thisFrame:
            thisFrame['roleList'] = result['roleList']['value'].split(',')

        if 'predicates' not in thisFrame:
            thisFrame['predicates'] = []
        predicates = thisFrame['predicates']

        if thisPredicateID != curPredicateID:
            thisPredicate = {}
            predicates.append(thisPredicate)
            curPredicateID = thisPredicateID

        # predicateText = result["predicateText"]["value"]
        predLabel = result["semanticPredicateLabel"]["value"]

        thisPredicate['label_predicate'] = predLabel
        if "operator" in result:
            thisPredicate['operator'] = result["operator"]["value"]

        if 'params' not in thisPredicate:
            thisPredicate['params'] = []
        params = thisPredicate['params']
        params.append(result["type"]["value"] + "(" + result["expression"]["value"] + ")")
        # thisPredicate['type'] = result["type"]["value"]
        # thisPredicate['value'] = result["value"]["value"]
        # print(example + " " + " " +  thisPredicateID + " " +  predLabel + " " +
        #      result["type"]["value"] + " " + result["value"]["value"] )
    return output


############################################################
# API -- return the current version
############################################################
def get_ulkb_info() -> {}:
     
        info = {}
        info["ulkb service"] = config.SPARQL_ENDPOINT
        
        return info


if __name__ == '__main__':
    # print(str(check_verb_name("MIMI")))

    # TEST MAPPING OF SEMANTIC ROLES
     #output = ulkb_pb_vn_mappings("lead.01")
     #output = ulkb_pb_vn_mappings("make_out.23")
     #print(str(output))
     
#     output = ulkb_lemma_mappings("talk")
     #print(str(output))
    #output = ulkb_pb_vn_mappings("make_out.23", True, True)
    
    # TEST SEMANTIC PREDICATES
    output = ulkb_sem_predicates_LONG("escape-51.1-1-1")
    # print(str(output))
    
    print(str(output))

    #print("\nulkb_sem_predicates_SHORT: escape-51.1")
    #output = ulkb_sem_predicates_SHORT("escape-51.1")
    #print(str(output))

    #print("\nulkb_sem_predicates_SHORT: escape-51.1")
    #output = ulkb_sem_predicates_LONG("escape-51.1")
    #print(str(output))

    # TEST API WITH LEMMAS
    #print("\nCalling ulkb_sem_roles_for_lemma for make_out ...")
    #output = ulkb_sem_roles_for_lemma("make_out")
    #print(str(output))

    #print("\nCalling ulkb_sem_roles_for_pb_by_role for carry.01 ...")
    #output = ulkb_sem_roles_for_pb_by_role("carry.01")
    #print(str(output))
    
    #ANALYZE ALL THE VERBNETS
    #outFile = "/Users/rosariouceda-sosa/Downloads/ULKBV4_PB_VN.csv"
    #analyze_pb_vn_lemmas(outFile )
