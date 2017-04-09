import json
import os

from pyquery import PyQuery as pq


data = []

for i in range(1, 11):
    asdf = pq(
        url='https://www.cooperativa.cl/noticias/site/tax/port/fid_noticia/taxport_3___{0:d}.html'.format(i),
        headers={
            'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19'
        }
    )

    elements = asdf('div.contenido article')

    for e in elements:
        news = {
            'url': 'http://www.cooperativa.cl' + e.xpath('./p/a/@href')[0],
            'header': e.xpath('./p/a/text()')[0].strip(),
            'subheader': e.xpath('./div/text()')[0].strip(),
            'source': 'cooperativa.cl',
        }
        data.append(news)

with open(os.path.join('data', 'cooperativa.json'), 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
