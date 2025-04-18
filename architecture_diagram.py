#!/usr/bin/env python3
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Fargate
from diagrams.aws.network import CloudFront, ALB, VPC, PrivateSubnet, PublicSubnet
from diagrams.aws.general import Users
from diagrams.aws.integration import SNS

# Set the output file name and format
output_file = "architecture_diagram"
output_format = "png"

# Create the diagram
with Diagram("Fargate PHP Hello World Architecture", 
             filename=output_file, 
             outformat=output_format,
             show=False):
    
    # External users
    users = Users("End Users")
    
    # CloudFront distribution
    cf = CloudFront("CloudFront")
    users >> cf
    
    # VPC with availability zones
    with Cluster("VPC"):
        # Create the ALB
        alb = ALB("Application\nLoad Balancer")
        
        # Connect CloudFront to ALB
        cf >> Edge(label="Custom Headers\nVerification") >> alb
        
        # Create two availability zones
        with Cluster("Availability Zone A"):
            with Cluster("Private Subnet"):
                fargate_a1 = Fargate("Fargate Task 1")
                fargate_a2 = Fargate("Fargate Task 2")
        
        with Cluster("Availability Zone B"):
            with Cluster("Private Subnet"):
                fargate_b1 = Fargate("Fargate Task 1")
                fargate_b2 = Fargate("Fargate Task 2")
        
        # Connect ALB to Fargate tasks
        alb >> fargate_a1
        alb >> fargate_a2
        alb >> fargate_b1
        alb >> fargate_b2
        
        # Add auto-scaling notification
        sns = SNS("Auto-scaling\nNotifications")
        fargate_a1 - Edge(style="dotted") - sns
        fargate_b1 - Edge(style="dotted") - sns

print(f"Architecture diagram generated: {output_file}.{output_format}")
