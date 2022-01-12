"""
GRPC clients
"""
import grpc

from ..grpc_defs import ace_pb2, ace_pb2_grpc
from ..grpc_defs.enhanced_amr_pb2 import Sentence
from ..grpc_defs.enhanced_amr_pb2_grpc import AMR_EnhancerStub

## Note: the following clients adapted from NSQA pipeline


class AMRClientTransformer(object):
    def __init__(self, host):
        # configure the host and the
        # the port to which the client should connect
        # to.
        self.host = host
        # instantiate a communication channel
        self.channel = grpc.insecure_channel(host)
        # bind the client to the server channel
        self.stub = ace_pb2_grpc.aceStub(self.channel)

    def get_amr(self, text):
        # req_sent = self.text_to_sentence(sentence)
        answer = self.stub.process_text(ace_pb2.acedoc_request(text=text))
        for sent in answer.sents:
            # print(sent.amr)
            return sent.amr


class EnhancedAMRClient(object):
    """
    Client for accessing the gRPC functionality
    """

    def __init__(self, host = 'localhost', server_port = 46001):
        # configure the host and the
        # the port to which the client should connect
        # to.
        self.host = host
        self.server_port = server_port

        # instantiate a communication channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client to the server channel
        self.stub = AMR_EnhancerStub(self.channel)

    def get_amr(self, message, has_amr = False, org_amr=None):
        """
        Client function to call the rpc for get_enhancedamr
        """
        sentence = Sentence(text=message, has_amr=has_amr, org_amr=org_amr)
        return self.stub.get_enhanced_amr(sentence)

