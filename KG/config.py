"""
Config file for isolating endpoint configuration difference. Checks for 
config.yaml in the project OR a config_sparql.yaml in the current directory
"""
import os

import yaml

SPARQL_ENDPOINT = "" 
config = "" 

thisDir = os.path.join(os.getcwd())

try:
    from app_config import config
    SPARQL_ENDPOINT = config.SPARQL_ENDPOINT
except ImportError:
    try :     
      with open(thisDir + "/config_sparql.yaml", "r") as f:
          config = yaml.safe_load(f)
          if type(config) is dict : 
              SPARQL_ENDPOINT = config['SPARQL_ENDPOINT']
          else :               
              SPARQL_ENDPOINT = config
              SPARQL_ENDPOINT = SPARQL_ENDPOINT.split("\"")[1]
    except : 
        raise Exception("Cannot find config_sparql.yaml in current directory (standalone) or config.yaml in root directory (AMR-CSlogic)")

if __name__ == "__main__":
    print(str(config))
    print(SPARQL_ENDPOINT)

