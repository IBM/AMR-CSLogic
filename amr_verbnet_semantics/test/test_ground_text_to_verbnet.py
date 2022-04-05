import json
from amr_verbnet_semantics.core.amr_verbnet_enhance \
    import ground_text_to_verbnet

if __name__ == '__main__':
    text = "You're in a corridor. You can see a shoe cabinet."
    ret = ground_text_to_verbnet(text, use_coreference=False, verbose=True)
    # print(json.dumps(ret, indent=2))
    print(ret['sentence_parses'][0]['amr'])
    print(ret['sentence_parses'][1]['amr'])

