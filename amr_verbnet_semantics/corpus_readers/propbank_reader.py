"""
An extension class based on NLTK PropbankCorpusReader to capture all rolesets.
Reference: https://www.nltk.org/_modules/nltk/corpus/reader/propbank.html
"""
from collections import defaultdict
from xml.etree import ElementTree

from nltk.corpus.reader import PropbankCorpusReader


class PropbankCorpusReaderEx(PropbankCorpusReader):
    def __init__(self, root, propfile, framefiles="", verbsfile=None,
                 parse_fileid_xform=None, parse_corpus=None, encoding="utf8"):
        PropbankCorpusReader.__init__(
            self, root, propfile, framefiles=framefiles, verbsfile=verbsfile,
            parse_fileid_xform=parse_fileid_xform, parse_corpus=parse_corpus,
            encoding=encoding)

        self._frame_file_roleset_dict, self._roleset_frame_file_dict \
            = self._build_framefile_roleset_dict()

    def _build_framefile_roleset_dict(self):
        frame_file_roleset_dict = defaultdict(set)
        roleset_frame_file_dict = dict()

        for framefile in self._framefiles:
            with self.abspath(framefile).open() as fp:
                etree = ElementTree.parse(fp).getroot()

            for roleset in etree.findall("predicate/roleset"):
                frame_file_roleset_dict[framefile].add(roleset.attrib["id"])
                roleset_frame_file_dict[roleset.attrib["id"]] = framefile
        return frame_file_roleset_dict, roleset_frame_file_dict

    def roleset(self, roleset_id):
        """
        :return: the xml description for the given roleset.
        """
        if roleset_id not in self._roleset_frame_file_dict:
            raise ValueError("Frameset file for %s not found" % roleset_id)

        framefile = self._roleset_frame_file_dict[roleset_id]

        # n.b.: The encoding for XML fileids is specified by the file
        # itself; so we ignore self._encoding here.
        with self.abspath(framefile).open() as fp:
            etree = ElementTree.parse(fp).getroot()
        for roleset in etree.findall("predicate/roleset"):
            if roleset.attrib["id"] == roleset_id:
                return roleset
        raise ValueError("Roleset %s not found in %s" % (roleset_id, framefile))

