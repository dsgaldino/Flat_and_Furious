# Publicar no GitHub (GitHub Desktop) — 3 passos

O commit das paginas `join.html` e `strava/callback.html` **ja esta feito** no seu PC.
Falta apenas enviar para o GitHub.

## Passo 1 — Abrir o projeto

1. Abra **GitHub Desktop**
2. **File → Add local repository**
3. Pasta: `C:\Users\dsgal\Documents\GitHub\Flat_and_Furious`
4. Se pedir, confirme **create a repository**

## Passo 2 — Repositório remoto

Se aparecer **"No remote"** ou push falhar:

1. **Repository → Repository settings** (ou Publish repository)
2. Nome: `Flat_and_Furious`
3. Conta: sua conta GitHub (ex. `dsgaldino`)
4. Marque **Keep this code private**
5. **Publish repository** ou **Save**

URL esperada: `https://github.com/dsgaldino/Flat_and_Furious`  
(Se seu usuario for outro, use o seu — deve bater com `dsgaldino.github.io` no Pages.)

## Passo 3 — Push

1. Na lista de changes, deve aparecer o commit  
   `Add Strava onboarding pages for GitHub Pages (join + callback)`  
   (se ainda houver arquivos unstaged, pode ignorar por agora — o site ja esta no commit.)
2. Clique **Push origin** (canto superior direito)

## Passo 4 — GitHub Pages (uma vez no browser)

1. https://github.com/dsgaldino/Flat_and_Furious/settings/pages  
2. **Build and deployment → Source:** **GitHub Actions**
3. Aba **Actions** → workflow **Deploy GitHub Pages** → aguarde verde

## Testar

- https://dsgaldino.github.io/Flat_and_Furious/join.html

Strava: callback domain `dsgaldino.github.io` (voce ja trocou).
