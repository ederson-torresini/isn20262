import json

import pulumi
import pulumi_aws as aws

if pulumi.get_stack() == "prod":
    aws.route53.Zone("negoci-online", name="negoci.online")

# --- DynamoDB (vazia) ---
table = aws.dynamodb.Table(
    "banheiros",
    attributes=[aws.dynamodb.TableAttributeArgs(name="id", type="S")],
    hash_key="id",
    billing_mode="PAY_PER_REQUEST",
)

# --- IAM ---
role = aws.iam.Role(
    "banheiros-role",
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
    "banheiros-logs",
    role=role.name,
    policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
)

aws.iam.RolePolicy(
    "banheiros-dynamodb",
    role=role.id,
    policy=table.arn.apply(
        lambda arn: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["dynamodb:Scan", "dynamodb:BatchWriteItem"],
                        "Resource": arn,
                    }
                ],
            }
        )
    ),
)


# --- Lambdas ---
def public_function(name, **kwargs):
    fn = aws.lambda_.Function(name, role=role.arn, timeout=10, **kwargs)
    url = aws.lambda_.FunctionUrl(
        f"{name}-url",
        function_name=fn.name,
        authorization_type="NONE",
        cors=aws.lambda_.FunctionUrlCorsArgs(
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["content-type"],
        ),
    )
    aws.lambda_.Permission(
        f"{name}-url-permission",
        function=fn.name,
        action="lambda:InvokeFunctionUrl",
        principal="*",
        function_url_auth_type="NONE",
    )
    aws.lambda_.Permission(
        f"{name}-invoke-permission",
        function=fn.name,
        action="lambda:InvokeFunction",
        principal="*",
        invoked_via_function_url=True,
    )
    return fn, url


table_env = aws.lambda_.FunctionEnvironmentArgs(variables={"TABLE_NAME": table.name})

get_fn, get_url = public_function(
    "banheiros-get",
    runtime=aws.lambda_.Runtime.PYTHON3D13,
    handler="handler.lambda_handler",
    code=pulumi.FileArchive("./banheiros_get"),
    environment=table_env,
)

post_fn, post_url = public_function(
    "banheiros-post",
    runtime=aws.lambda_.Runtime.PYTHON3D13,
    handler="handler.lambda_handler",
    code=pulumi.FileArchive("./banheiros_post"),
    environment=table_env,
)

web_fn, web_url = public_function(
    "banheiros-web",
    runtime=aws.lambda_.Runtime.NODE_JS22D_X,
    handler="index.handler",
    code=pulumi.FileArchive("./web"),
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            "API_GET_URL": get_url.function_url,
            "API_POST_URL": post_url.function_url,
        }
    ),
)

pulumi.export("table_name", table.name)
pulumi.export("get_url", get_url.function_url)
pulumi.export("post_url", post_url.function_url)
pulumi.export("web_url", web_url.function_url)
