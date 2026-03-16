terraform {
  # Hum S3 bucket banane ke baad yahan backend configure karenge
  # taaki remote state management active ho jaye.
  
  # backend "s3" {
  #   bucket         = "stock-prediction-tf-state-shikeb"
  #   key            = "dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-lock" # Multiple users ke liye locking
  # }
}
