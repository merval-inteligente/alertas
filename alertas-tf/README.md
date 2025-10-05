# Alertas Terraform - AWS Deployment

Infraestructura como código para deployar la API de Alertas en AWS Academy.

## 📋 Estructura

```
alertas-tf/
├── main.tf           # Recursos principales (EC2, Security Groups)
├── vpc.tf            # Red (VPC, Subnet, IGW, Route Table)
├── variables.tf      # Variables de configuración
├── outputs.tf        # Outputs para otros proyectos
├── user_data.sh      # Script de inicialización EC2
└── README.md         # Esta documentación
```

## 🏗️ Recursos Creados

### Red
- **VPC**: `10.0.0.0/16`
- **Subred Pública**: `10.0.1.0/24`
- **Internet Gateway**: Para acceso público
- **Route Table**: Enrutamiento a Internet

### Seguridad
- **Security Group Público**: Permite HTTP (80) desde Internet
- **Security Group Interno**: Permite TCP completo dentro de la VPC

### Compute
- **EC2 Instance**: Amazon Linux 2023, t3.micro
- **Docker + Docker Compose**: Instalados automáticamente
- **FastAPI**: Corriendo en puerto 8000, expuesto en puerto 80

## 🚀 Deployment

### 1. Instalar Terraform

**Windows (Chocolatey):**
```powershell
choco install terraform
```

**Windows (Manual):**
1. Descargar de https://www.terraform.io/downloads
2. Extraer `terraform.exe` a `C:\terraform`
3. Agregar a PATH

**Verificar instalación:**
```bash
terraform --version
```

### 2. Configurar AWS Credentials (AWS Academy)

Copia las credenciales desde AWS Academy y ejecuta:

```bash
export AWS_ACCESS_KEY_ID="ASIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
export AWS_DEFAULT_REGION="us-east-1"
```

**PowerShell:**
```powershell
$env:AWS_ACCESS_KEY_ID="ASIA..."
$env:AWS_SECRET_ACCESS_KEY="..."
$env:AWS_SESSION_TOKEN="..."
$env:AWS_DEFAULT_REGION="us-east-1"
```

### 3. Deploy

```bash
cd alertas-tf
terraform init
terraform plan
terraform apply -auto-approve
```

### 4. Acceder a la API

Terraform mostrará:
```
Outputs:

docs_endpoint = "http://3.82.45.123/docs"
health_endpoint = "http://3.82.45.123/health"
http_url = "http://3.82.45.123"
private_ip = "10.0.1.45"
public_ip = "3.82.45.123"
security_group_id = "sg-0abc123..."
subnet_id = "subnet-0def456..."
vpc_id = "vpc-0789abc..."
```

Accede a:
- **Swagger UI**: http://PUBLIC_IP/docs
- **Health Check**: http://PUBLIC_IP/health
- **API Root**: http://PUBLIC_IP/

## 🔧 Variables Personalizables

Puedes sobrescribir valores creando `terraform.tfvars`:

```hcl
project             = "mi-alertas"
region              = "us-west-2"
instance_type       = "t3.small"
vpc_cidr            = "172.16.0.0/16"
public_subnet_cidr  = "172.16.1.0/24"
enable_ssh          = true
```

O via CLI:
```bash
terraform apply -var="instance_type=t3.small" -var="enable_ssh=true"
```

## 📤 Outputs para Otros Proyectos

Esta infraestructura expone outputs que puedes usar en `chat-tf` y `merval-tf`:

```hcl
# En otro proyecto Terraform
data "terraform_remote_state" "alertas" {
  backend = "local"
  config = {
    path = "../alertas-tf/terraform.tfstate"
  }
}

resource "aws_instance" "chat" {
  vpc_security_group_ids = [
    data.terraform_remote_state.alertas.outputs.security_group_id
  ]
  subnet_id = data.terraform_remote_state.alertas.outputs.subnet_id
}
```

## 🧪 Verificación

### 1. Verificar que la instancia está corriendo
```bash
terraform output instance_id
```

### 2. SSH a la instancia (si enable_ssh=true)
```bash
PUBLIC_IP=$(terraform output -raw public_ip)
ssh ec2-user@$PUBLIC_IP
```

### 3. Ver logs de la aplicación
```bash
ssh ec2-user@$PUBLIC_IP "docker-compose -f /opt/alertas/docker-compose.yml logs"
```

### 4. Verificar Health Check
```bash
PUBLIC_IP=$(terraform output -raw public_ip)
curl http://$PUBLIC_IP/health
```

## 🗑️ Destruir Infraestructura

```bash
terraform destroy -auto-approve
```

## 📝 Notas AWS Academy

- Las credenciales expiran después de 4 horas
- Debes volver a ejecutar `export AWS_...` cuando expiren
- Los recursos se destruyen automáticamente al terminar la sesión del laboratorio
- Usa `terraform refresh` si necesitas actualizar el estado

## 🔍 Troubleshooting

### Error: "Error launching source instance"
- Verifica que las credenciales de AWS Academy sean válidas
- Asegúrate de estar en la región correcta (`us-east-1`)

### La API no responde
```bash
# Conectarse por SSH y ver logs
ssh ec2-user@PUBLIC_IP
cd /opt/alertas
docker-compose logs -f
```

### Cambios en el código
```bash
# SSH a la instancia
cd /opt/alertas
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

## 🔗 Enlaces

- **Repositorio GitHub**: https://github.com/merval-inteligente/alertas
- **Documentación API**: http://PUBLIC_IP/docs
- **Terraform Docs**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
