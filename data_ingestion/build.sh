#!/bin/bash

# Exit on error
set -e

# Configuration
AWS_REGION="us-east-2"  # Change this to your region
ECR_REPOSITORY="job-data-ingestion"
IMAGE_TAG="latest"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create ECR repository if it doesn't exist
#aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} || \
#    aws ecr create-repository --repository-name ${ECR_REPOSITORY}

# Authenticate Docker to ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build the Docker image
docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .

# Tag the image
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}

# Push the image to ECR
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}

echo "Image built and pushed successfully!" 