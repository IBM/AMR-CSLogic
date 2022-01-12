# Architecture

```
amr_verbnet_semantics
├── core
├── corpus_readers
├── etl
├── grpc_clients
├── grpc_defs
├── jericho_world
├── rest
├── service
│   └── predicate_kb
├── test
├── utils
└── web_app

third_party
├── (DATA)
├── (fairseq_ext)
├── (roberta.large)
└── (transition_amr_parser)
```


# Subcomponent
## third_party
The content "third_party" directory is IBM AMR parser and will be mostly produced by scripts/download_third_party.sh. 
According to the IP department, when we make this code OSS, we need to put all the external code in “third_party” directory.


## knowledge base
For querying the linguistic resource KB, either via corpus reader or via RDF triple store, we wrap the functionalities to provide several interfaces for use, which are defined in the abstract class as the following:
```
class AbstractKb:
    def __init__(self):
        pass

    def query_semantics(
            self, verbnet_id, verbnet_version=None, verbose=False):
        raise NotImplementedError()

    def query_propbank_verbnet_class_mapping(
            self, propbank_id, verbnet_version=None, verbose=False):
        raise NotImplementedError()

    def query_verbnet_semantic_roles(self, propbank_id, verbose=False):
        raise NotImplementedError()
```

The query_propbank_verbnet_class_mapping method is for querying the class id mappings between Propbank and VerbNet, which could be one-to-many mappings;
The query_verbnet_semantic_roles method is for querying the semantic roles defined by VerbNet for different arguments of a Propbank frame;
The query_semantics method is for querying the predicate calculus, i.e. verb semantics for a VerbNet class.

Under the amr_verbnet_semantics.service package, we implement the above interfaces in corpus.py that reads from the NLTK corpus, and in ulkb.py that reads from the RDF triple store. The results of using these two should be exactly the same unless there are some differences occured during the data curation stage for the triple store.