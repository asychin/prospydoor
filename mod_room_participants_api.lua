-- mod_room_participants_api.lua
-- HTTP API модуль для получения информации о участниках MUC комнат
-- Проект: Prosody Participant Count Hook (PPCH)
-- Дата: 2025-11-11

local http = require "net.http.server";
local json = require "util.json";
local jid_split = require "util.jid".split;
local jid_bare = require "util.jid".bare;

module:depends("http");

local muc_domain = module:get_option_string("muc_component");
if not muc_domain then
    -- Пробуем получить из конфигурации
    muc_domain = "muc." .. module.host;
end

module:log("info", "Room Participants API loaded for MUC domain: %s", muc_domain);


-- Функция для получения информации о комнате
local function get_room_info(room_name)
    -- Jitsi конвертирует имена комнат в нижний регистр
    room_name = room_name:lower();
    
    local room_jid = room_name .. "@" .. muc_domain;
    module:log("info", "=== Looking for room: %s ===", room_jid);
    
    -- Получаем MUC компонент
    local muc_component = prosody.hosts[muc_domain];
    if not muc_component then
        module:log("error", "MUC component not found: %s", muc_domain);
        return nil, "MUC component not found";
    end
    module:log("info", "MUC component found: %s", muc_domain);
    
    -- Получаем модуль MUC
    local muc_module = muc_component.modules.muc;
    if not muc_module then
        module:log("error", "MUC module not found");
        return nil, "MUC module not found";
    end
    module:log("info", "MUC module found");
    
    -- Получаем комнату
    local room = muc_module.get_room_from_jid(room_jid);
    if not room then
        module:log("info", "Room not found or empty: %s", room_jid);
        return {
            room_name = room_name,
            exists = false,
            participant_count = 0,
            has_participants = false
        };
    end
    module:log("info", "Room found: %s", room_jid);

    
    -- Подсчитываем участников
    local occupants = room._occupants;
    local count = 0;
    local participants = {};
    
    if occupants then
        for occupant_jid, occupant_data in pairs(occupants) do
            -- Пропускаем скрытых пользователей (focus, jibri, transcriber)
            local nick = occupant_data.nick;
            if nick then
                local _, _, resource = jid_split(nick);
                local participant_name = resource;

                if participant_name and not (
                    participant_name:match("^focus") or 
                    participant_name:match("^jibri") or 
                    participant_name:match("^transcriber") or
                    participant_name:match("^recorder")
                ) then
                    count = count + 1;
                    table.insert(participants, participant_name);
                end
            end
        end
    end
    
    module:log("info", "Room %s has %d participants", room_name, count);
    
    return {
        room_name = room_name,
        exists = true,
        participant_count = count,
        has_participants = count > 0,
        participants = participants,
        room_jid = room_jid
    };
end

-- HTTP handler
local function handle_get_room_participants(event, room_name)
    local response = event.response;
    
    if not room_name or room_name == "" then
        response.headers.content_type = "application/json";
        response.status_code = 400;
        return json.encode({
            error = "Room name is required",
            status = "error"
        });
    end
    
    local room_info, err = get_room_info(room_name);
    
    if err then
        response.headers.content_type = "application/json";
        response.status_code = 500;
        return json.encode({
            error = err,
            status = "error"
        });
    end
    
    response.headers.content_type = "application/json";
    response.headers["Access-Control-Allow-Origin"] = "*";
    response.status_code = 200;
    
    return json.encode(room_info);
end

-- Регистрация HTTP endpoints
module:provides("http", {
    route = {
        ["GET /room-participants/*"] = function(event)
            -- Извлекаем имя комнаты из пути
            local path = event.request.path;
            module:log("debug", "Received request path: %s", path);
            
            -- Пробуем разные паттерны извлечения
            local room_name = path:match("/room%-participants/(.+)$") or path:match("^(.+)$");
            
            if room_name and room_name:match("^/") then
                room_name = room_name:match("^/(.+)$");
            end
            
            module:log("debug", "Extracted room name: %s", tostring(room_name));
            return handle_get_room_participants(event, room_name);
        end;
        
        ["GET /health"] = function(event)
            event.response.headers.content_type = "application/json";
            return json.encode({
                status = "ok",
                module = "room_participants_api",
                muc_domain = muc_domain
            });
        end;
    };
});

module:log("info", "Room Participants API endpoints registered");
