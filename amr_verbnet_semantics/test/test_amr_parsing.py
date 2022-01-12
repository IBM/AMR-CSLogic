
from amr_verbnet_semantics.grpc_clients import AMRClientTransformer

amr_host = "mnlp-demo.sl.cloud9.ibm.com"
amr_port = 59990
amr_client = AMRClientTransformer(f"{amr_host}:{amr_port}")


if __name__ == "__main__":
    """
    list_text = [
        "The contractor builds houses for $100,000.",
        "$100,000 builds a house.",
        "$100,000 will build you a house.",
        "$100,000 builds a house out of sticks.",
        "$100,000 builds you a house out of sticks.",
        "The dresser is made out of maple carefully finished with Danish oil."
    ]
    """
    list_text = [
        "I loved him writing novels.",
        "I admired him for his honesty."
    ]
    for text in list_text:
        amr = amr_client.get_amr(text)
        print(amr)

