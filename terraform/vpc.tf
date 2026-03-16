# ==========================================
# ADVANCED VPC CREATION (For EKS & RDS)
# ==========================================

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-vpc"
    Environment = var.environment
    Terraform   = "true"
  }
}

# ==========================================
# PUBLIC SUBNETS (Required for EKS & ALB)
# ==========================================

# Subnet 1 (Zone A)
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true # Automatically give nodes a public IP

  tags = {
    Name                                           = "${var.project_name}-public-1"
    "kubernetes.io/cluster/${var.project_name}-cluster" = "shared" # Required by EKS
    "kubernetes.io/role/elb"                       = "1"          # Allows public load balancers
  }
}

# Subnet 2 (Zone B) - Multi-AZ is required for EKS and RDS
resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true

  tags = {
    Name                                           = "${var.project_name}-public-2"
    "kubernetes.io/cluster/${var.project_name}-cluster" = "shared"
    "kubernetes.io/role/elb"                       = "1"
  }
}

# ==========================================
# INTERNET ROUTING
# ==========================================

# Internet Gateway (Allows internet access to the VPC)
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-${var.environment}-igw"
  }
}

# Route Table (Directs traffic to the Internet Gateway)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

# Association: Tie the route table to the subnets
resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}
