
import requests
import json

from amr_verbnet_semantics.core.amr_verbnet_enhance import (
    build_graph_from_amr, visualize_semantic_graph)

host = "0.0.0.0"
port = 5000

# text = "For the fifth grade play , the chairs have been put into 27 rows with 16 chairs in each row . How many chairs have been put out for the play ?"
text = "You are carrying : a bronze-hilted dagger, a clay ocarina, armor, and silks ( worn ) ."
res = requests.get("http://{}:{}/amr_parsing".format(host, port), params={'text': text})
res = json.loads(res.text)
print(res)
for i, amr in enumerate(res["result"]):
    graph, amr_obj = build_graph_from_amr(amr=amr)
    visualize_semantic_graph(graph, graph_name="amr_semantic_graph_{}".format(i),
                             out_dir="./test-output/")
print("amr_semantic_graph DONE ...")

