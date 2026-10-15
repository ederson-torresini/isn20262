import boto3

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000",
    region_name="us-east-1",
    aws_access_key_id="local",
    aws_secret_access_key="local",
)

# Mantém os mesmos dados de teste de 3-pulumi/__main__.py.
LANCHONETES = [
    ("1", "Lanchonete Central", "Praça da Sé, São Paulo", "-23.5505", "-46.6333"),
    (
        "2",
        "Hamburgueria Paulista",
        "Av. Paulista, 1000, São Paulo",
        "-23.5614",
        "-46.6559",
    ),
    (
        "3",
        "Pastelaria do Mercado",
        "R. da Cantareira, 306, São Paulo",
        "-23.5413",
        "-46.6295",
    ),
    ("4", "Lanches da Vila", "R. Harmonia, 100, São Paulo", "-23.5551", "-46.6914"),
    (
        "5",
        "Dogão do Ibirapuera",
        "Av. Pedro Álvares Cabral, São Paulo",
        "-23.5874",
        "-46.6576",
    ),
    (
        "6",
        "Lanchonete Copacabana",
        "Av. Atlântica, 1500, Rio de Janeiro",
        "-22.9711",
        "-43.1822",
    ),
]

try:
    dynamodb.create_table(
        TableName="lanchonetes",
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    ).wait_until_exists()
except dynamodb.meta.client.exceptions.ResourceInUseException:
    pass

table = dynamodb.Table("lanchonetes")
from decimal import Decimal

for id_, nome, endereco, lat, lon in LANCHONETES:
    table.put_item(
        Item={
            "id": id_,
            "nome": nome,
            "endereco": endereco,
            "latitude": Decimal(lat),
            "longitude": Decimal(lon),
        }
    )
print(f"{len(LANCHONETES)} lanchonetes inseridas")
