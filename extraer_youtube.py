#!/usr/bin/env python3
"""Carga canales públicos con YouTube Data API v3. Requiere YT_API_KEY.

Este extractor escribe la misma estructura de CSV que generar_datos.py. El API
público no ofrece vistas/likes/comentarios diarios históricos; fact_video_diario
se registra como snapshot acumulado de cada ejecución, en modo append diario.
"""
from __future__ import annotations

import csv
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data"
API = "https://www.googleapis.com/youtube/v3/"
CHANNELS = {
    "TechNorte": "UC_TECHNORTE_DEMO",
    "GadgetLab": "UC_GADGETLAB_DEMO",
    "PixelPro": "UC_PIXELPRO_DEMO",
    "CircuitoTV": "UC_CIRCUITOTV_DEMO",
}


def get(resource: str, **params):
    key = os.environ.get("YT_API_KEY")
    if not key:
        raise SystemExit("Define YT_API_KEY en el entorno antes de ejecutar.")
    params.update(key=key, part=params.pop("part", "snippet,statistics,contentDetails"), maxResults=50)
    url = API + resource + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def save(name, rows, append=False):
    if not rows:
        return
    path = OUT / name
    exists = path.exists() and path.stat().st_size > 0
    mode = "a" if append and exists else "w"
    with path.open(mode, newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        if mode == "w":
            writer.writeheader()
        writer.writerows(rows)


def pages(playlist_id):
    token = None
    while True:
        result = get("playlistItems", playlistId=playlist_id, pageToken=token or "", part="snippet,contentDetails")
        yield from result.get("items", [])
        token = result.get("nextPageToken")
        if not token:
            break


def main():
    OUT.mkdir(exist_ok=True)
    today = date.today().isoformat()
    channel_rows, video_rows, tag_rows, snapshot_rows = [], [], [], []
    for name, channel_id in CHANNELS.items():
        ch = get("channels", id=channel_id, part="snippet,statistics,contentDetails").get("items", [])
        if not ch:
            print(f"Canal omitido (ID no encontrado o no accesible): {name} / {channel_id}")
            continue
        item = ch[0]
        stats = item.get("statistics", {})
        channel_rows.append({"channel_id": channel_id, "canal": item["snippet"]["title"],
            "suscriptores": stats.get("subscriberCount", ""), "vistas_medias_video": "",
            "engagement_pct": "", "videos_semana": "", "pct_shorts": ""})
        playlist_id = item["contentDetails"]["relatedPlaylists"]["uploads"]
        ids = [x.get("contentDetails", {}).get("videoId") for x in pages(playlist_id)]
        ids = [x for x in ids if x]
        for offset in range(0, len(ids), 50):
            batch = get("videos", id=",".join(ids[offset:offset+50]), part="snippet,statistics,contentDetails").get("items", [])
            for v in batch:
                snippet, stat = v.get("snippet", {}), v.get("statistics", {})
                content = v.get("contentDetails", {})
                # ISO 8601 duration to minutes
                import re
                m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", content.get("duration", "PT0S"))
                duration = ((int(m[1] or 0)*3600 + int(m[2] or 0)*60 + int(m[3] or 0))/60) if m else 0
                published = snippet.get("publishedAt", "")
                title = snippet.get("title", "")
                row = {"video_id": v["id"], "channel_id": channel_id, "titulo": title,
                    "publicado": published[:10], "hora_publicacion": published[11:19] or "00:00:00",
                    "duracion_min": round(duration, 3), "es_short": int(duration < 1),
                    "tags": ",".join(snippet.get("tags", [])), "tramo_duracion": "Shorts" if duration < 1 else "1–8 min" if duration < 8 else "8–15 min" if duration < 15 else "15–25 min" if duration < 25 else "25+ min",
                    "retencion_supuesta": .90 if duration < 1 else .50 if duration < 8 else .42 if duration < 15 else .35 if duration < 25 else .30,
                    "dia_semana": datetime.fromisoformat(published.replace("Z", "+00:00")).strftime("%A"),
                    "franja_horaria": f"{(int(published[11:13] or 0)//4)*4:02d}–{((int(published[11:13] or 0)//4)+1)*4:02d}",
                    "con_pregunta": int("?" in title), "con_numero": int(any(x.isdigit() for x in title)),
                    "mas_30_caracteres": int(len(title) > 30), "con_mayusculas": int(bool(re.search(r"[A-Z]{4,}", title)))}
                video_rows.append(row)
                tag_rows.extend({"video_id": v["id"], "tag": tag} for tag in snippet.get("tags", []))
                snapshot_rows.append({"fecha": today, "video_id": v["id"], "vistas_acum": stat.get("viewCount", 0),
                    "likes_acum": stat.get("likeCount", 0), "comentarios_acum": stat.get("commentCount", 0)})
        time.sleep(.05)
    save("dim_canal.csv", channel_rows)
    save("dim_video.csv", video_rows)
    save("dim_video_tag.csv", tag_rows)
    save("fact_video_diario.csv", snapshot_rows, append=True)
    print(f"Snapshot público del {today} guardado. Ejecuta a diario para acumular observaciones.")


if __name__ == "__main__":
    main()
