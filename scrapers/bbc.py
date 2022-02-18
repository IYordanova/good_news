#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import traceback
import logging
from scrapers.model import Article
from scrapers.file_writer import FileWriter

name = 'BBC'


class Bbc:
    base_url = 'https://www.bbc.co.uk'
    categories = ['news']

    def get_category_news_bodies(self, category):
        r1 = requests.get(f'{self.base_url}/{category}')
        if r1.status_code != 200:
            logging.error(f'Response from {name} was {r1.status_code}')
            return []

        bs_content = BeautifulSoup(r1.content, 'html5lib')
        news = bs_content.find_all('div', class_='gs-c-promo-body')
        logging.info(f'Found {len(news)} elements matching article`s class')
        return news

    def get_news(self):
        already_scraped_links = set()
        all_files = set()

        for category in self.categories:
            news = self.get_category_news_bodies(category)
            for news_item in news:
                try:
                    link = news_item.find('a')['href']
                    # ignore external or links to main page
                    if link.startswith('http'):
                        continue

                    link = f'{self.base_url}{link}'
                    if link in already_scraped_links:
                        continue
                    already_scraped_links.add(link)

                    title = news_item.find('h3', class_='gs-c-promo-heading__title').get_text()
                    logging.info(f'title: {title}, link: {link}')

                    article_response = requests.get(f'{link}')
                    if article_response.status_code != 200:
                        logging.error(f'Response from {name} was {article_response.status_code}')
                        return
                    soup_article = BeautifulSoup(article_response.content, 'html5lib')

                    select = soup_article.select('div[data-component="text-block"]')
                    article_body = '\n'.join(map(lambda x: x.get_text(), select))
                    all_files.add(FileWriter().write_to_file(Article(title, link, article_body), name))
                except:
                    logging.error(traceback.format_exc())

            return all_files
