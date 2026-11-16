# Migração: Lambda Web → React Estático no S3 com API Gateway

## Resumo das Mudanças

A aplicação "web" foi convertida de uma Lambda Node.js com Express para um site React estático hospedado no S3, com roteamento configurado no API Gateway.

### Arquitetura

```
┌─────────────────┐
│   CloudFront    │
└────────┬────────┘
         │
┌────────┴────────────────────┐
│   API Gateway (HTTP)        │
├────────┬────────────────────┤
│        │                    │
GET /    │   GET /banheiros   │
         │   POST /banheiros  │
         │                    │
     ┌───┴────┐           ┌───┴──────────┐
     │   S3   │           │   Lambdas    │
     │ (React)│           │  (Node.js)   │
     └────────┘           └──────────────┘
```

### Mudanças Realizadas

#### 1. Nova Aplicação React (`web-react/`)

- Criada com Vite + React 19
- Mantém a mesma funcionalidade: mapa Leaflet + formulário de cadastro
- Componente App.jsx com hooks (useState, useEffect)
- Integração com APIs Lambda via fetch
- Build estático: `npm run build` gera pasta `dist/`

#### 2. Publicação no S3 via Pulumi

- S3 bucket privado `banheiros-web` criado
- Arquivos estáticos (HTML, JS, CSS) enviados automaticamente
- Build React executado como parte do deploy Pulumi

#### 3. API Gateway - Roteamento Atualizado

- **GET /** → S3 (via integração AWS_PROXY com S3-proxy)
- **GET /{proxy+}** → S3 (arquivos estáticos: .js, .css, etc.)
- **GET /banheiros** → Lambda `banheiros-get`
- **POST /banheiros** → Lambda `banheiros-post`

#### 4. IAM Roles

- Novo role `apigateway-s3-role` permite API Gateway ler objetos do S3
- Role Lambda mantém acesso DynamoDB

#### 5. Lambda "web" Removida

- Eliminada função Lambda `banheiros-web`
- Express não é mais necessário

## Como Testar

### Local (Desenvolvimento)

```bash
cd 3-pulumi/web-react

# Dev server com hot reload
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

### Deployment com Pulumi

```bash
cd 3-pulumi

# Dev stack (CloudFront sem SSL)
pulumi up

# Prod stack (CloudFront + ACM + Route53)
pulumi up --stack prod
```

### Validação Pós-Deploy

1. **Verificar S3**

   ```bash
   aws s3 ls s3://banheiros-web/
   aws s3 cp s3://banheiros-web/index.html -
   ```

2. **Testar Roteamento**

   ```bash
   # Substituir <api-url> pela saída de: pulumi stack output api_url

   # Página estática (S3)
   curl -v <api-url>/
   curl -v <api-url>/assets/index-*.js

   # APIs Lambda
   curl -v <api-url>/banheiros
   curl -v -X POST <api-url>/banheiros \
     -H 'Content-Type: application/json' \
     -d '{"latitude": -27.59, "longitude": -48.55, "categorias": ["unissex"]}'
   ```

3. **CloudFront**
   ```bash
   pulumi stack output url
   ```

## Migrações Futuras (Opcional)

- **Cache headers**: Adicionar políticas de cache diferenciadas para .html vs assets
- **Error handling**: Configurar página de erro customizada no S3
- **Environment vars**: Usar `.env.production` no React build
- **Monitoramento**: CloudWatch logs para requisições S3

## Arquivos Alterados

| Arquivo       | Mudança                                                       |
| ------------- | ------------------------------------------------------------- |
| `__main__.py` | Config Pulumi: S3 bucket, build React, integração API Gateway |
| `web-react/`  | ✨ Nova aplicação React (Vite)                                |
| `web/`        | ⚠️ Pode ser removida (Lambda web descontinuada)               |

## Variáveis de Ambiente (React)

No `web-react/.env.production` (opcional):

```
VITE_API_GET_URL=/banheiros
VITE_API_POST_URL=/banheiros
```

Padrão: `/banheiros` (roteamento relativo)
