import json
import logging
import time

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


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
        t_r_a_s_h = ['Женская одежда', 'Мужская одежда', 'Женская обувь', 'Мужская обувь', 'Аксессуары',
                     'Обувь детская', 'Одежда детская', 'Распродажа', 'Новинки']
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
        result = [sub.get('href') for sub in subs if sub.get('href') and sub.text not in t_r_a_s_h]
        return result

    def get_items_from_page(self, page):
        soup = BeautifulSoup(page, 'html.parser')
        items = soup.find('div', {'class': 'catalog_block'}).find_all('div', {'class': 'catalog_item_wrapp'})
        return [item.find('div', {'class': 'item-title'}).find('a').get('href') for item in items]

    def get_pages_nums(self, page):
        soup = BeautifulSoup(page, 'html.parser')
        paginator = soup.find('span', {'class': 'nums'})
        if not paginator:
            return 1
        nums = paginator.find_all('a')[-1].text
        return int(nums)

    def get_all_items(self, link, nums):
        items = []
        for num in range(1, nums + 1):
            bot.send_request(f'{link}/?PAGEN_1={num}')
            items.extend(self.get_items_from_page(bot.LastPage))
        return items

    def save_json(self, data, path='links.json'):
        with open(path, 'w') as file:
            file.write(json.dumps(data, ensure_ascii=False))
            file.close()


if __name__ == "__main__":
    bot = API()
    categories_links = bot.get_catalog_menu_links()
    products_links = []
    for link in tqdm(categories_links):
        bot.send_request(link)
        page = bot.LastPage
        nums = bot.get_pages_nums(page)
        s = bot.get_all_items(link, nums)
        products_links.extend(s)
    bot.save_json({'links': products_links})
