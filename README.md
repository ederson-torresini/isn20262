# ISN 2026.2

Projeto da disciplina ISN 75620501, edição 2026.2.

## Escolhas tecnológicas

- Nuvem: [AWS](https://aws.amazon.com)
- Ferramenta de IaC: [Pulumi](https://www.pulumi.com/) com [Python](https://www.pulumi.com/docs/iac/languages-sdks/python/)

## Preparação do ambiente

No serviço [IAM](https://console.aws.amazon.com/iam/):

1. Criar um [grupo de usuário](https://console.aws.amazon.com/iam#/groups).
1. Criar um [usuário](https://console.aws.amazon.com/iam#/users) e associá-lo ao grupo criado. Importante: esse usuário não deve ter acesso ao AWS Management Console.
1. Criar uma política de acordo com [iam-policy.json](iam-policy.json) e associá-la ao grupo criado.
1. De volta ao usuário criado, deve-se criar uma chave de acesso, a qual é composta por um identificador (`AWS_ACCESS_KEY_ID`) e a chave propriamente dita (`AWS_SECRET_ACCESS_KEY`).

No [GitHub Codespaces](https://github.com/settings/codespaces):

- `AWS_ACCESS_KEY_ID`: identificador da chave de acesso ao AWS.
- `AWS_SECRET_ACCESS_KEY`: chave de acesso ao AWS, propriamente dita.
- `AWS_DEFAULT_REGION`: região da AWS. Por convenção, na equipe será adotado por padrão São Paulo (`sa-east-1`).
- `PULUMI_ACCESS_TOKEN`: chave de acesso ao Pulumi.

Fonte:

- [Configuring environment variables for the AWS CLI](https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-envvars.html)
- [pulumi login | CLI commands](https://www.pulumi.com/docs/iac/cli/commands/pulumi_login/).

### A executar em cada codespace

```bash
make install
```

## Referências

### Livros

- [Clean Architecture](http://biblioteca.ifsc.edu.br/index.asp?codigo_sophia=78771)
- [Software Architecture Patterns](https://drive.google.com/file/d/13ZDFWUOvS8e7vyTWUE6gmpxmCQK9sonu/view?usp=drive_link)

### Sites

História:

- [Éric Lévénez's site](https://levenez.com/)

Computação em nuvem:

- [Cloud Native Computing Foundation](https://cncf.io)
- [The New Stack](https://thenewstack.io/)
- [The NIST Definition of Cloud Computing](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-145.pdf)

Cultura DevOps:

- [devopsdays](https://devopsdays.org/)
- [Stack Overflow Survey 2025](https://survey.stackoverflow.co/2025)
- [The Twelve-Factor App](https://12factor.net/)

AWS:

- [AWS: Regiões e zonas de disponibilidade](https://aws.amazon.com/pt/about-aws/global-infrastructure/regions_az/)
- [Gartner | Quadrante Mágico de 2025 para Serviços estratégicos de plataforma de nuvem](https://aws.amazon.com/pt/resources/analyst-reports/gartner/magic-quadrant-for-strategic-cloud-platform-services-mq/)
