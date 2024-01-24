provider "aws" {
  alias = "preprd"
  profile = "demo-preprd"
  region = "ap-southeast-1"
}
provider "aws" {
  alias = "prd"
  profile = "demo-prd"
  region = "ap-southeast-1"
}

###############################prd account DB###############################
#create a RDS Database Instance
resource "aws_db_instance" "demo_prd" {
  provider               = aws.prd
  engine                 = "mysql"
  identifier             = "demo-prd"
  allocated_storage      =  20
  engine_version         = "8.0"
  instance_class         = "db.t3.micro"
  username               = var.db_user
  password               = var.db_password
  parameter_group_name   = "default.mysql8.0"
  vpc_security_group_ids = [var.prd_db_sg_id]
  skip_final_snapshot    = true
  publicly_accessible    = true
  copy_tags_to_snapshot  = true
  storage_encrypted      = true
  monitoring_interval    = 5
  auto_minor_version_upgrade = true
  enabled_cloudwatch_logs_exports = ["general", "error", "slowquery"]
}

resource "aws_ssm_parameter" "demo-db-tokenize-schema" {
  provider = aws.prd
  name  = "demo-db-tokenize-schema"
  type  = "SecureString"
  value = file("demo-db-tokenize-schema.json")
}

resource "aws_secretsmanager_secret" "tokenize_key" {
  provider    = aws.prd
  name        = "tokenize_key"
  description = "key for DB tokenization"
  recovery_window_in_days = 0
}

# There are 3 items defined in demo-db-tokenize-fpe-key.json, you can check the detail explaination in README
#   * salt - used in the process of generating the encryption key
#   * password - used in the process of generating the encryption key
#   * tweak - additional input parameter in the FPE algorithm, tweak's length to be either 7 bytes or 8 bytes
resource "aws_secretsmanager_secret_version" "tokenize_key" {
  provider      = aws.prd
  secret_id     = aws_secretsmanager_secret.tokenize_key.id
  secret_string = file("demo-db-tokenize-fpe-key.json")
}
###############################preprd account DB###############################
#create a RDS Database Instance
resource "aws_db_instance" "demo_preprd" {
  provider               = aws.preprd
  engine                 = "mysql"
  identifier             = "demo-preprd"
  allocated_storage      =  20
  engine_version         = "8.0"
  instance_class         = "db.t3.micro"
  username               = var.db_user
  password               = var.db_password
  parameter_group_name   = "default.mysql8.0"
  vpc_security_group_ids = [var.preprd_db_sg_id]
  skip_final_snapshot    = true
  copy_tags_to_snapshot  = true
  storage_encrypted      = true
  monitoring_interval    = 5
  publicly_accessible    = true
  auto_minor_version_upgrade = true
  enabled_cloudwatch_logs_exports = ["general", "error", "slowquery"]
}
