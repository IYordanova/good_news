#!/usr/bin/env python3
import os
import logging
import traceback
from datetime import datetime
from google.cloud import storage


class FileWriter:

    def __write_to_gcs(self, bucket_name, prefix, content, link):
        gcp_client = storage.Client()
        bucket = gcp_client.bucket(bucket_name)
        blob = bucket.blob(prefix)
        blob.upload_from_string(content)
        metadata = {'link': link}
        blob.metadata = metadata
        blob.patch()

    def __write_locally(self, filename, content):
        local_file = open(filename, 'w')
        local_file.write(content)
        local_file.close()

    def write_to_file(self, article, source_name):
        sink_folder = os.path.join('articles', source_name, f'{datetime.now():%Y-%m-%d}')
        filename = os.path.join(sink_folder, article.title)

        try:
            if os.getenv('ENVIRONMENT') == 'local':
                logging.info(f'Writing file {filename} to {filename}')
                self.__write_locally(filename, article.content)
            else:
                bucket_name = os.getenv('ARCHIVE_BUCKET')
                logging.info(f'Writing file {filename} to {os.path.join(bucket_name, filename)}')
                self.__write_to_gcs(bucket_name, filename, article.content, article.link)
            return filename
        except:
            logging.error(traceback.format_exc())
            return None

