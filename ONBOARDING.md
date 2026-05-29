# Onboarding de atletas — Flat & Furious

## Link de autorizacao Strava

Envie a cada membro (substitua `CLIENT_ID` e `REDIRECT_URI` pelos do seu app):

```
https://www.strava.com/oauth/authorize?client_id=CLIENT_ID&response_type=code&redirect_uri=http://auth.flatandfurious/&approval_prompt=force&scope=activity:read_all,profile:read_all
```

O `redirect_uri` deve ser **exatamente** `http://auth.flatandfurious/` (como no app Strava).

O atleta autoriza e recebe uma URL de redirecionamento contendo `code=...`.

## Registrar o token

### Opcao A — Local

```bash
python -m flatfurious auth --code "http://auth.flatandfurious/?code=XXXX&scope=..."
```

Ou registre varios de uma vez (arquivo com uma URL por linha):

```bash
python scripts/register_from_file.py data/pending_auth_urls.txt
```

**Atencao:** cada `code` so funciona **uma vez** e expira em poucos minutos. Se falhar, peca ao membro para autorizar de novo.

### Opcao B — GitHub Actions

1. Repositorio **privado** com secrets `CLIENT_ID` e `CLIENT_SECRET` configurados.
2. Actions > **Register Strava athlete** > Run workflow.
3. Cole o `auth_code` (code ou URL completa).

O workflow atualiza `data/tokens_athletes.csv` automaticamente.

## Apos registrar todos

1. Rode `python -m flatfurious sync` localmente ou aguarde o workflow **Daily Strava sync**.
2. No dia 1 do mes, o workflow **Monthly report** gera relatorio, site e `whatsapp.txt`.

## Checklist

- [ ] Repositório GitHub privado
- [ ] Secrets `CLIENT_ID` e `CLIENT_SECRET`
- [ ] Variable `SITE_BASE_URL` (opcional)
- [ ] GitHub Pages habilitado (Source: GitHub Actions)
- [ ] Todos os membros registrados via `auth`
- [ ] Primeiro `sync` concluido com sucesso
