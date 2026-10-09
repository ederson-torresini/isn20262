import json
import os
import boto3


def handler(event, context):
    ddb = boto3.client(
        "dynamodb",
        region_name="sa-east-1",
        endpoint_url=os.environ["DYNAMODB_ENDPOINT"],
        aws_access_key_id="local",
        aws_secret_access_key="local",
    )

    try:
        body = json.loads(event.get("body") or "")
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": json.dumps({"message": "Invalid JSON"})}

    if not isinstance(body, dict) or not body.get("id") or not body.get("name"):
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "id and name are required"}),
        }

    ddb.put_item(
        TableName="ProfilesTable",
        Item={
            "id": {"S": str(body["id"])},
            "name": {"S": str(body["name"])},
        },
    )

    return {
        "statusCode": 201,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"id": body["id"], "name": body["name"]}),
    }
