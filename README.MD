# Kasa Power Strip API

A lightweight FastAPI service that exposes simple REST endpoints to turn **ON** or **OFF** individual plugs on a TP-Link Kasa smart power strip over the local network. This is my temp (mostly vibe coded) solution until the HA integration is fixed.

---

## 🐳 Docker Compose

Create a `docker-compose.yml`:

```yaml
services:
  kasa-simple-api:
    image: christracy/kasa-simple-api
    container_name: kasa-simple-api
    environment:
      - TZ=America/Chicago
      - API_KEY=supersecret123
    restart: unless-stopped
    ports:
      - "8000:8000"
```

### Start the API

```bash
docker compose up -d
```

### View logs

```bash
docker compose logs -f kasa-api
```

---

## 🔐 Authentication

All endpoints require the following header:

```http
x-api-key: YOUR_SECRET_KEY
```

Example:

```http
x-api-key: supersecret
```

---

## 📡 API Endpoints

### Turn a Plug ON

```http
POST /power/on/{ip}/{plug_number}
```

#### Example

```bash
curl -X POST "http://localhost:8000/power/on/192.168.1.10/3"   -H "x-api-key: supersecret123"
```

#### Sample Response

```json
{
  "success": true,
  "result": {
    "ip": "192.168.1.10",
    "alias": "Plug 3",
    "plug_number": 3,
    "state": "on"
  }
}
```

---

### Turn a Plug OFF

```http
POST /power/off/{ip}/{plug_number}
```

#### Example

```bash
curl -X POST "http://localhost:8000/power/off/192.168.1.10/3"   -H "x-api-key: supersecret123"
```

#### Sample Response

```json
{
  "success": true,
  "result": {
    "ip": "192.168.1.10",
    "alias": "Plug 3",
    "plug_number": 3,
    "state": "off"
  }
}
```

---

## 🩺 Health Check

```http
GET /health
```

#### Example

```bash
curl http://localhost:8000/health
```

#### Response

```json
{
  "status": "ok"
}
```

---