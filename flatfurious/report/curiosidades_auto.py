"""Auto-generated fun facts from monthly metrics (no static phrase file)."""

from __future__ import annotations

import hashlib
from typing import Callable

AROUND_EARTH_KM = 40075

# Referencias do mundo real
_REF = {
    "enschede_utrecht": 120,
    "marco_zero": 42.195,
    "onibus_escolar_m": 12.0,
    "formiga_m": 0.01,
    "terna_artica_km_ano": 96_000,
    "cegonha_km_ano": 20_000,
    "monte_fuji_m": 3776,
    "everest_m": 8848,
    "k2_m": 8611,  # Himalaia — cume K2
}

# Trechos famosos (origem, destino, km) — rotacionam por mes
_FAMOUS_ROUTES: list[tuple[str, str, float]] = [
    ("Amsterdam", "Paris", 504),
    ("Londres", "Paris", 344),
    ("Rio de Janeiro", "Sao Paulo", 429),
    ("Madrid", "Barcelona", 621),
    ("Berlim", "Praga", 350),
    ("Nova York", "Boston", 360),
    ("Lisboa", "Porto", 313),
    ("Enschede", "Koln", 180),
    ("Cidade do Mexico", "Guadalajara", 540),
    ("Sydney", "Melbourne", 878),
    ("Buenos Aires", "Montevideu", 230),
    ("Cairo", "Alexandria", 220),
    ("Mumbai", "Goa", 590),
    ("Oslo", "Bergen", 463),
]

# Cervejas que rotacionam na curiosidade "daria pra beber X garrafas"
_BEER_BRANDS: list[str] = [
    "Grolsch",
    "Heineken",
    "Amstel",
    "Hertog Jan",
    "Bavaria",
    "Jupiler",
]

# Curiosidades chatas ou confusas — fora do sorteio
_AUTO_POOL_EXCLUDE = {
    "media_atleta",
    "piscinas",
}

# Categorias para forcar variedade (2 frases de tipos diferentes quando possivel)
_CATEGORIES: dict[str, list[str]] = {
    "natureza": [
        "formigas",
        "migracao_terna",
        "migracao_cegonha",
        "onibus_escolar",
    ],
    "subida": [
        "monte_fuji",
        "monte_everest",
        "monte_himalaia",
        "tres_cumes",
    ],
    "distancia": [
        "maratona",
        "rota_famosa",
        "grolsch",
        "pedestre",
        "pizzas",
        "latas",
    ],
    "rota_europa": [
        "enschede_utrecht",
    ],
    "tempo": ["cerveja"],
    "pelotao": ["pedaladas_media", "fim_de_semana"],
}

Context = dict[str, float | int | str]


def _fmt_int(n: float) -> str:
    return f"{int(round(n)):,}".replace(",", ".")


def _fmt_decimal(n: float, places: int = 1) -> str:
    return f"{n:.{places}f}".replace(".", ",")


def _builder_registry() -> dict[str, Callable[[Context], str | None]]:
    def formigas(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        ants = km * 1000 / _REF["formiga_m"]
        return (
            f"Uma fila de formigas (1 cm cada) com {_fmt_int(ants)} individuos "
            f"ia de Enschede ate passar a fronteira belga — e ainda sobra."
        )

    def onibus_escolar(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        buses = km * 1000 / _REF["onibus_escolar_m"]
        return (
            f"Daria para estacionar {_fmt_int(buses)} onibus escolares "
            f"bumper a bumper — {km:.0f} km de asfalto amarelo."
        )

    def migracao_terna(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        monthly_tern = _REF["terna_artica_km_ano"] / 12
        months = km / monthly_tern if monthly_tern else 0
        return (
            f"A terna-artica e a campea de migracao (~96 mil km/ano). "
            f"Neste mes o pelotao cobriu o equivalente a {_fmt_decimal(months, 1)} "
            f"meses de voo dela."
        )

    def migracao_cegonha(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        pct = km / _REF["cegonha_km_ano"] * 100
        return (
            f"Uma cegonha-branca percorre ~20 mil km por ano nas migracoes. "
            f"O grupo fez {_fmt_decimal(pct, 0)}% desse percurso anual so em um mes."
        )

    def monte_fuji(ctx: Context) -> str | None:
        elev = float(ctx.get("elevation_m", 0))
        if elev < 100:
            return None
        climbs = elev / _REF["monte_fuji_m"]
        return (
            f"Subida acumulada de {_fmt_int(elev)} m — "
            f"daria para escalar o Monte Fuji {_fmt_decimal(climbs, 1)} vezes."
        )

    def monte_everest(ctx: Context) -> str | None:
        elev = float(ctx.get("elevation_m", 0))
        if elev < 200:
            return None
        climbs = elev / _REF["everest_m"]
        return (
            f"Com {_fmt_int(elev)} m de subida, o pelotao subiria o Everest "
            f"{_fmt_decimal(climbs, 2)} vezes (sem oxigenio extra)."
        )

    def monte_himalaia(ctx: Context) -> str | None:
        elev = float(ctx.get("elevation_m", 0))
        if elev < 200:
            return None
        climbs = elev / _REF["k2_m"]
        return (
            f"Himalaia na conta: {_fmt_int(elev)} m de ganho — "
            f"equivalente a {_fmt_decimal(climbs, 2)} ascensoes ao K2."
        )

    def tres_cumes(ctx: Context) -> str | None:
        elev = float(ctx.get("elevation_m", 0))
        total = _REF["monte_fuji_m"] + _REF["everest_m"] + _REF["k2_m"]
        if elev < 500:
            return None
        stacks = elev / total
        return (
            f"Fuji + Everest + K2 empilhados mentalmente: "
            f"{_fmt_decimal(stacks, 2)} voltas completas com a subida do mes."
        )

    def maratona(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        n = km / _REF["marco_zero"]
        return f"O pelotao rodou o equivalente a {_fmt_decimal(n, 1)} maratonas oficiais."

    def rota_famosa(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        month_year = str(ctx["month_year"])
        digest = hashlib.sha256(f"rota:{month_year}".encode()).hexdigest()
        idx = int(digest[:8], 16) % len(_FAMOUS_ROUTES)
        origem, destino, dist = _FAMOUS_ROUTES[idx]
        trips = km / dist
        if trips >= 1.05:
            return (
                f"Com {km:.0f} km, o pelotao faria {origem} → {destino} "
                f"({_fmt_decimal(trips, 1)}x; trecho de {dist:.0f} km)."
            )
        pct = trips * 100
        return (
            f"O pelotao percorreu {pct:.0f}% do caminho {origem} → {destino} "
            f"({dist:.0f} km entre os dois)."
        )

    def enschede_utrecht(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        trips = km / _REF["enschede_utrecht"]
        return f"Enschede–Utrecht ({_REF['enschede_utrecht']} km) caberia {_fmt_decimal(trips, 1)}x."

    def grolsch(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        bottles = km * 1000 / 0.25
        return f"Em garrafas Grolsch de 25 cm: {_fmt_int(bottles)} unidades em fila indiana."

    def pedaladas_media(ctx: Context) -> str:
        rides = int(ctx["ride_count"])
        km = float(ctx["distance_km"])
        avg = km / rides if rides else 0
        return f"Foram {rides} pedaladas — media de {_fmt_decimal(avg, 1)} km por saida."

    def pedestre(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        steps = km * 1000 / 0.75
        return f"Um pedestre precisaria de {_fmt_int(steps)} passos para o mesmo percurso."

    def cerveja(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        hours = float(ctx.get("moving_hours", 0))
        if hours <= 0:
            hours = km / 22
        bottles = max(1, int(round(hours * 2)))  # 1 garrafa a cada 30 min em movimento
        month_year = str(ctx["month_year"])
        digest = hashlib.sha256(f"cerveja:{month_year}".encode()).hexdigest()
        brand = _BEER_BRANDS[int(digest[:8], 16) % len(_BEER_BRANDS)]
        return (
            f"Com {hours:.0f}h em movimento, daria pra beber {_fmt_int(bottles)} "
            f"garrafas de {brand} — uma a cada meia hora de estrada."
        )

    def pizzas(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        count = km * 1000 / 0.94
        return f"Da para alinhar {_fmt_int(count)} pizzas de 30 cm, uma atras da outra."

    def latas(ctx: Context) -> str:
        km = float(ctx["distance_km"])
        cokes = km * 1000 / 0.115
        return f"Seriam {_fmt_int(cokes)} latas de refrigerante em fila no acostamento."

    def fim_de_semana(ctx: Context) -> str:
        weekends = int(ctx.get("weekend_rides", 0))
        rides = int(ctx["ride_count"])
        return f"Dos {rides} treinos do mes, {weekends} foram no fim de semana."

    return {
        "formigas": formigas,
        "onibus_escolar": onibus_escolar,
        "migracao_terna": migracao_terna,
        "migracao_cegonha": migracao_cegonha,
        "monte_fuji": monte_fuji,
        "monte_everest": monte_everest,
        "monte_himalaia": monte_himalaia,
        "tres_cumes": tres_cumes,
        "maratona": maratona,
        "rota_famosa": rota_famosa,
        "enschede_utrecht": enschede_utrecht,
        "grolsch": grolsch,
        "pedaladas_media": pedaladas_media,
        "pedestre": pedestre,
        "cerveja": cerveja,
        "pizzas": pizzas,
        "latas": latas,
        "fim_de_semana": fim_de_semana,
    }


def _eligible_keys(ctx: Context, registry: dict[str, Callable[[Context], str | None]]) -> list[str]:
    """Curiosidades que fazem sentido com os dados do mes."""
    km = float(ctx["distance_km"])
    rides = int(ctx["ride_count"])
    elev = float(ctx.get("elevation_m", 0))

    rules: dict[str, bool] = {
        "formigas": km >= 5,
        "onibus_escolar": km >= 10,
        "migracao_terna": km >= 20,
        "migracao_cegonha": km >= 15,
        "monte_fuji": elev >= 100,
        "monte_everest": elev >= 200,
        "monte_himalaia": elev >= 200,
        "tres_cumes": elev >= 500,
        "maratona": km >= 1,
        "rota_famosa": km >= 15,
        "grolsch": km >= 50,
        "pedestre": km >= 30,
        "pizzas": km >= 20,
        "latas": km >= 10,
        "enschede_utrecht": km >= 60,
        "pedaladas_media": rides >= 1,
        "fim_de_semana": rides >= 1,
        "cerveja": km >= 1,
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


def _category_of(key: str) -> str:
    for cat, keys in _CATEGORIES.items():
        if key in keys:
            return cat
    return "outros"


def _pick_diverse_keys(
    pool: list[str], month_year: str, count: int = 2
) -> list[str]:
    """Pick `count` keys from different categories when possible."""
    if not pool:
        return []
    digest = hashlib.sha256(month_year.encode()).hexdigest()
    seed = int(digest[:8], 16)

    by_cat: dict[str, list[str]] = {}
    for key in pool:
        by_cat.setdefault(_category_of(key), []).append(key)

    cats = sorted(by_cat.keys())
    if len(cats) > 1:
        offset = seed % len(cats)
        cats = cats[offset:] + cats[:offset]

    picked: list[str] = []
    for cat in cats:
        if len(picked) >= count:
            break
        options = by_cat.get(cat, [])
        if not options:
            continue
        idx = (seed + len(picked) * 7) % len(options)
        picked.append(options[idx])

    if len(picked) < count:
        for offset in range(len(pool)):
            key = pool[(seed + offset) % len(pool)]
            if key not in picked:
                picked.append(key)
            if len(picked) >= count:
                break

    return picked[:count]


# Ordem de rotacao para curiosidade 2 — percorre o catalogo ao longo dos meses.
_SECONDARY_ROTATION: list[str] = [
    "formigas",
    "onibus_escolar",
    "migracao_cegonha",
    "migracao_terna",
    "monte_fuji",
    "monte_everest",
    "monte_himalaia",
    "tres_cumes",
    "maratona",
    "grolsch",
    "pizzas",
    "latas",
    "pedestre",
    "cerveja",
    "pedaladas_media",
    "fim_de_semana",
]


def _pick_secondary_key(month_year: str, pool: list[str], *, exclude: set[str]) -> str | None:
    """Segunda curiosidade: tipo rotaciona a cada mes (independente do parceiro)."""
    eligible = {k for k in pool if k not in exclude}
    if not eligible:
        return None
    year, month = map(int, month_year.split("-"))
    start = (year * 12 + month - 1) % len(_SECONDARY_ROTATION)
    for offset in range(len(_SECONDARY_ROTATION)):
        key = _SECONDARY_ROTATION[(start + offset) % len(_SECONDARY_ROTATION)]
        if key in eligible:
            return key
    return None


def _resolve_keys(
    month_year: str,
    registry: dict[str, Callable[[Context], str | None]],
    ctx: Context,
) -> list[str]:
    pool = _eligible_keys(ctx, registry)
    if len(pool) < 2:
        pool = _eligible_keys(ctx, registry) or sorted(
            k for k in registry if k not in _AUTO_POOL_EXCLUDE
        )

    picked: list[str] = []
    if "rota_famosa" in pool:
        picked.append("rota_famosa")

    if len(picked) < 2:
        # Rota famosa ja cobre comparacao de distancia; evita repetir trechos curtos.
        exclude = {"rota_famosa", "enschede_utrecht"}
        secondary = _pick_secondary_key(month_year, pool, exclude=exclude)
        if secondary:
            picked.append(secondary)
        elif len(picked) < 2:
            picked.extend(
                _pick_diverse_keys(pool, f"{month_year}:extra", count=2 - len(picked))
            )

    return picked[:2]


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
    """Duas curiosidades por mes — sorteio deterministico com variedade por categoria."""
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

    if len(phrases) < count:
        pool = _eligible_keys(ctx, registry)
        extra = _pick_diverse_keys(
            [k for k in pool if k not in keys], f"{month_year}:fallback", count=count
        )
        for key in extra:
            if key in keys:
                continue
            text = registry[key](ctx)
            if text and text not in phrases:
                phrases.append(text)
            if len(phrases) >= count:
                break

    return phrases[:count]
