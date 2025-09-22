# Cloud Platform Deployment Guide

This guide covers deploying GM Services to major cloud platforms including AWS, Google Cloud Platform, Microsoft Azure, and DigitalOcean.

## AWS Deployment

### AWS ECS with Fargate

#### Prerequisites

- AWS CLI configured
- ECS CLI installed
- Docker images pushed to ECR

#### Setup ECR Repository

```bash
# Create ECR repository
aws ecr create-repository --repository-name gm-services

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build and push image
docker build -t gm-services .
docker tag gm-services:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/gm-services:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/gm-services:latest
```

#### ECS Task Definition

Create `ecs-task-definition.json`:

```json
{
  "family": "gm-services",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "gm-services-app",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/gm-services:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        },
        {
          "name": "DATABASE_URL",
          "value": "postgresql://username:password@gm-services-db.cluster-xyz.us-east-1.rds.amazonaws.com:5432/gmservices"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:gm-services/secret-key"
        },
        {
          "name": "STRIPE_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:gm-services/stripe-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/gm-services",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### ECS Service

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name gm-services-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster gm-services-cluster \
  --service-name gm-services-service \
  --task-definition gm-services:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-abcdef],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/gm-services-tg/1234567890123456,containerName=gm-services-app,containerPort=5000
```

#### Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name gm-services-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-abcdef

# Create target group
aws elbv2 create-target-group \
  --name gm-services-tg \
  --protocol HTTP \
  --port 5000 \
  --vpc-id vpc-12345 \
  --target-type ip \
  --health-check-path /health

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/gm-services-alb/1234567890123456 \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/gm-services-tg/1234567890123456
```

### AWS RDS Setup

```bash
# Create RDS subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name gm-services-subnet-group \
  --db-subnet-group-description "Subnet group for GM Services" \
  --subnet-ids subnet-12345 subnet-67890

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier gm-services-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.3 \
  --master-username gmservices \
  --master-user-password YourSecurePassword123! \
  --allocated-storage 100 \
  --storage-type gp2 \
  --storage-encrypted \
  --db-subnet-group-name gm-services-subnet-group \
  --vpc-security-group-ids sg-database \
  --backup-retention-period 7 \
  --multi-az \
  --monitoring-interval 60 \
  --monitoring-role-arn arn:aws:iam::123456789012:role/rds-monitoring-role
```

### CloudFormation Template

Create `cloudformation-stack.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'GM Services Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]
  
  DatabasePassword:
    Type: String
    NoEcho: true
    Description: RDS master password

Resources:
  # VPC and Networking
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-gm-services-vpc'

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.2.0/24
      MapPublicIpOnLaunch: true

  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.3.0/24

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.4.0/24

  # RDS Database
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for GM Services database
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub '${Environment}-gm-services-db'
      DBInstanceClass: db.t3.medium
      Engine: postgres
      EngineVersion: '15.3'
      MasterUsername: gmservices
      MasterUserPassword: !Ref DatabasePassword
      AllocatedStorage: 100
      StorageType: gp2
      StorageEncrypted: true
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      BackupRetentionPeriod: 7
      MultiAZ: true
      DeletionProtection: true

  # ElastiCache Redis
  RedisSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: Subnet group for Redis
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

  RedisCluster:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupId: !Sub '${Environment}-gm-services-redis'
      ReplicationGroupDescription: Redis cluster for GM Services
      NodeType: cache.t3.micro
      Engine: redis
      NumCacheClusters: 2
      CacheSubnetGroupName: !Ref RedisSubnetGroup
      SecurityGroupIds:
        - !Ref RedisSecurityGroup

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub '${Environment}-gm-services'
      CapacityProviders:
        - FARGATE
        - FARGATE_SPOT

  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub '${Environment}-gm-services-alb'
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      SecurityGroups:
        - !Ref ALBSecurityGroup

Outputs:
  DatabaseEndpoint:
    Description: RDS endpoint
    Value: !GetAtt Database.Endpoint.Address
    Export:
      Name: !Sub '${Environment}-database-endpoint'

  LoadBalancerDNS:
    Description: Load balancer DNS name
    Value: !GetAtt ApplicationLoadBalancer.DNSName
    Export:
      Name: !Sub '${Environment}-alb-dns'
```

## Google Cloud Platform (GCP)

### GKE Deployment

#### Prerequisites

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize gcloud
gcloud init

# Install kubectl
gcloud components install kubectl

# Enable APIs
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

#### Create GKE Cluster

```bash
# Create cluster
gcloud container clusters create gm-services-cluster \
  --zone us-central1-a \
  --node-pool-name default-pool \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --disk-type pd-standard \
  --disk-size 50GB \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 10

# Get credentials
gcloud container clusters get-credentials gm-services-cluster --zone us-central1-a
```

#### Kubernetes Manifests

Create `k8s/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: gm-services
```

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gm-services-app
  namespace: gm-services
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gm-services-app
  template:
    metadata:
      labels:
        app: gm-services-app
    spec:
      containers:
      - name: app
        image: gcr.io/your-project/gm-services:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: gm-services-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: gm-services-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

Create `k8s/service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: gm-services-service
  namespace: gm-services
spec:
  selector:
    app: gm-services-app
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

#### Deploy to GKE

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/your-project/gm-services .

# Create secrets
kubectl create secret generic gm-services-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=secret-key="your-secret-key" \
  --namespace=gm-services

# Deploy application
kubectl apply -f k8s/
```

### Cloud SQL Setup

```bash
# Create Cloud SQL instance
gcloud sql instances create gm-services-db \
  --database-version=POSTGRES_15 \
  --tier=db-n1-standard-2 \
  --region=us-central1 \
  --storage-type=SSD \
  --storage-size=100GB \
  --storage-auto-increase \
  --backup-start-time=03:00 \
  --enable-bin-log \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=4

# Create database
gcloud sql databases create gmservices --instance=gm-services-db

# Create user
gcloud sql users create gmservices \
  --instance=gm-services-db \
  --password=SecurePassword123!
```

## Microsoft Azure

### Azure Container Instances (ACI)

#### Prerequisites

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create resource group
az group create --name gm-services-rg --location eastus
```

#### Azure Container Registry

```bash
# Create ACR
az acr create --resource-group gm-services-rg \
  --name gmservicesacr \
  --sku Basic \
  --admin-enabled true

# Login to ACR
az acr login --name gmservicesacr

# Build and push image
docker build -t gmservicesacr.azurecr.io/gm-services:latest .
docker push gmservicesacr.azurecr.io/gm-services:latest
```

#### Container Instance

Create `azure-container-instance.yaml`:

```yaml
apiVersion: 2019-12-01
location: eastus
name: gm-services-aci
properties:
  containers:
  - name: gm-services-app
    properties:
      image: gmservicesacr.azurecr.io/gm-services:latest
      ports:
      - port: 5000
        protocol: TCP
      environmentVariables:
      - name: FLASK_ENV
        value: production
      - name: DATABASE_URL
        secureValue: postgresql://username:password@server:5432/database
      resources:
        requests:
          cpu: 1
          memoryInGb: 2
  imageRegistryCredentials:
  - server: gmservicesacr.azurecr.io
    username: gmservicesacr
    password: <ACR_PASSWORD>
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 5000
    dnsNameLabel: gm-services
  osType: Linux
  restartPolicy: Always
type: Microsoft.ContainerInstance/containerGroups
```

Deploy:

```bash
az container create --resource-group gm-services-rg \
  --file azure-container-instance.yaml
```

### Azure Database for PostgreSQL

```bash
# Create PostgreSQL server
az postgres server create \
  --resource-group gm-services-rg \
  --name gm-services-db-server \
  --location eastus \
  --admin-user gmservices \
  --admin-password SecurePassword123! \
  --sku-name GP_Gen5_2 \
  --storage-size 102400 \
  --version 15

# Create database
az postgres db create \
  --resource-group gm-services-rg \
  --server-name gm-services-db-server \
  --name gmservices

# Configure firewall
az postgres server firewall-rule create \
  --resource-group gm-services-rg \
  --server gm-services-db-server \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

## DigitalOcean

### DigitalOcean Kubernetes (DOKS)

#### Prerequisites

```bash
# Install doctl
snap install doctl

# Authenticate
doctl auth init

# Install kubectl
snap install kubectl --classic
```

#### Create Kubernetes Cluster

```bash
# Create cluster
doctl kubernetes cluster create gm-services-cluster \
  --region nyc1 \
  --version 1.28.2-do.0 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3;auto-scale=true;min-nodes=1;max-nodes=5"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save gm-services-cluster
```

#### DigitalOcean Container Registry

```bash
# Create registry
doctl registry create gm-services-registry

# Login to registry
doctl registry login

# Build and push
docker build -t registry.digitalocean.com/gm-services-registry/gm-services:latest .
docker push registry.digitalocean.com/gm-services-registry/gm-services:latest
```

#### Kubernetes Deployment

Create `do-k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gm-services
  labels:
    app: gm-services
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gm-services
  template:
    metadata:
      labels:
        app: gm-services
    spec:
      containers:
      - name: gm-services
        image: registry.digitalocean.com/gm-services-registry/gm-services:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: gm-services-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: gm-services-service
spec:
  selector:
    app: gm-services
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
  annotations:
    service.beta.kubernetes.io/do-loadbalancer-name: "gm-services-lb"
    service.beta.kubernetes.io/do-loadbalancer-protocol: "http"
    service.beta.kubernetes.io/do-loadbalancer-healthcheck-path: "/health"
```

Deploy:

```bash
kubectl apply -f do-k8s/deployment.yaml
```

### DigitalOcean Managed Database

```bash
# Create PostgreSQL cluster
doctl databases create gm-services-db \
  --engine postgres \
  --region nyc1 \
  --size db-s-2vcpu-4gb \
  --num-nodes 1 \
  --version 15

# Get connection details
doctl databases connection gm-services-db

# Create database user
doctl databases user create gm-services-db gmservices

# Create database
doctl databases db create gm-services-db gmservices
```

## Monitoring and Logging

### AWS CloudWatch

```yaml
# CloudWatch log group
LogGroup:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: /ecs/gm-services
    RetentionInDays: 30

# CloudWatch dashboard
Dashboard:
  Type: AWS::CloudWatch::Dashboard
  Properties:
    DashboardName: GM-Services-Dashboard
    DashboardBody: !Sub |
      {
        "widgets": [
          {
            "type": "metric",
            "properties": {
              "metrics": [
                ["AWS/ECS", "CPUUtilization", "ServiceName", "gm-services-service"],
                [".", "MemoryUtilization", ".", "."]
              ],
              "period": 300,
              "stat": "Average",
              "region": "${AWS::Region}",
              "title": "ECS Metrics"
            }
          }
        ]
      }
```

### GCP Monitoring

```bash
# Create uptime check
gcloud alpha monitoring uptime create-http \
  --display-name="GM Services Health Check" \
  --hostname="your-domain.com" \
  --path="/health"

# Set up alerting
gcloud alpha monitoring policies create \
  --policy-from-file=monitoring-policy.yaml
```

### Azure Monitor

```bash
# Create Log Analytics workspace
az monitor log-analytics workspace create \
  --resource-group gm-services-rg \
  --workspace-name gm-services-logs

# Create Application Insights
az extension add --name application-insights
az monitor app-insights component create \
  --app gm-services-insights \
  --location eastus \
  --resource-group gm-services-rg
```

## Security Best Practices

### Network Security

```yaml
# AWS Security Groups
AppSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupDescription: Security group for GM Services application
    VpcId: !Ref VPC
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 5000
        ToPort: 5000
        SourceSecurityGroupId: !Ref ALBSecurityGroup
    SecurityGroupEgress:
      - IpProtocol: tcp
        FromPort: 443
        ToPort: 443
        CidrIp: 0.0.0.0/0

DatabaseSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    GroupDescription: Security group for database
    VpcId: !Ref VPC
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 5432
        ToPort: 5432
        SourceSecurityGroupId: !Ref AppSecurityGroup
```

### Secrets Management

```bash
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name "gm-services/database-credentials" \
  --description "Database credentials for GM Services" \
  --secret-string '{"username":"gmservices","password":"SecurePassword123!"}'

# GCP Secret Manager
gcloud secrets create database-credentials \
  --data-file=credentials.json

# Azure Key Vault
az keyvault create \
  --name gm-services-vault \
  --resource-group gm-services-rg \
  --location eastus

az keyvault secret set \
  --vault-name gm-services-vault \
  --name database-password \
  --value SecurePassword123!
```

## CI/CD Integration

### GitHub Actions for Multi-Cloud

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Platforms

on:
  push:
    branches: [main]

env:
  IMAGE_NAME: gm-services

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      id: build
      run: |
        docker build -t $IMAGE_NAME:$GITHUB_SHA .
        echo "digest=$(docker images --digests $IMAGE_NAME:$GITHUB_SHA --format "{{.Digest}}")" >> $GITHUB_OUTPUT

  deploy-aws:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Push to ECR and deploy to ECS
      run: |
        aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
        docker tag $IMAGE_NAME:$GITHUB_SHA $ECR_REGISTRY/$IMAGE_NAME:$GITHUB_SHA
        docker push $ECR_REGISTRY/$IMAGE_NAME:$GITHUB_SHA
        aws ecs update-service --cluster gm-services-cluster --service gm-services-service --force-new-deployment

  deploy-gcp:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Setup GCloud
      uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}

    - name: Push to GCR and deploy to GKE
      run: |
        gcloud auth configure-docker
        docker tag $IMAGE_NAME:$GITHUB_SHA gcr.io/$GCP_PROJECT_ID/$IMAGE_NAME:$GITHUB_SHA
        docker push gcr.io/$GCP_PROJECT_ID/$IMAGE_NAME:$GITHUB_SHA
        gcloud container clusters get-credentials gm-services-cluster --zone us-central1-a
        kubectl set image deployment/gm-services-app app=gcr.io/$GCP_PROJECT_ID/$IMAGE_NAME:$GITHUB_SHA
```

## Related Documentation

- [Docker Deployment](docker.md)
- [Environment Configuration](configuration.md)
- [Monitoring and Alerting](monitoring.md)
- [Security Configuration](../developer/security.md)