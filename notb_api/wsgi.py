import json

from elasticsearch import Elasticsearch

from flask import Flask, Response, request


es = Elasticsearch()
app = Flask(__name__)


INDEX = 'totb'
DOCUMENTS = 'news'


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
    body=DOCUMENT_MAPPING,
)


@app.route('/news', methods=['GET', 'POST'])
def news_search():
    data = request.json or {
        'header': request.args.get('header') or '',
        'subheader': request.args.get('subheader') or ''
    }

    es_query = {
        "query": {
            "more_like_this": {
                "fields": ["header", "subheader"],
                "like": ' '.join([data['header'], data['subheader']]).strip(),
                "min_term_freq": 1,
                "min_doc_freq": 1
            }
        }
    }

    es_response = es.search(
        index=INDEX,
        doc_type=DOCUMENTS,
        body=es_query,
    )

    return Response(
        json.dumps(
            es_response['hits']['hits']
        ),
        status=200,
        mimetype='application/json',
    )
