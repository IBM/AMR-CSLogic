#!/bin/bash

# Install dependencies and setups
# Usage: sh ./install.sh

set -e

echo "** ensuring latest version of pip is installed **"
pip install --upgrade pip

if [[ ${CONDA_DEFAULT_ENV:-''} != amr-verbnet ]]; then
  echo Create and activate the amr-verbnet env
  echo "Sorry, we can't do that for you in this script, at least, not on a Mac"
  exit 1
fi

pip install numpy

echo "** installing packages **"
pip install -e .

echo "** Downloading spaCy corpus **"
python -m spacy download en

# For constituency parsing
# pip install benepar --no-cache-dir
# python -c "import benepar; benepar.download('benepar_en3')"

# Install PyTorch 1.3
# pip install torch==1.3

echo "** Downloading Blazegraph for storing the KG **"
mkdir -p blazegraph
wget -O ./blazegraph/blazegraph.jar https://github.com/blazegraph/database/releases/download/BLAZEGRAPH_2_1_6_RC/blazegraph.jar
