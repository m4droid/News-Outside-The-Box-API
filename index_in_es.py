import json
import sys

from elasticsearch import Elasticsearch


es = Elasticsearch()

with open(sys.argv[1]) as f:
    data = json.load(f)

for news in data:
    es.index(index='totb', doc_type='news', body=news)
