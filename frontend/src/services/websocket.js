class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
  }

  connect() {
    const wsUrl = 'ws://localhost:8000/ws';
    
    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket verbunden');
        this.reconnectAttempts = 0;
        this.notifyListeners('connected', { connected: true });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners(data.type, data);
        } catch (error) {
          console.error('WebSocket Nachricht Parse-Fehler:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket Fehler:', error);
        this.notifyListeners('error', { error });
      };

      this.ws.onclose = () => {
        console.log('WebSocket getrennt');
        this.notifyListeners('disconnected', { connected: false });
        this.attemptReconnect();
      };
    } catch (error) {
      console.error('WebSocket Verbindung fehlgeschlagen:', error);
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Verbindungsversuch ${this.reconnectAttempts}/${this.maxReconnectAttempts}...`);
      setTimeout(() => this.connect(), this.reconnectDelay);
    } else {
      console.error('Max Verbindungsversuche erreicht');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType).push(callback);
  }

  off(eventType, callback) {
    if (this.listeners.has(eventType)) {
      const callbacks = this.listeners.get(eventType);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  notifyListeners(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach(callback => {
        callback(data);
      });
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket nicht verbunden');
    }
  }
}

export default new WebSocketService();
