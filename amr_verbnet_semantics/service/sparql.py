"""
Accessing the unified KB using SPARQL
"""
import json
from collections import defaultdict

from SPARQLWrapper import JSON, SPARQLWrapper

from app_config import config
from KG.service.ulkb_access_V5 import \
    ulkb_sem_predicates_LONG, \
    ulkb_pb_vn_mappings

query_prefix = """
prefix rrp: <http://www.ibm.com/RRP#>
prefix glo: <http://www.ibm.com/GLO_V2#>
prefix ulvn: <http://www.ibm.com/UL_VN#>
prefix ulwn: <http://www.ibm.com/UL_WN#>
prefix ulpb: <http://www.ibm.com/UL_PB#>
prefix ulkb: <http://www.ibm.com/UL_KB#>
"""

sparql = SPARQLWrapper(config.SPARQL_ENDPOINT)


def query_pb_vn_mapping_from_rdf(propbank_id,
                                 verbnet_version="verbnet3.4",
                                 verbose=False):
    """
    Query Propbank-VerbNet mappings from RDF KG.
    :param propbank_id: probank frame id
    :param verbnet_version: verbnet version of mapping
    :param verbose:
    :return:
    """
    if verbose:
        print("propbank_id:", propbank_id)

    output = ulkb_pb_vn_mappings(propbank_id)

    mapping_res = []
    if propbank_id in output:
        for vn_class in output[propbank_id]:
            mapping_res.append({
                "mapping": vn_class,
                "source": output["provenance"]
            })

    if len(mapping_res) == 0:
        return None
    return mapping_res


def query_verbnet_semantic_roles_from_rdf(propbank_id):
    results = dict()
    output = ulkb_pb_vn_mappings(propbank_id)

    if propbank_id not in output:
        return results

    for vn_class in output[propbank_id]:
        for arg_role in output[propbank_id][vn_class]:
            if arg_role not in results:
                results[arg_role] = []
            theme_role = output[propbank_id][vn_class][arg_role]
            results[arg_role].append({
                "description": "",
                "vncls": "-".join(vn_class.split("-")[1:]),
                "vntheta": theme_role.strip()[len("ThemRole("):-1].lower()
            })

    return results


def query_semantics_from_rdf(verbnet_class_id,
                             verbnet_version="verbnet3.4",
                             include_example=False,
                             verbose=False):
    if verbose:
        print("verbnet_class_id:", verbnet_class_id)

    output = ulkb_sem_predicates_LONG(verbnet_class_id)

    # Further construct the result
    semantics_by_role_set = defaultdict(list)
    for semantic_example in output:
        if len(semantic_example) == 0:
            continue

        example = semantic_example["example"]
        if "roleList" in semantic_example:
            role_set = set(semantic_example["roleList"])
        else:
            role_set = set()
        statements = []
        for predicate in semantic_example["predicates"]:
            arguments = []
            for param in predicate["params"]:
                arguments.append({
                    "type": param["type"].strip(),
                    "value": param["value"].strip()
                })

            statements.append({
                "predicate_value": predicate["label_predicate"],
                "arguments": arguments,
                "is_negative": "operator" in predicate
            })

        if include_example:
            semantics_by_role_set[(example, tuple(sorted(role_set)))].append(statements)
        else:
            semantics_by_role_set[tuple(sorted(role_set))].append(statements)
    return dict(semantics_by_role_set)


def query_verbnet_semantic_roles(propbank_id):
    query_text = """SELECT DISTINCT ?verb ?pbSemRole ?vnVerbLabel ?vnParamLabel WHERE {{
        ?verb rdfs:label "%s" . 
        #?verb rrp:inKB rrp:PropBank .
        ?verb rrp:hasParameter ?pbParam . 
        ?pbParam rdfs:label ?pbSemRole . 
        ?vnVerb rrp:inKB rrp:VerbNet . 
        ?vnVerb rdfs:label ?vnVerbLabel . 
        ?vnVerb rrp:hasComponent ?vnFrame . 
        ?vnFrame rrp:hasComponent ?semPred . 
        ?semPred rrp:hasParameter ?vnParam . 
        ?pbParam rrp:mapsTo ?vnParam . 
        ?vnParam rdfs:label ?vnParamLabel . 
        }}
        """ % propbank_id

    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        pb_sem_role = result["pbSemRole"]["value"]
        vn_verb_label = result["vnVerbLabel"]["value"]
        if "vnSemRole" in result:
            vn_sem_role = result["vnSemRole"]["value"]
        else:
            vn_sem_role = "N/A"
        print(pb_sem_role + "\t(" + vn_verb_label + ", " + vn_sem_role + ")")


def test_query_provenance(verb):
    query_text = """SELECT DISTINCT ?provenance WHERE {
                      ?entity rdfs:label "%s" .  # FOR the specific verb
                      ?entity rrp:provenance ?provenance .
                    }
                """ % verb

    sparql.setQuery(query_prefix + query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        print(result["provenance"]["value"])


if __name__ == "__main__":
    # query_verbnet_semantic_roles("admire.01")
    # query_verbnet_semantic_roles("enter.01")
    # query_verbnet_semantic_roles("possible.01")
    # query_verbnet_semantic_roles("green.02")
    # query_verbnet_semantic_roles("make_out.23")
    # query_verbnet_semantic_roles("make-out.08")
    # query_verbnet_semantic_roles("make_out.12")
    # print(query_pb_vn_mapping_from_rdf("be-located-at-91"))
    # query_verbnet_semantic_predicates("admire-31_2")
    # print(query_pb_vn_mapping_from_rdf("admire.01"))
    # print(query_pb_vn_mapping_from_rdf("enter.01"))
    print(query_semantics_from_rdf("escape-51.1-1"))
    # test_query_provenance("put-9.1-2")
    # roles = query_verbnet_semantic_roles_from_rdf("be-located-at-91")
    # roles = query_verbnet_semantic_roles_from_rdf("carry.01")
    roles = query_verbnet_semantic_roles_from_rdf("make_out.23")
    # roles = ulkb_sem_roles_for_pb("make_out.12")
    print(json.dumps(roles, indent=4, sort_keys=True))

