#!/usr/bin/env python3
"""Genera snapshots sintéticos reproducibles para el informe TechNorte."""
from __future__ import annotations

import csv
import math
import random
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data"
SEED = 7
START = date(2026, 8, 13)
END = date(2026, 11, 10)
TITLES = [
    "Mi setup de 2026", "Probé el móvil más barato del mercado", "5 apps que uso a diario",
    "Review honesta: ¿merece la pena?", "Unboxing sorpresa", "Tutorial: monta tu PC paso a paso",
    "TOP 10 gadgets baratos", "Qué pasó con esta marca", "Respondo vuestras preguntas",
    "Cómo editar vídeo gratis",
]
DURATIONS = [.5, .8, 6, 9, 12, 14, 18, 22, 28, 35]
TAGS = ["top 10", "review", "pc gaming", "tutorial", "unboxing", "android", "ofertas"]
CHANNELS = [
    ("UC_TECHNORTE_DEMO", "TechNorte", 412000, 118000, 3.9, 2.3, 38),
    ("UC_GADGETLAB_DEMO", "GadgetLab", 612000, 164000, 3.1, 3.5, 22),
    ("UC_PIXELPRO_DEMO", "PixelPro", 298000, 87000, 4.6, 1.4, 55),
    ("UC_CIRCUITOTV_DEMO", "CircuitoTV", 845000, 201000, 2.7, 4.1, 15),
]


def write_csv(name: str, rows: list[dict]) -> None:
    if not rows:
        return
    with (OUT / name).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def retencion(d: float) -> float:
    return .90 if d < 1 else .50 if d < 8 else .42 if d < 15 else .35 if d < 25 else .30


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    dates = [START + timedelta(days=i) for i in range((END - START).days + 1)]
    write_csv("dim_fecha.csv", [
        {"fecha": d.isoformat(), "anio": d.year, "mes_num": d.month, "mes": d.strftime("%B"),
         "dia": d.day, "dia_semana_num": d.isoweekday(), "dia_semana": d.strftime("%A"),
         "semana_anio": d.isocalendar().week, "es_fin_semana": int(d.isoweekday() >= 6)} for d in dates
    ])
    write_csv("dim_canal.csv", [dict(channel_id=c[0], canal=c[1], suscriptores=c[2],
        vistas_medias_video=c[3], engagement_pct=c[4], videos_semana=c[5], pct_shorts=c[6]) for c in CHANNELS])

    videos: list[dict] = []
    tag_rows: list[dict] = []
    snapshots: list[dict] = []
    channel_snapshots: list[dict] = []
    channel_video_views: dict[str, list[int]] = defaultdict(list)
    heat_acc: dict[tuple[int, int], list[int]] = defaultdict(list)
    next_video = 1
    tech_video_meta: list[tuple[dict, int, int, int]] = []

    for ch_idx, ch in enumerate(CHANNELS):
        channel_id, channel_name, initial_subs, mean_views = ch[:4]
        count = 30 if ch_idx == 0 else 25
        publish_dates = [END - timedelta(days=3 * i) for i in range(count)] if ch_idx == 0 else [
            END - timedelta(days=round(i * 89 / (count - 1))) for i in range(count)
        ]
        pub_dates_sorted = sorted(publish_dates)
        base_subs = initial_subs if ch_idx else 412000
        subs = base_subs
        for d_i, day in enumerate(dates):
            if ch_idx == 0:
                weekly = 1 + .18 * math.sin(d_i / 7 * 2 * math.pi)
                spike = 2.4 if d_i % 17 == 3 else 1
                increment = round(140 + rng.random() * 160 + (500 if d_i % 17 == 3 else 0))
                subs += increment
            else:
                weekly, spike = 1, 1
                increment = round(15 + rng.random() * 50)
                subs += increment
            channel_snapshots.append({"fecha": day.isoformat(), "channel_id": channel_id, "suscriptores": subs})

        for ix, pub in enumerate(publish_dates):
            dur = DURATIONS[ix % 10] if ch_idx == 0 else [5, 9, 12, 18, 25][ix % 5]
            short = dur < 1
            title_base = TITLES[ix % 10] if ch_idx == 0 else ["Review de tecnología", "Probamos este gadget", "Guía completa de compra", "¿Merece la pena?", "Top productos del mes"][ix % 5]
            title = title_base + (f" #{ix // 10 + 1}" if ch_idx == 0 and ix > 9 else (f" #{ix // 5 + 1}" if ch_idx else ""))
            if ch_idx == 0:
                avg_base = 210000 if short else 150000 if 8 <= dur <= 20 else 90000
                total = round(avg_base * (.4 + rng.random() * 1.5) * (2.2 if ix % 7 == 0 else 1))
            else:
                total = round(mean_views * (.45 + rng.random() * 1.1))
            likes_total = round(total * (.03 + rng.random() * .04))
            comments_total = round(total * (.002 + rng.random() * .004))
            vid = f"SYN_{next_video:04d}"
            next_video += 1
            pub_time = time(rng.choice([8, 12, 16, 18, 20, 21]), rng.choice([0, 15, 30, 45]))
            tags = rng.sample(TAGS, k=3)
            video = {"video_id": vid, "channel_id": channel_id, "titulo": title,
                "publicado": pub.isoformat(), "hora_publicacion": pub_time.strftime("%H:%M:%S"),
                "duracion_min": dur, "es_short": int(short), "tags": ",".join(tags),
                "vistas_totales_sinteticas": total}
            videos.append(video)
            tag_rows.extend({"video_id": vid, "tag": tag} for tag in tags)
            channel_video_views[channel_id].append(total)
            if ch_idx == 0:
                tech_video_meta.append((video, total, likes_total, comments_total))
            pub_dt = datetime.combine(pub, pub_time)
            age_max = (END - pub).days
            daily_raw = []
            for age in range(age_max + 1):
                # Decay curve puts the majority of short-form views in the first 48 hours.
                decay = .52 if short else .14
                raw = math.exp(-decay * age)
                daily_raw.append(raw)
            normalizer = sum(daily_raw) or 1
            cum_views = cum_likes = cum_comments = 0
            for age, weight in enumerate(daily_raw):
                snap_date = pub + timedelta(days=age)
                day_view = round(total * weight / normalizer)
                # Put rounding residue in the final snapshot so final cumulative totals match.
                if age == age_max:
                    day_view = total - cum_views
                cum_views += day_view
                cum_likes = round(likes_total * cum_views / max(total, 1))
                cum_comments = round(comments_total * cum_views / max(total, 1))
                if ch_idx == 0:
                    snapshots.append({"fecha": snap_date.isoformat(), "video_id": vid,
                        "vistas_acum": cum_views, "likes_acum": cum_likes, "comentarios_acum": cum_comments})
            dow = pub.isoweekday() - 1
            hour_bin = pub_time.hour // 4
            if ch_idx == 0:
                factor = [0.5, .5, 1, 1.4, 1.9, 1.5][hour_bin]
                heat_acc[(dow, hour_bin)].append(round(40000 * (1 + .5 * math.sin(dow / 6 * math.pi)) * factor * (.8 + rng.random() * .4)))

    # Materialize all TechNorte x date rows (zero snapshots before publication).
    snap_index = {(r["video_id"], date.fromisoformat(r["fecha"])): r for r in snapshots}
    full_snapshots = []
    for video, _, _, _ in tech_video_meta:
        pub = date.fromisoformat(video["publicado"])
        for day in dates:
            if day < pub:
                continue
            row = snap_index.get((video["video_id"], day))
            if row:
                full_snapshots.append(row)

    def calculated_title(v: dict) -> dict:
        title = v["titulo"]
        return {"tramo_duracion": "Shorts" if v["duracion_min"] < 1 else "1–8 min" if v["duracion_min"] < 8 else "8–15 min" if v["duracion_min"] < 15 else "15–25 min" if v["duracion_min"] < 25 else "25+ min",
                "retencion_supuesta": retencion(v["duracion_min"]),
                "dia_semana": date.fromisoformat(v["publicado"]).strftime("%A"),
                "franja_horaria": f"{(int(v['hora_publicacion'][:2]) // 4) * 4:02d}–{((int(v['hora_publicacion'][:2]) // 4) + 1) * 4:02d}",
                "con_pregunta": int("?" in title), "con_numero": int(any(c.isdigit() for c in title)),
                "mas_30_caracteres": int(len(title) > 30), "con_mayusculas": int(any(title[i:i+4].isupper() and any(c.isalpha() for c in title[i:i+4]) for i in range(max(len(title)-3, 0))))}
    for v in videos:
        v.update(calculated_title(v))
        v.pop("vistas_totales_sinteticas", None)
    write_csv("dim_video.csv", videos)
    write_csv("dim_video_tag.csv", tag_rows)
    write_csv("fact_video_diario.csv", full_snapshots)
    write_csv("fact_canal_diario.csv", channel_snapshots)
    write_csv("fact_heatmap_publicacion.csv", [
        {"dia_semana_num": d + 1, "dia_semana": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][d],
         "franja_num": b, "franja": f"{b*4:02d}–{(b+1)*4:02d}", "vistas_7d_medias": round(sum(heat_acc[(d,b)]) / max(len(heat_acc[(d,b)]), 1))}
        for d in range(7) for b in range(6)])
    themes = ["precio", "batería", "cámara", "garantía", "comparativa"]
    sentiments = [("Positivo", 68), ("Neutro", 22), ("Negativo", 10)]
    write_csv("fact_sentimiento.csv", [
        {"channel_id": CHANNELS[0][0], "sentimiento": s, "n": round(5000 * pct / 100), "tema": theme}
        for s, pct in sentiments for theme in themes
    ])
    write_csv("rasgo_titulo.csv", [{"rasgo": x, "orden": i} for i, x in enumerate(["Con ?", "Con número", "Más de 30 car.", "Con MAYÚSCULAS"], 1)])
    print(f"Generados CSV sintéticos en {OUT} (semilla {SEED}).")


if __name__ == "__main__":
    main()
