"""Wrappers for local and remote AMR parsing client"""
import collections
import copy
import datetime
import glob
import os
import pickle
import sys
import threading

from nltk import sent_tokenize
from nltk.tokenize import word_tokenize

from amr_verbnet_semantics.grpc_clients.clients import AMRClientTransformer
from app_config import config


class LocalAMRClient(object):
    def __init__(self, use_cuda=False):
        self.parser = None
        self.use_cuda = use_cuda

    def _get_parser(self, use_cuda=False):
        sys.path.append(os.path.abspath(config.THIRD_PARTY_PATH))
        from transition_amr_parser.parse import AMRParser
        pkg_root_path = os.path.join(os.path.dirname(__file__), "../../")
        cwd = os.getcwd()
        os.chdir(os.path.join(pkg_root_path, config.THIRD_PARTY_PATH))
        print("Loading checkpoint ...")
        amr_parser = AMRParser.from_checkpoint(
            checkpoint=config.AMR_MODEL_CHECKPOINT_PATH,
            roberta_cache_path=config.ROBERTA_CACHE_PATH)
        print("Loaded checkpoint ...")
        # for loading resources, parse a test sentence
        amr_parser.parse_sentences([['test']])
        os.chdir(cwd)

        # if not use_cuda:
        #     amr_parser.use_cuda = False
        #     list(map(lambda x: x.cpu(), amr_parser.models))
        #     amr_parser.embeddings.roberta.cpu()

        return amr_parser

    def get_amr(self, text):
        if self.parser is None:
            # Lazy loading
            self.parser = self._get_parser(use_cuda=self.use_cuda)

        res = self.parser.parse_sentences([word_tokenize(text)])
        return res[0][0]


class RemoteAMRClient(object):
    def __init__(self):
        self.amr_host = "mnlp-demo.sl.cloud9.ibm.com"
        self.amr_port = 59990
        self.parser = None

    def get_amr(self, text):
        if self.parser is None:
            # Lazy loading
            self.parser = AMRClientTransformer(f"{self.amr_host}:{self.amr_port}")
        return self.parser.get_amr(text)


class CacheClient:
    def __init__(self, amr_client, cache_capacity=5000, delete_ratio=0.2,
                 snapshot_interval=1000, use_snapshot=True):
        self.amr_client = amr_client
        self.delete_ratio = delete_ratio
        self.capacity = cache_capacity
        self.snapshot_prefix = 'snapshot.pickle_'
        self.snapshot_interval = snapshot_interval
        self.count = 0
        self.cache = collections.OrderedDict()
        if use_snapshot:
            self._read_snapshot()

    def _read_snapshot(self):
        dt_name_pairs = []
        i = len(self.snapshot_prefix)
        for name in glob.glob(f'*/{self.snapshot_prefix}*'):
            try:
                dt = datetime.datetime.strptime(os.path.basename(name)[i:],
                                                '%Y-%m-%d_%H-%M-%S')
                dt_name_pairs.append((dt, name))
            except:
                # do not handle an exception from datetime.datetime.strptime
                pass

        try:
            if dt_name_pairs:
                dt_name_pairs.sort(key=lambda x: x[0])
                latest_name = dt_name_pairs[-1][1]
                self.cache = pickle.load(open(latest_name, 'rb'))
        except Exception as e:
            print(e)

    def get_amr(self, sentence):
        # use cache
        if sentence in self.cache:
            amr = self.cache[sentence]
            self.cache.move_to_end(sentence, last=False)  # move key "sentence" to the head

        else:
            amr = self.amr_client.get_amr(text=sentence)
            self.cache[sentence] = amr

            # delete unused keys
            if len(self.cache) == self.capacity:
                n = int(self.delete_ratio * self.capacity)
                for _ in range(n):
                    self.cache.popitem(last=True)

        # save snapshot
        self.count += 1
        if self.count == self.snapshot_interval:
            self.count = 0
            now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            file_name = f'{self.snapshot_prefix}{now}'
            thread = threading.Thread(target=self.save_snapshot,
                                      args=(file_name,
                                            copy.deepcopy(self.cache)))
            thread.start()

        return amr

    @staticmethod
    def save_snapshot(file_name, cache):
        try:
            pickle.dump(cache, open(file_name, 'wb'))
            print(f'cache is saved on {file_name}')
        except Exception as e:
            print(e)


if config.AMR_PARSING_MODEL == "local":
    amr_client = LocalAMRClient(config.use_cuda)
elif config.AMR_PARSING_MODEL == "remote":
    amr_client = RemoteAMRClient()
else:
    raise Exception("Missing AMR parsing configuration ...")

amr_client = CacheClient(amr_client)


def parse_text(text, verbose=False):
    sentences = sent_tokenize(text)

    if verbose:
        print("\ntext:\n", text)
        print("\nsentences:\n==>", "\n\n==>".join(sentences))
        print("parsing ...")

    sentence_parses = []
    for sent in sentences:
        sent_amr = amr_client.get_amr(sent)
        sentence_parses.append(sent_amr)

    if verbose:
        print("\nsentence_parses:", sentence_parses)
    return sentence_parses


if __name__ == "__main__":
    text = "The quick brown fox jumped over the lazy moon."
    amr_client = LocalAMRClient(config.use_cuda)
    amr = amr_client.get_amr(text)
    print("\ntext:", text)
    print("\namr:", amr)

    # parse_text("You enter a kitchen.")
    # parse_text("The quick brown fox jumped over the lazy moon.")
    # parse_text("You see a dishwasher and a fridge.")
    # parse_text("Here 's a dining table .")
    # parse_text("You see a red apple and a dirty plate on the table .")

