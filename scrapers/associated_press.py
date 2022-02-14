#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import traceback
import logging
from scrapers.model import Article
from scrapers.file_writer import FileWriter

name = 'Associated Press'


class AssociatedPress:
    base_url = 'https://apnews.com'
    categories = ['']

    def __headline_filter(self, link_tag):
        class_names = link_tag.get('class')
        if class_names is None:
            return False

        return any('title' in class_name or 'headline' in class_name for class_name in class_names)

    def __article_body_filter(self, p_tag):
        class_names = p_tag.get('class')
        if class_names is None:
            return False

        return any('Component-root' in class_name for class_name in class_names)

    def __get_category_news_bodies(self, category):
        r1 = requests.get(f'{self.base_url}/{category}')
        if r1.status_code != 200:
            logging.error(f'Response from {name} was {r1.status_code}')
            return []

        bs_content = BeautifulSoup(r1.content, 'html5lib')
        all_links = bs_content.find_all(['a'])
        news = list(filter(self.__headline_filter, all_links))
        logging.info(f'Found {len(news)} elements matching article`s class')
        return news

    def get_news(self):
        already_scraped_links = set()
        all_files = set()

        for category in self.categories:
            news = self.__get_category_news_bodies(category)
            for news_item in news:
                try:
                    link = news_item['href']
                    # ignore external or links to main page
                    if link.startswith('http'):
                        continue

                    link = f'{self.base_url}{link}'
                    if link in already_scraped_links:
                        continue
                    already_scraped_links.add(link)

                    title = news_item.find('h3').get_text()
                    logging.info(f'title: {title}, link: {link}')

                    article_response = requests.get(f'{link}')
                    if article_response.status_code != 200:
                        logging.error(f'Response from {name} was {article_response.status_code}')
                        return
                    soup_article = BeautifulSoup(article_response.content, 'html5lib')

                    all_paragraphs = soup_article.find_all(['p'])
                    article_paragraphs = list(filter(self.__article_body_filter, all_paragraphs))
                    article_body = '\n'.join(map(lambda x: x.get_text(), article_paragraphs))
                    all_files.add(FileWriter().write_to_file(Article(title, link, article_body), name))
                except:
                    logging.error(traceback.format_exc())

            return all_files
