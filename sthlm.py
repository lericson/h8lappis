
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


search_url = 'https://bostad.stockholm.se/Lista/'


def iter():

    soup = BeautifulSoup(requests.get(search_url).text, 'html.parser')

    objlist = soup.find(class_='objlist')

    for row in objlist('tr'):
        cells = row('td')
        if not cells:
            continue
        cell_text = [cell.text.strip() for cell in cells]
        permalink = urljoin(search_url, cells[2].find('a')['href'])

        yield {'municipality': cell_text[0],
               'district': cell_text[1],
               'address': cell_text[2],
               'floor': cell_text[3],
               'rooms': cell_text[4],
               'permalink': permalink,
               'area': int(cell_text[5]) if cell_text[5] else None,
               'rent': int(cell_text[6]) if cell_text[6] else None,
               'expires': datetime.strptime(cell_text[7], '%Y-%m-%d').date(),
               'labels': {prop.text.strip().lower() for prop in
                          cells[8].find_all(class_='objProp')}}
