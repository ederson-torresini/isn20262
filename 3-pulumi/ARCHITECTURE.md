# Arquitetura Atualizada: React + S3 + API Gateway + Lambda

## 📋 Resumo da Migração

A aplicação "web" foi completamente refatorada:

| Aspecto        | Antes                         | Depois                 |
| -------------- | ----------------------------- | ---------------------- |
| **Frontend**   | Lambda Node.js + Express      | React Estático (Vite)  |
| **Hospedagem** | Lambda (serverless)           | S3 (storage)           |
| **Roteamento** | API Gateway (todos em Lambda) | API Gateway (híbrido)  |
| **Cache**      | CloudFront                    | CloudFront (melhorado) |
| **Build**      | npm ci --omit=dev             | npm run build (dist/)  |

## 🏗️ Arquitetura Final

```
                     ┌─ INTERNET ─┐
                     │             │
                     ▼             ▼
            ┌──────────────────────────────┐
            │        CloudFront CDN        │
            │   (HTTPS + Cache Global)     │
            └──────────┬───────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
    ┌────────────────┐          ┌────────────┐
    │  API Gateway   │          │  API Gw.   │
    │  (default)     │          │  (/*path)  │
    │  PUT/POST/GET  │          │  (GET only)│
    └────────┬───────┘          └────────┬───┘
             │                           │
        ┌────┴──────────────────┐        │
        │                       │        │
        ▼                       ▼        ▼
    ┌────────────┐      ┌────────────┐ ┌──────────┐
    │ Lambda GET │      │ Lambda POST│ │S3 (Files)│
    │ /banheiros │      │ /banheiros │ │  (React) │
    └────┬───────┘      └────┬───────┘ └──────────┘
         │                   │
         └───────────┬───────┘
                     │
                     ▼
            ┌──────────────────────┐
            │   DynamoDB Table     │
            │   (banheiros)        │
            └──────────────────────┘
```

## 📁 Estrutura de Arquivos

```
3-pulumi/
├── __main__.py                 ← Config Pulumi (Python)
├── MIGRATION.md               ← Esta documentação
├── web/                       ⚠️  Legacy (pode remover)
│   ├── package.json
│   └── index.js
│
├── web-react/                 ✨ NOVO
│   ├── src/
│   │   ├── App.jsx           ← Componente principal
│   │   ├── App.css           ← Estilos
│   │   └── main.jsx
│   ├── public/
│   ├── dist/                 ← Build output (enviado ao S3)
│   ├── package.json
│   ├── vite.config.js
│   └── ...
│
├── banheiros_get/            ← Lambda GET (mantido)
├── banheiros_post/           ← Lambda POST (mantido)
├── Pulumi.yaml
├── Pulumi.dev.yaml
└── .gitignore
```

## 🔀 Fluxo de Requisições

### 1️⃣ GET / (Página Principal)

```
Client → CloudFront → API Gateway (default) → S3 → index.html
                                                  → React.js
                                                  → Leaflet.js
```

### 2️⃣ GET /assets/\* (Arquivos Estáticos)

```
Client → CloudFront → API Gateway (/*path) → S3 → JS/CSS/SVG
```

**Cache Policy**: `Managed-CachingOptimized` (long-lived cache)

### 3️⃣ GET /banheiros (API Lambda)

```
Client → CloudFront → API Gateway (/banheiros) → Lambda → DynamoDB
                                                  │
                                                  → Scan
```

**Cache Policy**: `Managed-CachingDisabled` (no cache)

### 4️⃣ POST /banheiros (Cadastro)

```
Client → CloudFront → API Gateway (/banheiros POST) → Lambda → DynamoDB
                                                        │
                                                        → BatchWriteItem
```

## 🚀 Deployment

### Local (Dev)

```bash
cd 3-pulumi/web-react
npm run dev  # Hot reload em http://localhost:5173
```

### Production (AWS)

```bash
cd 3-pulumi

# Stack development (sem SSL/Route53)
pulumi up  # Acesso via CloudFront domain

# Stack production (com SSL + domínio)
pulumi --stack prod up  # Acesso via negoci.online
```

### O que o Pulumi Faz

1. ✅ Cria bucket S3 privado
2. ✅ Compila React (`npm run build`)
3. ✅ Faz upload dos arquivos estáticos
4. ✅ Cria funções Lambda (GET/POST)
5. ✅ Configura API Gateway com roteamento híbrido
6. ✅ Configura CloudFront com múltiplos origins
7. ✅ (Prod) Cria certificado ACM + registros Route53

## 🔑 Variáveis de Ambiente (React)

No `web-react/vite.config.js`, as variáveis são:

- `VITE_API_GET_URL`: `/banheiros` (default)
- `VITE_API_POST_URL`: `/banheiros` (default)

Roteamento **relativo** = funciona em qualquer domínio (dev/prod)

## ✅ Validação Pós-Deploy

### 1. S3 tem os arquivos?

```bash
aws s3 ls s3://banheiros-web/
# Deve listar: index.html, assets/index-*.js, assets/index-*.css
```

### 2. CloudFront carrega a página?

```bash
export CF_URL=$(pulumi stack output url)
curl -v "$CF_URL"  # 200 + HTML
curl -v "$CF_URL/assets/index-*.js" # 200 + JS
```

### 3. API Lambda funciona?

```bash
export API_URL=$(pulumi stack output api_url)
curl -v "$API_URL/banheiros"  # 200 + JSON
curl -X POST "$API_URL/banheiros" \
  -H 'Content-Type: application/json' \
  -d '{"latitude":-27.59,"longitude":-48.55,"categorias":["unissex"]}'
```

### 4. Interação completa (browser)

```bash
export URL=$(pulumi stack output url)
open "$URL"  # Ou xdg-open (Linux) / echo (Windows)
```

Deve aparecer:

- Mapa Leaflet (carregado)
- Marcadores (GET /banheiros)
- Formulário de cadastro (POST /banheiros)

## 🛠️ Troubleshooting

| Problema               | Solução                                      |
| ---------------------- | -------------------------------------------- |
| S3 403 (access denied) | Verificar bucket ACL + Cloud Front OAI       |
| React não carrega      | Verificar `dist/` foi criado (npm run build) |
| API retorna 404        | Verificar Lambda environment + IAM DynamoDB  |
| Cache incorreto        | Limpar CloudFront + browser cache            |
| Domínio não resolve    | Aguardar Route53 + DNS propagação (~5min)    |

## 📊 Comparação: Lambda vs S3

| Critério           | Lambda      | S3                        |
| ------------------ | ----------- | ------------------------- |
| **Latência**       | 100-500ms   | 10-100ms (com CloudFront) |
| **Custo**          | $/invocação | $/GB armazenado           |
| **Escalabilidade** | Automática  | Ilimitada                 |
| **Logs**           | CloudWatch  | CloudFront logs           |
| **Cache**          | CloudFront  | CloudFront nativo         |

**Resultado**: S3 é 5-10x mais rápido para conteúdo estático

## 🔄 Futuras Melhorias

- [ ] Adicionar SPA routing (React Router + CloudFront error handling)
- [ ] Implementar CI/CD (GitHub Actions → Pulumi)
- [ ] Monitoramento (CloudWatch + SNS)
- [ ] Analytics (CloudFront logs → S3 → Athena)
- [ ] Versioning de assets (hash nos nomes)
- [ ] Environment-specific builds (.env.production)

## 📚 Referências

- Pulumi AWS: https://www.pulumi.com/registry/packages/aws/
- Vite: https://vitejs.dev/guide/
- React: https://react.dev/
- Leaflet: https://leafletjs.com/
- CloudFront caching: https://docs.aws.amazon.com/cloudfront/latest/developerguide/cache-behavior.html
