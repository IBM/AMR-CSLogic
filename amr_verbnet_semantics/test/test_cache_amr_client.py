import time

from amr_verbnet_semantics.service.amr import CacheClient, LocalAMRClient

if __name__ == "__main__":

    amr_client = LocalAMRClient()
    amr_client = CacheClient(amr_client, use_snapshot=False)

    list_text = ['You drop the peanut oil on the ground.',
                 'You pick up the peanut oil from the ground.',
                 'You take the peanut oil from the folding chair.',
                 'You drop the red hot pepper on the ground.',
                 'But the thing is empty.',
                 'The shelf is wooden.',
                 'Now why would someone leave that there?',
                 'When you stand up, you notice a shelf.',
                 'You bend down to tie your shoe.',
                 'You see a yellow onion, some peanut oil, some sugar, some salt and some black pepper on the folding chair.']

    # before caching
    start = time.time()
    for text in list_text:
        amr = amr_client.get_amr(text)
    print(f'before caching: {time.time() - start:.3f} seconds')


    # after caching
    start = time.time()
    for text in list_text:
        amr = amr_client.get_amr(text)
    print(f'after caching: {time.time() - start:.3f} seconds')
