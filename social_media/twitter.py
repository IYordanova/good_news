#!/usr/bin/env python3
from google.cloud import storage
import logging

class Twitter:

    def __get_links(self, bucket_name, prefix):
        gcp_client = storage.Client()
        blobs = gcp_client.get(bucket_name, prefix=prefix)
        return blobs[0].metadata['link']

    def post(self, files_to_post):
        logging.info("printing")
