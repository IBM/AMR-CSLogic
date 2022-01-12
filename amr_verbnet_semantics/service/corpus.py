"""
Corpus query interfaces for the KB.
"""

from amr_verbnet_semantics.service.abstract_kb import AbstractKb
from amr_verbnet_semantics.service.propbank import \
    query_verbnet_semantic_roles_from_corpus
from amr_verbnet_semantics.service.semlink import \
    query_pb_vn_mapping_from_semlink
from amr_verbnet_semantics.service.verbnet import query_semantics_from_corpus


class CorpusKb(AbstractKb):
    def __init__(self):
        super().__init__()

    def query_semantics(self, verbnet_id, verbnet_version=None, verbose=False):
        return query_semantics_from_corpus(verbnet_id, verbnet_version)

    def query_propbank_verbnet_class_mapping(
            self, propbank_id, verbnet_version=None, verbose=False):
        return query_pb_vn_mapping_from_semlink(propbank_id)

    def query_verbnet_semantic_roles(self, propbank_id, verbose=False):
        return query_verbnet_semantic_roles_from_corpus(propbank_id, verbose)


if __name__ == '__main__':
    corpus_kb = CorpusKb()
    print(corpus_kb.query_semantics("escape-51.1", verbnet_version="verbnet3.4"))
    print()
    print(corpus_kb.query_semantics("spray-9.7-2", verbnet_version="verbnet3.4"))
    print()
    print(corpus_kb.query_propbank_verbnet_class_mapping("enter.01"))
    print()
    print(corpus_kb.query_verbnet_semantic_roles("enter.01"))

