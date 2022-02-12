#!/usr/bin/env python3
import os
import logging
from datetime import datetime

from google.cloud import language_v1
from google.cloud import storage


class SentimentAnalyzer:

    def __list_bucket(self, bucket_name, prefix):
        gcp_client = storage.Client()
        blobs = gcp_client.list_blobs(bucket_name, prefix=prefix)
        return map(lambda b: b.name, blobs)

    def __analyze_file_sentiment(self, gcs_content_uri):
        """
          gcs_content_uri Google Cloud Storage URI where the file content is located.
          e.g. gs://[Your Bucket]/[Path to File]
        """

        client = language_v1.LanguageServiceClient()
        document = {
            "gcs_content_uri": gcs_content_uri,
            "type_": language_v1.Document.Type.PLAIN_TEXT,
            "language": "en"
        }
        response = client.analyze_sentiment(request={
            'document': document,
            'encoding_type': language_v1.EncodingType.UTF8
        })

        logging.info(u"Document {} sentiment score: {}, magnitude: {}".format(
            gcs_content_uri,
            response.document_sentiment.score,
            response.document_sentiment.magnitude
        ))

        return response.document_sentiment.score, response.document_sentiment.magnitude

    def analyze(self, source_name):
        bucket_name = os.getenv('ARCHIVE_BUCKET')
        files_to_analyze = self.__list_bucket(
            bucket_name,
            os.path.join('articles', source_name, f'{datetime.now():%Y-%m-%d}')
        )
        scored_files = map(lambda f: (f, self.__analyze_file_sentiment(f'gs://{bucket_name}/{f}')), files_to_analyze)
        return map(lambda ft: ft[0], sorted(list(scored_files), key=lambda x: (x[1][0], x[1][1]))[:3])
