import requests
import logging
import warnings
import os


warnings.filterwarnings("ignore")
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


TB_TOKEN = os.environ.get('TB_TOKEN')
BASE_URL = 'https://api.tinybird.co/v0/pipes/'
ENDPOINTS_CONFIG = [
    {'name': 'tb_bird_records_ingestion_logs', 'field': 'ingestion_count'},
    {'name': 'tb_birds_by_hour_and_country_copy_logs', 'field': 'copy_count'},
    {'name': 'tb_tiny_birds_records_bq_sync_logs', 'field': 'replace_count'}
]


def get_data_from_tb_endpoint(endpoint_name:str, token:str=TB_TOKEN) -> list:
    '''
    Returns the data from a Tinybird endpoint call.
    '''
    url = f'{BASE_URL}{endpoint_name}.json'
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            records = data['data']
    except Exception as e:
        logger.error(f"Error: {e}")
        pass
        
    return records


def get_alerts_from_tb_endpoints(endpoint_field:str, records:list) -> dict:   
    '''
    Returns an alert object with errors, events and records messages.
    '''
    alerts = {
        "errors": "",
        "events": "",
        "records": ""
    }
    event_type = endpoint_field.split('_')[0]

    if len(records) > 0:
        error_count = records[0]['error_count']
        event_count = records[0][endpoint_field]

        if error_count > 0:
            alerts['errors'] = "There are errors."
                
        if event_count == 0:
            alerts['events'] =  f"There were no {event_type} events."
    
    else:
        alerts['events'] = "No records for today."

    return alerts


def monitor() -> None:
    '''
    Get alerts from each endpoint list.
    '''

    for endpoint in ENDPOINTS_CONFIG:
        records = get_data_from_tb_endpoint(endpoint['name'])
        alerts = get_alerts_from_tb_endpoints(endpoint['field'], records)
        logging.info(alerts)


if __name__ == '__main__':
    monitor()