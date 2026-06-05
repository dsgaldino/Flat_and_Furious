# Junho/2026 — curiosidades (2) ✅ APROVADO

Semi-pronto em `reports/2026/06/` — curiosidades entram sozinhas quando houver km.

**Regra:** 2 curiosidades por mes.
- Curiosidade 1: rota famosa (**Cairo → Alexandria**, 220 km)
- Curiosidade 2: **cerveja** (garrafas no tempo pedalado; marca rotaciona por mes)

**Dados hoje (04/06):** 0 km · 0 pedaladas — exemplo abaixo usa numeros de **maio** so para mostrar o formato.

## Proposta para aprovar

1. Com {km} km, o pelotao faria Cairo → Alexandria ({vezes}x; trecho de 220 km).
2. Com {horas}h em movimento, daria pra beber {garrafas} garrafas de {cerveja} — uma a cada meia hora de estrada.

## Exemplo de redacao (formato, numeros de maio/2026)

1. Com 1439 km, o pelotao faria Cairo → Alexandria (6,5x; trecho de 220 km).
2. Com 72h em movimento, daria pra beber 145 garrafas de Hertog Jan — uma a cada meia hora de estrada.

*(Marca fixa para jun/2026: **Hertog Jan**; garrafas = 2x horas em movimento.)*

## No fechamento de junho

1. Atualizar dados Strava (`activities_formatted.csv`)
2. Rodar: `python -m flatfurious scaffold --through 2026-06 --no-migrate`

Gera automaticamente:
- Cur. 1: Cairo → Alexandria (rota de jun/2026)
- Cur. 2: garrafas de **Hertog Jan** (2x horas em movimento)
