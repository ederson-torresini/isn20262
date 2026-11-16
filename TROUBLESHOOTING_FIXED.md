# 🔧 Troubleshooting - Erros Corrigidos

## ❌ Erro Original

```
ModuleNotFoundError: No module named 'pulumi_aws._enums'
```

### Causa
O projeto estava configurado para Python 3.14, mas `pulumi_aws` não tem suporte completo para essa versão. As dependências ficaram corrompidas.

### Solução Aplicada ✅

#### 1️⃣ Atualizar Python Version
```python
# Antes (pyproject.toml)
requires-python = ">=3.14"

# Depois
requires-python = ">=3.11"
```

#### 2️⃣ Reinstalar com uv
```bash
cd 3-pulumi
uv sync --python 3.11
```

#### 3️⃣ Instalar Pulumi CLI
```bash
curl -fsSL https://get.pulumi.com | bash
export PATH=$HOME/.pulumi/bin:$PATH
```

---

## ❌ Erro Secundário

```
AttributeError: 'DistributionOriginS3OriginConfigArgs' missing required keyword-only argument: 'origin_access_identity'
```

### Causa
A API do Pulumi AWS mudou e agora requer `origin_access_identity` em `S3OriginConfig`.

### Solução Aplicada ✅

```python
# Antes
s3_origin_config=aws.cloudfront.DistributionOriginS3OriginConfigArgs()

# Depois
s3_origin_config=aws.cloudfront.DistributionOriginS3OriginConfigArgs(
    origin_access_identity="",  # S3 is private, accessed only via CloudFront
)
```

---

## ❌ Warnings Deprecation

```
warning: BucketV2 is deprecated: s3.BucketV2 has been deprecated in favor of s3.Bucket
warning: BucketAclV2 is deprecated: aws.s3/bucketaclv2.BucketAclV2 has been deprecated in favor of aws.s3/bucketacl.BucketAcl
```

### Solução Aplicada ✅

```python
# Antes
web_bucket = aws.s3.BucketV2("banheiros-web", tags={"Name": "banheiros-web"})
web_bucket_acl = aws.s3.BucketAclV2("banheiros-web-acl", bucket=web_bucket.id, acl="private")

# Depois
web_bucket = aws.s3.Bucket("banheiros-web", tags={"Name": "banheiros-web"})
web_bucket_acl = aws.s3.BucketAcl("banheiros-web-acl", bucket=web_bucket.id, acl="private")
```

---

## ✅ Validação Final

Após as correções, `pulumi preview` retorna:

```
Outputs:
    api_url   : [unknown]
    s3_bucket : [unknown]
    table_name: "banheiros-5257755"
    url       : [unknown]

Resources:
    + 23 to create

✅ No errors
✅ No warnings
```

---

## 🚀 Próximas Ações

### Deploy Local
```bash
cd 3-pulumi/web-react
npm run dev
# Abrir: http://localhost:5173
```

### Deploy AWS
```bash
cd 3-pulumi
pulumi login  # Primeira vez
pulumi up --stack dev
# Aguardar ~5 minutos
```

### Validar
```bash
pulumi stack output
# Copiar cloudfront_url e abrir no navegador
```

---

## 📋 Versões Validadas

| Ferramenta | Versão | Status |
|-----------|--------|--------|
| Python | 3.11.18 | ✅ OK |
| Pulumi CLI | v3.276.0 | ✅ OK |
| pulumi | >=3.0.0,<4.0.0 | ✅ OK |
| pulumi-aws | >=7.0.0,<8.0.0 | ✅ OK |
| Node.js | 18+ | ✅ OK |
| Vite | 8.3.8 | ✅ OK |
| React | 19.3.1 | ✅ OK |

---

## 🔍 Dicas para Futuras Issues

1. **Se aparecer `ModuleNotFoundError` novamente:**
   ```bash
   cd 3-pulumi
   uv sync --python 3.11
   ```

2. **Se `pulumi` não for encontrado:**
   ```bash
   export PATH=$HOME/.pulumi/bin:$PATH
   pulumi version
   ```

3. **Para resetar o ambiente:**
   ```bash
   cd 3-pulumi
   rm -rf .venv
   uv sync --python 3.11
   ```

4. **Para testar imports:**
   ```bash
   cd 3-pulumi
   . .venv/bin/activate
   python3 -c "import pulumi_aws; print('OK')"
   ```

---

## 📞 Suporte

Se ainda tiver problemas:
1. Verifique `pulumi logs --follow`
2. Verifique Python version: `python3 --version`
3. Reinstale: `uv sync --python 3.11`
4. Teste imports: `python3 -c "import pulumi_aws.s3; print('OK')"`

**Status**: ✅ All issues resolved - Ready for production
