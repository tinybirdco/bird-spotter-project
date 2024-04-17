import requests
import logging
import warnings
import os
import datetime as dt


warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TODAY = dt.datetime.now().strftime('%Y-%m-%d')


BASE_URL = 'https://api.tinybird.co/v0/pipes/'
ENDPOINTS_CONFIG = [
    {'name': 'tb_bird_records_ingestion_logs', 'field': 'append_count', "limit": 1},
    {'name': 'tb_birds_by_hour_and_country_copy_logs', 'field': 'copy_count', "limit": 9}, # 9 copy jobs will happen before 8am UTC
    {'name': 'tb_tiny_birds_records_bq_sync_logs', 'field': 'replace_count', "limit": 1},
]


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


def get_data_from_tb_endpoint(endpoint_name) -> list:
    '''
    Returns the data from a Tinybird endpoint call.
    '''
    token = get_token(None)
    url = f'{BASE_URL}{endpoint_name}.json'
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            records = data['data']
            return records
    except Exception as e:
        logger.error(f"Error: {e}")
        pass


def get_alerts_from_tb_endpoints(endpoint:dict, records:list, alerts: dict) -> dict:   
    '''
    Append alerts if any of the log operations failed.
    '''
    
    last_record = records[0]
    last_record_date = last_record['date']

    if last_record_date != TODAY:
            alerts["alert_message"].append(
                f"Alert! Ingestion operation missing. Last ingestion date is not today: {last_record_date}"
            )
            alerts["alert_count"][endpoint['field']] += 1
    else:
        if last_record[endpoint['field']] < endpoint['limit']:
            alerts["alert_count"][endpoint['field']] += 1
            alerts["alert_message"].append(
                f"Alert! Last {endpoint['field']} count is less than {endpoint['limit']}."
            )
        elif last_record[endpoint['field']] == endpoint['limit']:
            alerts["alert_message"].append(
                f"Last {endpoint['field']} count is equal to {endpoint['limit']}. All fine!"
            )
        else:
            alerts["alert_message"].append(
                f"Alert! Last {endpoint['field']} count is greater than {endpoint['limit']}. Check it!"
            )


def log_alerts(alerts: dict) -> None:
    '''
    Log alerts.
    '''
    for alert in alerts['alert_message']:
        logger.info(alert)
    logger.info("Alerts summary:")
    logger.info(f"Append error count: {alerts['alert_count']['append_count']}")
    logger.info(f"Copy error count: {alerts['alert_count']['copy_count']}")
    logger.info(f"Replace error count: {alerts['alert_count']['replace_count']}")


def monitor() -> None:
    '''
    Get alerts from each endpoint list.
    '''

    alerts = {
        "alert_count":
            {
                "replace_count": 0,
                "copy_count": 0,
                "append_count": 0
            },
        "alert_message": []
    } 
    for endpoint in ENDPOINTS_CONFIG:
        records = get_data_from_tb_endpoint(endpoint['name'])
        get_alerts_from_tb_endpoints(endpoint, records, alerts)
    
    log_alerts(alerts)


if __name__ == '__main__':
    monitor()