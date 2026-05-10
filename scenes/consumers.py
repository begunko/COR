import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer

USER_COLORS = [
    "#ff6600",
    "#00cc44",
    "#3388ff",
    "#ff3377",
    "#ffcc00",
    "#33cccc",
    "#cc33ff",
    "#ff8833",
]


class ChunkConsumer(AsyncWebsocketConsumer):
    rooms = {}

    async def connect(self):
        self.chunk_id = self.scope["url_route"]["kwargs"]["chunk_id"]
        self.room_group_name = f"chunk_{self.chunk_id}"

        if self.chunk_id not in self.rooms:
            self.rooms[self.chunk_id] = {
                "users": {},
                "cubes": {},
                "next_color": 0,
                "next_cube_id": 0,
            }

        room = self.rooms[self.chunk_id]

        self.user_id = str(len(room["users"]) + 1)
        color_index = room["next_color"] % len(USER_COLORS)
        self.user_color = USER_COLORS[color_index]
        room["next_color"] += 1

        room["users"][self.user_id] = {
            "color": self.user_color,
            "position": {"x": 0, "y": 0, "z": 0},
        }

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(
            text_data=json.dumps(
                {
                    "type": "welcome",
                    "user_id": self.user_id,
                    "color": self.user_color,
                    "cubes": room["cubes"],
                    "cursors": {
                        uid: data
                        for uid, data in room["users"].items()
                        if uid != self.user_id
                    },
                }
            )
        )

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
        room = self.rooms.get(self.chunk_id)
        if room and self.user_id in room["users"]:
            del room["users"][self.user_id]

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_left",
                "user_id": self.user_id,
            },
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        room = self.rooms.get(self.chunk_id)
        if not room:
            return

        if data.get("type") in ("cube_move", "object_create", "object_updated"):
            object_id = data.get("object_id") or data.get("cube_id")
            position = data.get("position")
            color = data.get(
                "color", USER_COLORS[room["next_cube_id"] % len(USER_COLORS)]
            )
            obj_type = data.get("object_type", "cube")

            if object_id not in room["cubes"]:
                room["cubes"][object_id] = {
                    "color": color,
                    "position": position,
                    "type": obj_type,
                    "params": data.get("params", {}),
                }
                room["next_cube_id"] += 1
            else:
                room["cubes"][object_id]["position"] = position

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "cube_moved",
                    "cube_id": object_id,
                    "object_type": obj_type,
                    "color": color,
                    "position": position,
                    "rotation": data.get("rotation", {"x": 0, "y": 0, "z": 0}),
                    "scale": data.get("scale", {"x": 1, "y": 1, "z": 1}),
                    "user_id": self.user_id,
                    "params": data.get("params", {}),
                },
            )

        elif data.get("type") == "object_delete":
            object_id = data.get("object_id")
            if object_id and object_id in room["cubes"]:
                del room["cubes"][object_id]
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "object_deleted",
                        "object_id": object_id,
                        "user_id": self.user_id,
                    },
                )

        elif data.get("type") == "cursor_move":
            position = data.get("position")
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

    async def cube_moved(self, event):
        if event["user_id"] != self.user_id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "cube_moved",
                        "cube_id": event["cube_id"],
                        "color": event["color"],
                        "position": event["position"],
                        "rotation": event.get("rotation", {"x": 0, "y": 0, "z": 0}),
                        "scale": event.get("scale", {"x": 1, "y": 1, "z": 1}),
                        "user_id": event["user_id"],
                    }
                )
            )

    async def object_deleted(self, event):
        if event["user_id"] != self.user_id:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "object_deleted",
                        "object_id": event["object_id"],
                    }
                )
            )

    async def cursor_moved(self, event):
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
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_left",
                    "user_id": event["user_id"],
                }
            )
        )
