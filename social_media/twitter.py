#!/usr/bin/env python3
import os

from google.cloud import storage
import logging
import tweepy

class Twitter:

    def __get_links(self, bucket_name, prefix):
        gcp_client = storage.Client()
        blobs = list(gcp_client.list_blobs(bucket_name, prefix=prefix))
        return blobs[0].metadata['link']

    def post(self, files_to_post):
        pre_post = "\n".join(files_to_post)
        logging.info(f"Tweeting {len(files_to_post)} links: {pre_post}")
        bucket_name = os.getenv("ARCHIVE_BUCKET")

        tweet = '\n'.join(map(lambda f: self.__get_links(bucket_name, f), files_to_post))
        tweet = 'The best of today:\n' + tweet

        auth = tweepy.OAuthHandler(
            consumer_key=os.getenv("CONSUMER_KEY"),
            consumer_secret=os.getenv("CONSUMER_SECRET_KEY")
        )
        auth.set_access_token(
            os.getenv("ACCESS_TOKEN"),
            os.getenv("ACCESS_TOKEN_SECRET")
        )
        api = tweepy.API(auth)
        status = api.update_status(tweet)

        logging.info(status)
