import json
import logging
from timeit import default_timer as timer
from typing import Any, Optional
from types import MappingProxyType
from urllib.parse import urlparse

import boto3
from botocore.translate import build_retry_config

from graph import build_graph
from schedule_module import modified_critical_path
from plots import plot_schedule

# Initialize the S3 client outside of the handler
s3_client = boto3.client('s3')

# Initialize the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

BUCKET_NAME = "central-supelec-data-groupe2"


def read_graph(bucket_name: str, key: str) -> dict[str, Any]:
    try:
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
        body = s3_object['Body']
        return json.loads(body.read())
    except Exception as e:
        logger.error(f"Failed to upload receipt to S3: {str(e)}")
        raise

def read_bind(bucket_name: str, key: str) -> Optional[dict[str, Any]]:
    try:
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
        body = s3_object['Body']
        return json.loads(body.read())
    except s3_client.exceptions.NoSuchKey:
        return None
    except Exception as e:
        logger.error(f"Failed to upload receipt to S3: {str(e)}")
        raise

def upload_json(bucket_name: str, key: str, schedule):
    """Helper function to upload schedule to S3"""
    try:
        s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=bytes(json.dumps(schedule).encode("utf-8"))
        )
    except Exception as e:
        logger.error(f"Failed to upload file to S3: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        num_cores = 3
        desc = "1000_7_seed_42"
        file_name = f"task_graph_{desc}"
        in_url = f"https://{BUCKET_NAME}.s3.eu-west-1.amazonaws.com/input_data/{file_name}.json"
        out_url = f"https://{BUCKET_NAME}.s3.eu-west-1.amazonaws.com/output_data/{file_name}_{num_cores}nodes-output.json"

        in_parsed_url = urlparse(in_url)
        out_parsed_url = urlparse(out_url)
        in_bucket_name = in_parsed_url.netloc.split(".")[0]
        in_file_path = in_parsed_url.path.lstrip("/")
        out_bucket_name = out_parsed_url.netloc.split(".")[0]
        out_file_path = out_parsed_url.path.lstrip("/")
        file_name = in_file_path.split(".")[0]
        bind_file_name = f"{file_name}_bind.json"

        processors = MappingProxyType({0: 4, 250: 10, 500: 7, 750: 3, 1000: 8})
        num_cores = max(processors.values())

        start = timer()
        dag = read_graph(in_bucket_name, in_file_path)
        G = build_graph(dag["tasks"])
        data = read_bind(in_bucket_name, bind_file_name)

        schedule, _, tasks_order, ub = modified_critical_path(G, processors, data)

        result = {f"core_{core}": [] for core in range(num_cores)}
        for task in schedule:
            result[f"core_{task.processor}"].append({"task": task.id, "start_time": task.start_time, "duration": task.duration})

        upload_json(out_bucket_name, out_file_path, result)
        upload_json(out_bucket_name, bind_file_name, {"order": tasks_order, "ub": ub})
        end = timer()

        logger.info(f"Required time: {end-start}s")
        logger.info("Schedule created")

        plot_schedule(result)

    except Exception as e:
        logger.error(f"Failed to create a schedule: {str(e)}")
        raise
