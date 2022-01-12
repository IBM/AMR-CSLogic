"""spaCy NLP Parsing"""

from nltk.tokenize import sent_tokenize
import spacy
import neuralcoref

nlp = None


def full_parsing(text, do_coreference=False, do_word_tokenize=False,
                 do_pos_tag=False, do_dependency_parse=False,
                 do_constituency_parse=False):
    global nlp
    if nlp is None:
        nlp = spacy.load('en')

    annotation = dict()

    if do_coreference:
        nlp = spacy.load('en')
        neuralcoref.add_to_pipe(nlp)
        doc = nlp(text)
        annotation["coreference"] = doc._.coref_clusters

    if any([do_word_tokenize, do_pos_tag, do_dependency_parse, do_constituency_parse]):
        annotation["sentences"] = []

        for sentence in sent_tokenize(text):
            sentence_parse = dict()
            sentence_parse["text"] = sentence

            doc = nlp(sentence)
            if do_word_tokenize:
                tokens = []
                for token in doc:
                    tokens.append(token.text)
                sentence_parse["word_tokenize"] = tokens

            if do_pos_tag:
                pos_tag = []
                for token in doc:
                    pos_tag.append(token.pos_)
                sentence_parse["pos_tag"] = pos_tag

            if do_dependency_parse:
                dep_parse = []
                for token in doc:
                    dep_parse.append((token.dep_, token.head.i, token.i))
                sentence_parse["dependency_parse"] = dep_parse

            if do_constituency_parse:
                import benepar
                nlp = spacy.load('en')
                if spacy.__version__.startswith('2'):
                    nlp.add_pipe(benepar.BeneparComponent("benepar_en3"))
                else:
                    nlp.add_pipe("benepar", config={"model": "benepar_en3"})
                doc = nlp(sentence)
                sent = list(doc.sents)[0]
                sentence_parse["constituency_parse"] = sent._.parse_string

            annotation["sentences"].append(sentence_parse)
    return annotation


if __name__ == "__main__":
    # text = 'My sister has a dog. She loves him .'
    # text = 'Angela lives in Boston. She is quite happy in that city.'
    text = 'Autonomous cars shift insurance liability toward manufacturers.'
    print(full_parsing(text, do_coreference=True,
                       do_word_tokenize=True,
                       do_pos_tag=True,
                       do_dependency_parse=True,
                       do_constituency_parse=True))

