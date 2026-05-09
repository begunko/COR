export class WebSocketClient {
    constructor(url, handlers = {}) {
        this.url = url;
        this.handlers = handlers;  // { onOpen, onMessage, onClose, onError }
        this.ws = null;
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            if (this.handlers.onOpen) this.handlers.onOpen();
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (this.handlers.onMessage) this.handlers.onMessage(data);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            if (this.handlers.onClose) this.handlers.onClose();
            // Автопереподключение
            setTimeout(() => this.connect(), 2000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (this.handlers.onError) this.handlers.onError(error);
        };
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}