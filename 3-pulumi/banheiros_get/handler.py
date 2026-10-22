import json
import os
from decimal import Decimal

import boto3

# DYNAMODB_ENDPOINT só é definido em testes locais (DynamoDB Local).
table = boto3.resource(
    "dynamodb", endpoint_url=os.environ.get("DYNAMODB_ENDPOINT") or None
).Table(os.environ["TABLE_NAME"])

HEADERS = {"Content-Type": "application/json"}


def default(o):
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError(type(o))


def scan_all():
    items = []
    kwargs = {}
    while True:
        page = table.scan(**kwargs)
        items.extend(page["Items"])
        if "LastEvaluatedKey" not in page:
            return items
        kwargs["ExclusiveStartKey"] = page["LastEvaluatedKey"]


def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps(scan_all(), default=default, ensure_ascii=False),
    }
