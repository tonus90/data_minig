"""
Источник: https://5ka.ru/special_offers/

Задача организовать сбор данных,
необходимо иметь метод сохранения данных в .json файлы

результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл скачанные данные сохраняются в Json вайлы, для каждой категории товаров должен быть создан отдельный файл и содержать товары исключительно соответсвующие данной категории.

пример структуры данных для файла:

{
"name": "имя категории",
"code": "Код соответсвующий категории (используется в запросах)",
"products": [{PRODUCT},  {PRODUCT}........] # список словарей товаров соответсвующих данной категории
}
"""

import requests
import json
from pathlib import Path

class GetCat:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}

    def __init__(self, url_p, resc, save_path):
        self.url_p = url_p #стартовый url
        self.dict_cats = {} #словарь категорий
        self.data_c = resc.json() #список категорий будет хранится тут
        self.i = 0 #переменная для перехода к следующей категории
        self.save_path = save_path #путь сохранения

    def _cat_dict_gen(self): #метод для создания словаря каждой категории вида {'code':123, 'name':'asd'}
        i = self.data_c[self.i] #вытащим из списка категорий 0-ю категорию (увеличивать будем по self.i - 1,2,3,4 и тд)
        self.dict_cats['code'] = i['parent_group_code']
        self.dict_cats['name'] = i['parent_group_name']
        yield self.dict_cats #создали словарь категорий и отдали

    def _get_params(self): #метод генерирует параметры ссылки для категории полученной в методе выше (_cat_dict_gen)
        for i in self._cat_dict_gen():  #вытащим словарь
            params = {
                'store': None,
                'records_per_page': 12,
                'page': 1,
                'categories': int(i['code']), #добавим код категории в параметры
                'ordering': None,
                'price_promo__gte': None,
                'price_promo__lte': None,
                'search': None
            }
            return params #вернем параметры

    def _get_prods(self): #получить список продуктов для категории
        response = requests.get(self.url_p, params=self._get_params(), headers=self.headers) #вытащим с сайта первые продукты (page=1) по данной категории акции
        result_list = [] #итоговый лист продуктов
        url = self.url_p #юрл для цикла ниже
        while url: #пока в юрл что-то есть делаем:
            data = response.json() #создадим дату продуктов данной категории page=1. На втором шаге забираем нижний response с page=2 и тд
            url = data['next'] #перекинем юрл на page=2, перекинем юрл на page3
            if url == None: #если юрл закончатся или не будет некста в page=1, то выходим изцикла
                break
            response = requests.get(url) #вытащим с сайта продукты для page=2, page=3 и тд
            my_list = [prod for prod in data['results']] #списко продуктов page=1, потом заберем продукты с page=2 в лист
            result_list = result_list+my_list #добавим список продуктов page=1 в итог, потом к page=1 добавим продукты с page=2 и тд
        return result_list #вернем список всех продуктов для категории

    def _get_res_dict_for_cat(self): #получить результирующий для задания словарь типа: {'code':123, 'name':'asd', 'PRODUCTS':[...]}
        for i in range(len(self.data_c)): #проходимся по всему кол-ву категорий
            for j in self._cat_dict_gen(): #достаем словарик для категории типа {'code':123, 'name':'asd'}
                my_dict = {key: value for key, value in j.items()} #создадим уже итоговый словарь
            my_dict['PRODUCTS'] = self._get_prods() #к которому присоединим ключ PRODUCTS со значением наших продуктов
            self.i += 1 #окей, первую категорию в списке категорий готово, увеличиваем счетчик на 1, чтобы перейти ко второй категории
            yield my_dict #выкидываем словарь для первой категории

    def go(self): #метод запуска
        for product in self._get_res_dict_for_cat(): #берем результирующий словарь
            product_path = self.save_path.joinpath(f"{product['name']} {product['code']}.json") #прописываем для него путь
            self._save(product, product_path) #сохраняем файл с помощью нижнего метода

    def _save(self, data: dict, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False)) #сохраняем в виде json


if __name__ == "__main__":

    url_p = 'https://5ka.ru/api/v2/special_offers/' #юрл продуктов
    url_c = 'https://5ka.ru/api/v2/categories/' #юрл категорий

    def get_save_path(dir_name):
        save_path = Path(__file__).parent.joinpath(dir_name)
        if not save_path.exists():
            save_path.mkdir()
        return save_path #функция для создания директории




    response_c = requests.get(url_c, headers = {'User-Agent': 'Hello WORLD!))'}) #сделаем запрос на юрл

    save_path_categories = get_save_path("categories") #сделать директорию с именем категории
    res = GetCat(url_p, response_c, save_path_categories) #сделать объект, в него прокинем стартовый юрл, готовый респонз категорий и путь директории categories
    res.go() #запустим метод go для объекта класса
