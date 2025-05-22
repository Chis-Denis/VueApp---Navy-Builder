class WebSocketService {
    constructor() {
        this.ws = null;
        this.subscribers = new Set();
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        if (this.isConnecting) return;
        this.isConnecting = true;

        try {
            this.ws = new WebSocket('ws://127.0.0.1:8000/ws');

            this.ws.onopen = () => {
                console.log('WebSocket connected successfully');
                this.isConnecting = false;
                this.reconnectAttempts = 0;
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.notifySubscribers(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onclose = () => {
                console.log('WebSocket connection closed');
                this.isConnecting = false;
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnecting = false;
                this.attemptReconnect();
            };
        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.isConnecting = false;
            this.attemptReconnect();
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            setTimeout(() => this.connect(), 5000);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }

    subscribe(callback) {
        if (typeof callback !== 'function') {
            console.error('Subscriber must be a function');
            return () => {};
        }
        this.subscribers.add(callback);
        return () => this.subscribers.delete(callback);
    }

    notifySubscribers(data) {
        this.subscribers.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('Error in subscriber callback:', error);
            }
        });
    }

    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
            return true;
        } else {
            console.error('WebSocket not connected. Message not sent:', message);
            this.connect(); // Try to reconnect
            return false;
        }
    }
}

export const websocketService = new WebSocketService(); 