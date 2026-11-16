#!/bin/bash
# Setup Pulumi Project
# Usage: ./setup.sh

set -e

echo "🚀 Setup Pulumi Project - React + S3 + Lambda"
echo

cd "$(dirname "$0")/3-pulumi"

echo "1️⃣ Verificando Python 3.11..."
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 não encontrado"
    echo "Instalando..."
    apt-get update && apt-get install -y python3.11 python3.11-venv
fi
echo "✓ Python 3.11 OK"

echo
echo "2️⃣ Instalando/Atualizando dependências..."
uv sync --python 3.11
echo "✓ Dependências OK"

echo
echo "3️⃣ Verificando Pulumi CLI..."
if ! command -v pulumi &> /dev/null; then
    echo "Instalando Pulumi CLI..."
    curl -fsSL https://get.pulumi.com | bash
    export PATH=$HOME/.pulumi/bin:$PATH
fi
echo "✓ Pulumi CLI OK: $(pulumi version)"

echo
echo "4️⃣ Ativando venv..."
. .venv/bin/activate
echo "✓ venv ativado"

echo
echo "5️⃣ Testando imports..."
python3 << 'PYTHON'
try:
    import pulumi
    import pulumi_aws
    import pulumi_aws.s3
    print("✓ Todos os imports OK")
except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)
PYTHON

echo
echo "6️⃣ Rodando Pulumi preview..."
pulumi preview --stack dev 2>&1 | tail -20

echo
echo "✅ Setup Completo!"
echo
echo "Próximas ações:"
echo "  1. Testar localmente:"
echo "     cd web-react && npm run dev"
echo
echo "  2. Fazer deploy:"
echo "     pulumi up --stack dev"
echo
echo "  3. Validar:"
echo "     pulumi stack output"
echo

# Adicionar Pulumi ao PATH se necessário
if ! command -v pulumi &> /dev/null; then
    echo "⚠️ Adicionando Pulumi ao PATH..."
    export PATH=$HOME/.pulumi/bin:$PATH
    echo "export PATH=\$HOME/.pulumi/bin:\$PATH" >> ~/.bashrc
    echo "✓ Adicione 'export PATH=\$HOME/.pulumi/bin:\$PATH' ao seu ~/.bashrc"
fi
