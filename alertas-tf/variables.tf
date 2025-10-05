variable "project" {
  description = "Project name for resource tagging"
  type        = string
  default     = "alertas"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "enable_ssh" {
  description = "Enable SSH access to EC2 instance"
  type        = bool
  default     = false
}

variable "key_name" {
  description = "Name of the SSH key pair to use for EC2 instance"
  type        = string
  default     = "millaveuade"
}

variable "mongodb_uri" {
  description = "MongoDB connection URI (optional, will use GitHub secrets if not provided)"
  type        = string
  default     = ""
  sensitive   = true
}
