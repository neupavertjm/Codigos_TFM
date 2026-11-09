"""Concordancias KWIC (keyword-in-context) sobre el corpus recolectado.

Para un termino, muestra cada ocurrencia con su contexto a izquierda y derecha,
y lo exporta a Excel. Es el formato de consulta clasico para el analisis
terminologico (citable directamente en la tesis).

Uso:
    python kwic.py
    python kwic.py "gank"
    python kwic.py "gank" 60      (60 = caracteres de contexto a cada lado)
"""

import os
import re
import sys

import pandas as pd

import config

VENTANA = 50  # caracteres de contexto por defecto a cada lado


def kwic_de_texto(texto, termino, ventana):
    patron = re.compile(r"\b" + re.escape(termino) + r"\b", re.IGNORECASE)
    lineas = []
    for m in patron.finditer(texto or ""):
        ini, fin = m.start(), m.end()
        izq = texto[max(0, ini - ventana):ini].replace("\n", " ")
        centro = texto[ini:fin]
        der = texto[fin:fin + ventana].replace("\n", " ")
        lineas.append((izq, centro, der))
    return lineas


def main():
    termino = sys.argv[1] if len(sys.argv) > 1 else input("Termino para KWIC: ").strip()
    ventana = int(sys.argv[2]) if len(sys.argv) > 2 else VENTANA

    ruta = os.path.join(config.CORPUS_DIR, config.CORPUS_FILE)
    if not os.path.exists(ruta):
        print(f"No se encontro el corpus en {ruta}. Ejecuta antes recolectar.py.")
        return

    corpus = pd.read_excel(ruta)
    filas = []
    for _, fila in corpus.iterrows():
        for izq, centro, der in kwic_de_texto(str(fila["texto"]), termino, ventana):
            filas.append({
                "contexto_izquierdo": izq,
                "termino": centro,
                "contexto_derecho": der,
                "tipo": fila["tipo"],
                "subreddit": fila["subreddit"],
                "fecha": fila["fecha"],
                "url": fila["url"],
            })

    if not filas:
        print(f"No hay ocurrencias de '{termino}' en el corpus.")
        return

    salida = os.path.join(config.CORPUS_DIR, f"kwic_{termino}.xlsx")
    pd.DataFrame(filas).to_excel(salida, index=False)
    print(f"{len(filas)} concordancias de '{termino}'  ->  {salida}\n")

    # Vista rapida por consola (primeras 15).
    for izq, centro, der in [(f["contexto_izquierdo"], f["termino"], f["contexto_derecho"]) for f in filas[:15]]:
        print(f"...{izq[-ventana:]:>{ventana}}  [{centro}]  {der}...")


if __name__ == "__main__":
    main()
