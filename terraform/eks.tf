# ==========================================
# DAY 5: KUBERNETES (AWS EKS CLUSTER)
# ==========================================

# 1. The EKS Control Plane (The "Brain" of Kubernetes)
resource "aws_eks_cluster" "main" {
  name     = "${var.project_name}-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.30" # Standard, stable Kubernetes version

  vpc_config {
    # Kubernetes needs to know which network subnets to run inside
    subnet_ids = [
      aws_subnet.public_1.id,
      aws_subnet.public_2.id
    ]
  }

  # Ensure the IAM role exists before creating the cluster
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]

  tags = {
    Environment = var.environment
  }
}

# 2. Managed Node Group (The "Workers" of Kubernetes - EC2 Instances)
resource "aws_eks_node_group" "main_nodes" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.project_name}-node-group"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  # Node sizing (using t3.medium as it matches RAM requirements for ML)
  instance_types = ["t3.medium"]
  capacity_type  = "ON_DEMAND"

  # Auto-scaling configurations
  scaling_config {
    desired_size = 2 # Start with 2 worker nodes
    max_size     = 4 # Scale up to 4 if traffic increases
    min_size     = 1 # Keep at least 1 alive at night
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ecr_readonly_policy
  ]
}
