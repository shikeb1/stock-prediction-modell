# ==========================================
# POSTGRESQL DATABASE (AWS RDS)
# ==========================================

# Subnet group telling RDS which subnets it's allowed to use
resource "aws_db_subnet_group" "default" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  tags = {
    Name = "My DB subnet group"
  }
}

# The PostgreSQL Instance
resource "aws_db_instance" "postgres" {
  identifier           = "${var.project_name}-db"
  allocated_storage    = 20 # 20 GB is sufficient and free-tier eligible
  engine               = "postgres"
  engine_version       = "15" # Exact version matching your tech stack roadmap
  instance_class       = "db.t3.micro"
  
  db_name              = "stockdb" # Database name
  username             = var.db_username
  password             = var.db_password
  
  db_subnet_group_name = aws_db_subnet_group.default.name
  skip_final_snapshot  = true # Allows us to easily delete during testing/learning
  publicly_accessible  = true # Allows your local machine to connect to test

  tags = {
    Environment = var.environment
  }
}
