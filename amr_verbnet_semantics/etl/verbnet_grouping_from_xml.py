#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 2021
@author: Zhicheng (Jason) Liang
"""

import json
import os
import xml.etree.ElementTree as ET


def read_groupings(file_dir, output_dir):
    groupings = []
    for file_name in os.listdir(file_dir):
        if file_name.endswith(".xml"):
            groupings.append(file_name)

    results = dict()
    for file_name in groupings:
        vn_id = file_name.strip()[:-len(".xml")]
        file_path = os.path.join(file_dir, file_name)
        page = parse_grouping_file(file_path)
        results[vn_id] = page

    # Save to file
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output_path = os.path.join(output_dir, "all_verbnet_grouping_from_xml.json")
    with open(output_path, "w") as f:
        json.dump(results, f)
        print("Written to {}".format(output_path))
    print("\n# of grouping: {}\n".format(len(groupings)))
    print("DONE.")
    return


def process_mapping(mapping):
    elems = mapping.replace("\n", " ").split(":")
    source = "_".join(elems[0].strip().split())
    value_str = elems[1].strip()
    values = []
    if len(value_str) > 0:
        first_value = value_str.split()[0]
        if "_" in first_value:
            # Multi-word expressions
            values.append(first_value)
            value_str = " ".join(value_str.split()[1:])
    values += [v.strip() for v in value_str.split(",")]
    return source, values


def parse_grouping_file(file_path):
    print("==> Crawling {} ...".format(file_path))

    page = dict()
    tree = ET.parse(file_path)
    page["id"] = tree.getroot().attrib["lemma"]
    senses = []

    for child_sense in tree.getroot().findall("sense"):
        # Sense number
        sense = dict()
        sense["sense_index"] = child_sense.attrib["n"].strip()
        sense["description"] = child_sense.attrib["name"].strip()

        # Examples
        elem_examples = child_sense.find("examples")
        if elem_examples is not None and elem_examples.text is not None:
            examples = [line.strip() for line in elem_examples.text.strip().split("\n")]
            sense["examples"] = examples

        # Mappings
        mappings = dict()
        elem_mappings = child_sense.find("mappings")

        # WordNet
        elem_wn = elem_mappings.find("wn")
        if elem_wn is not None and elem_wn.text is not None:
            mapping = elem_wn.text.strip()
            if len(mapping) > 0:
                wn_version = elem_wn.attrib["version"]
                key = "WordNet_{}_Sense_Numbers".format(wn_version)
                mappings[key] = [v.strip() for v in mapping.split(",")]

        # FrameNet
        elem_fn = elem_mappings.find("fn")
        if elem_fn is not None and elem_fn.text is not None:
            mapping = elem_fn.text.strip()
            if len(mapping) > 0:
                mappings["FrameNet"] = [v.strip() for v in mapping.split(",")]

        # PropBank
        elem_pb = elem_mappings.find("pb")
        if elem_pb is not None and elem_pb.text is not None:
            mapping = elem_pb.text.strip()
            if len(mapping) > 0:
                mappings["PropBank"] = [v.strip() for v in mapping.split(",")]

        # VerbNet
        elem_vn = elem_mappings.find("vn")
        if elem_vn is not None and elem_vn.text is not None:
            mapping = elem_vn.text.strip()
            if len(mapping) > 0:
                mappings["VerbNet"] = [v.strip() for v in mapping.split(",")]

        sense["mappings"] = mappings
        senses.append(sense)

    page["senses"] = senses
    return page


"""
Usage:
export PYTHONPATH=.
python code/wikipedia/verbnet_grouping_from_xml.py \
    --input_dir ./data/corpora/sense-inventories \
    --output_dir ./data/verbnet_out_from_xml
"""
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", type=str, help="Path to sense-inventories directory")
    parser.add_argument("--output_dir", type=str, help="Path to output directory")
    args = parser.parse_args()

    read_groupings(args.input_dir, args.output_dir)

