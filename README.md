# Bird Spotter Project

A Tinybird project to monitor data source ingestion, copy processes and BigQuery syncs using fake bird data and Tinybird endpoints and service data sources.

In order to fake 

## Installation

1. Clone the repository
2. Create a virtual environment:

```bash
python3 -m venv .bird-spotter-project-env
source .bird-spotter-project-env/bin/activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Set your Tinybird Token as an environment variable:

```bash
export TB_TOKEN=your_api_key
```

This Token should have the proper permissions to append data to the `bird_records` data source and to read the `tb_bird_records_ingestion_logs`, `tb_birds_by_hour_and_country_copy_logs`,  `tb_tiny_bird_records_bq_sync_logs` and `bird_records_sample` endpoints.

### Project Structure

Workspace: bird_spotter

**Data Sources**

* `bird_records`: it will be populated by hfi via python scripts
* `birds_by_hour_and_country_from_copy`: it is populated from a copy pipe every hour
* `tiny_bird_records`: it will be replaced by BQ every day


**Copy pipes**

* `birds_aggregated_by_hour_and_country`: copy pipe that aggregates the data from `bird_records` by hour and country and populates `birds_by_hour_and_country_from_copy`


**Endpoints**

* `tb_bird_records_ingestion_logs`: check ingestion events and errors by date
* `tb_birds_by_hour_and_country_copy_logs`: check copy events and errors by hour
* `tb_tiny_bird_records_bq_sync_logs`: check bq syncs by date
* `bird_records_sample`: sample of the `bird_records` data source

**Python Scripts**

* `ingestion.py`: ingest data into `bird_records`
* `monitor.py`: monitor the ingestion, copy and sync processes

**Workflows**

* `ingestion.yml`: ingest data from a Tinybird endpoint (faking a real data set) into `bird_records` using the events API every day at 1:00 UTC
* `monitor.yml`: monitor the ingestion, copy and sync processes every day at 8:00 UTC 

**TODO**

- [x] Fake a no ingestion error
- [ ] Fake a data ingestion error
- [ ] Fake a quarantine error