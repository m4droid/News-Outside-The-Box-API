import json
import re
from urllib.parse import urlparse, unquote

from elasticsearch import Elasticsearch

from flask import Flask, Response, request


es = Elasticsearch()
app = Flask(__name__)


INDEX = 'totb'
DOCUMENTS = 'news'

LEFT_EVIL = [
    'elmostrador.cl',
    'theclinic.cl',
    'elciudadano.cl'
]

RIGHT_EVIL = [
    'emol.com',
    'latercera.com',
]

NEUTRAL_EVIL = [
    'cooperativa.cl'
]

THE_OTHER_SIDE = {s: list(RIGHT_EVIL) for s in LEFT_EVIL}
THE_OTHER_SIDE.update({s: list(LEFT_EVIL) for s in RIGHT_EVIL})
THE_OTHER_SIDE.update({s: list(LEFT_EVIL) + list(RIGHT_EVIL) for s in NEUTRAL_EVIL})


def analyzer_mapper(analyzer):
    return {
        "type": "string",
        "analyzer": analyzer,
        "search_analyzer": analyzer,
        "search_quote_analyzer": analyzer,
    }


DOCUMENT_MAPPING = {
    "news": {
        "properties": {
            "header": analyzer_mapper('spanish'),
            "subheader": analyzer_mapper('spanish'),
        }
    }
}


es.indices.put_mapping(
    index=INDEX,
    doc_type=DOCUMENTS,
    body=DOCUMENT_MAPPING
)


@app.route('/news', methods=['POST'])
def news_search():
    data = {
        'url': request.json.get('url') or '',
        'header': request.json.get('header') or '',
        'subheader': request.json.get('subheader') or ''
    }

    data['header'] = data['header'].replace('\r\n', '')
    data['subheader'] = data['subheader'].replace('\r\n', '')

    news_headers = [data.get('header'), data.get('subheader')] if data is not None else []

    if data.get('url') is not None:
        matcher = re.match(r'https:\/\/l\.facebook.com\/l\.php\?u=(.*)&.*$', data['url'])
        if matcher is not None:
            uri = urlparse(unquote(matcher.group(1)))
            data['source'] = uri.netloc.replace('www.', '')
    if 'source' not in data:
        data['source'] = None

    es_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "more_like_this": {
                            "fields": ["header", "subheader"],
                            "like": ' '.join(news_headers).strip(),
                            "min_term_freq": 1,
                            "min_doc_freq": 1
                        }
                    },
                ],
                "filter": {
                    "bool": {
                        "should": []
                    }
                }
            }
        }
    }

    es_query['query']['bool']['filter']['bool']['should'] = [
        {"term": {"source": source}} for source in THE_OTHER_SIDE.get(data['source'], [])
    ]

    es_response = es.search(index=INDEX, doc_type=DOCUMENTS, body=es_query)

    news = [h for h in es_response['hits']['hits'] if 'header' in h['_source']]

    return Response(json.dumps(news), status=200, mimetype='application/json')
