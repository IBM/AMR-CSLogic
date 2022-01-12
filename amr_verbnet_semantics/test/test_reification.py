"""
Test module for reification using penman package.
"""

from penman.codec import PENMANCodec
from penman.models.amr import model
from penman.transform import reify_edges

codec = PENMANCodec(model=model)
g = codec.decode("""
(d / dress
      :ARG1-of (r / red-02)
      :ARG1-of (c / clean-04)
      :location (n / nightstand))
""")
g = reify_edges(g, model)
print(codec.encode(g))


"""
Output:

(d / dress
   :ARG1-of (r / red-02)
   :ARG1-of (c / clean-04)
   :ARG1-of (_ / be-located-at-91
               :ARG2 (n / nightstand)))
"""

