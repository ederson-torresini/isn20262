# Execução local com AWS SAM

Usa o mesmo código da Lambda (`../pulumi/lanchonetes`) com DynamoDB Local.

```bash
cd aws-sam
docker compose up -d                 # DynamoDB Local (rede sam-local)
uv pip install boto3
python seed.py                       # cria tabela e dados (requer boto3)
sam build
sam local start-api --env-vars env.json --add-host host.docker.internal:host-gateway
```

Teste:

```bash
curl -X POST localhost:3000/lanchonetes-proximas \
  -d '{"latitude": -23.55, "longitude": -46.63, "limite": 3}'
```

Invocação direta:

```bash
sam local invoke LanchonetesProximas --env-vars env.json \
  --add-host host.docker.internal:host-gateway -e event.json
```
