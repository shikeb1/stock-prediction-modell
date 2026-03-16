# 1. S3 BUCKET FOR STATE STORAGE
resource "aws_s3_bucket" "terraform_state" {
  bucket = "stock-prediction-tf-state-12345" # MUST BE GLOBALLY UNIQUE

  lifecycle {
    prevent_destroy = true # Prevents accidental deletion of the state bucket
  }
}

# 2. VERSIONING FOR STATE BUCKET
resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 3. ENCRYPTION FOR STATE BUCKET
resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 4. DYNAMODB FOR STATE LOCKING
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "stock-prediction-tf-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
