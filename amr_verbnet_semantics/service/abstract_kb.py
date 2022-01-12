"""
Unified query interfaces for the KB.
"""


class AbstractKb:
    def __init__(self):
        pass

    def query_semantics(
            self, verbnet_id, verbnet_version=None, verbose=False):
        raise NotImplementedError()

    def query_propbank_verbnet_class_mapping(
            self, propbank_id, verbnet_version=None, verbose=False):
        raise NotImplementedError()

    def query_verbnet_semantic_roles(self, propbank_id, verbose=False):
        raise NotImplementedError()


