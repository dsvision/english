import pickle
import re
import requests
import json
import time

# define common variables for the framework
url = "http://api.wordnik.com:80/v4/word.json/{0}/definitions"
data = {"api_key": "ce5134acdef93bdff800e08953a0002fe6d38a3a4611e441f"}

def cleaned(definition):
    text = re.sub(r"[^a-zA-z ]", "", definition["text"]).lower()
    d = text.split("  ")
    if len(d) > 1:
        return None

    # get only the first part of the definition. Seconds normally are examples
    d = d[0].split(";")[0]

    # avoid self defintions
    if definition["word"].lower() in d:
        return None

    # clean spaces
    return d.strip()


def get_definitions(word):
    # query the REST server
    response = requests.get(url.format(word), headers=data)

    # the json is a list of definitions, if any
    definitions = []
    for case in response.json():
        c = cleaned(case)
        if c is not None:
            definitions.append(c)
    return definitions


N = 14500

with open("data/words.txt") as f:
    words = [w.strip() for w in f.readlines()]
    chunks = [words[i:i + N] for i in range(0, len(words), N)]

time_to_sleep = 2

start_time = time.time()

with open("data/definitions.pickle", "wb") as output:
    for i, chunk in enumerate(chunks):
        print("Processing chunk {0}: {1}-{2}".format(i, chunk[0], chunk[1]))

        definitions = []
        for word in chunk:
            # get the definition
            d = get_definitions(word)
            print("{0} has {1} definitions".format(word, len(d)))
            pickle.dump((word, d), output, protocol=2)

        diff = time.time() - start_time
        if diff < 0:
            diff = 0
            start_time = time.time()

        time.sleep(time_to_sleep - diff % time_to_sleep)