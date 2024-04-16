import logging
import requests
import warnings
import os
import json
import random

BASE_URL = 'https://api.tinybird.co/v0/pipes/'

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_token(token: str) -> str:
    '''
    Get the Tinybird API token:
        :param token: Tinybird API token
    '''

    if not token:
        token = os.environ.get("TB_TOKEN")
    
        if not token:
            raise ValueError("Token not found. "
                            "Please set it as an environment variable named 'TB_TOKEN'.")
    
    return token

def get_ndjson(endpoint_name:str) -> list:
    '''Get ndjson from a url.'''
    logger.info(f"Getting data from {endpoint_name}...")
    token = get_token(None)
    url = f"{BASE_URL}{endpoint_name}.json"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            records = data['data']
            return records

    except requests.exceptions.HTTPError as e:
        raise Exception(f"Error getting data from Tinybird: {e}")


def generate_random_bit():
    '''Generate a random bit.'''
    return random.randint(0, 1)


def ingest_data(datasource_name, endpoint_name):
    '''Ingest data into a data source from an endpoint file path'''
    token = get_token(None)
    params = {
        'name': datasource_name,
        'token': token,
    }

    endpoint_data = get_ndjson(endpoint_name)
    row_count = len([row for row in endpoint_data])
    logger.info(f"Sending {row_count} rows to {datasource_name}...")
    data = '\n'.join([json.dumps(row) for row in endpoint_data])
    
    try:
        r = requests.post('https://api.tinybird.co/v0/events', params=params, data=data)
        r.raise_for_status()
        logger.info("Data appended!")
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error sending data to Tinybird: {e}")
        raise Exception(f"Error sending data to Tinybird: {e}")


def ingestion():
    '''Ingest data from an endpoint to a data source depending on a random result.'''
    if generate_random_bit():
        logger.info("Ingesting data...")
        ingest_data(
            'bird_records',
            'bird_records_sample'
        )
    else:
        logger.info("No ingestion this time.")

if __name__ == '__main__':
    ingestion()