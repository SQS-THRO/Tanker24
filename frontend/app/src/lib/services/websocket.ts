const API_BASE = typeof window !== 'undefined' 
	? (localStorage.getItem('backend_url') || 'http://127.0.0.1:8000')
	: 'http://127.0.0.1:8000';

export type StationMessage =
	| { type: 'caching_stations'; lat: number; lon: number }
	| { type: 'new_station'; name: string; brand: string; lat: number; lon: number }
	| { type: 'updated_station'; name: string; brand: string; lat: number; lon: number }
	| { type: 'error'; message: string }
	| { type: 'complete'; lat: number; lon: number };

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected';

export interface WebSocketService {
	subscribe(lat: number, lon: number): void;
	onMessage(callback: (message: StationMessage) => void): () => void;
	onStatusChange(callback: (status: ConnectionStatus) => void): () => void;
	disconnect(): void;
}

export function createWebSocketService(): WebSocketService {
	let ws: WebSocket | null = null;
	let messageCallbacks: Set<(message: StationMessage) => void> = new Set();
	let statusCallbacks: Set<(status: ConnectionStatus) => void> = new Set();
	let reconnectAttempts = 0;
	const maxReconnectAttempts = 5;
	let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

	const getStatus = (): ConnectionStatus => {
		if (!ws) return 'disconnected';
		if (ws.readyState === WebSocket.CONNECTING) return 'connecting';
		if (ws.readyState === WebSocket.OPEN) return 'connected';
		return 'disconnected';
	};

	const notifyStatusChange = () => {
		const status = getStatus();
		statusCallbacks.forEach((cb) => cb(status));
	};

	const connect = () => {
		if (ws) {
			ws.close();
		}

		ws = new WebSocket(`${API_BASE.replace('http', 'ws')}/ws/stations`);

		ws.onopen = () => {
			reconnectAttempts = 0;
			notifyStatusChange();
		};

		ws.onmessage = (event) => {
			try {
				const message = JSON.parse(event.data) as StationMessage;
				messageCallbacks.forEach((cb) => cb(message));
			} catch (e) {
				console.error('Failed to parse websocket message:', e);
			}
		};

		ws.onclose = () => {
			notifyStatusChange();
			attemptReconnect();
		};

		ws.onerror = () => {
			ws?.close();
		};

		notifyStatusChange();
	};

	const attemptReconnect = () => {
		if (reconnectAttempts >= maxReconnectAttempts) return;

		reconnectAttempts++;
		const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);

		reconnectTimeout = setTimeout(() => {
			connect();
		}, delay);
	};

	connect();

	return {
		subscribe(lat: number, lon: number) {
			if (ws && ws.readyState === WebSocket.OPEN) {
				ws.send(JSON.stringify({ type: 'subscribe', lat, lon }));
			}
		},

		onMessage(callback: (message: StationMessage) => void) {
			messageCallbacks.add(callback);
			return () => messageCallbacks.delete(callback);
		},

		onStatusChange(callback: (status: ConnectionStatus) => void) {
			statusCallbacks.add(callback);
			callback(getStatus());
			return () => statusCallbacks.delete(callback);
		},

		disconnect() {
			if (reconnectTimeout) {
				clearTimeout(reconnectTimeout);
			}
			if (ws) {
				ws.close();
				ws = null;
			}
			messageCallbacks.clear();
			statusCallbacks.clear();
		}
	};
}
