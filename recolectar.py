"""Recolector de corpus de Reddit para la tesis.

Busca el termino o terminos que escribas (en espanol o en ingles) en los
subreddits definidos en config.py, y recoge tanto los POSTS como los COMENTARIOS
donde aparece el termino. Guarda cada ocurrencia en un Excel que se va
acumulando: puedes lanzar el script tantas veces como quieras y el corpus crece
sin duplicar lo que ya estaba guardado.

Uso:
    python recolectar.py
    python recolectar.py "gank, feed, nerf"
"""

import os
import re
import sys
from datetime import datetime, timezone

import pandas as pd
import praw
from langdetect import detect, DetectorFactory, LangDetectException

import config

DetectorFactory.seed = 0  # deteccion de idioma reproducible

COLUMNAS = [
    "id", "termino", "tipo", "subreddit", "fecha", "autor",
    "score", "idioma", "titulo_post", "texto", "url",
]


def conectar():
    reddit = praw.Reddit(
        client_id=config.REDDIT["client_id"],
        client_secret=config.REDDIT["client_secret"],
        user_agent=config.REDDIT["user_agent"],
    )
    reddit.read_only = True
    return reddit


def detectar_idioma(texto):
    try:
        return detect(texto)
    except LangDetectException:
        return "?"


def fecha_utc(timestamp):
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")


def recolectar_termino(reddit, termino):
    """Devuelve una lista de filas (dict) con las ocurrencias del termino."""
    # Coincidencia por palabra completa (evita que 'ace' matchee dentro de 'place').
    patron = re.compile(r"\b" + re.escape(termino.lower()) + r"\b")
    filas = []

    for nombre in config.SUBREDDITS:
        subreddit = reddit.subreddit(nombre)
        print(f"  r/{nombre}: buscando '{termino}'...")
        try:
            resultados = subreddit.search(
                termino, limit=config.LIMITE_POR_SUBREDDIT, sort="relevance"
            )
            for sub in resultados:
                texto_post = f"{sub.title} {sub.selftext}".strip()

                # 1) El propio post, si contiene el termino.
                if patron.search(texto_post.lower()):
                    filas.append({
                        "id": sub.id,
                        "termino": termino,
                        "tipo": "post",
                        "subreddit": nombre,
                        "fecha": fecha_utc(sub.created_utc),
                        "autor": str(sub.author),
                        "score": sub.score,
                        "idioma": detectar_idioma(texto_post),
                        "titulo_post": sub.title,
                        "texto": texto_post,
                        "url": f"https://reddit.com{sub.permalink}",
                    })

                # 2) Los comentarios del hilo donde aparezca el termino.
                sub.comments.replace_more(limit=0)
                for c in sub.comments.list():
                    if patron.search((c.body or "").lower()):
                        filas.append({
                            "id": c.id,
                            "termino": termino,
                            "tipo": "comentario",
                            "subreddit": nombre,
                            "fecha": fecha_utc(c.created_utc),
                            "autor": str(c.author),
                            "score": c.score,
                            "idioma": detectar_idioma(c.body),
                            "titulo_post": sub.title,
                            "texto": c.body,
                            "url": f"https://reddit.com{c.permalink}",
                        })
        except Exception as e:
            print(f"    aviso: error en r/{nombre}: {e}")
            continue

    return filas


def cargar_corpus(ruta):
    if os.path.exists(ruta):
        return pd.read_excel(ruta)
    return pd.DataFrame(columns=COLUMNAS)


def main():
    if len(sys.argv) > 1:
        entrada = sys.argv[1]
    else:
        entrada = input("Termino(s) a buscar (separa varios con comas): ")
    terminos = [t.strip() for t in entrada.split(",") if t.strip()]

    if not terminos:
        print("No se indico ningun termino.")
        return

    reddit = conectar()
    todas = []
    for termino in terminos:
        print(f"\nTermino: {termino}")
        todas.extend(recolectar_termino(reddit, termino))

    nuevas = pd.DataFrame(todas, columns=COLUMNAS)
    print(f"\nOcurrencias encontradas en esta ejecucion: {len(nuevas)}")

    os.makedirs(config.CORPUS_DIR, exist_ok=True)
    ruta = os.path.join(config.CORPUS_DIR, config.CORPUS_FILE)

    corpus = cargar_corpus(ruta)
    total_antes = len(corpus)
    corpus = pd.concat([corpus, nuevas], ignore_index=True)
    # Una ocurrencia es unica por (id de Reddit + termino buscado).
    corpus = corpus.drop_duplicates(subset=["id", "termino"], keep="first")
    nuevas_netas = len(corpus) - total_antes

    corpus.to_excel(ruta, index=False)
    print(f"Anadidas {nuevas_netas} ocurrencias nuevas (descartando duplicados).")
    print(f"Corpus total: {len(corpus)} ocurrencias  ->  {ruta}")


if __name__ == "__main__":
    main()
