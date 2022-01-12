"""
VerbNet query wrapper
"""
from collections import defaultdict
from nltk.corpus.util import LazyCorpusLoader

from amr_verbnet_semantics.corpus_readers.verbnet_reader import \
    VerbnetCorpusReaderEx
from amr_verbnet_semantics.service.sparql import query_semantics_from_rdf
from app_config import config


vn_dict = None


def load_vn_dict():
    global vn_dict
    vn_dict = {
        "verbnet3.2": LazyCorpusLoader("verbnet3.2", VerbnetCorpusReaderEx, r"(?!\.).*\.xml"),
        "verbnet3.3": LazyCorpusLoader("verbnet3.3", VerbnetCorpusReaderEx, r"(?!\.).*\.xml"),
        "verbnet3.4": LazyCorpusLoader("verbnet3.4", VerbnetCorpusReaderEx, r"(?!\.).*\.xml")
    }


def query_semantics_from_corpus(verbnet_id, verbnet_version,
                                include_example=False, verbose=False):
    global vn_dict
    if vn_dict is None:
        load_vn_dict()

    semantics = defaultdict(list)
    frames = vn_dict[verbnet_version].frames(verbnet_id)

    for frame in frames:
        role_set = set()
        for element in frame["syntax"]:
            role = element["modifiers"]["value"].strip()
            if len(role) > 0 and role.istitle():
                # not empty string and is title-case
                role_set.add(role)

        if include_example:
            example = frame["example"].replace("\n", "")
            semantics[(example, tuple(sorted(role_set)))].append(frame["semantics"])
        else:
            semantics[tuple(sorted(role_set))].append(frame["semantics"])
    return dict(semantics)


def query_semantics(verbnet_id, verbnet_version):
    if config.KB_SOURCE == "rdf":
        return query_semantics_from_rdf(verbnet_id, verbnet_version)
    return query_semantics_from_corpus(verbnet_id, verbnet_version)


if __name__ == '__main__':
    verbnet_id = "escape-51.1"
    verbnet_version = "verbnet3.4"
    print("\nQuerying verbnet class {} in version {} ...".format(verbnet_id, verbnet_version))
    print("\nresult:")
    print(query_semantics(verbnet_id, verbnet_version))

