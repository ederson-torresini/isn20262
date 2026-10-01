import pulumi
import pulumi_aws as aws

if pulumi.get_stack() == "prod":
    aws.route53.Zone("negoci-online", name="negoci.online")
