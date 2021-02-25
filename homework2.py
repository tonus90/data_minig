import requests
from pathlib import Path
import bs4
from urllib.parse import urljoin
import pymongo
import datetime

"""
Необходимо собрать структуры товаров по акции и сохранить их в MongoDB

пример структуры и типы обязательно хранить поля даты как объекты datetime
{
    "url": str,
    "promo_name": str,
    "product_name": str,
    "old_price": float,
    "new_price": float,
    "image_url": str,
    "date_from": "DATETIME",
    "date_to": "DATETIME",
}
"""

class MagnitParse:
    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client['db_data_mining']
        self.collection = self.db['magnit_products_hm']

    def _get_response(self, url):
        # TODO: написать обработку ошибки
        return requests.get(url)

    def _get_soup(self, url):
        response = self._get_response(url)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def _parse(self, product_a):
        data = {}
        for key, funk in self._get_template().items():
            try:
                data[key] = funk(product_a)
            except (AttributeError, ValueError) as err:
                print(err)
        return data

    def _save(self, data: dict):
        self.collection.insert_one(data)

    def run(self):
        soup = self._get_soup(self.start_url)
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})
        for prod_a in catalog.find_all('a', recursive=False):
            product_data = self._parse(prod_a)
            print(product_data)
            self._save(product_data)

    def _get_template(self):
        return {
            'url': lambda a: urljoin(self.start_url, a.attrs.get('href', '')),
            'promo_name': lambda a: a.find('div', attrs={'class': 'card-sale__name'}).text,
            'product_name': lambda a: a.find('div', attrs={'class': 'card-sale__title'}).text,
            'old_price': lambda a: float('.'.join(a.find('div', attrs={'class': 'label__price label__price_old'}).text.split())),
            'new_price': lambda a: float('.'.join(a.find('div', attrs={'class': 'label__price label__price_new'}).text.split())),
            'image_url': lambda a: urljoin('https://magnit.ru', a.find('img').attrs.get('data-src', '')),
            'date_from': lambda a: self._get_datetime(a.find('div', attrs={'class': 'card-sale__date'}).text.split())[0],
            'date_to': lambda a: self._get_datetime(a.find('div', attrs={'class': 'card-sale__date'}).text.split())[1],
        }

    def _get_datetime(self, list_with_date):
        year = 2021
        months = {
            'янв': 1,
            'фев': 2,
            'мар': 3,
            'апр': 4,
            'май': 5,
            'июн': 6,
            'июл': 7,
            'авг': 8,
            'сен': 9,
            'окт': 10,
            'ноя': 11,
            'дек': 12,
        }

        my_dict = {
            '0': 'с',
            '1': 'до',
        }

        for i in range(len(my_dict)):
            list_with_date.remove(my_dict[str(i)])

        date_since = datetime.datetime(year, months[list_with_date[1][:3:]], int(list_with_date[0]))
        date_undo = datetime.datetime(year, months[list_with_date[3][:3:]], int(list_with_date[2]))
        return [date_since, date_undo]

        # my_list = curr_date.split("\n")
        # date_from = my_list[1][2::].split(' ')
        # date_from[1] = months[date_from[1].replace(date_from[1], date_from[1][:3:])]
        # my_str_from = ' '.join(date_from)
        # date_to = my_list[2][3::].split(' ')
        # date_to[1]=months[date_to[1].replace(date_to[1], date_to[1][:3:])]
        # my_str_to = ' '.join(date_to)
        # my_date_list = [my_str_from, my_str_to]
        # result = []
        # for i in my_date_list:
        #     result.append(time.strptime(f'{i} {year}', '%d %b %Y'))





if __name__ == '__main__':
    url = 'https://magnit.ru/promo/'
    def get_save_path(dir_name):
        save_path = Path(__file__).parent.joinpath(dir_name)
        if not save_path.exists():
            save_path.mkdir()
        return save_path

    save_path = get_save_path('magnit_products')
    db_client = pymongo.MongoClient('mongodb://localhost:27017') #'mogodb://login:password@localhost:27017/db_name'
    parser = MagnitParse(url, db_client)
    parser.run()

