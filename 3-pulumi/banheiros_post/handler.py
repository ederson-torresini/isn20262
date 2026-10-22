import base64
import json
import os
import uuid
from decimal import Decimal

import boto3

# DYNAMODB_ENDPOINT só é definido em testes locais (DynamoDB Local).
table = boto3.resource(
    "dynamodb", endpoint_url=os.environ.get("DYNAMODB_ENDPOINT") or None
).Table(os.environ["TABLE_NAME"])

HEADERS = {"Content-Type": "application/json"}
BOOL_FIELDS = ("masculino", "feminino", "infantil", "fraldario")


def response(status, body):
    return {
        "statusCode": status,
        "headers": HEADERS,
        "body": json.dumps(body, ensure_ascii=False),
    }


def parse(item):
    """Valida um banheiro e devolve (item, None) ou (None, erro)."""
    if not isinstance(item, dict):
        return None, "cada banheiro deve ser um objeto JSON"
    try:
        lat, lon = float(item["latitude"]), float(item["longitude"])
    except (KeyError, TypeError, ValueError):
        return None, "latitude e longitude numéricas são obrigatórias"
    if isinstance(item["latitude"], bool) or isinstance(item["longitude"], bool):
        return None, "latitude e longitude devem ser números"
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None, "latitude/longitude fora do intervalo"
    out = {
        "id": str(uuid.uuid4()),
        "latitude": Decimal(str(lat)),
        "longitude": Decimal(str(lon)),
    }
    for field in BOOL_FIELDS:
        value = item.get(field, False)
        if not isinstance(value, bool):
            return None, f"{field} deve ser booleano"
        out[field] = value
    return out, None


def lambda_handler(event, context):
    body = event.get("body") or ""
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode()
    try:
        payload = json.loads(body)
    except ValueError:
        return response(400, {"erro": "JSON inválido"})

    # Aceita um banheiro ou uma lista deles.
    entries = payload if isinstance(payload, list) else [payload]
    if not entries:
        return response(400, {"erro": "nenhum banheiro informado"})

    parsed = []
    for entry in entries:
        item, erro = parse(entry)
        if erro:
            return response(400, {"erro": erro})
        parsed.append(item)

    with table.batch_writer() as batch:
        for item in parsed:
            batch.put_item(Item=item)

    ids = [i["id"] for i in parsed]
    return response(201, {"ids": ids})
