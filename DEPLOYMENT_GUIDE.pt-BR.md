# 🚀 Guia de Deploy - React Estático + Lambda Híbrido

## ⚡ Quick Start (5 minutos)

```bash
# 1. Instalar dependências (primeira vez)
cd 3-pulumi
pip install -r requirements.txt  # Pulumi dependencies
pulumi login  # Autenticar com Pulumi

# 2. Deploy
pulumi up  # Escolher stack: dev (padrão)

# 3. Acessar
pulumi stack output  # Ver URLs
# Abrir no browser: https://cloudfront-url/
```

## 📋 Pré-requisitos

✅ AWS CLI configurado (`aws configure`)
✅ Pulumi CLI instalado (`brew install pulumi` ou `choco install pulumi`)
✅ Python 3.10+ instalado
✅ Node.js 18+ instalado (`node -v`)
✅ Repositório clonado

## 🔄 Fluxo de Deploy

### Dev Stack (Recomendado para começar)

```bash
cd 3-pulumi

# 1. Preview (ver o que será criado)
pulumi preview --stack dev

# 2. Deploy
pulumi up --stack dev
# → Escolher "details" para ver progresso
# → Confirmar com "yes"

# 3. Resultados
pulumi stack output --stack dev
# Outputs:
#   api_url: https://xxx.execute-api.us-east-1.amazonaws.com
#   cloudfront_url: https://dxxx.cloudfront.net
#   s3_bucket: banheiros-web-dev
```

### Production Stack (Com SSL + DNS)

```bash
# Pré-requisito: Domínio registrado no Route53

cd 3-pulumi

# 1. Preview
pulumi preview --stack prod

# 2. Deploy
pulumi up --stack prod
# → Aguardar ~5-10 minutos
# → CloudFront + Route53 + SSL

# 3. Validar
pulumi stack output --stack prod
# Outputs:
#   domain: banheiros.seu-dominio.com
#   cloudfront_url: https://dxxx.cloudfront.net
```

## 📊 Depois do Deploy

### Testar Acesso

```bash
# 1. Frontend (React)
curl -v https://cloudfront-url/
# Esperado: HTML index.html (200 OK)

# 2. API GET
curl https://cloudfront-url/banheiros
# Esperado: Array JSON com banheiros

# 3. API POST
curl -X POST https://cloudfront-url/banheiros \
  -H "Content-Type: application/json" \
  -d '{"latitude": -23.55, "longitude": -46.63, "name": "Teste"}'
# Esperado: { "id": "...", "createdAt": "..." }

# 4. Logs Lambda
aws logs tail /aws/lambda/banheiros-get --follow
aws logs tail /aws/lambda/banheiros-post --follow
```

### Validar Cache

```bash
# S3 public?
aws s3api get-bucket-acl s3://banheiros-web
# Esperado: Private (sem PublicRead)

# CloudFront configurado?
aws cloudfront get-distribution --id XXXXX | grep -A5 Origins

# Cache funcionando?
curl -v https://cloudfront-url/ | grep -i cache-control
# Esperado: Cache-Control: no-cache (index.html) ou max-age=3600 (assets)
```

## 🔄 Atualizar Aplicação

### Workflow de Atualização

```bash
# 1. Editar código React
vim 3-pulumi/web-react/src/App.jsx

# 2. Testar localmente
cd 3-pulumi/web-react
npm run dev  # Hot reload

# 3. Build
npm run build  # Verifica erros

# 4. Deploy
cd ..
pulumi up --stack dev
# → Pulumi fará: npm run build + S3 upload + CloudFront invalidation

# 5. Verificar
sleep 60  # Aguardar propagação CloudFront
curl -v https://cloudfront-url/
```

## 🛠️ Troubleshooting

### Erro: "AWS credentials not found"
```bash
# Solução: Configurar AWS
aws configure
# Preencher: Access Key ID, Secret Access Key, Region (us-east-1)
```

### Erro: "Pulumi not installed"
```bash
# Solução: Instalar
curl -fsSL https://get.pulumi.com | sh
pulumi version
```

### S3 upload falha
```bash
# Verificar bucket
aws s3 ls s3://banheiros-web

# Verificar permissões IAM
aws iam get-role --role-name banheiros-web-role

# Logs Pulumi
pulumi logs --follow --stack dev
```

### CloudFront mostra erro 403 (Forbidden)
```bash
# Verificar origin
aws cloudfront get-distribution --id XXXXX | jq '.Distribution.DistributionConfig.Origins'

# Verificar bucket policy
aws s3api get-bucket-policy s3://banheiros-web

# Invalidar cache
aws cloudfront create-invalidation --distribution-id XXXXX --paths "/*"
```

### Requisição lenta
```bash
# Verificar cache headers
curl -v -I https://cloudfront-url/assets/index-xxx.js | grep -i cache-control

# Ver comportamento cache no code
# Em: 3-pulumi/__main__.py, linhas ~220-240
```

## 📉 Monitoramento

### Logs em Tempo Real

```bash
# Frontend (CDN)
aws cloudfront get-distribution-statistics --distribution-id XXXXX

# Lambda GET
aws logs tail /aws/lambda/banheiros-get --follow --format short

# Lambda POST
aws logs tail /aws/lambda/banheiros-post --follow --format short

# DynamoDB
aws dynamodb scan --table-name banheiros
```

### Métricas CloudWatch

```bash
# CPU Lambda
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=banheiros-get \
  --start-time 2026-11-16T00:00:00Z \
  --end-time 2026-11-17T00:00:00Z \
  --period 300 \
  --statistics Average

# Requisições CloudFront
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name Requests \
  --dimensions Name=DistributionId,Value=XXXXX \
  --start-time 2026-11-16T00:00:00Z \
  --end-time 2026-11-17T00:00:00Z \
  --period 300 \
  --statistics Sum
```

## 🧹 Cleanup

### Deletar Resources (Reverter Deploy)

```bash
# 1. Listar o que será deletado
pulumi destroy --stack dev --show

# 2. Confirmar deleção
pulumi destroy --stack dev
# → Escolher "yes"
# → Aguardar ~2-3 minutos

# 3. Verificar
aws s3 ls | grep banheiros  # Deve estar vazio
aws cloudfront list-distributions  # Deve estar vazio
aws lambda list-functions  # Deve estar vazio
```

**Aviso**: Isso **não** deleta o stack do Pulumi, apenas os recursos AWS.

### Deletar Stack Pulumi

```bash
# CUIDADO: Isso é irreversível!

# 1. Remover do backend Pulumi
pulumi stack rm dev
# → Confirmar: yes

# 2. Listar stacks restantes
pulumi stack ls
```

## 📚 Referências Rápidas

### Comandos Pulumi Essenciais

```bash
# Status
pulumi stack ls
pulumi stack select dev
pulumi stack output

# Deploy
pulumi preview
pulumi up --yes  # Skip confirmation
pulumi destroy

# Debugging
pulumi logs --follow --stack dev
pulumi refresh  # Sincronizar com AWS
pulumi cancel  # Parar deploy em andamento

# Configuração
pulumi config set aws:region us-east-1
pulumi config show  # Ver secrets (não-sensíveis)
```

### Comandos AWS Essenciais

```bash
# S3
aws s3 ls s3://banheiros-web
aws s3 cp index.html s3://banheiros-web/
aws s3 sync web-react/dist/ s3://banheiros-web/

# CloudFront
aws cloudfront get-distribution --id XXXXX
aws cloudfront create-invalidation --distribution-id XXXXX --paths "/*"
aws cloudfront get-invalidation --distribution-id XXXXX --id INVALIDATION-ID

# Lambda
aws lambda invoke --function-name banheiros-get response.json
aws logs tail /aws/lambda/banheiros-get --follow

# DynamoDB
aws dynamodb scan --table-name banheiros
aws dynamodb query --table-name banheiros --key-condition-expression "id = :id" --expression-attribute-values '{":id": {"S": "123"}}'
```

## 🎯 Checklist de Deploy

```
PRÉ-DEPLOY
  [ ] AWS credentials configurado (aws configure)
  [ ] Pulumi login done (pulumi login)
  [ ] npm install completo (web-react/node_modules/)
  [ ] npm run build testado localmente
  [ ] Código Python validado (python3 -m py_compile __main__.py)

DURANTE
  [ ] pulumi preview rodou sem erros
  [ ] pulumi up confirmado
  [ ] Aguardar ~5 minutos para deploy
  [ ] Sem erros em Pulumi logs

PÓS-DEPLOY
  [ ] pulumi stack output mostra URLs
  [ ] curl no /banheiros retorna dados
  [ ] curl no / retorna index.html
  [ ] CloudFront mostra 2 origins
  [ ] S3 bucket está privado
  [ ] Lambda IAM roles estão corretos
  [ ] Logs não mostram erros

VALIDAÇÃO
  [ ] Website acessível via URL
  [ ] Mapa carrega no navegador
  [ ] Formulário funciona (POST)
  [ ] Cache headers corretos
  [ ] Performance aceitável
```

## 🆘 Support

### Documentação Completa

Consulte os arquivos em `3-pulumi/`:
- `START_HERE.md` - Overview completo
- `ARCHITECTURE.md` - Arquitetura detalhada
- `MIGRATION.md` - Guia de migração
- `CHECKLIST.md` - Validação pré/pós
- `README_IMPLEMENTATION.md` - Detalhes técnicos

### Contato

Para problemas específicos:
1. Verificar `pulumi logs --follow`
2. Verificar `aws logs`
3. Consultar documentação
4. Abrir issue no GitHub

---

**Last Updated**: 2026-11-16
**Version**: 1.0.0
**Status**: ✅ Production Ready
