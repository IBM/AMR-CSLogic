#!/bin/bash

# Download Propbank
# Example: sh scripts/download_propbank.sh [save_dir]
# Usage: sh scripts/download_propbank.sh ~/nltk_data/corpora/

set -e
save_dir=$1

# Propbank frames 3.1
mkdir -p ${save_dir}
wget -O ${save_dir}/propbank-frames-3.1.zip https://github.com/propbank/propbank-frames/archive/refs/tags/v3.1.zip
echo "Unzip ..."
unzip ${save_dir}/propbank-frames-3.1.zip -d ${save_dir}
echo "Saved to ${save_dir}/propbank-frames-3.1"

# Replace with the latest propbank frames folder
cp -R ${save_dir}/propbank ${save_dir}/propbank-latest
rm -rf ${save_dir}/propbank-latest/frames/
cp -R ${save_dir}/propbank-frames-3.1/frames/ ${save_dir}/propbank-latest

echo "DONE."