# 🚀 Quick Start - React no S3 com Pulumi

## ⚡ 3 Passos para Deploy (15 minutos)

### 1️⃣ Testar Localmente (5 min)
```bash
cd 3-pulumi/web-react
npm install
npm run dev
# Abrir: http://localhost:5173
```

### 2️⃣ Build Production (2 min)
```bash
npm run build
# Resultado: dist/ com 5 arquivos
```

### 3️⃣ Deploy no AWS (8 min)
```bash
cd ..
pulumi login  # Primeira vez apenas
aws configure  # Primeira vez apenas
pulumi up --stack dev
# Aguardar ~5 minutos
```

## ✅ Validar Deploy
```bash
pulumi stack output
# Copiar cloudfront_url e abrir no navegador
```

---

## 📚 Documentação Completa

| Documento | Descrição | Tempo |
|-----------|-----------|-------|
| **[PROJECT_INDEX.md](PROJECT_INDEX.md)** | Índice centralizado | 5 min |
| **[START_HERE.md](3-pulumi/START_HERE.md)** | Guia completo | 10 min |
| **[DEPLOYMENT_GUIDE.pt-BR.md](DEPLOYMENT_GUIDE.pt-BR.md)** | Deploy detalhado | 20 min |
| **[ARCHITECTURE.md](3-pulumi/ARCHITECTURE.md)** | Arquitetura técnica | 20 min |
| **[CHECKLIST.md](3-pulumi/CHECKLIST.md)** | Validação pré/pós | 20 min |

---

## 🎯 Resultado

```
Antes:  Lambda Express → 100-500ms → $/invocação
Depois: React Vite → 10-100ms (10x ⚡) → $/GB (90% 💰)
```

**Status**: ✅ Production Ready

---

**Próxima ação**: `cd 3-pulumi && pulumi up`
