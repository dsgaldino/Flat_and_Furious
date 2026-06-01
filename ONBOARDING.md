# Onboarding de atletas — Flat & Furious

## Para o administrador (uma vez)

1. No [Strava API](https://www.strava.com/settings/api), app **Flat and Furious**:
   - **Authorization Callback Domain:** `dsgaldino.github.io`
   - (Antigo `auth.flatandfurious` não use mais.)
2. No `.env` do repo:
   ```env
   STRAVA_REDIRECT_URI=https://dsgaldino.github.io/Flat_and_Furious/strava/callback.html
   ```
3. Faça deploy do site (`site/public`) no GitHub Pages (push ou workflow).
4. (Opcional) Em `site/public/assets/join.js`, defina `ADMIN_WHATSAPP` com seu número (ex. `31612345678`) para o botão WhatsApp ir direto para você.

---

## Link para enviar aos amigos

**Página de boas-vindas (recomendado):**

```
https://dsgaldino.github.io/Flat_and_Furious/join.html
```

Eles leem as diretrizes, clicam em **Autorizar no Strava** e, ao final, veem uma página de **obrigado** (sem erro no navegador).

---

## O que o amigo faz

1. Abre `join.html` no celular ou PC.
2. Lê as diretrizes do grupo.
3. Clica em **Autorizar no Strava** e confirma no Strava.
4. Na página de sucesso:
   - Clica em **Enviar no WhatsApp** (mensagem já vem com o link), **ou**
   - **Copiar link de confirmação** e te manda.

O `code` expira em poucos minutos — peça para enviar logo.

---

## O que você faz (por amigo)

Cole a URL que ele enviou (a página de callback completa):

```bash
python -m flatfurious auth --code "https://dsgaldino.github.io/Flat_and_Furious/strava/callback.html?code=..."
```

Ou vários de uma vez:

```bash
python scripts/register_from_file.py data/pending_auth_urls.txt
```

Depois:

```bash
python -m flatfurious sync --full
```

Confira `data/members.csv` (nome igual ao Strava + `group_join_date`).

---

## Link Strava direto (alternativa)

Só se não usar `join.html`:

```
https://www.strava.com/oauth/authorize?client_id=160663&response_type=code&redirect_uri=https://dsgaldino.github.io/Flat_and_Furious/strava/callback.html&approval_prompt=force&scope=activity:read_all,profile:read_all
```

O `redirect_uri` tem que ser **idêntico** em: link, `.env`, troca do `code` e app Strava.

---

## GitHub Actions (opcional)

Actions → **Register Strava athlete** → cole o `auth_code` ou URL completa.

---

## Checklist

- [ ] Callback domain no Strava: `dsgaldino.github.io`
- [ ] `STRAVA_REDIRECT_URI` no `.env` e GitHub Secrets
- [ ] `join.html` no ar (GitHub Pages)
- [ ] Membros em `data/members.csv`
- [ ] Tokens em `data/tokens_athletes.csv` via `auth`
- [ ] `python -m flatfurious sync --full` OK
