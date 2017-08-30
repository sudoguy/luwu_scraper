import logging
import time

import requests
from bs4 import BeautifulSoup


class API(object):
    def __init__(self):
        self.BASE_URL = 'https://luwu.ru'
        self.LastResponse = None
        self.LastPage = None
        self.session = requests.Session()

        self.products = []

        # handle logging
        self.logger = logging.getLogger('[luwu-scraper]')
        self.logger.setLevel(logging.DEBUG)
        logging.basicConfig(format='%(asctime)s %(message)s',
                            filename='luwu.log',
                            level=logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def send_request(self, endpoint, post=None):
        if not self.session:
            self.logger.critical("Session is not created.")
            raise Exception("Session is not created!")

        self.session.headers.update({'Connection': 'close',
                                     'Accept': '*/*',
                                     'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                     'Cookie2': '$Version=1',
                                     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
                                     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'})
        if 'http' not in endpoint:
            endpoint = self.BASE_URL + endpoint

        if post is not None:  # POST
            response = self.session.post(endpoint, data=post)
        else:  # GET
            response = self.session.get(endpoint)

        if response.status_code == 200:
            self.LastResponse = response
            self.LastPage = response.text
            return True
        else:
            self.logger.warning("Request return " +
                                str(response.status_code) + " error!")
            if response.status_code == 429:
                sleep_minutes = 5
                self.logger.warning("That means 'too many requests'. "
                                    "I'll go to sleep for %d minutes." % sleep_minutes)
                time.sleep(sleep_minutes * 60)

            # for debugging
            try:
                self.LastResponse = response
                self.LastPage = response.text.decode('cp1251')
            except Exception as e:
                self.logger.error(str(e))
        return False

    def get_catalog_menu_links(self, page=None):
        if not page:
            self.send_request(self.BASE_URL)
            page = self.LastPage
        soup = BeautifulSoup(page, 'html.parser')
        soup = soup.find('div', {'class': 'catalog_menu'}).find('ul', {'class': 'menu'})
        categories = soup.find_all('li', {'class': 'menu_item_l1'})
        categories = [name.find_all('a', {'class': ''}) for name in categories]
        subs = []
        for cat in categories:
            subs.extend(cat)
        result = [sub.get('href') for sub in subs if sub.get('href')]
        return result

    def get_items_from_page(self, page):
        pass


if __name__ == "__main__":
    bot = API()
    categories_links = bot.get_catalog_menu_links()
    print(categories_links)
