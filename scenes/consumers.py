# scenes/consumers.py
# ==============================================================================
# WEBSOCKET CONSUMER — реал-тайм совместное редактирование чанка
#
# Принцип работы:
#   1. Клиент подключается к ws://.../ws/chunk/<chunk_id>/
#   2. Сервер назначает user_id и цвет курсора
#   3. При создании объекта клиент отправляет временный client_id
#   4. Сервер создаёт WorldObject с СВОИМ UUID и возвращает mapping
#   5. Все изменения транслируются всем участникам комнаты
# ==============================================================================

import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer

# Цвета для курсоров пользователей
USER_COLORS = [
    "#ff6600",  # оранжевый
    "#00cc44",  # зелёный
    "#3388ff",  # синий
    "#ff3377",  # розовый
    "#ffcc00",  # жёлтый
    "#33cccc",  # бирюзовый
    "#cc33ff",  # фиолетовый
    "#ff8833",  # персиковый
]


class ChunkConsumer(AsyncWebsocketConsumer):
    """
    WebSocket-комната для одного чанка.
    Все пользователи в комнате видят изменения друг друга в реальном времени.
    """

    # Общий словарь комнат (в памяти сервера)
    # В продакшене нужно заменить на Redis
    rooms = {}

    async def connect(self):
        """Подключение нового пользователя к чанку"""
        self.chunk_id = self.scope["url_route"]["kwargs"]["chunk_id"]
        self.room_group_name = f"chunk_{self.chunk_id}"

        # Инициализируем комнату, если её ещё нет
        if self.chunk_id not in self.rooms:
            self.rooms[self.chunk_id] = {
                "users": {},  # {user_id: {color, position, channel_name}}
                "objects": {},  # {server_uuid: {object_data}} — кеш объектов комнаты
                "next_color": 0,  # счётчик для раздачи цветов
                "next_user_num": 0,  # счётчик для user_id
            }

        room = self.rooms[self.chunk_id]

        # Назначаем пользователю ID и цвет
        room["next_user_num"] += 1
        self.user_id = f"user_{room['next_user_num']}"
        color_index = room["next_color"] % len(USER_COLORS)
        self.user_color = USER_COLORS[color_index]
        room["next_color"] += 1

        # Сохраняем данные пользователя
        room["users"][self.user_id] = {
            "color": self.user_color,
            "position": {"x": 0, "y": 0, "z": 0},
            "channel_name": self.channel_name,
        }

        # Добавляем в группу
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Отправляем приветствие с текущим состоянием комнаты
        await self.send(
            text_data=json.dumps(
                {
                    "type": "welcome",
                    "user_id": self.user_id,
                    "color": self.user_color,
                    "objects": room["objects"],  # все объекты в комнате
                    "cursors": {
                        uid: {"color": data["color"], "position": data["position"]}
                        for uid, data in room["users"].items()
                        if uid != self.user_id
                    },
                }
            )
        )

        # Оповещаем остальных о новом пользователе
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_joined",
                "user_id": self.user_id,
                "color": self.user_color,
                "position": {"x": 0, "y": 0, "z": 0},
            },
        )

    async def disconnect(self, close_code):
        """Отключение пользователя"""
        room = self.rooms.get(self.chunk_id)
        if room and self.user_id in room["users"]:
            del room["users"][self.user_id]

        # Оповещаем остальных
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_left",
                "user_id": self.user_id,
            },
        )

        # Покидаем группу
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # ==========================================================================
    # ОБРАБОТКА ВХОДЯЩИХ СООБЩЕНИЙ
    # ==========================================================================

    async def receive(self, text_data):
        """Обрабатывает сообщения от клиента"""
        data = json.loads(text_data)
        room = self.rooms.get(self.chunk_id)
        if not room:
            return

        msg_type = data.get("type")

        # ===== СОЗДАНИЕ ОБЪЕКТА =====
        if msg_type == "object_create":
            client_id = data.get("client_id")  # временный ID от клиента

            # Сервер ВСЕГДА генерирует свой UUID
            server_id = str(uuid.uuid4())

            obj_data = {
                "client_id": client_id,
                "server_id": server_id,
                "object_type": data.get("object_type", "mesh"),
                "color": data.get("color", "#ff6600"),
                "position": data.get("position", {"x": 0, "y": 0, "z": 0}),
                "rotation": data.get("rotation", {"x": 0, "y": 0, "z": 0}),
                "scale": data.get("scale", {"x": 1, "y": 1, "z": 1}),
                "params": data.get("params", {}),
                "created_by": self.user_id,
            }

            # Сохраняем в кеш комнаты
            room["objects"][server_id] = obj_data

            # Отправляем ВСЕМ (включая создателя) подтверждение
            # с маппингом client_id -> server_id
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "object_created",
                    "client_id": client_id,
                    "server_id": server_id,
                    "object_type": obj_data["object_type"],
                    "color": obj_data["color"],
                    "position": obj_data["position"],
                    "rotation": obj_data["rotation"],
                    "scale": obj_data["scale"],
                    "params": obj_data["params"],
                    "user_id": self.user_id,
                },
            )

        # ===== ОБНОВЛЕНИЕ ОБЪЕКТА =====
        elif msg_type == "object_updated":
            server_id = data.get("server_id") or data.get("object_id")

            if not server_id:
                return

            position = data.get("position")
            rotation = data.get("rotation")
            scale = data.get("scale")
            params = data.get("params")

            # Обновляем кеш
            if server_id in room["objects"]:
                obj = room["objects"][server_id]
                if position:
                    obj["position"] = position
                if rotation:
                    obj["rotation"] = rotation
                if scale:
                    obj["scale"] = scale
                if params:
                    obj["params"] = params

            # Транслируем всем КРОМЕ отправителя
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "object_updated_broadcast",
                    "server_id": server_id,
                    "position": position,
                    "rotation": rotation,
                    "scale": scale,
                    "params": params,
                    "user_id": self.user_id,
                },
            )

        # ===== УДАЛЕНИЕ ОБЪЕКТА =====
        elif msg_type == "object_delete":
            server_id = data.get("server_id") or data.get("object_id")

            if server_id and server_id in room["objects"]:
                del room["objects"][server_id]

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "object_deleted",
                    "server_id": server_id,
                    "user_id": self.user_id,
                },
            )

        # ===== ПЕРЕМЕЩЕНИЕ КУРСОРА =====
        elif msg_type == "cursor_move":
            position = data.get("position", {"x": 0, "y": 0, "z": 0})

            if self.user_id in room["users"]:
                room["users"][self.user_id]["position"] = position

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "cursor_moved",
                    "user_id": self.user_id,
                    "color": self.user_color,
                    "position": position,
                },
            )

    # ==========================================================================
    # ОТПРАВКА СОБЫТИЙ КЛИЕНТАМ
    # ==========================================================================

    async def object_created(self, event):
        """Трансляция создания объекта"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "object_created",
                    "client_id": event["client_id"],
                    "server_id": event["server_id"],
                    "object_type": event["object_type"],
                    "color": event["color"],
                    "position": event["position"],
                    "rotation": event["rotation"],
                    "scale": event["scale"],
                    "params": event["params"],
                    "user_id": event["user_id"],
                }
            )
        )

    async def object_updated_broadcast(self, event):
        """Трансляция обновления объекта (только другим пользователям)"""
        if event["user_id"] != self.user_id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "object_updated",
                        "server_id": event["server_id"],
                        "position": event.get("position"),
                        "rotation": event.get("rotation"),
                        "scale": event.get("scale"),
                        "params": event.get("params"),
                        "user_id": event["user_id"],
                    }
                )
            )

    async def object_deleted(self, event):
        """Трансляция удаления объекта"""
        if event["user_id"] != self.user_id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "object_deleted",
                        "server_id": event["server_id"],
                    }
                )
            )

    async def cursor_moved(self, event):
        """Трансляция перемещения курсора"""
        if event["user_id"] != self.user_id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "cursor_moved",
                        "user_id": event["user_id"],
                        "color": event["color"],
                        "position": event["position"],
                    }
                )
            )

    async def user_joined(self, event):
        """Оповещение о новом пользователе"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "cursor_moved",
                    "user_id": event["user_id"],
                    "color": event["color"],
                    "position": event["position"],
                }
            )
        )

    async def user_left(self, event):
        """Оповещение об уходе пользователя"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_left",
                    "user_id": event["user_id"],
                }
            )
        )
