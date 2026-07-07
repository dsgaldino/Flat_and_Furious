# Conectar o projeto ao GitHub

## 1. Criar o repositorio (se ainda nao existir)

1. Acesse https://github.com/new
2. Nome: `Flat_and_Furious` (ou o mesmo nome da pasta local)
3. Visibilidade: **Public** (tokens ficam fora do git — ver [PUBLIC_REPO.md](PUBLIC_REPO.md))
4. Nao marque README/gitignore (ja existem localmente)

## 2. Primeiro push (terminal na pasta do projeto)

Substitua `SEU_USUARIO` pelo seu usuario GitHub:

```powershell
cd "C:\Users\dsgal\Documents\GitHub\Flat_and_Furious"

git init
git branch -M main
git add .
git commit -m "Initial commit: pipeline Flat and Furious automatizado"

git remote add origin https://github.com/SEU_USUARIO/Flat_and_Furious.git
git push -u origin main
```

Se o repositorio remoto ja existir com commits, use antes do push:

```powershell
git pull origin main --rebase
```

## 3. Secrets do GitHub Actions

Em **Settings → Secrets and variables → Actions → New repository secret**:

| Nome | Valor |
|------|--------|
| `CLIENT_ID` | ID do app em https://www.strava.com/settings/api |
| `CLIENT_SECRET` | Client Secret (rotacione se ja vazou) |

Em **Variables** (opcional):

| Nome | Exemplo |
|------|---------|
| `SITE_BASE_URL` | `https://SEU_USUARIO.github.io/Flat_and_Furious` |

## 4. GitHub Pages

**Settings → Pages → Build and deployment → Source:** GitHub Actions.

O workflow `deploy_pages.yml` publica `site/public/` apos cada relatorio mensal.

## 5. Registrar atleta pelo GitHub (sem PC)

**Actions → Register Strava athlete → Run workflow** → cole a URL ou o `code`.

## 6. Testar automacao

| Acao | Onde |
|------|------|
| Sync manual | Actions → Daily Strava sync → Run workflow |
| Relatorio manual | Actions → Monthly report → Run workflow (campo month opcional) |

## Remote ja configurado localmente

O Git local ja foi inicializado com:

```text
origin  https://github.com/dsgal/Flat_and_Furious.git
```

Se seu usuario GitHub for outro, ajuste:

```powershell
git remote set-url origin https://github.com/SEU_USUARIO/Flat_and_Furious.git
```

**Importante:** crie o repositorio vazio no GitHub antes do primeiro `git push`. Se aparecer `Repository not found`, o repo ainda nao existe ou o nome/usuario esta errado.

Verifique com: `git remote -v`
