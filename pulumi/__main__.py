"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import ec2
from pulumi_tls import PrivateKey

project = "isn20262"

# VPC
vpc = ec2.Vpc(
    f"{project}-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": f"{project}-vpc"},
)

# Internet Gateway
igw = ec2.InternetGateway(
    f"{project}-igw",
    vpc_id=vpc.id,
    tags={"Name": f"{project}-igw"},
)

# Public subnet
public_subnet = ec2.Subnet(
    f"{project}-public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="sa-east-1a",
    map_public_ip_on_launch=True,
    tags={"Name": f"{project}-public-subnet"},
)

# Route table with route to the internet, associated with the public subnet
public_route_table = ec2.RouteTable(
    f"{project}-public-rt",
    vpc_id=vpc.id,
    routes=[
        ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        ),
    ],
    tags={"Name": f"{project}-public-rt"},
)

ec2.RouteTableAssociation(
    f"{project}-public-rta",
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id,
)

# Security group allowing SSH and HTTP access
security_group = ec2.SecurityGroup(
    f"{project}-sg",
    vpc_id=vpc.id,
    description="Allow SSH and HTTP inbound traffic",
    ingress=[
        ec2.SecurityGroupIngressArgs(
            description="SSH",
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],
        ),
        ec2.SecurityGroupIngressArgs(
            description="HTTP",
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
        ),
        ec2.SecurityGroupIngressArgs(
            description="HTTPS",
            protocol="tcp",
            from_port=443,
            to_port=443,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    tags={"Name": f"{project}-sg"},
)

# SSH key pair for remote access to the instance
ssh_key = PrivateKey(
    f"{project}-ssh-key",
    algorithm="RSA",
    rsa_bits=4096,
)

key_pair = ec2.KeyPair(
    f"{project}-key-pair",
    public_key=ssh_key.public_key_openssh,
    tags={"Name": f"{project}-key-pair"},
)

# Latest Amazon Linux 2023 AMI (free tier eligible)
amazon_linux = ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[
        ec2.GetAmiFilterArgs(
            name="name",
            values=["al2023-ami-*-x86_64"],
        ),
        ec2.GetAmiFilterArgs(
            name="virtualization-type",
            values=["hvm"],
        ),
    ],
)

# EC2 instance - t3.micro is the free tier eligible size
instance = ec2.Instance(
    f"{project}-instance",
    instance_type="t3.micro",
    ami=amazon_linux.id,
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[security_group.id],
    associate_public_ip_address=True,
    key_name=key_pair.key_name,
    tags={"Name": f"{project}-instance"},
)

pulumi.export("vpc_id", vpc.id)
pulumi.export("public_subnet_id", public_subnet.id)
pulumi.export("security_group_id", security_group.id)
pulumi.export("instance_id", instance.id)
pulumi.export("instance_public_ip", instance.public_ip)
pulumi.export("key_pair_name", key_pair.key_name)
pulumi.export("ssh_private_key", pulumi.Output.secret(ssh_key.private_key_pem))
