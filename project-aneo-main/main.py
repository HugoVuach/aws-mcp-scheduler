import json
import logging
from typing import Any, Optional
from urllib.parse import urlparse

import boto3

from graph import build_graph
from schedule import modified_critical_path

# Initialize the S3 client outside of the handler
s3_client = boto3.client('s3')

# Initialize the logger
logger = logging.getLogger()
logger.setLevel("INFO")


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
        logger.error(f"Failed to upload receipt to S3: {str(e)}")
        raise


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Main Lambda handler function
    Parameters:
        event: Dict containing the Lambda function event data
        context: Lambda runtime context
    Returns:
        Dict containing status message
    """
    try:
        in_url = event["graph"]
        num_cores = event["nodes"]
        out_url = event["output"]

        in_parsed_url = urlparse(in_url)
        out_parsed_url = urlparse(out_url)
        in_bucket_name = in_parsed_url.netloc.split(".")[0]
        in_file_path = in_parsed_url.path.lstrip("/")
        out_bucket_name = out_parsed_url.netloc.split(".")[0]
        out_file_path = out_parsed_url.path.lstrip("/")
        file_name = in_file_path.split(".")[0]
        bind_file_name = f"{file_name}_bind.json"

        dag = read_graph(in_bucket_name, in_file_path)
        G = build_graph(dag["tasks"])
        data = read_bind(in_bucket_name, bind_file_name)

        schedule, _, tasks_order, ub = modified_critical_path(G, num_cores, data)

        result = {f"core_{core}": [] for core in range(num_cores)}
        for task in schedule:
            result[f"core_{task.processor}"].append({"task": task.id, "start_time": task.start_time, "duration": task.duration})

        upload_json(out_bucket_name, out_file_path, result)
        upload_json(out_bucket_name, bind_file_name, {"order": tasks_order, "ub": ub})

        logger.info("Schedule created")
        return {
            "statusCode": 200,
            "message": "Schedule created"
        }

    except Exception as e:
        logger.error(f"Failed to create a schedule: {str(e)}")
        raise
