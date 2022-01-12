from nltk.corpus.reader import VerbnetCorpusReader
from nltk.corpus.util import LazyCorpusLoader

verbnet = LazyCorpusLoader("verbnet3.4", VerbnetCorpusReader, r"(?!\.).*\.xml")
print(verbnet.frames("escape-51.1-1"))
try:
    print(verbnet.frames("escape-51.1-2"))
except Exception as e:
    print(e)

print(verbnet.frames("leave-51.2"))
print(verbnet.subclasses("escape-51.1-1"))

