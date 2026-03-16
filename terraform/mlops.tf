# ==========================================
# MLOps: SAGEMAKER, DVC, And MLFLOW
# ==========================================

# 1. DVC (Data Version Control) Data Lake
resource "aws_s3_bucket" "dvc_storage" {
  bucket = "${var.project_name}-dvc-data-lake-12345" # MUST BE UNIQUE

  tags = {
    Purpose = "DVC Data Versioning"
  }
}

# 2. MLflow Artifact Store
resource "aws_s3_bucket" "mlflow_artifacts" {
  bucket = "${var.project_name}-mlflow-artifacts-12345" # MUST BE UNIQUE

  tags = {
    Purpose = "MLflow Model Registry"
  }
}

# 3. SageMaker Notebook (Model Development Environment - Day 8)
resource "aws_sagemaker_notebook_instance" "ml_dev" {
  name          = "${var.project_name}-training-notebook"
  role_arn      = aws_iam_role.sagemaker_role.arn
  instance_type = "ml.t3.medium" # Default instance suitable for general ML
  
  subnet_id     = aws_subnet.public_1.id

  tags = {
    Environment = var.environment
    Phase       = "MLOps"
  }
}
