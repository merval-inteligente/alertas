output "public_ip" {
  description = "Public IP address of the Alertas EC2 instance"
  value       = aws_instance.alertas.public_ip
}

output "private_ip" {
  description = "Private IP address of the Alertas EC2 instance (for VPC communication)"
  value       = aws_instance.alertas.private_ip
}

output "vpc_id" {
  description = "VPC ID (to be used by other Terraform projects)"
  value       = aws_vpc.main.id
}

output "subnet_id" {
  description = "Public Subnet ID (to be used by other Terraform projects)"
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "Internal Security Group ID (to be used by other Terraform projects)"
  value       = aws_security_group.alertas_internal.id
}

output "public_security_group_id" {
  description = "Public Security Group ID (allows HTTP from Internet)"
  value       = aws_security_group.alertas_public.id
}

output "http_url" {
  description = "HTTP URL to access the API"
  value       = "http://${aws_instance.alertas.public_ip}"
}

output "health_endpoint" {
  description = "Health check endpoint"
  value       = "http://${aws_instance.alertas.public_ip}/health"
}

output "docs_endpoint" {
  description = "API documentation endpoint (Swagger UI)"
  value       = "http://${aws_instance.alertas.public_ip}/docs"
}

output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.alertas.id
}

output "availability_zone" {
  description = "Availability Zone of the EC2 instance"
  value       = aws_instance.alertas.availability_zone
}
