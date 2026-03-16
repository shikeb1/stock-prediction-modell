# ==========================================
# GLOBAL VARIABLES
# ==========================================

variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "stock-prediction"
}

variable "environment" {
  description = "The environment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

# ==========================================
# VPC VARIABLES
# ==========================================

variable "vpc_cidr" {
  description = "The IP address range for the main VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# ==========================================
# ECR VARIABLES
# ==========================================

variable "ecr_repositories" {
  description = "List of ECR repositories to create"
  type        = list(string)
  default     = ["stock-backend", "stock-frontend"]
}

# ==========================================
# DATABASE VARIABLES
# ==========================================

variable "db_username" {
  description = "Username for the PostgreSQL RDS instance"
  type        = string
  default     = "postgresadmin"
}

variable "db_password" {
  description = "Password for the PostgreSQL RDS instance (Set this via TF_VAR_db_password environment variable and DO NOT commit)"
  type        = string
  sensitive   = true
}
