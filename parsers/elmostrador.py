import json
import os

from pyquery import PyQuery as pq


data = []

for i in range(1, 10):
    asdf = pq(
        url='http://www.elmostrador.cl/noticias/page/{0:d}/'.format(i),
        headers={
            'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19'
        }
    )

    elements = asdf('section article')

    for e in elements:
        header = e.xpath('./div/h4/a/text()')
        subheader = e.xpath('./div/p/text()')
        link = e.xpath('./div/h4/a/@href')
        if len(subheader) == 0 or len(link) == 0:
            continue
        news = {
            'url': link[0],
            'header': header[0].strip(),
            'subheader': subheader[0].strip(),
            'source': 'elmostrador.cl',
        }
        data.append(news)

with open(os.path.join('data', 'elmostrador.json'), 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
