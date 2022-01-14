#!/bin/bash

# this is called from setup.py in the main project dir

echo "** Installing third_party **"
rm -rf third_party
mkdir third_party

rm -rf transition-amr-parser-0.4.2
wget https://github.com/IBM/transition-amr-parser/archive/refs/tags/v0.4.2.zip
unzip v0.4.2.zip
pushd transition-amr-parser-0.4.2
sed -I "" 's/torch<=1.2,<=1.3/torch==1.3.0/g' setup.py # -i   doesn't work on osx
pip install -e .
popd
rm v0.4.2.zip

wget https://dl.fbaipublicfiles.com/fairseq/models/roberta.large.tar.gz
tar -zxvf roberta.large.tar.gz
mv roberta.large third_party
rm roberta.large.tar.gz
