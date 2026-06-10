from __future__ import annotations

from fastapi import APIRouter, WebSocket
from fastapi_websockets import AsyncWebSocketConsumer, get_channel_layer


router = APIRouter()
channel_layer = get_channel_layer()


class EchoConsumer(AsyncWebSocketConsumer):
    async def receive_text(self, text_data: str) -> None:
        await self.send_json({"message": text_data})


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    consumer = EchoConsumer(layer=channel_layer)
    await consumer(websocket)
