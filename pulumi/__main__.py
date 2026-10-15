import json

import pulumi
import pulumi_aws as aws

if pulumi.get_stack() == "prod":
    aws.route53.Zone("negoci-online", name="negoci.online")

# --- DynamoDB ---
table = aws.dynamodb.Table(
    "lanchonetes",
    attributes=[aws.dynamodb.TableAttributeArgs(name="id", type="S")],
    hash_key="id",
    billing_mode="PAY_PER_REQUEST",
)

lanchonetes_teste = [
    ("1", "Lanchonete Central", "Praça da Sé, São Paulo", -23.5505, -46.6333),
    ("2", "Hamburgueria Paulista", "Av. Paulista, 1000, São Paulo", -23.5614, -46.6559),
    (
        "3",
        "Pastelaria do Mercado",
        "R. da Cantareira, 306, São Paulo",
        -23.5413,
        -46.6295,
    ),
    ("4", "Lanches da Vila", "R. Harmonia, 100, São Paulo", -23.5551, -46.6914),
    (
        "5",
        "Dogão do Ibirapuera",
        "Av. Pedro Álvares Cabral, São Paulo",
        -23.5874,
        -46.6576,
    ),
    (
        "6",
        "Lanchonete Copacabana",
        "Av. Atlântica, 1500, Rio de Janeiro",
        -22.9711,
        -43.1822,
    ),
]

for id_, nome, endereco, lat, lon in lanchonetes_teste:
    aws.dynamodb.TableItem(
        f"lanchonete-{id_}",
        table_name=table.name,
        hash_key=table.hash_key,
        item=json.dumps(
            {
                "id": {"S": id_},
                "nome": {"S": nome},
                "endereco": {"S": endereco},
                "latitude": {"N": str(lat)},
                "longitude": {"N": str(lon)},
            }
        ),
    )

# --- Lambda ---
role = aws.iam.Role(
    "lanchonetes-proximas-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
)

aws.iam.RolePolicyAttachment(
    "lanchonetes-proximas-logs",
    role=role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
)

aws.iam.RolePolicy(
    "lanchonetes-proximas-dynamodb",
    role=role.id,
    policy=table.arn.apply(
        lambda arn: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {"Effect": "Allow", "Action": ["dynamodb:Scan"], "Resource": arn}
                ],
            }
        )
    ),
)

fn = aws.lambda_.Function(
    "lanchonetes-proximas",
    runtime=aws.lambda_.Runtime.PYTHON3D13,
    handler="handler.lambda_handler",
    role=role.arn,
    code=pulumi.FileArchive("./lanchonetes"),
    timeout=10,
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={"TABLE_NAME": table.name}
    ),
)

pulumi.export("table_name", table.name)
pulumi.export("function_name", fn.name)
