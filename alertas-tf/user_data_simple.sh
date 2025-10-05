#!/bin/bash
set -e
exec > >(tee /var/log/user-data.log) 2>&1

echo "========== Alertas API - Simple Deployment =========="
dnf update -y
dnf install -y python3.11 python3.11-pip git

mkdir -p /opt/alertas
cd /opt/alertas

# Clone repo
git clone https://github.com/merval-inteligente/alertas.git .

# Install dependencies WITH pytz
pip3.11 install fastapi uvicorn[standard] motor pymongo python-dotenv pydantic pydantic-settings pytz

# Create .env
cat > .env <<'EOF'
MONGODB_URI=mongodb+srv://guest:guest@cluster.mongodb.net/MervalDB?retryWrites=true&w=majority
DATABASE_NAME=MervalDB
EOF

# Create simple systemd service (run as root to use port 80)
cat > /etc/systemd/system/alertas.service <<'EOF'
[Unit]
Description=Alertas API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/alertas
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 80
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable alertas
systemctl start alertas

# Wait and check
sleep 30

if systemctl is-active --quiet alertas; then
    echo "✅ SUCCESS!"
    curl http://localhost/health 2>/dev/null || echo "API is starting..."
else
    echo "❌ FAILED:"
    journalctl -u alertas -n 100 --no-pager
fi

echo "========== DONE =========="
