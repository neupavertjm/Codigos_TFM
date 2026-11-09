# Plantilla de configuracion.
# Copia este archivo como  config.py  y rellena tus credenciales.
# config.py esta en .gitignore: no se sube al repositorio.
#
# Como obtener las credenciales de Reddit:
#   1. Entra en https://www.reddit.com/prefs/apps
#   2. "create another app"  ->  tipo "script"
#   3. Copia el client_id (la cadena bajo el nombre de la app) y el secret aqui.

REDDIT = {
    "client_id": "TU_CLIENT_ID",
    "client_secret": "TU_CLIENT_SECRET",
    "user_agent": "script para TFM v1.0 by tu_usuario",
}

# Subreddits donde se busca. Usa  ["all"]  para buscar en todo Reddit.
SUBREDDITS = ["leagueoflegends", "VALORANT", "GlobalOffensive", "csgo", "cs2"]

# Donde se acumula el corpus.
CORPUS_DIR = "corpus"
CORPUS_FILE = "corpus_reddit.xlsx"

# Maximo de posts a recuperar por subreddit en cada busqueda.
LIMITE_POR_SUBREDDIT = 100
