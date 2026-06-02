"""Auto-generated fun facts from monthly metrics (no static phrase file)."""

from __future__ import annotations

import hashlib
from typing import Callable

AROUND_EARTH_KM = 40075

# Real-world reference distances (km)
_REF = {
    "amsterdam_paris": 504,
    "enschede_utrecht": 120,
    "marco_zero": 42.195,
    "ultra_distance": 200,
}

# Curiosidades fixas por mes (ex.: janeiro/2026 usou Amsterdam-Paris so naquele relatorio)
MONTH_CURIOSITY_KEYS: dict[str, list[str]] = {
    "2026-01": ["enschede_koln", "amsterdam_paris"],
    "2026-02": ["maratona", "everest"],
}

# Nunca entram no sorteio automatico (confusas, numeros ridiculos ou repetitivas)
_AUTO_POOL_EXCLUDE = {
    "media_atleta",
    "piscinas",
    "pizzas",
    "formigas",
    "latas",
}


def _eligible_keys(ctx: Context, registry: dict[str, Callable[[Context], str | None]]) -> list[str]:
    """Curiosidades que fazem sentido com os dados do mes."""
    km = float(ctx["distance_km"])
    rides = int(ctx["ride_count"])
    elev = float(ctx.get("elevation_m", 0))

    rules: dict[str, bool] = {
        "maratona": km >= 1,
        "enschede_koln": km >= 1,
        "amsterdam_paris": km >= 1,
        "volta_mundo": km >= 80,
        "grolsch": km >= 80,
        "pedestre": km >= 80,
        "pedaladas_media": rides >= 1,
        "fim_de_semana": rides >= 1,
        "tempo_trabalho": km >= 1,
        "everest": elev >= 1000,
    }

    eligible = []
    for key in sorted(registry):
        if key in _AUTO_POOL_EXCLUDE:
            continue
        if not rules.get(key, True):
            continue
        text = registry[key](ctx)
        if text:
            eligible.append(key)
    return eligible

Context = dict[str, float | int | str]


def _fmt_int(n: float) -> str:
    return f"{int(round(n)):,}".replace(",", ".")


def _fmt_decimal(n: float, places: int = 1) -> str:
    return f"{n:.{places}f}".replace(".", ",")


def _builder_registry() -> dict[str, Callable[[Context], str | None]]:
    def maratona(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        n = km / _REF["marco_zero"]
        return f"O grupo rodou o equivalente a {_fmt_decimal(n, 1)} maratonas neste mes."

    def volta_mundo(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        pct = km / AROUND_EARTH_KM * 100
        return f"Daqui a pouco da volta ao mundo: {_fmt_decimal(pct, 2)}% do perimetro terrestre so neste mes."

    def amsterdam_paris(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        trips = km / _REF["amsterdam_paris"]
        return f"Daria para ir de Amsterdam a Paris {_fmt_decimal(trips, 1)}x com essa distancia."

    def grolsch(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        bottles = km * 1000 / 0.25
        return f"Em garrafas Grolsch de 25 cm, seriam {_fmt_int(bottles)} unidades enfileiradas."

    def pedaladas_media(ctx: Context) -> str:
        rides = int(ctx["ride_count"])
        km = float(ctx["distance_km"])
        avg = km / rides if rides else 0
        return f"Foram {rides} pedaladas, media de {_fmt_decimal(avg, 1)} km por saida."

    def pedestre(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        steps = km * 1000 / 0.75
        return (
            f"Um pedestre precisaria de {_fmt_int(steps)} passos "
            f"para cobrir a mesma distancia."
        )

    def everest(ctx: Context) -> str | None:
        elev = float(ctx.get("elevation_m", 0))
        if elev <= 0:
            return None
        everests = elev / 8848
        return f"Subida acumulada: {_fmt_int(elev)} m — como {_fmt_decimal(everests, 2)}× o Everest."

    def tempo_trabalho(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        hours = float(ctx.get("moving_hours", 0))
        if hours <= 0:
            hours = km / 22
        return (
            f"Tempo em movimento estimado: {hours:.0f}h — "
            f"um turno de {_fmt_decimal(hours / 8, 1)} dias de trabalho."
        )

    def pizzas(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        count = km * 1000 / 0.94
        return f"Da para alinhar {_fmt_int(count)} pizzas de 30 cm, uma atras da outra."

    def media_atleta(ctx: Context) -> str:
        athletes = int(ctx.get("eligible_athlete_count") or ctx.get("athlete_count") or 0)
        km = float(ctx["distance_km"])
        per = km / athletes if athletes else km
        return (
            f"Em media, cada ciclista do pelotao pedalou {per:.0f} km neste mes "
            f"({athletes} atletas no grupo)."
        )

    def enschede_koln(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        return f"Em linha reta, {km:.0f} km passam de Enschede ate além de Koln."

    def latas(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        cokes = km * 1000 / 0.115
        return f"Seriam {_fmt_int(cokes)} latas de refrigerante colocadas em fila."

    def piscinas(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        pools = km * 1000 * 0.00033 / 2500
        return f"Em volume de lata, encheria {_fmt_decimal(pools, 2)} piscinas olimpicas."

    def formigas(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        ants = km * 1000 / 0.01
        return f"Uma fila de formigas de {_fmt_int(ants)} individuos alcançaria a mesma distancia."

    def fim_de_semana(ctx: Context) -> str:
        weekends = int(ctx.get("weekend_rides", 0))
        return f"Dos {int(ctx['ride_count'])} treinos, {weekends} foram no fim de semana."

    return {
        "maratona": maratona,
        "volta_mundo": volta_mundo,
        "amsterdam_paris": amsterdam_paris,
        "grolsch": grolsch,
        "pedaladas_media": pedaladas_media,
        "pedestre": pedestre,
        "everest": everest,
        "tempo_trabalho": tempo_trabalho,
        "pizzas": pizzas,
        "media_atleta": media_atleta,
        "enschede_koln": enschede_koln,
        "latas": latas,
        "piscinas": piscinas,
        "formigas": formigas,
        "fim_de_semana": fim_de_semana,
    }


def _pick_two_indices(n: int, seed: int) -> tuple[int, int]:
    """Two distinct indices in [0, n) from one seed."""
    if n <= 1:
        return 0, 0
    i0 = seed % n
    i1 = (seed // n) % (n - 1)
    if i1 >= i0:
        i1 += 1
    return i0, i1


def _resolve_keys(
    month_year: str,
    registry: dict[str, Callable[[Context], str | None]],
    ctx: Context,
) -> list[str]:
    if month_year in MONTH_CURIOSITY_KEYS:
        return MONTH_CURIOSITY_KEYS[month_year]

    pool = _eligible_keys(ctx, registry)
    if len(pool) < 2:
        pool = sorted(k for k in registry if k not in _AUTO_POOL_EXCLUDE)

    digest = hashlib.sha256(month_year.encode()).hexdigest()
    seed = int(digest[:8], 16)
    if len(pool) == 1:
        return pool
    i0, i1 = _pick_two_indices(len(pool), seed)
    return [pool[i0], pool[i1]]


def gerar_curiosidades_auto(
    month_year: str,
    distance_km: float,
    *,
    ride_count: int = 0,
    athlete_count: int = 0,
    eligible_athlete_count: int = 0,
    elevation_m: float = 0,
    moving_hours: float = 0,
    longest_ride_km: float = 0,
    weekend_rides: int = 0,
    count: int = 2,
) -> list[str]:
    """Duas curiosidades por mes: override manual ou sorteio deterministico por hash."""
    if distance_km < 1:
        return []

    ctx: Context = {
        "distance_km": distance_km,
        "month_year": month_year,
        "ride_count": ride_count,
        "athlete_count": athlete_count,
        "eligible_athlete_count": eligible_athlete_count or athlete_count,
        "elevation_m": elevation_m,
        "moving_hours": moving_hours,
        "longest_ride_km": longest_ride_km,
        "weekend_rides": weekend_rides,
    }

    registry = _builder_registry()
    keys = _resolve_keys(month_year, registry, ctx)
    phrases: list[str] = []
    for key in keys:
        builder = registry.get(key)
        if not builder:
            continue
        text = builder(ctx)
        if text:
            phrases.append(text)
        if len(phrases) >= count:
            break

    # Fallback se alguma curiosidade exigir dado ausente (ex.: everest sem elevacao)
    if len(phrases) < count:
        pool = _eligible_keys(ctx, registry) or sorted(
            k for k in registry if k not in _AUTO_POOL_EXCLUDE
        )
        digest = hashlib.sha256(f"{month_year}:fallback".encode()).hexdigest()
        seed = int(digest[:8], 16)
        used = set(keys)
        for offset in range(len(pool)):
            key = pool[(seed + offset) % len(pool)]
            if key in used:
                continue
            text = registry[key](ctx)
            if text:
                phrases.append(text)
                used.add(key)
            if len(phrases) >= count:
                break

    return phrases[:count]
