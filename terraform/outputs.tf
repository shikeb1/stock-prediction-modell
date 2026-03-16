# ==========================================
# GLOBAL OUTPUTS
# ==========================================

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "ecr_repository_urls" {
  description = "The URLs of the ECR repositories"
  value       = aws_ecr_repository.repos[*].repository_url
}

# ==========================================
# KUBERNETES OUTPUTS
# ==========================================

output "eks_cluster_name" {
  description = "The name of the EKS Cluster"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "Endpoint for connecting to the EKS cluster API"
  value       = aws_eks_cluster.main.endpoint
}

# ==========================================
# DATABASE & CACHE OUTPUTS
# ==========================================

output "rds_postgres_endpoint" {
  description = "The connection endpoint for the PostgreSQL RDS instance"
  value       = aws_db_instance.postgres.endpoint
}

output "redis_endpoint" {
  description = "The connection endpoint for the Redis ElastiCache cluster"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

# ==========================================
# MLOps OUTPUTS
# ==========================================

output "dvc_bucket_name" {
  description = "The name of the S3 bucket used for DVC Data Version Control"
  value       = aws_s3_bucket.dvc_storage.bucket
}

output "sagemaker_notebook_url" {
  description = "The URL to access the SageMaker Jupyter Notebook"
  value       = "https://console.aws.amazon.com/sagemaker/home?region=${var.aws_region}#/notebook-instances/${aws_sagemaker_notebook_instance.ml_dev.name}"
}
