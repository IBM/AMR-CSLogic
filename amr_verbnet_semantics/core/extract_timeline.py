import json
import os
import re

import wikipedia


def extract_time_line(page_title, output_dir):
    print("Crawling page <{}>".format(page_title))

    timelines = dict()
    t = wikipedia.page(page_title)
    # print(t.content)
    # input()

    pattern = r"(===(?P<time>\s(.*)\s)===(\n+)(?P<description>(.*))(\n+))|(==(?P<category>\s(.*)\s)==\n)"
    matched = re.finditer(pattern, t.content)
    cur_category = None
    for m in matched:
        if m.groupdict()["category"] is not None:
            if m.groupdict()["category"] not in timelines:
                cur_category = m.groupdict()["category"].strip()
                timelines[cur_category] = list()
        else:
            timeline = dict()
            timeline["time"] = m.group("time").strip()
            timeline["description"] = m.group("description").strip()
            timelines[cur_category].append(timeline)
            # print(cur_category)
            # print(timeline)
            # input()

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output_path = os.path.join(output_dir, "_".join(page_title.split()) + ".json")
    with open(output_path, "w") as f:
        json.dump(timelines, f)
        print("Written to {}".format(output_path))

    print("DONE.")
    return timeline


def test_summary():
    # print(wikipedia.summary("Wikipedia"))
    print(wikipedia.summary("Timeline of the COVID-19 pandemic in January 2020"))


if __name__ == "__main__":
    extract_time_line("Timeline of the COVID-19 pandemic in January 2020", "./data/wikipedia")

