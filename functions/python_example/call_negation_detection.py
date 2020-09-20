#!/usr/bin/env python
from __future__ import print_function

import boto3
import json
import time
import os
import logging
import warnings
import csv
import datetime

from botocore.exceptions import ClientError

from urllib.parse import unquote_plus
import traceback
import re


import utils
from extract_section import ExtractSection

# ignore warnings
warnings.filterwarnings("ignore")

## Initialize logging
logger = utils.load_log_config()

# Read configuration
configuration = utils.load_osenv()
logging.info(f"read configuration:{len(configuration)}")


def handler(event, context):

    ## check if s3_enrich_in is available
    s3_enrich_in = event['Input']['detail']['data']['s3_enrich_in']

    # if s3_enrich in is empty
    if s3_enrich_in == "":

        return {
            'statusCode': 200,
            'body': json.dumps(event['Input'])
        }

    ## extract clinical studies - call negation detection.
    try:
        response = utils.read_obj_from_bucket(s3_enrich_in)
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

    content = response['Body'].read().decode('utf-8')
    lines = content.split("\n")
    print("No of lines in the document:{}".format(len(lines)))

    clinical_studies_text = ''
    try:
        if len(lines) > 0:
            es = ExtractSection(lines)
            clinical_studies_text = es.extract_clinical_studies()
            print(clinical_studies_text)

            ## update negation_detection
            event['Input']['detail']['metadata']['is_negated'] = True

    except Exception as e:
        logging.error(
            "Exception occurred while processing event" + traceback.format_exc())
        print('Error extracting clinical studies text from text document at: {}'.format(
            s3_enrich_in))
        raise e

    print(json.dumps(event['Input'], indent=2))

    return {
        'statusCode': 200,
        'body': json.dumps(event['Input'])
    }
