import requests
import bs4
from urllib.parse import urljoin
from lesson3.database.db import Database


"""
FIFO
FILO
"""

class GbBlogParse:
    def __init__(self, start_url, database: Database):
        self.db = database
        self.start_url = start_url
        self.done_urls = set()
        self.tasks = [self.get_task(self.start_url, self.parse_feed), ]
        self.done_urls.add(self.start_url)

    def get_task(self, url, callback):
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)
        return task

    def _get_response(self, url):
        response = requests.get(url)
        return response

    def _get_soup(self, url):
        soup = bs4.BeautifulSoup(self._get_response((url)).text, 'lxml')
        return soup

    def parse_post(self, url, soup):
        title = soup.find('h1', attrs={'class': 'blogpost-title'}).text
        image = soup.find('div', attrs={'class': 'hidden', 'itemprop': "image"}).text
        author_tag = soup.find('div', attrs={'itemprop':"author"})
        author_url = urljoin(url, author_tag.parent.attrs.get('href'))
        author_name = author_tag.text
        tags = [{'name': tag.text, 'url': urljoin(url, tag.attrs.get("href"))} for tag in soup.find_all('a', attrs={'class': "small"})]

        data = {
            'post_data': {
                'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
                'url': url,
            },
            'author_data': {
                'url': urljoin(url, author_tag.parent.attrs.get('href')),
                'name': author_tag.text,
            },
            'tags_data': [{'name': tag.text, 'url': urljoin(url, tag.attrs.get("href"))} for tag in soup.find_all('a', attrs={'class': "small"})],

        }
        return data


    def parse_feed(self, url, soup): #парсим ленту
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        pag_urls = set([urljoin(url, href.attrs.get('href'))
                        for href in ul.find_all('a') if href.attrs.get('href')])

        for pag_url in pag_urls:
            if pag_url not in self.done_urls:
                self.tasks.append(self.get_task(pag_url, self.parse_feed))

        post_items = soup.find('div', attrs={'class': "post-items-wrapper"})
        post_urls = set([urljoin(url, href.attrs.get('href'))
                        for href in post_items.find_all('a', attrs={'class': 'post-item__title'}) if href.attrs.get('href')])
        for post_url in post_urls:
            if post_url not in self.done_urls:
                self.tasks.append(self.get_task(post_url, self.parse_post))



    def run(self):
        for task in self.tasks:
            task_result = task()
            if task_result:
                self.save(task_result)


    def save(self, data):
        self.db.create_post(data)

if __name__ == '__main__':
    database = Database('sqlite:///gb_blog.db')
    parser = GbBlogParse('https://geekbrains.ru/posts', database)
    parser.run()