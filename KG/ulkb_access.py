#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 21:07:04 2021

@author: rosariouceda-sosa
"""

import requests
from nltk.stem import PorterStemmer
from SPARQLWrapper import JSON, SPARQLWrapper

from app_config import config

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

query_roles_for_pb_str = """SELECT DISTINCT ?verb ?pbSemRole ?pbSemRoleDesc ?vnVerbLabel ?vnVarType ?vnVarExpression WHERE {{
  ?verb rdfs:label "{}" . 
  #?verb rrp:inKB rrp:PropBank .
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
  ?vnParam rrp:varExpression ?vnVarExpression . 
  }}
"""

query_roles_for_lemma_str = """SELECT DISTINCT ?pbSemRole ?vnVerbLabel ?vnVarType ?vnVarExpression WHERE {{  
  ?entity rdfs:label "{}" . 
  ?entity a rrp:Lemma . 
  ?vnVerb rrp:hasComponent ?entity .
  ?vnVerb rrp:inKB rrp:VerbNet . 
  ?vnVerb rdfs:label ?vnVerbLabel . 
  ?verb rrp:hasParameter ?pbParam . 
  ?verb rrp:inKB rrp:PropBank. 
  ?pbParam rdfs:label ?pbSemRole . 
  ?vnVerb rrp:hasComponent ?vnFrame . 
  ?vnFrame rrp:hasComponent ?semPred . 
  ?semPred rrp:hasParameter ?vnParam . 
  ?pbParam rrp:mapsTo ?vnParam . 
  ?vnParam rrp:varType ?vnVarType . 
  ?vnParam rrp:varExpression ?vnVarExpression . 
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

query_sem_predicates_node_str = """SELECT DISTINCT ?example ?operator ?semanticPredicate ?semanticPredicateLabel ?param ?type ?value  WHERE {{
                  {} rrp:hasComponent ?frame . 
                  ?frame rrp:example ?example . 
                  ?frame rrp:hasComponent ?semanticPredicate . 
                  ?semanticPredicate a rrp:SemanticPredicate .
                  ?semanticPredicate rdfs:label ?semanticPredicateLabel. 
                  ?semanticPredicate rrp:hasParameter ?param . 
                  OPTIONAL {{
                    ?semanticPredicate rrp:logicOperatorName ?operator .  
                   }}
                  ?param rrp:varType ?type . 
                  ?param rrp:varName ?value .
                  ?semanticPredicate rrp:textInfo ?predicateText .  
                }} ORDER BY ?semanticPredicate
                  """

query_sem_predicates_str = """SELECT DISTINCT ?example ?operator ?semanticPredicate ?semanticPredicateLabel ?param ?type ?expression  WHERE {{
                  ?entity rdfs:label ?label . 
                  FILTER regex(?label, "{}", "i")
                  ?entity rrp:hasComponent ?frame . 
                  ?frame rrp:example ?example . 
                  ?frame rrp:hasComponent ?semanticPredicate . 
                  ?semanticPredicate a rrp:SemanticPredicate .
                  ?semanticPredicate rdfs:label ?semanticPredicateLabel. 
                  ?semanticPredicate rrp:hasParameter ?param . 
                  OPTIONAL {{
                    ?semanticPredicate rrp:logicOperatorName ?operator .  
                   }}
                  ?param rrp:varType ?type . 
                  ?param rrp:varName ?value .
                  ?param rrp:varExpression ?expression . 
                  ?semanticPredicate rrp:textInfo ?predicateText .  
                }} ORDER BY ?semanticPredicate
                  """

query_check_verb_name_str = """SELECT DISTINCT ?entity ?provenance  WHERE {{
  {{ ?entity a rrp:Lemma }} UNION {{ ?entity a rrp:LinguisticClass }} 
  ?entity rdfs:label ?name . 
  FILTER regex(?name, "{}", "i")
  ?entity rrp:provenance ?provenance. 
}} ORDER BY ?mapping"""


###############################################################################
# AUXILIARY FUNCTIONS
###############################################################################

def get_label(_entity: str) -> str:
    global WDURI
    if WDURI not in _entity:
        _entity = WDURI + _entity
    query = query_label_str.format(_entity)
    r = requests.get(url_CURRENT, params={'format': 'json', 'query': query})
    resData = r.json()
    for result in resData["results"]["bindings"]:
        return result["entityLabel"]["value"]
        #
    return ""


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
# API  -- ulkb_pb_vn_mappings("enter.01")
# Usage : from a propbank verb, it gives the mappings for it. Right 
#         now it gets 
#####################################################################
# TO DEPRECATE
def ulkb_sem_roles_for_pb(_pbName: str) -> {}:
    return ulkb_pb_vn_mappings(_pbName)


def ulkb_pb_vn_mappings(_pbName: str) -> {}:
    returnResults = []
    query_text = query_roles_for_pb_str.format(_pbName)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    returnResults = {}
    # ?verb ?pbSemRole ?vnVerbLabel ?vnParamLabel
    verbResults = {}

    for result in results["results"]["bindings"]:
        pbSemRole = result["pbSemRole"]["value"]
        vnVerbLabel = result["vnVerbLabel"]["value"]
        vnVarType = result["vnVarType"]["value"]
        vnVarExpression = result["vnVarExpression"]["value"]
        if vnVerbLabel not in verbResults:
            verbResults[vnVerbLabel] = {}
        curVerb = verbResults[vnVerbLabel]
        if pbSemRole not in curVerb:
            curVerb[pbSemRole] = vnVarType + "(" + vnVarExpression + ")"
        # print(pbSemRole + "\t(" + vnVerbLabel + ", " + vnParamLabel + ")")
    returnResults["info"] = "semantic roles for " + _pbName
    returnResults[_pbName] = verbResults
    return returnResults


#####################################################################
# API  -- ulkb_sem_roles_for_pb_by_role("enter.01")
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
        vnVarExpression = result["vnVarExpression"]["value"]
        if pbSemRole not in verbResults:
            verbResults[pbSemRole] = []
        verbResults[pbSemRole].append({
            "vncls": "-".join(vnVerbLabel.split("-")[1:]),
            "vntheta": vnVarExpression.lower(),
            "description": pbSemRoleDesc
        })
    return verbResults


#####################################################################
# API  -- ulkb_lemma_mappings("put")
# Usage: from a lemma, get a list of mappings from pb to vn that 
#           correspond to that lemma
#####################################################################
# TO DEPRECATE
def ulkb_sem_roles_for_lemma(_lemma: str) -> {}:
    return ulkb_lemma_mappings(_lemma)


def ulkb_lemma_mappings(_lemma: str) -> {}:
    returnResults = []
    query_text = query_roles_for_lemma_str.format(_lemma)
    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    returnResults = {}
    # ?pbSemRole ?vnVerbLabel ?vnVarType ?vnVarExpression
    verbResults = {}

    for result in results["results"]["bindings"]:
        pbSemRole = result["pbSemRole"]["value"]
        vnVerbLabel = result["vnVerbLabel"]["value"]

        vnVarType = result["vnVarType"]["value"]
        vnVarExpression = result["vnVarExpression"]["value"]
        if vnVerbLabel not in verbResults:
            verbResults[vnVerbLabel] = {}
        curVerb = verbResults[vnVerbLabel]
        if pbSemRole not in curVerb:
            curVerb[pbSemRole] = vnVarType + "(" + vnVarExpression + ")"
        # print(pbSemRole + "\t(" + vnVerbLabel + ", " + vnParamLabel + ")")
    returnResults["info"] = "semantic roles for lemma " + _lemma
    returnResults[_lemma] = verbResults
    return returnResults


#####################################################################
# API  -- ulkb_sem_predicates_SHORT("escape-51.1-2")
# Usage: from a VN verb, get a list of its semantic predicates. The 
#       predicate expressions are strings 
#####################################################################
def ulkb_sem_predicates_for_vn_SHORT(_verb: str) -> []:
    return ulkb_sem_predicates_SHORT(_verb)


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
        params.append(result["type"]["value"] + "(" + result["expression"]["value"] + ")")
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
# TO DEPRECATE
def ulkb_sem_predicates_for_vn(_verb: str) -> []:
    return ulkb_sem_predicates_LONG(_verb)


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
        params.append({'type': result["type"]["value"], 'value': result["expression"]["value"]})
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


if __name__ == '__main__':
    # print(str(check_verb_name("MIMI")))

    # TEST SEMANTIC ROLES
    # output = ulkb_sem_roles_for_pb("put.01")
    # print(str(output))
    # TEST SEMANTIC PREDICATES
    # output = ulkb_sem_predicates_for("escape-51.1-1-1")
    # print(str(output))

    # output = ulkb_sem_predicates_for_SHORT("escape-51.1-1-1")
    # print(str(output))
    # TEST API WITH LEMMAS
    print("\nCalling ulkb_sem_roles_for_lemma for make_out ...")
    output = ulkb_sem_roles_for_lemma("make_out")
    print(str(output))

    print("\nCalling ulkb_sem_roles_for_pb_by_role for carry.01 ...")
    output = ulkb_sem_roles_for_pb_by_role("carry.01")
    print(str(output))
