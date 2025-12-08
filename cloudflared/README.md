# Cloudflare Tunnel Configuration

Este diretório contém a configuração do Cloudflare Tunnel para expor o nginx através do Cloudflare, sem necessidade de expor portas publicamente no host.

## Pré-requisitos

1. Conta no Cloudflare com um domínio gerenciado
2. Acesso ao Cloudflare Dashboard
3. Permissões para criar e gerenciar Tunnels

## Métodos de Configuração

Existem duas formas de configurar o Cloudflare Tunnel:

### Método 1: Token-based (Recomendado para setup rápido)

Este método usa um token de autenticação único que pode ser gerado no Cloudflare Dashboard.

#### Passos:

1. Acesse o [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Vá para **Zero Trust** > **Networks** > **Tunnels**
3. Clique em **Create a tunnel**
4. Selecione **Cloudflared**
5. Escolha um nome para o tunnel (ex: `my-tunnel`)
6. Após criar, você verá um token. Copie este token
7. Adicione o token no arquivo `.env` na raiz do projeto:
   ```bash
   CLOUDFLARE_TUNNEL_TOKEN=seu_token_aqui
   ```
8. Configure o hostname no Cloudflare Dashboard (DNS > Records) criando um CNAME apontando para o tunnel

#### Configuração (Método 1):

1. Adicione o token no arquivo `.env`:
```bash
CLOUDFLARE_TUNNEL_TOKEN=seu_token_aqui
```

2. O token será usado automaticamente pelo docker-compose. Não é necessário configurar no config.yml quando usando variável de ambiente.

#### Exemplo de config.yml (se quiser usar arquivo de config em vez de env var):

```yaml
tunnel: <YOUR_TUNNEL_TOKEN>

ingress:
  - hostname: exemplo.seudominio.com
    service: http://nginx:80
  - service: http_status:404
```

### Método 2: Credentials File (Recomendado para produção)

Este método usa um arquivo de credenciais JSON que é mais seguro para ambientes de produção.

#### Passos:

1. Acesse o [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Vá para **Zero Trust** > **Networks** > **Tunnels**
3. Clique em **Create a tunnel**
4. Selecione **Cloudflared**
5. Escolha um nome para o tunnel (ex: `my-tunnel`)
6. Após criar, você verá um ID do tunnel (ex: `abc123def456`)
7. Clique no tunnel criado e vá para a aba **Configure**
8. Baixe o arquivo de credenciais (será um arquivo JSON)
9. Renomeie o arquivo para `<tunnel-id>.json` (ex: `abc123def456.json`)
10. Coloque o arquivo neste diretório (`cloudflared/`)
11. Edite `config.yml` e descomente a linha `credentials-file:` substituindo `<tunnel-id>` pelo ID do seu tunnel
12. Configure o hostname no ingress (substitua `<YOUR_DOMAIN>` pelo seu domínio)

#### Exemplo de config.yml (Método 2):

```yaml
credentials-file: /etc/cloudflared/abc123def456.json

ingress:
  - hostname: exemplo.seudominio.com
    service: http://nginx:80
  - service: http_status:404
```

## Configuração do Domínio

Após configurar o tunnel, você precisa configurar o DNS no Cloudflare:

1. No Cloudflare Dashboard, vá para **DNS** > **Records**
2. Adicione um registro CNAME:
   - **Name**: subdomínio (ex: `exemplo` para `exemplo.seudominio.com`)
   - **Target**: `<tunnel-id>.cfargotunnel.com` (o ID do seu tunnel)
   - **Proxy status**: Proxied (ícone laranja)

## Verificação

Após configurar tudo:

1. Inicie os serviços: `docker-compose -f docker-compose-less.yml up -d cloudflared`
2. Verifique os logs: `docker-compose -f docker-compose-less.yml logs cloudflared`
3. Você deve ver mensagens indicando que o tunnel está conectado
4. Acesse seu domínio no navegador - deve redirecionar para o nginx

## Troubleshooting

### Tunnel não conecta

- Verifique se o token ou arquivo de credenciais está correto
- Verifique os logs do container: `docker logs cloudflared`
- Certifique-se de que o nginx está rodando: `docker ps | grep nginx`

### DNS não resolve

- Verifique se o registro CNAME está configurado corretamente no Cloudflare
- Aguarde alguns minutos para a propagação do DNS
- Verifique se o proxy está ativado (ícone laranja) no registro DNS

## Referências

- [Documentação oficial do Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Guia de configuração do Cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide/)

