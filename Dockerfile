# Użycie oficjalnego obrazu Python jako podstawy
FROM python:3.12-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Skopiowanie pliku requirements.txt do kontenera
COPY requirements.txt .

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

# Skopiowanie wszystkich plików aplikacji do kontenera
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Ustawienie zmiennej środowiskowej, aby nie buforować wyjścia Python (przydatne przy logach w Dockerze)
ENV PYTHONUNBUFFERED=1

# Polecenie uruchamiające aplikację FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
