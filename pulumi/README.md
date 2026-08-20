# Infraestrutura AWS (VPC + EC2) via Pulumi

Programa Pulumi em Python que provisiona uma VPC com subnet pública e uma instância EC2 (`t3.micro`, elegível ao free tier) para acesso remoto via SSH.

## Recursos provisionados

- **VPC** (`10.0.0.0/16`) com DNS habilitado.
- **Internet Gateway** anexado à VPC.
- **Subnet pública** (`10.0.1.0/24`, `sa-east-1a`) com atribuição automática de IP público.
- **Route table** pública, roteando `0.0.0.0/0` para o Internet Gateway.
- **Security group** liberando entrada em `22` (SSH), `80` (HTTP) e `443` (HTTPS), e toda saída.
- **Par de chaves SSH** (`tls.PrivateKey` + `ec2.KeyPair`), gerado automaticamente pelo Pulumi.
- **Instância EC2** `t3.micro` com Amazon Linux 2023 (AMI mais recente), na subnet pública, usando o par de chaves gerado.

## Pré-requisitos

- Conta AWS com permissões para criar recursos de VPC, EC2 e chaves (`ec2:*`).
- Credenciais AWS configuradas no ambiente (AWS CLI, variáveis de ambiente ou similar).
- Pulumi CLI instalado e autenticado (`pulumi login`).
- Python 3.12+ e [`uv`](https://docs.astral.sh/uv/) instalados.

## Configuração

Região definida em [Pulumi.dev.yaml](Pulumi.dev.yaml):

```yaml
config:
  aws:region: sa-east-1
```

Para alterar a região:

```bash
pulumi config set aws:region <regiao>
```

## Deploy

1. Instale as dependências do projeto:
   ```bash
   uv sync
   ```
2. Ative o ambiente virtual:
   ```bash
   source .venv/bin/activate
   ```
3. Selecione a stack (crie caso ainda não exista):
   ```bash
   pulumi stack select dev
   ```
4. Visualize as mudanças planejadas:
   ```bash
   pulumi preview
   ```
5. Aplique o deploy:
   ```bash
   pulumi up
   ```
6. Para destruir os recursos quando não forem mais necessários:
   ```bash
   pulumi destroy
   ```

## Outputs

Após o `pulumi up`, a stack exporta:

- `vpc_id` — ID da VPC criada.
- `public_subnet_id` — ID da subnet pública.
- `security_group_id` — ID do security group.
- `instance_id` — ID da instância EC2.
- `instance_public_ip` — IP público da instância.
- `key_pair_name` — nome do par de chaves associado à instância.
- `ssh_private_key` — chave privada SSH (secreta).

Recupere os outputs com:

```bash
pulumi stack output instance_public_ip
```

## Acesso via SSH

A chave privada é exportada como _secret_ e não aparece em texto claro nos logs do Pulumi. Para recuperá-la e conectar na instância:

```bash
pulumi stack output ssh_private_key --show-secrets > key.pem
chmod 400 key.pem
ssh -i key.pem ec2-user@$(pulumi stack output instance_public_ip)
```

## Ajuda

- Documentação do Pulumi: https://www.pulumi.com/docs/
- Pulumi AWS SDK: https://www.pulumi.com/registry/packages/aws/
