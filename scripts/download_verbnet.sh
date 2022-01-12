#!/bin/bash

# Download VerbNet
# Example: sh scripts/download_verbnet.sh [save_dir]
# Usage: sh scripts/download_verbnet.sh ~/nltk_data/corpora/

set -e
save_dir=$1

# VerbNet 3.2
wget -P ${save_dir} http://verbs.colorado.edu/verb-index/vn/verbnet-3.2.tar.gz
echo "Unzip ..."
tar xvzf ${save_dir}/verbnet-3.2.tar.gz -C ${save_dir} && mv ${save_dir}/new_vn ${save_dir}/verbnet3.2
echo "Saved to ${save_dir}/verbnet3.2"

# VerbNet 3.3
wget -P ${save_dir} http://verbs.colorado.edu/verb-index/vn/verbnet-3.3.tar.gz
echo "Unzip ..."
tar xvzf ${save_dir}/verbnet-3.3.tar.gz -C ${save_dir}
echo "Saved to ${save_dir}/verbnet3.3"

# VerbNet 3.4
git clone https://github.com/cu-clear/verbnet.git ./verbnet_clone
cp -R ./verbnet_clone/verbnet3.4 ${save_dir}
rm -rf ./verbnet_clone
echo "Saved to ${save_dir}/verbnet3.4"

echo "Download & unzip DONE."

