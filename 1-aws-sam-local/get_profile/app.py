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

    profile_id = (event.get("queryStringParameters") or {}).get("id")
    if not profile_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "id query parameter is required"}),
        }

    item = ddb.get_item(
        TableName="ProfilesTable",
        Key={"id": {"S": profile_id}},
    ).get("Item")

    if not item:
        return {"statusCode": 404, "body": json.dumps({"message": "Not found"})}

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"id": item["id"]["S"], "name": item["name"]["S"]}),
    }
