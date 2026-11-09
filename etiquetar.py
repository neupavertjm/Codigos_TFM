"""Etiquetado morfosintactico (POS) de los terminos del corpus con spaCy.

Para cada termino recolectado, mira con que categoria gramatical aparece en sus
contextos reales de Reddit y asigna la mas frecuente. El resultado es
ORIENTATIVO y debe revisarlo el autor de la investigacion.

Uso:
    python etiquetar.py
"""

import os
from collections import Counter

import pandas as pd
import spacy

import config

ETIQUETAS = {
    "NOUN": "sustantivo",
    "PROPN": "sustantivo propio",
    "VERB": "verbo",
    "ADJ": "adjetivo",
    "ADV": "adverbio",
}


def main():
    ruta = os.path.join(config.CORPUS_DIR, config.CORPUS_FILE)
    if not os.path.exists(ruta):
        print(f"No se encontro el corpus en {ruta}. Ejecuta antes recolectar.py.")
        return

    nlp = spacy.load("es_core_news_sm")
    corpus = pd.read_excel(ruta)

    resultados = []
    for termino, grupo in corpus.groupby("termino"):
        termino_low = str(termino).lower()
        conteo = Counter()
        for texto in grupo["texto"].astype(str):
            doc = nlp(texto)
            for token in doc:
                if token.text.lower() == termino_low and token.pos_ in ETIQUETAS:
                    conteo[ETIQUETAS[token.pos_]] += 1
        categoria = conteo.most_common(1)[0][0] if conteo else "sin determinar"
        resultados.append({
            "termino": termino,
            "categoria_linguistica": categoria,
            "ocurrencias": len(grupo),
            "reparto_pos": str(dict(conteo)),
        })

    salida = os.path.join(config.CORPUS_DIR, "terminos_etiquetados.xlsx")
    pd.DataFrame(resultados).to_excel(salida, index=False)
    for r in resultados:
        print(f"{r['termino']}: {r['categoria_linguistica']} ({r['ocurrencias']} ocurrencias)")
    print(f"\nGuardado  ->  {salida}")


if __name__ == "__main__":
    main()
