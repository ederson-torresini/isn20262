import json
import subprocess
from pathlib import Path

import pulumi
import pulumi_aws as aws

DOMAIN = "negoci.online"
is_prod = pulumi.get_stack() == "prod"

if is_prod:
    zone = aws.route53.Zone("negoci-online", name=DOMAIN)

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

# --- S3 Bucket for static website ---
web_bucket = aws.s3.Bucket(
    "banheiros-web",
    tags={"Name": "banheiros-web"},
    acl="private",
)

# Origin Access Identity for CloudFront to access private S3 bucket
oai = aws.cloudfront.OriginAccessIdentity(
    "banheiros-oai",
    comment="OAI for banheiros-web S3 bucket",
)

# Bucket Policy to allow CloudFront to read objects
bucket_policy = aws.s3.BucketPolicy(
    "banheiros-web-policy",
    bucket=web_bucket.id,
    policy=pulumi.Output.concat(
        '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":"',
        oai.iam_arn,
        '"},"Action":"s3:GetObject","Resource":"',
        web_bucket.arn,
        '/*"}]}',
    ),
)

# Build React app
web_dir = Path(__file__).parent / "web-react"
subprocess.run(["npm", "ci"], cwd=web_dir, check=True)
subprocess.run(["npm", "run", "build"], cwd=web_dir, check=True)

# Upload React app files to S3
dist_dir = web_dir / "dist"
for file_path in dist_dir.rglob("*"):
    if file_path.is_file():
        relative_path = file_path.relative_to(dist_dir)
        mime_type = "text/html"
        if file_path.suffix == ".js":
            mime_type = "application/javascript"
        elif file_path.suffix == ".css":
            mime_type = "text/css"
        elif file_path.suffix == ".svg":
            mime_type = "image/svg+xml"
        elif file_path.suffix == ".png":
            mime_type = "image/png"
        elif file_path.suffix == ".jpg" or file_path.suffix == ".jpeg":
            mime_type = "image/jpeg"

        aws.s3.BucketObject(
            f"web-{relative_path.as_posix().replace('/', '-').replace('.', '_')}",
            bucket=web_bucket.id,
            key=relative_path.as_posix(),
            source=pulumi.FileAsset(str(file_path)),
            content_type=mime_type,
            cache_control="max-age=3600" if relative_path.name != "index.html" else "max-age=0, no-cache",
        )

# --- API Gateway (HTTP API) ---
api = aws.apigatewayv2.Api("banheiros-api", protocol_type="HTTP")

aws.apigatewayv2.Stage(
    "banheiros-stage", api_id=api.id, name="$default", auto_deploy=True
)


# --- Lambdas ---
def public_function(name, method, path, **kwargs):
    fn = aws.lambda_.Function(name, role=role.arn, timeout=10, **kwargs)
    integration = aws.apigatewayv2.Integration(
        f"{name}-integration",
        api_id=api.id,
        integration_type="AWS_PROXY",
        integration_method="POST",
        integration_uri=fn.invoke_arn,
        payload_format_version="2.0",
    )
    aws.apigatewayv2.Route(
        f"{name}-route",
        api_id=api.id,
        route_key=f"{method} {path}",
        target=integration.id.apply(lambda i: f"integrations/{i}"),
    )
    aws.lambda_.Permission(
        f"{name}-apigw-permission",
        function=fn.name,
        action="lambda:InvokeFunction",
        principal="apigateway.amazonaws.com",
        source_arn=api.execution_arn.apply(lambda a: f"{a}/*/*"),
    )
    return fn


table_env = aws.lambda_.FunctionEnvironmentArgs(variables={"TABLE_NAME": table.name})

get_fn = public_function(
    "banheiros-get",
    "GET",
    "/banheiros",
    runtime=aws.lambda_.Runtime.NODE_JS22D_X,
    handler="index.handler",
    code=pulumi.FileArchive("./banheiros_get"),
    environment=table_env,
)

post_fn = public_function(
    "banheiros-post",
    "POST",
    "/banheiros",
    runtime=aws.lambda_.Runtime.NODE_JS22D_X,
    handler="index.handler",
    code=pulumi.FileArchive("./banheiros_post"),
    environment=table_env,
)

# --- CloudFront (+ ACM e Route53 em prod) ---
aliases = []
viewer_cert = aws.cloudfront.DistributionViewerCertificateArgs(
    cloudfront_default_certificate=True
)

if is_prod:
    us_east_1 = aws.Provider("us-east-1", region="us-east-1")

    cert = aws.acm.Certificate(
        "cert",
        domain_name=DOMAIN,
        validation_method="DNS",
        opts=pulumi.ResourceOptions(provider=us_east_1),
    )

    validation_record = aws.route53.Record(
        "cert-validation",
        name=cert.domain_validation_options[0].resource_record_name,
        zone_id=zone.zone_id,
        type=cert.domain_validation_options[0].resource_record_type,
        records=[cert.domain_validation_options[0].resource_record_value],
        ttl=60,
    )

    cert_validation = aws.acm.CertificateValidation(
        "cert-val",
        certificate_arn=cert.arn,
        validation_record_fqdns=[validation_record.fqdn],
        opts=pulumi.ResourceOptions(provider=us_east_1),
    )

    aliases = [DOMAIN]
    viewer_cert = aws.cloudfront.DistributionViewerCertificateArgs(
        acm_certificate_arn=cert_validation.certificate_arn,
        ssl_support_method="sni-only",
        minimum_protocol_version="TLSv1.2_2021",
    )

caching_disabled = aws.cloudfront.get_cache_policy(name="Managed-CachingDisabled")
caching_optimized = aws.cloudfront.get_cache_policy(name="Managed-CachingOptimized")
all_viewer_except_host = aws.cloudfront.get_origin_request_policy(
    name="Managed-AllViewerExceptHostHeader"
)

api_hostname = api.api_endpoint.apply(lambda e: e.replace("https://", "").split("/")[0])
s3_domain = web_bucket.bucket_regional_domain_name

distribution = aws.cloudfront.Distribution(
    "banheiros-cdn",
    enabled=True,
    is_ipv6_enabled=True,
    http_version="http2and3",
    aliases=aliases,
    default_root_object="index.html",
    origins=[
        aws.cloudfront.DistributionOriginArgs(
            domain_name=api_hostname,
            origin_id="api",
            custom_origin_config=aws.cloudfront.DistributionOriginCustomOriginConfigArgs(
                http_port=80,
                https_port=443,
                origin_protocol_policy="https-only",
                origin_ssl_protocols=["TLSv1.2"],
            ),
        ),
        aws.cloudfront.DistributionOriginArgs(
            domain_name=s3_domain,
            origin_id="s3",
            s3_origin_config=aws.cloudfront.DistributionOriginS3OriginConfigArgs(
                origin_access_identity=oai.cloudfront_access_identity_path,
            ),
        ),
    ],
    default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
        target_origin_id="s3",
        viewer_protocol_policy="redirect-to-https",
        allowed_methods=["GET", "HEAD"],
        cached_methods=["GET", "HEAD"],
        cache_policy_id=caching_optimized.id,
    ),
    ordered_cache_behaviors=[
        aws.cloudfront.DistributionOrderedCacheBehaviorArgs(
            path_pattern="/banheiros*",
            target_origin_id="api",
            viewer_protocol_policy="redirect-to-https",
            allowed_methods=["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"],
            cached_methods=["GET", "HEAD"],
            cache_policy_id=caching_disabled.id,
            origin_request_policy_id=all_viewer_except_host.id,
        ),
    ],
    viewer_certificate=viewer_cert,
    restrictions=aws.cloudfront.DistributionRestrictionsArgs(
        geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
            restriction_type="none"
        )
    ),
)

if is_prod:
    for rtype in ["A", "AAAA"]:
        aws.route53.Record(
            f"alias-{rtype}",
            zone_id=zone.zone_id,
            name=DOMAIN,
            type=rtype,
            aliases=[
                aws.route53.RecordAliasArgs(
                    name=distribution.domain_name,
                    zone_id=distribution.hosted_zone_id,
                    evaluate_target_health=False,
                )
            ],
        )

pulumi.export("table_name", table.name)
pulumi.export("api_url", api.api_endpoint)
pulumi.export("s3_bucket", web_bucket.id)
pulumi.export(
    "url",
    (
        f"https://{DOMAIN}"
        if is_prod
        else distribution.domain_name.apply(lambda d: f"https://{d}")
    ),
)
