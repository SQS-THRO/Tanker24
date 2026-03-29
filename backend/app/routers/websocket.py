import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.services.station_cache_service import station_cache_service, ws_manager

router = APIRouter()


@router.websocket("/ws/stations")
async def websocket_stations(websocket: WebSocket):
	await websocket.accept()

	queue = await ws_manager.connect()

	try:
		async def receive_messages():
			while True:
				data = await websocket.receive_text()
				try:
					message = json.loads(data)
					if message.get("type") == "subscribe":
						lat = message.get("lat")
						lon = message.get("lon")
						if lat is not None and lon is not None:
							await station_cache_service.enqueue_request(lat, lon, queue)
				except json.JSONDecodeError:
					pass

		async def send_messages():
			while True:
				message = await queue.get()
				await websocket.send_text(message)

		receive_task = asyncio.create_task(receive_messages())
		send_task = asyncio.create_task(send_messages())

		done, pending = await asyncio.wait(
			[receive_task, send_task],
			return_when=asyncio.FIRST_COMPLETED
		)

		for task in pending:
			task.cancel()

	except WebSocketDisconnect:
		pass
	finally:
		await ws_manager.disconnect(queue)
