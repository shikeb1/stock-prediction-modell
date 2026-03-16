# ==========================================
# MLOps: KSERVE (Model Serving on Kubernetes)
# ==========================================

# 1. KServe requires cert-manager to handle webhooks and certificates
resource "helm_release" "cert_manager" {
  name             = "cert-manager"
  repository       = "https://charts.jetstack.io"
  chart            = "cert-manager"
  namespace        = "cert-manager"
  create_namespace = true
  version          = "v1.13.0" # Stable version

  set {
    name  = "installCRDs"
    value = "true"
  }

  depends_on = [ aws_eks_node_group.main_nodes ]
}

# 2. KServe requires Knative Serving for Serverless Auto-scaling (Scale to Zero)
resource "helm_release" "knative_serving" {
  name             = "knative-serving"
  repository       = "https://knative.dev/charts"
  chart            = "serving-core"
  namespace        = "knative-serving"
  create_namespace = true

  depends_on = [ helm_release.cert_manager ]
}

# 3. KServe Installation
resource "helm_release" "kserve" {
  name             = "kserve"
  repository       = "https://kserve.github.io/kserve/"
  chart            = "kserve"
  namespace        = "kserve"
  create_namespace = true

  depends_on = [ helm_release.knative_serving ]
}

# ==========================================
# KSERVE IAM ROLE (To download models from MLflow S3)
# ==========================================

resource "aws_iam_role" "kserve_s3_role" {
  name = "${var.project_name}-kserve-s3-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${replace(aws_eks_cluster.main.identity[0].oidc[0].issuer, "https://", "")}"
        }
        Condition = {
          "StringEquals" = {
            "${replace(aws_eks_cluster.main.identity[0].oidc[0].issuer, "https://", "")}:sub" = "system:serviceaccount:default:kserve-sa"
          }
        }
      }
    ]
  })
}

resource "aws_iam_policy" "kserve_s3_policy" {
  name = "${var.project_name}-kserve-s3-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.mlflow_artifacts.arn,
          "${aws_s3_bucket.mlflow_artifacts.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "kserve_s3_attach" {
  role       = aws_iam_role.kserve_s3_role.name
  policy_arn = aws_iam_policy.kserve_s3_policy.arn
}
