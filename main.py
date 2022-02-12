#!/usr/bin/env python3
import time
import traceback
import logging
from scrapers.bbc import Bbc
from scrapers.associated_press import AssociatedPress
from scrapers.the_guardian import TheGuardian


def __scrape_news(source):
    try:
        start = time.time()
        found_files = source.get_news()
        end = time.time()
        logging.info(f'Scraped {source.name} and found {len(found_files)} news in {end - start} seconds')
    except:
        logging.error(traceback.format_exc())


def main():
    __scrape_news(Bbc())
    __scrape_news(TheGuardian())
    __scrape_news(AssociatedPress())


if __name__ == '__main__':
    main()
