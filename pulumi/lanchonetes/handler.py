import json
import math
import os

import boto3

# DYNAMODB_ENDPOINT só é definido em testes locais (SAM + DynamoDB Local).
table = boto3.resource(
    "dynamodb", endpoint_url=os.environ.get("DYNAMODB_ENDPOINT")
).Table(os.environ["TABLE_NAME"])

DEFAULT_LIMIT = 5


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, ensure_ascii=False),
    }


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
    # Aceita evento direto ou via Function URL / API Gateway (body em string).
    payload = event
    if isinstance(event.get("body"), str):
        try:
            payload = json.loads(event["body"])
        except json.JSONDecodeError:
            return response(400, {"erro": "JSON inválido"})

    try:
        lat = float(payload["latitude"])
        lon = float(payload["longitude"])
        limit = int(payload.get("limite", DEFAULT_LIMIT))
    except (KeyError, TypeError, ValueError):
        return response(400, {"erro": "Informe 'latitude' e 'longitude' numéricas"})

    if not (-90 <= lat <= 90 and -180 <= lon <= 180) or limit < 1:
        return response(400, {"erro": "Parâmetros fora do intervalo válido"})

    resultado = []
    for item in scan_all():
        dist = haversine_km(lat, lon, float(item["latitude"]), float(item["longitude"]))
        resultado.append(
            {
                "id": item["id"],
                "nome": item["nome"],
                "endereco": item.get("endereco"),
                "latitude": float(item["latitude"]),
                "longitude": float(item["longitude"]),
                "distancia_km": round(dist, 3),
            }
        )

    resultado.sort(key=lambda x: x["distancia_km"])
    return response(200, {"lanchonetes": resultado[:limit]})
