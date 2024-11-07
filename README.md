# FastAPI Orders API

Aplikacja API stworzona w FastAPI do zarządzania zamówieniami w sklepie internetowym. Aplikacja umożliwia tworzenie, aktualizację statusu zamówień oraz konwersję walut dla kwoty zamówienia.

## Technologie

- **FastAPI** - do obsługi endpointów REST
- **SQLAlchemy** - ORM do komunikacji z bazą danych SQLite
- **Pydantic** - do walidacji i serializacji danych
- **Docker** - do konteneryzacji aplikacji
- **Docker Compose** - do łatwego zarządzania usługami

## Funkcje

- Tworzenie zamówień
- Aktualizacja statusu zamówień
- Pobieranie kursów walut z API (NBP lub inne)
- Konwersja kwoty zamówienia do wybranej waluty

## Wymagania

- **Docker**: https://docs.docker.com/get-docker/
- **Docker Compose**: https://docs.docker.com/compose/install/

## Instalacja i uruchomienie

### 2. Budowanie i uruchamianie aplikacji za pomocą Docker Compose

Uruchom poniższe polecenie, aby zbudować obraz Dockera i uruchomić aplikację:

```
docker-compose up --build
```

Aplikacja powinna być dostępna pod adresem http://localhost:8000.

## Testowanie

Aby uruchomić testy (jeśli są skonfigurowane), użyj polecenia:
```
pytest
```

## Konfiguracja środowiska

Zmienne środowiskowe można skonfigurować w pliku .env lub bezpośrednio w docker-compose.yml, jeśli aplikacja wymaga takich ustawień.

