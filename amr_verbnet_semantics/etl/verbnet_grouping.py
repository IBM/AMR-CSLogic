#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 2021
@author: Zhicheng (Jason) Liang
"""

import json
import os
import re

import requests
from bs4 import BeautifulSoup

category_url = "http://verbs.colorado.edu/html_groupings/"


def read_grouping_category(url, output_dir):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    groupings = []
    for elem in soup.find_all('a'):
        href = elem.get('href')
        if href.endswith(".html"):
            groupings.append(href)
    print("\n# of grouping pages: {}\n".format(len(groupings)))

    results = dict()
    for html in groupings:
        vn_id = html.strip()[:-len(".html")]
        page = parse_grouping_page(url + html)
        results[vn_id] = page

    # Save to file
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output_path = os.path.join(output_dir, "all_verbnet_grouping.json")
    with open(output_path, "w") as f:
        json.dump(results, f)
        print("Written to {}".format(output_path))
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


def parse_grouping_page(url):
    print("==> Crawling {} ...".format(url))

    page = dict()
    req = requests.get(url)

    # BUG FIX: the original html missed the right angle bracket for the font tag
    html_content = req.text.replace('color="33066"', 'color="33066">')

    soup = BeautifulSoup(html_content, 'html.parser')
    page["id"] = soup.head.title.text
    senses = []

    for child in soup.body.findChildren():
        # Sense number
        if child.name == "h3":
            sense = dict()
            pattern = r"Sense\sNumber\s(?P<sense_index>(.[^:]*)):(?P<description>(.*))"
            matched = list(re.finditer(pattern, child.text))
            sense["sense_index"] = matched[0].group("sense_index").strip()
            sense["description"] = matched[0].group("description").strip()

        # Examples
        if child.text == "Examples:":
            examples = []
            for br in child.find_next_siblings("br"):
                example = br.next_sibling.replace("\n", "").strip()
                if len(example) > 0:
                    examples.append(example)
            sense["examples"] = examples

        # Mappings
        if child.text == "Mappings:":
            mappings = dict()
            for font in child.parent.find_all("font"):
                mapping_str = font.text.strip()
                if font.attrs["color"] == "008000" and "\n" in mapping_str:
                    for mapping in mapping_str.split("\n"):
                        mapping = mapping.strip()
                        if len(mapping) > 0:
                            source, values = process_mapping(mapping)
                            mappings[source] = values
                else:
                    mapping = mapping_str.strip()
                    if len(mapping) > 0:
                        source, values = process_mapping(mapping)
                        mappings[source] = values
            sense["mappings"] = mappings
            senses.append(sense)
            continue

    page["senses"] = senses
    return page


# Usage: python verbnet_grouping.py --output_dir ./data/verbnet_out
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, help="Path to output directory")
    args = parser.parse_args()

    read_grouping_category(category_url, args.output_dir)

