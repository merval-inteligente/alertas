terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Data source para obtener la AMI más reciente de Amazon Linux 2023
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Group público para HTTP
resource "aws_security_group" "alertas_public" {
  name        = "${var.project}-public-sg"
  description = "Security group for public HTTP access"
  vpc_id      = aws_vpc.main.id

  # HTTP desde Internet
  ingress {
    description = "HTTP from Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH opcional (solo si enable_ssh = true)
  dynamic "ingress" {
    for_each = var.enable_ssh ? [1] : []
    content {
      description = "SSH access"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  # Todo el tráfico saliente
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project}-public-sg"
    Project = var.project
  }
}

# Security Group interno para comunicación VPC
resource "aws_security_group" "alertas_internal" {
  name        = "${var.project}-internal-sg"
  description = "Security group for internal VPC communication"
  vpc_id      = aws_vpc.main.id

  # Permitir todo el tráfico TCP dentro de la VPC
  ingress {
    description = "TCP from VPC"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  # Todo el tráfico saliente
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project}-internal-sg"
    Project = var.project
  }
}

# Instancia EC2 para la API de Alertas
resource "aws_instance" "alertas" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [
    aws_security_group.alertas_public.id,
    aws_security_group.alertas_internal.id
  ]

  # SSH key pair
  key_name = var.key_name

  user_data = templatefile("${path.module}/user_data_simple.sh", {
    mongodb_uri = var.mongodb_uri
  })

  # Habilitar IP pública
  associate_public_ip_address = true

  # Tagging
  tags = {
    Name    = "${var.project}-api"
    Project = var.project
  }

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true
    
    tags = {
      Name    = "${var.project}-root-volume"
      Project = var.project
    }
  }
}
