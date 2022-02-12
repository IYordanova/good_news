#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import traceback
import logging
from scrapers.model import Article
from scrapers.file_writer import FileWriter


name = 'The Guardian'


class TheGuardian:
    base_url = 'https://www.theguardian.com'
    categories = ['world']

    def get_category_news_bodies(self, category):
        r1 = requests.get(f'{self.base_url}/{category}')
        if r1.status_code != 200:
            logging.error(f'Response from {name} was {r1.status_code}')
            return

        bs_content = BeautifulSoup(r1.content, 'html5lib')
        news = bs_content.find_all('h3', class_='fc-item__title')
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
                    if link in already_scraped_links:
                        continue
                    already_scraped_links.add(link)

                    title = news_item.get_text()
                    logging.info(f'title: {title}, link:{link}')

                    # Reading the content (it is divided in paragraphs)
                    article_response = requests.get(link)
                    if article_response.status_code != 200:
                        logging.error(f'Response from {name} was {article_response.status_code}')
                        return
                    soup_article = BeautifulSoup(article_response.content, 'html5lib')

                    all_paragraphs = soup_article.find_all(['p'])
                    article_paragraphs = list(all_paragraphs)
                    article_body = '\n'.join(map(lambda x: x.get_text(), article_paragraphs))
                    all_files.add(FileWriter().write_to_file(Article(title, link, article_body), name))
                except:
                    logging.error(traceback.format_exc())

            return all_files
