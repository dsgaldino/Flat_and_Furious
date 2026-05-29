"""Fun facts generator for monthly summaries."""

import random


def gerar_curiosidades(dist_km: float, mes_ano: str) -> list[str]:
    altura_garrafa = 0.25
    volume_lata = 0.00033
    volume_piscina = 2500
    altura_eiffel = 330
    altura_cristo = 38
    altura_empire = 443
    altura_monte_everest = 8848
    circunf_pizza = 0.94
    tam_formiga = 0.01
    tam_passo_humano = 0.75
    circunferencia_terra = 40075

    frases_possiveis = []
    total_garrafas = dist_km * 1000 / altura_garrafa
    eiffels = total_garrafas / (altura_eiffel / altura_garrafa)

    frases_possiveis.append(
        f"Se empilhassemos garrafas de Grolsch com a distancia pedalada em {mes_ano}, "
        f"daria pra montar {eiffels:.1f} Torres Eiffel."
    )

    volume_total = dist_km * 1000 * volume_lata
    piscinas = volume_total / volume_piscina
    frases_possiveis.append(
        f"Com as latas de Coca que equivalem a distancia pedalada em {mes_ano}, "
        f"daria pra encher {piscinas:.2f} piscinas olimpicas."
    )

    cristos = total_garrafas / (altura_cristo / altura_garrafa)
    frases_possiveis.append(
        f"Isso equivale a empilhar {cristos:.1f} Cristos Redentores em garrafas de cerveja."
    )

    empires = total_garrafas / (altura_empire / altura_garrafa)
    frases_possiveis.append(
        f"Foram o suficiente pra empilhar {empires:.1f} predios Empire State de garrafas."
    )

    everests = total_garrafas / (altura_monte_everest / altura_garrafa)
    frases_possiveis.append(
        f"Isso daria {everests:.1f} montes Everest empilhando garrafas de Grolsch."
    )

    voltas = dist_km / circunferencia_terra
    frases_possiveis.append(
        f"O grupo pedalou o equivalente a {voltas:.2%} de uma volta ao mundo."
    )

    pizzas = dist_km * 1000 / circunf_pizza
    frases_possiveis.append(
        f"Foram {int(pizzas):,} pizzas enfileiradas com 30cm de diametro."
    )

    formigas = dist_km * 1000 / tam_formiga
    frases_possiveis.append(
        f"Daria pra fazer uma fila com {int(formigas):,} formigas marchando sem parar."
    )

    passos = dist_km * 1000 / tam_passo_humano
    frases_possiveis.append(
        f"Seriam necessarios {int(passos):,} passos humanos pra percorrer essa distancia."
    )

    tam_lata = 0.115
    latas = dist_km * 1000 / tam_lata
    frases_possiveis.append(
        f"Seriam {int(latas):,} latas de Coca enfileiradas pelo chao."
    )

    return random.sample(frases_possiveis, min(2, len(frases_possiveis)))
