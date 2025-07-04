# Task Manager

Task Manager to aplikacja back-endowa napisana w Pythonie z użyciem Django, Django REST Framework oraz PostgreSQL. Służy do zarządzania zadaniami i spełnia wymagania typowego systemu ticketowego.

## Spis treści
- [Opis funkcjonalności](#opis-funkcjonalności)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Konfiguracja pliku .env i SECRET_KEY](#konfiguracja-pliku-env-i-secret_key)
- [Konfiguracja bazy danych PostgreSQL](#konfiguracja-bazy-danych-postgresql)
- [Testy](#testy)
- [Struktura projektu](#struktura-projektu)
- [Dostęp do API i panelu administracyjnego](#dostęp-do-api-i-panelu-administracyjnego)
- [Dokumentacja i testowanie API przez Swaggera](#dokumentacja-i-testowanie-api-przez-swaggera)
- [Dostępne endpointy API](#dostępne-endpointy-api)
- [Przykłady zapytań curl](#przykłady-zapytań-curl)
- [Autor](#autor)

## Opis funkcjonalności

Aplikacja umożliwia:
- Dodawanie, edycję, usuwanie i przeglądanie zadań.
- Filtrowanie zadań po wszystkich polach (id, nazwa, opis, status, przypisany użytkownik).
- Wyszukiwanie zadań po nazwie i opisie (case-insensitive).
- Przeglądanie historii zmian zadań wraz z możliwością sprawdzenia stanu zadania w dowolnym momencie.
- Rejestrację i logowanie użytkowników (JWT).
- System uprawnień (autoryzacja do operacji na zadaniach).
- Panel administracyjny Django.
- Testy jednostkowe (pytest).
- Obsługę przez Docker/Docker Compose oraz możliwość uruchomienia przez gunicorn.

### Model zadania (Task)
- `id` – automatycznie nadawany numer (kolejna liczba całkowita)
- `name` – nazwa zadania (wymagane, krótki tekst)
- `description` – opis zadania (opcjonalny, dłuższy tekst)
- `status` – status zadania (wymagany, domyślnie "Nowy", możliwe wartości: "Nowy", "W toku", "Rozwiązany")
- `assigned_to` – przypisany użytkownik (opcjonalny, wybierany z listy użytkowników)

## Wymagania
- Python 3.11+
- PostgreSQL 14+
- Docker (opcjonalnie, do uruchomienia w kontenerze)
- Django, Django REST Framework
- Pozostałe zależności w pliku `requirements.txt`

## Instalacja

### Instalacja lokalna (bez Dockera)
1. Sklonuj repozytorium:
   ```bash
   git clone <adres_repozytorium>
   cd task_manager
   ```
2. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```
3. Utwórz plik `.env` na podstawie przykładu i wygeneruj własny SECRET_KEY (instrukcja poniżej).
4. Wykonaj migracje:
   ```bash
   python manage.py migrate
   ```
5. Uruchom serwer deweloperski:
   ```bash
   python manage.py runserver
   ```
   Lub produkcyjnie przez gunicorn (jeśli zainstalowany):
   ```bash
   gunicorn config.wsgi:application
   ```

### Instalacja przez Dockera
1. Upewnij się, że masz zainstalowanego Dockera i Docker Compose.
2. Przygotuj plik `.env` (możesz skopiować `.env.example` lub utworzyć własny).
3. Uruchom aplikację:
   ```bash
   docker-compose up --build
   ```

## Konfiguracja pliku .env i SECRET_KEY

Aby uruchomić projekt, potrzebny jest plik `.env` z odpowiednimi danymi, w tym SECRET_KEY. Możesz to zrobić na dwa sposoby:

### 1. Automatycznie przez Dockera
Jeśli korzystasz z Dockera, uruchom:
```bash
  docker-compose up --build
```
Docker pobierze zmienne środowiskowe z pliku `.env` (jeśli istnieje) lub możesz przygotować plik `.env.example` i skopiować go do `.env` przed uruchomieniem. Jeśli nie masz pliku `.env`, utwórz go na podstawie poniższego wzoru.

### 2. Ręcznie (lokalnie)
Jeśli uruchamiasz projekt lokalnie bez Dockera:
1. Utwórz plik `.env` w głównym katalogu projektu na podstawie poniższego przykładu:
   ```
   DB_NAME=task_manager_base
   DB_USER=user123
   DB_PASSWORD=haslo123
   DB_HOST=db
   DB_PORT=5432
   SECRET_KEY=tu_wklej_wygenerowany_klucz
   ```
2. SECRET_KEY wygeneruj poleceniem (wymaga zainstalowanego Pythona i Django):
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Skopiuj wygenerowany klucz i wklej do pliku `.env`.

**Uwaga:**
- Plik `.env` jest niezbędny do działania projektu – bez niego aplikacja się nie uruchomi.

### Przykład pliku `.env` i opis zmiennych

Przykładowa zawartość pliku `.env`:
```
DB_NAME=task_manager_base
DB_USER=user123
DB_PASSWORD=haslo123
DB_HOST=db
DB_PORT=5432
SECRET_KEY=tu_wklej_wygenerowany_klucz
```

Opis zmiennych:
- `DB_NAME` – nazwa bazy danych PostgreSQL, z której korzysta aplikacja
- `DB_USER` – nazwa użytkownika bazy danych
- `DB_PASSWORD` – hasło użytkownika bazy danych
- `DB_HOST` – adres hosta bazy danych (np. `db` jeśli korzystasz z Dockera, `localhost` lokalnie)
- `DB_PORT` – port bazy danych (domyślnie 5432 dla PostgreSQL)
- `SECRET_KEY` – tajny klucz Django wymagany do uruchomienia projektu (unikalny, generowany samodzielnie)

## Konfiguracja bazy danych PostgreSQL

Aplikacja domyślnie korzysta z bazy danych PostgreSQL. Przed uruchomieniem projektu upewnij się, że baza danych jest dostępna i skonfigurowana zgodnie z poniższymi krokami:

### 1. Konfiguracja lokalna
1. Zainstaluj PostgreSQL 14+ na swoim komputerze.
2. Utwórz nową bazę danych i użytkownika np:
   ```bash
   psql -U postgres
   CREATE DATABASE task_manager_base;
   CREATE USER user123 WITH PASSWORD 'haslo123';
   GRANT ALL PRIVILEGES ON DATABASE task_manager_base TO user123;
   ```
3. W pliku `.env` ustaw odpowiednie dane dostępowe np:
   ```
   DB_NAME=task_manager_base
   DB_USER=user123
   DB_PASSWORD=haslo123
   DB_HOST=localhost
   DB_PORT=5432
   SECRET_KEY=tu_wklej_wygenerowany_klucz
   ```

## Testy

Testy jednostkowe napisane są z użyciem pytest. Można je uruchomić na dwa sposoby:

### 1. W Dockerze
Wejdź do kontenera poleceniem:
```bash
docker-compose exec web sh
```
Następnie uruchom testy:
```bash
pytest
```

### 2. Lokalnie
Jeśli uruchamiasz projekt lokalnie (bez Dockera), użyj polecenia w aktywowanym virtualenv projektu Pythona:
```bash
pytest
```

## Struktura projektu
- `tasks/` — aplikacja do zarządzania zadaniami
- `config/` — pliki konfiguracyjne projektu
- `staticfiles/` — pliki statyczne

## Dostęp do API i panelu administracyjnego
Aby korzystać z API oraz panelu administracyjnego Django:
1. Utwórz użytkownika z uprawnieniami administratora (superuser) w bazie danych:
   ```bash
   python manage.py createsuperuser
   ```
   Postępuj zgodnie z instrukcjami i podaj wymagane dane.
2. Zaloguj się do panelu administracyjnego pod adresem `http://localhost:8000/admin/` używając utworzonych danych.
3. W panelu administracyjnym możesz dodawać kolejnych użytkowników oraz zarządzać uprawnieniami.

## Dokumentacja i testowanie API przez Swaggera

Do API możesz uzyskać dostęp oraz testować endpointy przez interfejs Swaggera. Po uruchomieniu aplikacji wejdź w przeglądarce na adres:

```
http://localhost:8000/docs/
```

Swagger umożliwia interaktywne testowanie wszystkich dostępnych endpointów API, w tym rejestrację, logowanie, operacje na zadaniach oraz historię zmian.

## Dostępne endpointy API

Poniżej znajduje się lista głównych endpointów dostępnych w aplikacji wraz z wymaganymi parametrami. Wszystkie operacje na zadaniach wymagają autoryzacji JWT.

- `POST   /register/` — rejestracja nowego użytkownika
  - Parametry (JSON):
    - `username` (str, wymagany)
    - `password` (str, wymagany)
    - `password2` (str, wymagany — powtórzenie hasła)

- `POST   /login/` — logowanie użytkownika
  - Parametry (JSON):
    - `username` (str, wymagany)
    - `password` (str, wymagany)
  - Odpowiedź (JSON):
    - token JWT dostępu (np. `access` lub `refresh`)

- `POST   /token/refresh/` — odświeżenie tokena JWT
  - Parametry (JSON):
    - `refresh` (str, wymagany — token odświeżający)
  - Odpowiedź (JSON):
    - `access` (str) — nowy token dostępu

- `GET    /tasks/` — pobranie listy zadań (wymaga autoryzacji)
  - Parametry (query, opcjonalne):
    - `search` (str) — wyszukiwanie tekstowe (case-insensitive, po nazwie i opisie)
    - `id` (int) — ID zadania
    - `name` (str) — nazwa zadania (fragment, case-insensitive)
    - `description` (str) — opis zadania (fragment, case-insensitive)
    - `status` (str) — status zadania (Nowy, W toku, Rozwiązany)
    - `assigned_to` (int) — ID użytkownika przypisanego do zadania

- `POST   /tasks/` — utworzenie nowego zadania (wymaga autoryzacji)
  - Parametry (JSON):
    - `name` (str, wymagany)
    - `description` (str, opcjonalny)
    - `status` (str, opcjonalny — domyślnie "Nowy")
    - `assigned_to` (int, opcjonalny — ID użytkownika)

- `GET    /tasks/{id}/` — pobranie szczegółów zadania (wymaga autoryzacji)
  - Parametry:
    - `id` (int, ID zadania — wymagany)

- `PUT    /tasks/{id}/` — edycja zadania (wymaga autoryzacji)
  - Parametry:
    - `id` (int, ID zadania — wymagany)
    - Parametry (JSON):
      - `name` (str, wymagany)
      - `description` (str, opcjonalny)
      - `status` (str, wymagany)
      - `assigned_to` (int, opcjonalny)

- `PATCH  /tasks/{id}/` — częściowa edycja zadania (wymaga autoryzacji)
  - Parametry:
    - `id` (int, ID zadania — wymagany)
    - Parametry (JSON):
      - dowolne pole zadania do zmiany (oprócz id)

- `DELETE /tasks/{id}/` — usunięcie zadania (wymaga autoryzacji)
  - Parametry:
    - `id` (int, ID zadania — wymagany)

### Task History
- `GET    /task-history/` — pobranie historii zmian wszystkich zadań (wymaga autoryzacji)
  - Parametry (query, opcjonalne):
    - `task` (int) — ID zadania
    - `task_id_snapshot` (int) — ID zadania (zrzut backupowy)
    - `changed_by` (int) — ID użytkownika
    - `changed_by_username` (str) — nazwa użytkownika
    - `timestamp_from` (str, $date-time) — od daty (ISO 8601)
    - `timestamp_to` (str, $date-time) — do daty (ISO 8601)

  Pozwala zobaczyć, jak wyglądało zadanie w dowolnym momencie w przeszłości (np. status, przypisany użytkownik).

## Przykłady zapytań curl

**Rejestracja użytkownika:**
```bash
curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "haslo123", "password2": "haslo123"}'
```

**Logowanie i pobranie tokena JWT:**
```bash
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "haslo123"}'
```

**Dodanie zadania:**
```bash
curl -X POST http://localhost:8000/tasks/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Nowe zadanie", "description": "Opis", "status": "Nowy", "assigned_to": null}'
```

**Pobranie zadań przypisanych do użytkownika o id=2:**
```bash
curl -X GET "http://localhost:8000/tasks/?assigned_to=2" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Filtrowanie zadań po statusie:**
```bash
curl -X GET "http://localhost:8000/tasks/?status=Nowy" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Wyszukiwanie zadań zawierających słowo 'gotowanie' w nazwie lub opisie:**
```bash
curl -X GET "http://localhost:8000/tasks/?search=gotowanie" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Pobranie historii zmian dla zadania o id=1:**
```bash
curl -X GET "http://localhost:8000/task-history/?task=1" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```
## Autor
- d4krzyk
