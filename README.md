# 🚪 Prosody Participant Count Hook (PPCH)

**"The Hook to Prosody via Python"**

Standalone microservice to check for participants in Jitsi Meet rooms without joining the room itself.

**PPCH** = **P**rosody **P**articipant **C**ount **H**ook 🐍

---

## 🚀 Quick Start

### 1. Prosody Module Installation (REQUIRED!)

**PPCH requires a specific Prosody module to function.**

Copy the module to the Prosody plugins directory:
```bash
cp mod_room_participants_api.lua /path/to/jitsi/.jitsi-meet-cfg/prosody/prosody-plugins-custom/
```

Add the module to the Jitsi `.env` file:
```bash
cd /path/to/jitsi
echo "GLOBAL_MODULES=http,room_participants_api" >> .env
```

Restart Prosody:
```bash
docker compose restart prosody
```

### 2. PPCH Configuration

Copy the example configuration:
```bash
cd ppch
cp .env.example .env
```

Edit `.env`:
```bash
nano .env
```

**Mandatory changes:**
- `PPCH_API_KEY` - your secret API key
- `PROSODY_URL` - Prosody URL (usually `http://prosody:5280`)
- `MUC_DOMAIN` - your MUC domain (e.g., `muc.meet.yourdomain.com`)

### 3. Launch

```bash
cd ppch
docker compose up -d
```

### 4. Verification

```bash
# Health check
curl http://localhost:8890/health

# Check room (use your API key from .env)
# IMPORTANT: room name must be in LOWERCASE!
curl -H "X-API-Key: your-api-key" \
  http://localhost:8890/api/rooms/testroom/participants
```

**Expected response (if module is installed correctly):**
```json
{
  "status": "ok",
  "service": "Prosody Participant Count Hook",
  "version": "1.0.0",
  "prosody_status": "ok"  // <-- Should be "ok", not "error"!
}
```

---

## 📂 Project Structure

```
ppch/
├── docker-compose.yml       # Docker Compose configuration
├── .env                     # Settings (create from .env.example)
├── .env.example             # Example settings
├── Dockerfile               # Docker image
├── requirements.txt         # Python dependencies
├── README.md                # This documentation
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application
│   ├── config.py           # Configuration
│   └── middleware.py       # API Key middleware
```

---

## ⚙️ Configuration (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `PPCH_API_KEY` | API Key for authentication | ⚠️ Change me! |
| `PPCH_PORT` | API Port | 8890 |
| `PROSODY_URL` | Prosody HTTP API URL | http://docker-jitsi-meet-prosody-1:5280 |
| `MUC_DOMAIN` | Jitsi MUC Domain | muc.meet.yourdomain.com |
| `DEBUG` | Debug mode | false |
| `TZ` | Timezone | UTC |

---

## 🔧 Management

### Start
```bash
cd ppch
docker compose up -d
```

### View Logs
```bash
cd ppch
docker compose logs -f
```

### Restart
```bash
cd ppch
docker compose restart
```

### Stop
```bash
cd ppch
docker compose down
```

### Rebuild (after code changes)
```bash
cd ppch
docker compose up -d --build
```

---

## 📡 API Endpoints

### GET /health
Health check (no authentication required)

```bash
curl http://localhost:8890/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "Prosody Participant Count Hook",
  "version": "1.0.0",
  "prosody_status": "ok"
}
```

### GET /api/rooms/{room_name}/participants
Get room participant info (requires API Key)

```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8890/api/rooms/MyRoom/participants
```

**Response:**
```json
{
  "room_name": "MyRoom",
  "exists": false,
  "participant_count": 0,
  "has_participants": false,
  "participants": [],
  "room_jid": null
}
```

### GET /docs
Swagger UI documentation (no authentication required)

Open in browser: http://localhost:8890/docs

---

## 💻 Usage Examples

### Python
```python
import requests

API_URL = "http://localhost:8890"
API_KEY = "your-api-key"

response = requests.get(
    f"{API_URL}/api/rooms/MyRoom/participants",
    headers={"X-API-Key": API_KEY}
)
data = response.json()

if data["has_participants"]:
    print(f"Room has {data['participant_count']} participants")
else:
    print("Room is empty")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const API_URL = 'http://localhost:8890';
const API_KEY = 'your-api-key';

async function checkRoom(roomName) {
  const response = await axios.get(
    `${API_URL}/api/rooms/${roomName}/participants`,
    { headers: { 'X-API-Key': API_KEY } }
  );
  return response.data;
}

checkRoom('MyRoom')
  .then(data => {
    console.log(`Participants: ${data.participant_count}`);
  });
```

### Bash
```bash
#!/bin/bash

API_URL="http://localhost:8890"
API_KEY="your-api-key"
ROOM_NAME="MyRoom"

response=$(curl -s -H "X-API-Key: $API_KEY" \
  "$API_URL/api/rooms/$ROOM_NAME/participants")

count=$(echo "$response" | jq -r '.participant_count')
echo "Participants in room: $count"
```

---

## 🔒 Security

1. **Change the API Key** in `.env` before using in production.
2. API is available on `localhost:8890` by default.
3. For external access, configure nginx reverse proxy with HTTPS.
4. Do not expose the port directly to the internet.

---

## 🐛 Debugging

### Check Container Status
```bash
cd ppch
docker compose ps
```

### View Logs
```bash
cd ppch
docker compose logs --tail=100
```

### Check Connection to Prosody
```bash
# Enter the container
docker exec -it ppch sh

# Check Prosody availability
curl http://docker-jitsi-meet-prosody-1:5280/room_participants_api/health
```

### Network Issues

If PPCH cannot connect to Prosody:

1. Ensure the main Jitsi stack is running:
   ```bash
   docker ps | grep prosody
   ```

2. Check network name:
   ```bash
   docker network ls | grep jitsi
   ```

3. If the network name differs, change it in `docker-compose.yml`:
   ```yaml
   networks:
     jitsi:
       external: true
       name: your-network-name
   ```

---

## 📊 Requirements

- Docker Engine 20.10+
- Docker Compose V2
- Running Jitsi Meet stack with Prosody
- **Prosody module `mod_room_participants_api.lua` installed and loaded** ⚠️

### Prosody Module Installation

1. Copy `mod_room_participants_api.lua` to the plugins directory:
   ```bash
   cp mod_room_participants_api.lua /path/to/jitsi/.jitsi-meet-cfg/prosody/prosody-plugins-custom/
   ```

2. Add the module to Jitsi `.env`:
   ```bash
   # In /path/to/jitsi/.env add or update:
   GLOBAL_MODULES=http,room_participants_api
   ```

3. Restart Prosody:
   ```bash
   cd /path/to/jitsi
   docker compose restart prosody
   ```

4. Check logs:
   ```bash
   docker logs jitsi-prosody-1 | grep room_participants_api
   # Should output: "Room Participants API loaded for MUC domain: ..."
   ```

---

## 🔗 Jitsi Integration

PPCH connects to the existing Jitsi network (`jitsi_meet.jitsi`) and communicates with the Prosody container directly.

**Requirements:**
1. Main Jitsi stack must be running.
2. Prosody must have `room_participants_api` module loaded.
3. In main Jitsi `.env`: `GLOBAL_MODULES=http,room_participants_api`.

**Important about room names:**
- Jitsi automatically converts room names to **lowercase**
- Use `bravephoenixescreatelovingly` instead of `BravePhoenixesCreateLovingly`
- The API automatically converts names to lowercase for convenience

---

## 📚 Full Documentation

See main documentation in project root:
- [../PPCH.md](../PPCH.md) - Full Documentation
- [../PPCH-QUICKSTART.md](../PPCH-QUICKSTART.md) - Quick Start

---

## ❓ FAQ

**Q: Can I run multiple instances?**

A: Yes, change `PPCH_PORT` in `.env` for each instance.

**Q: How to change the port?**

A: Change `PPCH_PORT=8890` to the desired port in the `.env` file.

**Q: API doesn't see rooms with participants**

A: Ensure that:
- Prosody module is loaded (`GLOBAL_MODULES=http,room_participants_api`)
- Container can connect to Prosody (check logs)
- You are using the correct room name (without domain)

---

## 📝 Changelog

**v1.0.0** (2025-11-11)
- ✅ Standalone microservice
- ✅ Own docker-compose.yml
- ✅ Own .env file
- ✅ API Key authentication
- ✅ Health check
- ✅ Swagger documentation

---

**Status:** ✅ Ready for use  
**Version:** 1.0.0  
**Date:** 2025-11-11
