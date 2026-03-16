# ==========================================
# REDIS CACHE (AWS ELASTICACHE)
# ==========================================

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "default" {
  name       = "${var.project_name}-redis-subnet-group"
  subnet_ids = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

# The Redis Server
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.project_name}-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro" # Free-tier sized
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7" # Exact version matching roadmap (Redis 7)
  engine_version       = "7.0"
  port                 = 6379

  subnet_group_name    = aws_elasticache_subnet_group.default.name

  tags = {
    Environment = var.environment
  }
}
