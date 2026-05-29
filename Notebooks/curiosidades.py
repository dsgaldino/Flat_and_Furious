
import random

def gerar_curiosidades(dist_km, mes_ano):
    curiosidades = []

    altura_garrafa = 0.25  # m
    volume_lata = 0.00033  # m³
    volume_piscina = 2500  # m³
    altura_eiffel = 330
    altura_cristo = 38
    altura_empire = 443
    altura_monte_everest = 8848
    circunf_pizza = 0.94
    tam_formiga = 0.01
    tam_passo_humano = 0.75
    circunferencia_terra = 40075  # km

    frases_possiveis = []

    # 1. Torres Eiffel com garrafas empilhadas
    total_garrafas = dist_km * 1000 / altura_garrafa
    eiffels = total_garrafas / (altura_eiffel / altura_garrafa)
    frases_possiveis.append(
        f"🍺 Se empilhássemos garrafas de Grolsch com a distância pedalada em {mes_ano}, daria pra montar {eiffels:.1f} Torres Eiffel."
    )

    # 2. Piscinas olímpicas com latas de Coca-Cola
    volume_total = dist_km * 1000 * volume_lata
    piscinas = volume_total / volume_piscina
    frases_possiveis.append(
        f"🥤 Com as latas de Coca que equivalem à distância pedalada em {mes_ano}, daria pra encher {piscinas:.2f} piscinas olímpicas."
    )

    # 3. Torres do Cristo Redentor
    cristos = total_garrafas / (altura_cristo / altura_garrafa)
    frases_possiveis.append(
        f"🗿 Isso equivale a empilhar {cristos:.1f} Cristos Redentores em garrafas de cerveja."
    )

    # 4. Torres Empire State
    empires = total_garrafas / (altura_empire / altura_garrafa)
    frases_possiveis.append(
        f"🏙️ Foram o suficiente pra empilhar {empires:.1f} prédios Empire State de garrafas."
    )

    # 5. Monte Everest
    everests = total_garrafas / (altura_monte_everest / altura_garrafa)
    frases_possiveis.append(
        f"⛰️ Isso daria {everests:.1f} montes Everest empilhando garrafas de Grolsch."
    )

    # 6. Voltas na Terra
    voltas = dist_km / circunferencia_terra
    frases_possiveis.append(
        f"🌍 O grupo pedalou o equivalente a {voltas:.2%} de uma volta ao mundo."
    )

    # 7. Pizzas lado a lado
    pizzas = dist_km * 1000 / circunf_pizza
    frases_possiveis.append(
        f"🍕 Foram {int(pizzas):,} pizzas enfileiradas com 30cm de diâmetro."
    )

    # 8. Formigas marchando
    formigas = dist_km * 1000 / tam_formiga
    frases_possiveis.append(
        f"🐜 Daria pra fazer uma fila com {int(formigas):,} formigas marchando sem parar."
    )

    # 9. Passos humanos
    passos = dist_km * 1000 / tam_passo_humano
    frases_possiveis.append(
        f"🚶 Seriam necessários {int(passos):,} passos humanos pra percorrer essa distância."
    )

    # 10. Latas de Coca lado a lado (~11.5cm por lata)
    tam_lata = 0.115
    latas = dist_km * 1000 / tam_lata
    frases_possiveis.append(
        f"🥫 Seriam {int(latas):,} latas de Coca enfileiradas pelo chão."
    )

    # Seleciona 2 curiosidades aleatórias por mês
    return random.sample(frases_possiveis, 2)
