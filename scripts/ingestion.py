import logging
import requests
import warnings
import os
import json

BASE_URL = 'https://api.tinybird.co/v0/pipes/'
TB_TOKEN = os.environ.get('TB_TOKEN')

warnings.filterwarnings("ignore")
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ndjson(endpoint_name:str, token=TB_TOKEN) -> list:
    '''Get ndjson from a url.'''
    logger.info(f"Getting data from {endpoint_name}...")

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


def ingest_data(datasource_name, endpoint_name, token=TB_TOKEN):
    '''Ingest data into a data source from an endpoint file path'''
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

    ingest_data(
        'bird_records',
        'bird_records_sample'
    )

if __name__ == '__main__':
    ingestion()