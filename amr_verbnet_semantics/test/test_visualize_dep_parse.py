
"""
import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("This is a sentence.")
displacy.serve(doc, style="dep")
"""

import spacy
from spacy import displacy
from pathlib import Path

nlp = spacy.load("en_core_web_sm")
sentences = ["For the fifth grade play , the chairs have been put into 27 rows with 16 chairs in each row .",
             "How many chairs have been put out for the play ?"]
for sent in sentences:
    doc = nlp(sent)
    svg = displacy.render(doc, style="dep", jupyter=False)
    Path("./test-output/").mkdir(parents=True, exist_ok=True)
    file_name = '-'.join([w.text for w in doc if not w.is_punct]) + ".svg"
    output_path = Path("./test-output/" + file_name)
    output_path.open("w", encoding="utf-8").write(svg)

