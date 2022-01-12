"""
Load configuration from .yaml file.
"""
import os
import yaml

from amr_verbnet_semantics.utils.format_util import DictObject, to_json


config_file_path = os.path.join(os.path.dirname(__file__), "config.yaml")
if not os.path.exists(config_file_path):
    raise Exception("Please create a config.yaml file following the config_template.yaml in the project root dir ...")

with open(config_file_path, "r") as f:
    config = yaml.safe_load(f)

config = DictObject(config)


if __name__ == "__main__":
    print(to_json(config))
    print(config.SPARQL_ENDPOINT)

