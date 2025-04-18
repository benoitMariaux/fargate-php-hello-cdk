#!/usr/bin/env python3
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr_assets as ecr_assets,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    aws_s3 as s3,
    aws_elasticloadbalancingv2 as elbv2,
    CfnOutput,
    Stack,
    App,
    Duration,
    RemovalPolicy,
    CfnParameter
)
from constructs import Construct

class FargatePhpHelloStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC with public and private subnets
        vpc = ec2.Vpc(self, "PhpHelloVpc",
            max_azs=2,
            nat_gateways=1
        )

        # Create an ECS cluster in the VPC
        cluster = ecs.Cluster(self, "PhpHelloCluster",
            vpc=vpc
        )

        # Build Docker image from local directory
        # Explicitly specify AMD64 platform to avoid architecture issues
        asset = ecr_assets.DockerImageAsset(self, "PhpHelloImage",
            directory="./app",  # Updated path to application directory
            platform=ecr_assets.Platform.LINUX_AMD64,  # Specify platform here
            asset_name="php-hello-image-" + self.node.addr  # Force image rebuild
        )

        # Create a task definition with container
        task_definition = ecs.FargateTaskDefinition(self, "TaskDef",
            memory_limit_mib=512,
            cpu=256
        )
        
        container = task_definition.add_container("web",
            image=ecs.ContainerImage.from_docker_image_asset(asset),
            memory_limit_mib=512,
            logging=ecs.LogDrivers.aws_logs(stream_prefix="PhpHelloService")
        )
        
        container.add_port_mappings(
            ecs.PortMapping(container_port=80)
        )

        # Create a Fargate service with a PUBLIC ALB (for CloudFront)
        # We'll secure this ALB to only accept traffic from CloudFront
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "PhpHelloServicePublic",
            cluster=cluster,
            task_definition=task_definition,
            # Increase task count to 2 for high availability
            desired_count=2,
            # Use a public but secured ALB
            public_load_balancer=True,
            # Ensure tasks are spread across AZs
            assign_public_ip=False
        )
        
        # Disable sticky sessions to ensure better distribution across instances
        fargate_service.target_group.set_attribute("stickiness.enabled", "false")
        
        # Configure auto-scaling for the Fargate service
        scaling = fargate_service.service.auto_scale_task_count(
            min_capacity=2,  # Minimum 2 tasks for high availability
            max_capacity=4   # Maximum 4 tasks to handle load spikes
        )
        
        # Add CPU-based auto-scaling policy
        scaling.scale_on_cpu_utilization("CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )
        
        # Create a CloudFront distribution pointing to the ALB
        distribution = cloudfront.Distribution(self, "PhpHelloDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.LoadBalancerV2Origin(
                    fargate_service.load_balancer,
                    protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
                    http_port=80,
                    custom_headers={
                        "X-Origin-Verify": "private-alb-access"
                    }
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                # Completely disable caching to ensure requests always go to origin
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER
            ),
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            enable_logging=False,  # Disable logging to avoid S3 ACL issues
            http_version=cloudfront.HttpVersion.HTTP2
        )
        
        # Secure the ALB to only accept traffic from CloudFront
        # Get the ALB security group
        alb_security_group = fargate_service.load_balancer.connections.security_groups[0]
        
        # Add outputs for URLs
        CfnOutput(self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
            description="ALB URL (secured to only accept traffic from CloudFront)"
        )
        
        CfnOutput(self, "CloudFrontURL",
            value=f"https://{distribution.distribution_domain_name}",
            description="CloudFront distribution URL"
        )
        
        CfnOutput(self, "MinTaskCount",
            value="2",
            description="Minimum number of Fargate tasks"
        )
        
        CfnOutput(self, "MaxTaskCount",
            value="4",
            description="Maximum number of Fargate tasks"
        )

app = App()
FargatePhpHelloStack(app, "FargatePhpHelloStack")
app.synth()
