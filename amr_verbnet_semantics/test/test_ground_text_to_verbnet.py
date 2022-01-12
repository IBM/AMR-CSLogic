import time

from amr_verbnet_semantics.core.amr_verbnet_enhance import \
    ground_text_to_verbnet

if __name__ == '__main__':
    start = time.time()
    
    text = "You're in a corridor. You can see a shoe cabinet. The shoe cabinet contains a top hat. You lean against the wall, inadvertently pressing a secret button. The wall opens up to reveal a coat hanger. The coat hanger is normal. But the thing is empty. You can make out a hat rack. Looks like someone's already been here and taken everything off it, though. Hm. Oh well You hear a noise behind you and spin around, but you can't see anything other than an umbrella stand. The umbrella stand is usual. But the thing is empty, unfortunately. Hm. Oh well You hear a noise behind you and spin around, but you can't see anything other than a key holder! The key holder is ordinary. But the thing is empty. It would have been so cool if there was stuff on the key holder."
    ret = ground_text_to_verbnet(text, use_coreference=True)
    print(f"ret: {ret}")
    print(f"grounded_stmt of last sentence: {ret['sentence_parses'][-1]['grounded_stmt']}")

    print(f'finish with {time.time()-start:.3f} seconds')
