variable "db_user" {
  description = "DB user"
  type        = string
  default     = ""
}

variable "db_password" {
  description = "DB password"
  type        = string
  default     = ""
}

variable "prd_db_sg_id" {
  description = "Security Group id of production DB"
  type        = string
  default     = ""
}

variable "preprd_db_sg_id" {
  description = "Security Group id of production DB"
  type        = string
  default     = ""
}
