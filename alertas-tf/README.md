# 🚀 Alertas Terraform - AWS Infrastructure# Alertas Terraform - AWS Deployment



Infraestructura como código (IaC) para deployar la API de Alertas en AWS usando Terraform.Infraestructura como código para deployar la API de Alertas en AWS Academy.



## 📋 Arquitectura## 📋 Estructura



``````

┌─────────────────────────────────────────────────┐alertas-tf/

│              Internet (0.0.0.0/0)               │├── main.tf           # Recursos principales (EC2, Security Groups)

└────────────────────┬────────────────────────────┘├── vpc.tf            # Red (VPC, Subnet, IGW, Route Table)

                     │├── variables.tf      # Variables de configuración

          ┌──────────▼──────────┐├── outputs.tf        # Outputs para otros proyectos

          │  Internet Gateway   │├── user_data.sh      # Script de inicialización EC2

          └──────────┬──────────┘└── README.md         # Esta documentación

                     │```

     ┌───────────────▼──────────────────┐

     │   VPC: 10.0.0.0/16               │## 🏗️ Recursos Creados

     │                                  │

     │  ┌────────────────────────────┐  │### Red

     │  │ Public Subnet: 10.0.1.0/24 │  │- **VPC**: `10.0.0.0/16`

     │  │                            │  │- **Subred Pública**: `10.0.1.0/24`

     │  │  ┌──────────────────────┐  │  │- **Internet Gateway**: Para acceso público

     │  │  │  EC2 t3.micro       │  │  │- **Route Table**: Enrutamiento a Internet

     │  │  │  Amazon Linux 2023  │  │  │

     │  │  │                     │  │  │### Seguridad

     │  │  │  ┌──────────────┐   │  │  │- **Security Group Público**: Permite HTTP (80) desde Internet

     │  │  │  │  FastAPI     │   │  │  │- **Security Group Interno**: Permite TCP completo dentro de la VPC

     │  │  │  │  Port 80     │◄──┼──┼──┼── HTTP Traffic

     │  │  │  └──────────────┘   │  │  │### Compute

     │  │  │                     │  │  │- **EC2 Instance**: Amazon Linux 2023, t3.micro

     │  │  │  ┌──────────────┐   │  │  │- **Docker + Docker Compose**: Instalados automáticamente

     │  │  │  │  MongoDB     │───┼──┼──┼── Atlas Cloud- **FastAPI**: Corriendo en puerto 8000, expuesto en puerto 80

     │  │  │  │  (External)  │   │  │  │

     │  │  │  └──────────────┘   │  │  │## 🚀 Deployment

     │  │  └──────────────────────┘  │  │

     │  └────────────────────────────┘  │### 1. Instalar Terraform

     └───────────────────────────────────┘

```**Windows (Chocolatey):**

```powershell

## 🏗️ Recursos AWS Creadoschoco install terraform

```

### Red (VPC)

- **VPC**: `10.0.0.0/16` - Red privada aislada**Windows (Manual):**

- **Subnet Pública**: `10.0.1.0/24` en `us-east-1a`1. Descargar de https://www.terraform.io/downloads

- **Internet Gateway**: Conectividad a Internet2. Extraer `terraform.exe` a `C:\terraform`

- **Route Table**: Enrutamiento `0.0.0.0/0` → IGW3. Agregar a PATH



### Seguridad (Security Groups)**Verificar instalación:**

- **alertas-public-sg**: ```bash

  - Ingress: HTTP (80) desde `0.0.0.0/0`terraform --version

  - Ingress: SSH (22) desde `0.0.0.0/0` (si `enable_ssh=true`)```

  - Egress: Todo el tráfico permitido

  ### 2. Configurar AWS Credentials (AWS Academy)

- **alertas-internal-sg**:

  - Ingress: TCP 0-65535 desde `10.0.0.0/16` (VPC)Copia las credenciales desde AWS Academy y ejecuta:

  - Egress: Todo el tráfico permitido

```bash

### Compute (EC2)export AWS_ACCESS_KEY_ID="ASIA..."

- **Tipo**: `t3.micro` (1 vCPU, 1 GB RAM)export AWS_SECRET_ACCESS_KEY="..."

- **AMI**: Amazon Linux 2023 (latest)export AWS_SESSION_TOKEN="..."

- **Storage**: 30 GB gp3 EBS encryptedexport AWS_DEFAULT_REGION="us-east-1"

- **IP Pública**: Asignada automáticamente```

- **Key Pair**: `millaveuade` (para SSH)

**PowerShell:**

### Software Instalado```powershell

- Python 3.11$env:AWS_ACCESS_KEY_ID="ASIA..."

- FastAPI + Uvicorn$env:AWS_SECRET_ACCESS_KEY="..."

- Motor (MongoDB async driver)$env:AWS_SESSION_TOKEN="..."

- Pydantic V2$env:AWS_DEFAULT_REGION="us-east-1"

- Alert scoring system (`alert_utils.py`)```



## 📁 Estructura del Proyecto### 3. Configurar Variables



```Crea un archivo `terraform.tfvars` con tus credenciales:

alertas-tf/

├── main.tf                    # Recursos principales (EC2, data sources)```bash

├── vpc.tf                     # Networking (VPC, Subnet, IGW, RT, SGs)# Copia el archivo de ejemplo

├── variables.tf               # Variables configurablescp terraform.tfvars.example terraform.tfvars

├── outputs.tf                 # Outputs exportados

├── user_data_simple.sh        # Script de inicialización EC2# Edita terraform.tfvars y actualiza:

├── terraform.tfvars.example   # Template de variables (SÍ commitear)# - mongodb_uri: Tu URI de MongoDB Atlas

├── terraform.tfvars           # Variables con secretos (NO commitear)# - enable_ssh: true si necesitas acceso SSH para debug

├── .gitignore                 # Ignora tfstate, tfvars, .terraform/```

└── README.md                  # Esta documentación

```**⚠️ IMPORTANTE**: `terraform.tfvars` está en `.gitignore` y **NO debe commitearse** ya que contiene credenciales sensibles.



## 🚀 Guía de Deployment### 4. Deploy



### Prerrequisitos```bash

cd alertas-tf

1. **Terraform** >= 1.0terraform init

   ```powershellterraform plan  # Verifica que todo esté correcto

   # Windows con Chocolateyterraform apply -auto-approve

   choco install terraform```

   

   # Verificar**Nota**: Si no creaste `terraform.tfvars`, Terraform te pedirá el `mongodb_uri` interactivamente.

   terraform --version

   ```### 5. Acceder a la API



2. **AWS CLI** (opcional pero recomendado)Terraform mostrará:

   ```powershell```

   choco install awscliOutputs:

   ```

docs_endpoint = "http://3.82.45.123/docs"

3. **Credenciales AWS Academy**health_endpoint = "http://3.82.45.123/health"

   - Ir a AWS Academy → AWS Detailshttp_url = "http://3.82.45.123"

   - Copiar credenciales (válidas por 4 horas)private_ip = "10.0.1.45"

public_ip = "3.82.45.123"

### Paso 1: Configurar AWS Credentialssecurity_group_id = "sg-0abc123..."

subnet_id = "subnet-0def456..."

**PowerShell:**vpc_id = "vpc-0789abc..."

```powershell```

$env:AWS_ACCESS_KEY_ID="ASIA..."

$env:AWS_SECRET_ACCESS_KEY="wJa..."Accede a:

$env:AWS_SESSION_TOKEN="IQoJ..."- **Swagger UI**: http://PUBLIC_IP/docs

$env:AWS_DEFAULT_REGION="us-east-1"- **Health Check**: http://PUBLIC_IP/health

```- **API Root**: http://PUBLIC_IP/



**Bash/Linux:**## 🔧 Variables Personalizables

```bash

export AWS_ACCESS_KEY_ID="ASIA..."Puedes sobrescribir valores creando `terraform.tfvars`:

export AWS_SECRET_ACCESS_KEY="wJa..."

export AWS_SESSION_TOKEN="IQoJ..."```hcl

export AWS_DEFAULT_REGION="us-east-1"project             = "mi-alertas"

```region              = "us-west-2"

instance_type       = "t3.small"

**Verificar:**vpc_cidr            = "172.16.0.0/16"

```bashpublic_subnet_cidr  = "172.16.1.0/24"

aws sts get-caller-identityenable_ssh          = true

``````



### Paso 2: Configurar Variables SensiblesO via CLI:

```bash

**Crear `terraform.tfvars` (NUNCA commitear este archivo):**terraform apply -var="instance_type=t3.small" -var="enable_ssh=true"

```

```bash

cd alertas-tf## 📤 Outputs para Otros Proyectos

cp terraform.tfvars.example terraform.tfvars

```Esta infraestructura expone outputs que puedes usar en `chat-tf` y `merval-tf`:



**Editar `terraform.tfvars`:**```hcl

```hcl# En otro proyecto Terraform

# MongoDB connection string (REQUERIDO)data "terraform_remote_state" "alertas" {

mongodb_uri = "mongodb+srv://user:password@cluster.mongodb.net/MervalDB?retryWrites=true&w=majority"  backend = "local"

  config = {

# Enable SSH access for debugging (opcional)    path = "../alertas-tf/terraform.tfstate"

enable_ssh = true  }

}

# Custom instance type (opcional)

# instance_type = "t3.small"resource "aws_instance" "chat" {

```  vpc_security_group_ids = [

    data.terraform_remote_state.alertas.outputs.security_group_id

> ⚠️ **IMPORTANTE**: `terraform.tfvars` contiene credenciales sensibles y está en `.gitignore`. **NO lo subas a GitHub**.  ]

  subnet_id = data.terraform_remote_state.alertas.outputs.subnet_id

### Paso 3: Inicializar Terraform}

```

```bash

cd alertas-tf## 🧪 Verificación

terraform init

```### 1. Verificar que la instancia está corriendo

```bash

Esto descarga el provider de AWS (~100 MB) y configura el backend local.terraform output instance_id

```

### Paso 4: Planificar Deployment

### 2. SSH a la instancia (si enable_ssh=true)

```bash```bash

terraform planPUBLIC_IP=$(terraform output -raw public_ip)

```ssh ec2-user@$PUBLIC_IP

```

Revisa que:

- Se van a crear 8 recursos### 3. Ver logs de la aplicación

- El `user_data` muestra `(sensitive value)` ✅```bash

- La región es `us-east-1`ssh ec2-user@$PUBLIC_IP "docker-compose -f /opt/alertas/docker-compose.yml logs"

```

### Paso 5: Aplicar Infraestructura

### 4. Verificar Health Check

```bash```bash

terraform apply -auto-approvePUBLIC_IP=$(terraform output -raw public_ip)

```curl http://$PUBLIC_IP/health

```

**Tiempo estimado**: 2-3 minutos

- VPC y subnets: ~15 segundos## 🗑️ Destruir Infraestructura

- Security groups: ~5 segundos

- EC2 instance: ~15 segundos```bash

- User data script (instalación): ~90 segundosterraform destroy -auto-approve

```

### Paso 6: Verificar Deployment

## 📝 Notas AWS Academy

```bash

# Ver outputs- Las credenciales expiran después de 4 horas

terraform output- Debes volver a ejecutar `export AWS_...` cuando expiren

- Los recursos se destruyen automáticamente al terminar la sesión del laboratorio

# Testear health endpoint- Usa `terraform refresh` si necesitas actualizar el estado

$IP = terraform output -raw public_ip

Invoke-WebRequest http://$IP/health## 🔍 Troubleshooting

```

### Error: "Error launching source instance"

**Respuesta esperada:**- Verifica que las credenciales de AWS Academy sean válidas

```json- Asegúrate de estar en la región correcta (`us-east-1`)

{

  "status": "healthy",### La API no responde

  "database": "connected",```bash

  "message": "API funcionando correctamente"# Conectarse por SSH y ver logs

}ssh ec2-user@PUBLIC_IP

```cd /opt/alertas

docker-compose logs -f

## 🌐 Endpoints Disponibles```



Terraform expone los siguientes outputs:### Cambios en el código

```bash

| Output | Descripción | Ejemplo |# SSH a la instancia

|--------|-------------|---------|cd /opt/alertas

| `http_url` | URL base de la API | `http://54.147.6.0` |git pull

| `health_endpoint` | Health check | `http://54.147.6.0/health` |docker-compose down

| `docs_endpoint` | Swagger UI | `http://54.147.6.0/docs` |docker-compose build

| `public_ip` | IP pública EC2 | `54.147.6.0` |docker-compose up -d

| `private_ip` | IP privada VPC | `10.0.1.171` |```

| `vpc_id` | ID de la VPC | `vpc-0a9472df...` |

| `subnet_id` | ID de la subnet | `subnet-093647...` |## 🔗 Enlaces

| `security_group_id` | SG interno | `sg-060fffa1e...` |

| `public_security_group_id` | SG público | `sg-039219b0e...` |- **Repositorio GitHub**: https://github.com/merval-inteligente/alertas

| `instance_id` | ID de la instancia | `i-0d0e2fc0d...` |- **Documentación API**: http://PUBLIC_IP/docs

| `availability_zone` | AZ de la subnet | `us-east-1a` |- **Terraform Docs**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs


## 🧪 Pruebas y Verificación

### 1. Health Check
```powershell
$IP = terraform output -raw public_ip
Invoke-WebRequest "http://$IP/health"
```

### 2. Swagger UI
```powershell
Start-Process "http://$(terraform output -raw public_ip)/docs"
```

### 3. Generar Alertas
```powershell
$IP = terraform output -raw public_ip
Invoke-RestMethod -Uri "http://$IP/alerts/generate" -Method POST
```

### 4. SSH a la Instancia
```bash
PUBLIC_IP=$(terraform output -raw public_ip)
ssh -i ~/.ssh/millaveuade.pem ec2-user@$PUBLIC_IP
```

**Dentro de la instancia:**
```bash
# Ver estado del servicio
sudo systemctl status alertas

# Ver logs en tiempo real
sudo journalctl -u alertas -f

# Ver logs de instalación
tail -100 /var/log/user-data.log

# Ver configuración
cat /opt/alertas/.env
```

## 🔧 Variables Configurables

| Variable | Tipo | Default | Descripción |
|----------|------|---------|-------------|
| `mongodb_uri` | string | **REQUERIDO** | URI de MongoDB Atlas (sensible) |
| `project` | string | `"alertas"` | Nombre del proyecto (tags) |
| `region` | string | `"us-east-1"` | AWS region |
| `instance_type` | string | `"t3.micro"` | Tipo de instancia EC2 |
| `vpc_cidr` | string | `"10.0.0.0/16"` | CIDR de la VPC |
| `public_subnet_cidr` | string | `"10.0.1.0/24"` | CIDR de la subnet |
| `enable_ssh` | bool | `false` | Habilitar puerto 22 |
| `key_name` | string | `"millaveuade"` | Key pair para SSH |

**Sobrescribir via CLI:**
```bash
terraform apply \
  -var="instance_type=t3.small" \
  -var="enable_ssh=true" \
  -var="project=alertas-prod"
```

## 📤 Integración con Otros Proyectos

Los outputs de este proyecto pueden ser utilizados por `chat-tf` y `merval-tf`:

**Ejemplo - Data Source (Remote State):**
```hcl
# En chat-tf/main.tf
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
  
  # Usar la misma VPC que alertas
}
```

## 🗑️ Destruir Infraestructura

```bash
terraform destroy -auto-approve
```

**Recursos destruidos:** VPC, Subnet, IGW, Route Table, 2 Security Groups, EC2 instance  
**Tiempo**: ~1 minuto

> ⚠️ Los datos en la instancia EC2 se perderán permanentemente. MongoDB Atlas (externo) no se ve afectado.

## 🔐 Seguridad y Buenas Prácticas

### ✅ Implementadas

- ✅ **Variables sensibles**: `mongodb_uri` marcada como `sensitive = true`
- ✅ **Gitignore**: `*.tfvars`, `*.tfstate*`, `.terraform/` ignorados
- ✅ **EBS encryption**: Volumen root encriptado con AWS KMS
- ✅ **Credenciales externas**: MongoDB en Atlas (no en EC2)
- ✅ **User data templating**: `templatefile()` para inyectar secrets sin hardcodeo
- ✅ **Ejemplo seguro**: `terraform.tfvars.example` sin credenciales reales

### ⚠️ Consideraciones AWS Academy

- Las credenciales expiran cada **4 horas**
- Los recursos se **destruyen automáticamente** al terminar el laboratorio
- **No usar para producción** - Solo para desarrollo/aprendizaje

## 🐛 Troubleshooting

### Error: "No valid credential sources found"

**Solución**: Reexportar credenciales de AWS Academy

```powershell
$env:AWS_ACCESS_KEY_ID="..."
$env:AWS_SECRET_ACCESS_KEY="..."
$env:AWS_SESSION_TOKEN="..."
```

### API no responde en puerto 80

**Diagnóstico via SSH:**
```bash
ssh -i ~/.ssh/millaveuade.pem ec2-user@PUBLIC_IP

# Ver estado del servicio
sudo systemctl status alertas

# Ver logs
sudo journalctl -u alertas -n 100 --no-pager

# Verificar .env
cat /opt/alertas/.env
```

## 📝 Changelog

### v1.1.0 (2025-10-05)
- ✨ Variables sensibles con `templatefile()`
- 🔒 MongoDB URI mediante `terraform.tfvars`
- 📖 Documentación completa del README
- ✅ Deployment validado exitosamente

### v1.0.0 (2025-10-05)
- 🎉 Release inicial con VPC + EC2
- 🚀 User data script automático
- 📤 Outputs para otros proyectos

---

**Repositorio**: [merval-inteligente/alertas](https://github.com/merval-inteligente/alertas)
