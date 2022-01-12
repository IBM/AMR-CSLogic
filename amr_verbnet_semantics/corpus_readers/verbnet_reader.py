"""
An extension class based on NLTK VerbnetCorpusReader to capture the negation of statement.
Reference: https://www.nltk.org/_modules/nltk/corpus/reader/verbnet.html
"""
from nltk.corpus.reader import VerbnetCorpusReader


class VerbnetCorpusReaderEx(VerbnetCorpusReader):
    def __init__(self, root, fileids, wrap_etree=False):
        VerbnetCorpusReader.__init__(self, root, fileids, wrap_etree)

    def _get_semantics_within_frame(self, vnframe):
        """Returns semantics within a single frame

        A utility function to retrieve semantics within a frame in VerbNet
        Members of the semantics dictionary:
        1) Predicate value
        2) Arguments

        :param vnframe: An ElementTree containing the xml contents of
            a VerbNet frame.
        :return: semantics: semantics dictionary
        """
        semantics_within_single_frame = []
        for pred in vnframe.findall("SEMANTICS/PRED"):
            arguments = [
                {"type": arg.get("type"), "value": arg.get("value")}
                for arg in pred.findall("ARGS/ARG")
            ]
            semantics_within_single_frame.append(
                {
                    "predicate_value": pred.get("value"),
                    "arguments": arguments,
                    "is_negative": pred.get("bool", False) == "!"
                }
            )
        return semantics_within_single_frame
