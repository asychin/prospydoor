# 🚀 Prosody Participant Count Hook (PPCH) - Quick Start

## Start in 3 Steps

### 1️⃣ Prosody Module Installation (REQUIRED!)

**PPCH will NOT work without this module!**

```bash
# Copy the module to the Prosody directory
cd ppch
cp mod_room_participants_api.lua /path/to/jitsi/.jitsi-meet-cfg/prosody/prosody-plugins-custom/

# Add the module to Jitsi .env
cd /path/to/jitsi
echo "GLOBAL_MODULES=http,room_participants_api" >> .env

# Restart Prosody
docker compose restart prosody

# Verify the module is loaded
docker logs jitsi-prosody-1 | grep "Room Participants API loaded"
# Should output: "Room Participants API loaded for MUC domain: muc.meet.yourdomain.com"
```

### 2️⃣ PPCH Configuration

```bash
cd ppch
cp .env.example .env
nano .env  # Change PPCH_API_KEY to your secret key
```

### 3️⃣ Launch

```bash
docker compose up -d
```

### ✅ Verification

```bash
# Health check
curl http://localhost:8890/health
# Should return: {"status":"ok",...,"prosody_status":"ok"}

# Check room (IMPORTANT: room name in lowercase!)
curl -H "X-API-Key: your-key-from-env" \
  http://localhost:8890/api/rooms/testroom/participants
```

---

## 📊 API Response

If there are participants in the room:
```json
{
  "room_name": "testroom",
  "exists": true,
  "participant_count": 2,
  "has_participants": true,
  "participants": ["user1", "user2"],
  "room_jid": "testroom@muc.meet.yourdomain.com"
}
```

If the room is empty:
```json
{
  "room_name": "testroom",
  "exists": false,
  "participant_count": 0,
  "has_participants": false,
  "participants": [],
  "room_jid": null
}
```

---

## 🔧 Management Commands

```bash
cd ppch

# Logs
docker compose logs -f

# Restart
docker compose restart

# Stop
docker compose down

# Rebuild
docker compose up -d --build
```

---

## 📚 Documentation

- [README.md](README.md) - Full documentation
- Swagger UI: http://localhost:8890/docs
