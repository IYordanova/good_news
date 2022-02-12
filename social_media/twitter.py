#!/usr/bin/env python3
import os

from google.cloud import storage
import logging
import tweepy

class Twitter:

    def __get_links(self, bucket_name, prefix):
        gcp_client = storage.Client()
        blobs = gcp_client.get(bucket_name, prefix=prefix)
        return blobs[0].metadata['link']

    def post(self, files_to_post):
        logging.info(f"Posting {len(files_to_post)} links")
        bucket_name = os.getenv("ARCHIVE_BUCKET")
        auth = os.getenv("BEARER_TOKEN")

        tweet = '\n'.join(map(lambda f: self.__get_links(bucket_name, f), files_to_post))

        client = tweepy.Client(bearer_token=auth)
        status = client.create_tweet(text=tweet)
        logging.info(status.data)
