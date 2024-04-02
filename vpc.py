import pulumi
import pulumi_aws as aws
from pulumi_aws import ec2


#variables
ec2_vpc_name = 'vpc_pulumi'
ec2_igw_name = 'pulumi_igw'
ec2_public_subnet = 'pub_subnet_pulumi'
ec2_private_subnet = 'private_subnet_pulumi'
ec2_elastic_ip = 'eip_pulumi'
ec2_natgateway = 'natgw_pulumi'
ec2_public = 'public_route_table_pulumi'
ec2_private = 'private_route_table_pulumi'

vpc = aws.ec2.Vpc("ec2_vpc_name",
    cidr_block="10.0.0.0/16",

     tags={
        "Name": "ec2_vpc_name",
    }
)

igw = aws.ec2.InternetGateway("ec2_igw_name",
    vpc_id=vpc.id,
    tags={
        "Name": "ec2_igw_name",
    })

publicsubnet = aws.ec2.Subnet("ec2_public_subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.0.0/24",
    map_public_ip_on_launch=True,
    tags={
        "Name": "ec2_public_subnet",
    })

privatesubnet = aws.ec2.Subnet("ec2_private_subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=False,
    tags={
        "Name": "ec2_private_subnet",
    })

eip = aws.ec2.Eip("ec2_elastic_ip",
   vpc=True)

nat_gw = aws.ec2.NatGateway("ec2_natgateway",
    subnet_id=publicsubnet.id,
    allocation_id=eip.allocation_id
    )

pubroutetable = aws.ec2.RouteTable("ec2_public",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        )
    ],
    tags={
        "Name": "ec2_public",
    })

prvroutetable = aws.ec2.RouteTable("ec2_private",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            nat_gateway_id=nat_gw.id
        )
    ],
    tags={
        "Name": "ec2_private",
    })

pub_route_association = aws.ec2.RouteTableAssociation("public_route_association",
        route_table_id=pubroutetable.id,
        subnet_id=publicsubnet.id
)

sg = aws.ec2.SecurityGroup("pulumi_sg",
        description="Allow HTTP traffic to EC2 instance",
        ingress=[{
                "protocol": "tcp",
                "from_port": 80,
                "to_port": 80,
                "cidr_blocks": ["0.0.0.0/0"],
            },
        {
            "protocol": "tcp",
            "from_port": 443,
            "to_port": 443,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        }
        ],
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    vpc_id=vpc.id
)
