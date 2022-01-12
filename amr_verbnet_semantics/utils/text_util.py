"""
Utility functions for text-related processing
"""
from nltk.tokenize import word_tokenize, sent_tokenize


def is_extractable(text, triple):
    """
    Check if a triple can be extracted from text by examing the text spans
    of subject and object.
    :param text: the text to extract triple from
    :param triple: the target triple to extract
    :return:
    """
    subj, pred, obj = triple
    text_tokens = word_tokenize(text.lower())

    subj_spans = []
    obj_spans = []
    subj_tokens = word_tokenize(subj.lower())
    obj_tokens = word_tokenize(obj.lower())

    subj_matched = False
    obj_matched = False
    for idx, tok in enumerate(text_tokens):
        cur_subj_idx = len(subj_spans)
        cur_obj_idx = len(obj_spans)
        if cur_subj_idx < len(subj_tokens) and tok == subj_tokens[cur_subj_idx]:
            subj_spans.append(idx)
            if len(subj_spans) == len(subj_tokens):
                subj_matched = True
        else:
            subj_spans = []

        if cur_obj_idx < len(obj_tokens) and tok == obj_tokens[cur_obj_idx]:
            obj_spans.append(idx)
            if len(obj_spans) == len(obj_tokens):
                obj_matched = True
        else:
            obj_spans = []

    extractable = subj_matched and obj_matched
    return extractable


def split_text_into_sentences(text):
    sentences = []
    for sent in sent_tokenize(text):
        sent = sent.replace("\n\n", ": ")
        sub_sentences = []
        split_sents = sent.split("\n")
        for idx, p in enumerate(split_sents):
            if p.strip().endswith(":"):
                sub_sentences.append(p.strip())
            elif len(p.strip()) > 0 and not p.strip().endswith(".") \
                    and idx != len(split_sents) - 1:
                sub_sentences.append(p.strip() + ",")
            else:
                sub_sentences.append(p.strip())
        sentences.append(" ".join(sub_sentences))
    return sentences


if __name__ == "__main__":
    text = """End of Ledge
A ledge from the east ends here, and a tunnel leads north into the wall. There is a rather odd smokey odor in the warm air of the tunnel.
There is a dishevelled and slightly unkempt princess here.
The princess walks east. She glances back at you as she goes.

 End of Ledge
A ledge from the east ends here, and a tunnel leads north into the wall. There is a rather odd smokey odor in the warm air of the tunnel.

 You are carrying:
  A golden dragon statuette
  A blue crystal sphere
  A newspaper
  A matchbook
  A china teapot
  The china teapot contains:
    A quantity of water
  A lamp (providing light)"""
    print(text)
    print()
    print(split_text_into_sentences(text))

