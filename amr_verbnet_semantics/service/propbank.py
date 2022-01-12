"""PropBank query wrapper"""
import re

from nltk.corpus import treebank
from nltk.corpus.util import LazyCorpusLoader

from amr_verbnet_semantics.corpus_readers.propbank_reader import \
    PropbankCorpusReaderEx
from amr_verbnet_semantics.service.sparql import \
    query_verbnet_semantic_roles_from_rdf
from app_config import config


propbank = None


def load_propbank():
    global propbank
    propbank = LazyCorpusLoader(
        "propbank-latest",
        PropbankCorpusReaderEx,
        "prop.txt",
        r"frames/.*\.xml",
        "verbs.txt",
        lambda filename: re.sub(r"^wsj/\d\d/", "", filename),
        treebank,
    )  # Must be defined *after* treebank corpus.


def query_verbnet_semantic_roles(propbank_id):
    if config.KB_SOURCE == "rdf":
        return query_verbnet_semantic_roles_from_rdf(propbank_id)
    return query_verbnet_semantic_roles_from_corpus(propbank_id)


def query_verbnet_semantic_roles_from_corpus(propbank_id, verbose=False):
    global propbank
    if propbank is None:
        load_propbank()

    if verbose:
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

    if verbose:
        print("query_propbank_roles role_mappings:", role_mappings)
    return role_mappings


def query_propbank_roleset_ids():
    global propbank
    if propbank is None:
        load_propbank()

    roleset_ids = set()
    for roleset in propbank.rolesets():
        roleset_ids.add(roleset.attrib["id"])
    return roleset_ids


if __name__ == "__main__":
    # print(query_propbank_roleset_ids())
    # print(query_verbnet_semantic_roles_from_corpus("make_out.23"))
    # print(query_verbnet_semantic_roles_from_corpus("make"))
    # print(query_verbnet_semantic_roles_from_corpus("make.01"))
    # print(query_verbnet_semantic_roles_from_corpus("make.02"))
    # print(query_verbnet_semantic_roles_from_corpus("make_up.08"))
    # print(query_verbnet_semantic_roles_from_corpus("possible.01"))
    # print(query_verbnet_semantic_roles_from_corpus("green.02"))
    # print(query_verbnet_semantic_roles_from_corpus("except.01"))
    print(query_verbnet_semantic_roles_from_corpus("carry.01"))

