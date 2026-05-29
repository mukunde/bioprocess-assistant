# Image Python légère
FROM python:3.11-slim

WORKDIR /app

# Deps Python en premier pour bénéficier du cache de layers Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Code de l'app
COPY . .

# Render assigne dynamiquement la variable PORT; fallback 8000 en local
EXPOSE 8000

# Shell form pour que ${PORT} soit expansé.
# --host 0.0.0.0 bind sur toutes les interfaces (obligatoire en container).
# --headless empêche Chainlit de tenter d'ouvrir un navigateur au démarrage.
CMD chainlit run app.py --host 0.0.0.0 --port ${PORT:-8000} --headless
