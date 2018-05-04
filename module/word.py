

import json
import io

def write():
    return "I'm the word"

def read_data():
    with io.open("static/resources/source2.json") as fp:
        json_data = json.load(fp)
    return json_data
