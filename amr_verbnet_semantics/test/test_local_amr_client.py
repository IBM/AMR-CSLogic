from amr_verbnet_semantics.service.amr import LocalAMRClient

if __name__ == "__main__":

    amr_client = LocalAMRClient()

    list_text = [
        "I loved him writing novels.",
        "I admired him for his honesty."
    ]
    for text in list_text:
        amr = amr_client.get_amr(text)
        print(amr)

