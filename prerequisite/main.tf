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
  #checkov:skip=CKV_AWS_157: "Ensure that RDS instances have Multi-AZ enabled"
  #checkov:skip=CKV_AWS_353: "Ensure that RDS instances have performance insights enabled"
  #checkov:skip=CKV_AWS_293: "Ensure that AWS database instances have deletion protection enabled"
  #checkov:skip=CKV_AWS_354: "Ensure RDS Performance Insights are encrypted using KMS CMKs"
  #checkov:skip=CKV_AWS_161: "Ensure RDS database has IAM authentication enabled"
  #checkov:skip=CKV_AWS_149: "Ensure that Secrets Manager secret is encrypted using KMS CMK"
  #checkov:skip=CKV_AWS_17: "Ensure all data stored in RDS is not publicly accessible"
  provider             = aws.prd
  engine               = "mysql"
  identifier           = "demo-prd"
  allocated_storage    =  20
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  username             = "myrdsuser"
  password             = "<PASSWORD>"
  parameter_group_name = "default.mysql8.0"
  vpc_security_group_ids = ["sg-00d690421110fc11f"]
  skip_final_snapshot  = true
  publicly_accessible  =  true
  copy_tags_to_snapshot = true
  storage_encrypted    = true
  monitoring_interval  = 5
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
  #checkov:skip=CKV2_AWS_57: "Ensure Secrets Manager secrets should have automatic rotation enabled"
  #checkov:skip=CKV_AWS_337: "Ensure SSM parameters are using KMS CMK"
  provider    = aws.prd
  name        = "tokenize_key"
  description = "key for DB tokenization"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "tokenize_key" {
  provider      = aws.prd
  secret_id     = aws_secretsmanager_secret.tokenize_key.id
  secret_string = <<EOF
  {
    "salt": "mnemonicBILL",
    "password": "tokeniztion",
    "tweak": "CBD09280979564"
  }
EOF
}
###############################preprd account DB###############################
#create a RDS Database Instance
resource "aws_db_instance" "demo_preprd" {
  #checkov:skip=CKV_AWS_157: "Ensure that RDS instances have Multi-AZ enabled"
  #checkov:skip=CKV_AWS_353: "Ensure that RDS instances have performance insights enabled"
  #checkov:skip=CKV_AWS_293: "Ensure that AWS database instances have deletion protection enabled"
  #checkov:skip=CKV_AWS_354: "Ensure RDS Performance Insights are encrypted using KMS CMKs"
  #checkov:skip=CKV_AWS_161: "Ensure RDS database has IAM authentication enabled"
  #checkov:skip=CKV_AWS_149: "Ensure that Secrets Manager secret is encrypted using KMS CMK"
  #checkov:skip=CKV_AWS_17: "Ensure all data stored in RDS is not publicly accessible"
  provider             = aws.preprd
  engine               = "mysql"
  identifier           = "demo-preprd"
  allocated_storage    =  20
  engine_version       = "8.0"
  instance_class       = "db.t3.micro"
  username             = "myrdsuser"
  password             = "<PASSWORD>"
  parameter_group_name = "default.mysql8.0"
  vpc_security_group_ids = ["sg-02474e3861f63f0a1"]
  skip_final_snapshot  = true
  copy_tags_to_snapshot = true
  storage_encrypted    = true
  monitoring_interval  = 5
  publicly_accessible  = true
  auto_minor_version_upgrade = true
  enabled_cloudwatch_logs_exports = ["general", "error", "slowquery"]
}
