from __future__ import print_function

import time
import traceback
import logging
import datetime

from airflow.operators.python_operator import PythonOperator

from scrapers.associated_press import AssociatedPress, name as ap_name
from scrapers.bbc import Bbc, name as bbc_name
from scrapers.the_guardian import TheGuardian, name as guardian_name
from analyzers.sentiment_analyzer import SentimentAnalyzer
from social_media.twitter import Twitter


default_dag_args = {
    'start_date': datetime.datetime(2022, 2, 12),
}

with models.DAG(
        'news',
        schedule_interval=datetime.timedelta(days=1),
        catchup=False,
        tags=['news'],
        default_args=default_dag_args) as dag:
    def scrape_news(**op_kwargs):
        source_name = op_kwargs['source_name']
        if source_name == bbc_name:
            scraper = Bbc()
        elif source_name == guardian_name:
            scraper = TheGuardian()
        elif source_name == ap_name:
            scraper = AssociatedPress()
        else:
            raise Exception(f"{source_name} not supported")
        try:
            start = time.time()
            found = scraper.get_news()
            end = time.time()
            logging.info(f'Scraped {source_name} and found {found} news in {end - start} seconds')
        except:
            logging.error(traceback.format_exc())


    def analyze_news(**op_kwargs):
        source_name = op_kwargs['source_name']
        try:
            start = time.time()
            SentimentAnalyzer().analyze(source_name)
            end = time.time()
            logging.info(f'Analyzed files for {source_name} in {end - start} seconds')
        except:
            logging.error(traceback.format_exc())


    def post_results(**op_kwargs):
        task_ids = op_kwargs['taskIds']
        try:
            scored_files = op_kwargs['ti'].xcom_pull(task_ids=task_ids)
            Twitter().post(scored_files)
            logging.info(f'Posted final to social media')
        except:
            logging.error(traceback.format_exc())


    bbc_news = PythonOperator(
        task_id='bbc_news_scrape',
        python_callable=scrape_news,
        provide_context=True,
        op_kwargs={'source_name': bbc_name}
    )
    bbc_analyze = PythonOperator(
        task_id='bbc_news_analyze',
        python_callable=analyze_news,
        xcom_push=True,
        provide_context=True,
        op_kwargs={'source_name': bbc_name}
    )

    guardian_news = PythonOperator(
        task_id='guardian_news_scrape',
        python_callable=scrape_news,
        provide_context=True,
        op_kwargs={'source_name': guardian_name}
    )
    guardian_analyze = PythonOperator(
        task_id='guardian_news_analyze',
        python_callable=analyze_news,
        xcom_push=True,
        provide_context=True,
        op_kwargs={'source_name': guardian_name}
    )

    ap_scraper = AssociatedPress()
    ap_news = PythonOperator(
        task_id='ap_news_scrape',
        python_callable=scrape_news,
        provide_context=True,
        op_kwargs={'source_name': ap_name}
    )
    ap_analyze = PythonOperator(
        task_id='ap_news_analyze',
        python_callable=analyze_news,
        xcom_push=True,
        provide_context=True,
        op_kwargs={'source_name': ap_name}
    )

    post_results = PythonOperator(
        task_id='post_results',
        python_callable=post_results,
        provide_context=True,
        op_kwargs={'taskIds': ['bbc_news_analyze', 'guardian_news_analyze', 'ap_news_analyze']}
    )

    bbc_news >> bbc_analyze >> post_results
    guardian_news >> guardian_analyze >> post_results
    ap_news >> ap_analyze >> post_results
