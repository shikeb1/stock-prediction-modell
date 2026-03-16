# ==========================================
# ECR REPOSITORIES
# ==========================================

resource "aws_ecr_repository" "repos" {
  # count loop creates a repo for each item in the var.ecr_repositories list
  count                = length(var.ecr_repositories)
  name                 = var.ecr_repositories[count.index]
  image_tag_mutability = "MUTABLE"
  force_delete         = true # Allows Terraform to delete the repo even if images exist

  image_scanning_configuration {
    scan_on_push = true # Automatically scans Docker images for vulnerabilities
  }

  tags = {
    Environment = var.environment
    Terraform   = "true"
  }
}
