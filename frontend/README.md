# Trading Bot UI - React Frontend

Moderne Web-UI für TheMoneyBroker Trading Bot.

## Features

- 📊 **Dashboard** - Echtzeit-Übersicht über Portfolio, Positionen und Performance
- ⚙️ **Konfiguration** - Risk Management und Trading-Parameter
- 🎯 **Strategien** - Trading-Strategien verwalten und hinzufügen
- 📝 **Orders** - Order-Verwaltung und manuelle Trades
- 🔧 **Einstellungen** - Broker-Verbindung konfigurieren
- 🔴 **Live-Updates** - WebSocket-Verbindung für Echtzeit-Daten
- 🎨 **Modernes Design** - Tailwind CSS UI

## Installation

### Backend starten

1. **Python Dependencies installieren:**
```bash
cd ..
pip install -r requirements.txt
```

2. **API-Server starten:**
```bash
cd api
python main.py
```

Der Backend-Server läuft auf `http://localhost:8000`

### Frontend starten

1. **Node Dependencies installieren:**
```bash
cd frontend
npm install
```

2. **Development Server starten:**
```bash
npm run dev
```

Die UI ist verfügbar auf `http://localhost:5173`

## Verwendung

### 1. Broker verbinden

- Navigieren Sie zu **Einstellungen**
- Geben Sie Ihre Alpaca API Credentials ein
- Wählen Sie "Paper Trading" für Tests
- Klicken Sie auf "Mit Broker verbinden"

### 2. Risk Management konfigurieren

- Navigieren Sie zu **Konfiguration**
- Setzen Sie Ihre Risk-Parameter:
  - Maximale Positionsgröße
  - Tägliches Verlust-Limit
  - Maximale offene Positionen
  - Risiko pro Trade
- Speichern Sie die Konfiguration

### 3. Strategie hinzufügen

- Navigieren Sie zu **Strategien**
- Klicken Sie auf "Strategie hinzufügen"
- Konfigurieren Sie die SMA Crossover Parameter
- Aktivieren Sie die Strategie

### 4. Bot starten

- Klicken Sie auf den **Start**-Button im Header
- Der Bot analysiert nun die Märkte automatisch
- Beobachten Sie Positionen und Orders im Dashboard

## Architektur

```
frontend/
├── src/
│   ├── components/      # React Komponenten
│   │   └── Layout.jsx   # Hauptlayout mit Navigation
│   ├── pages/           # Seiten
│   │   ├── Dashboard.jsx
│   │   ├── Configuration.jsx
│   │   ├── Strategies.jsx
│   │   ├── Orders.jsx
│   │   └── Settings.jsx
│   ├── services/        # API & WebSocket Services
│   │   ├── api.js
│   │   └── websocket.js
│   ├── App.jsx          # Haupt-App Komponente
│   ├── main.jsx         # Entry Point
│   └── index.css        # Tailwind Styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## API Endpoints

### Broker
- `POST /broker/connect` - Broker verbinden
- `POST /broker/disconnect` - Broker trennen

### Account & Trading
- `GET /account` - Account-Informationen
- `GET /positions` - Alle Positionen
- `GET /orders` - Alle Orders
- `POST /orders` - Order platzieren
- `DELETE /orders/{id}` - Order stornieren

### Configuration
- `POST /risk/configure` - Risk Management konfigurieren
- `GET /strategies` - Strategien abrufen
- `POST /strategies` - Strategie hinzufügen

### Bot Control
- `POST /bot/start` - Bot starten
- `POST /bot/stop` - Bot stoppen
- `GET /bot/status` - Bot-Status abrufen

### WebSocket
- `WS /ws` - Live-Updates für Portfolio und Bot-Status

## Development

### Build für Production

```bash
npm run build
```

Die Production-Build wird in `dist/` erstellt.

### Linting

```bash
npm run lint
```

## Technologie-Stack

- **React 18** - UI Framework
- **Vite** - Build Tool & Dev Server
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **Axios** - HTTP Client
- **Recharts** - Charts & Visualisierung
- **Lucide React** - Icons
- **WebSocket** - Live-Updates

## Konfiguration

### API Proxy

Vite ist konfiguriert um API-Requests zu proxyen:

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

### Tailwind Customization

Passen Sie das Design in `tailwind.config.js` an:

```javascript
theme: {
  extend: {
    colors: {
      primary: { ... }
    }
  }
}
```

## Sicherheit

- ✅ API Keys werden nur im Browser-State gespeichert
- ✅ CORS korrekt konfiguriert
- ✅ Paper Trading standardmäßig aktiviert
- ⚠️ Verwenden Sie HTTPS in Production
- ⚠️ Implementieren Sie Authentication für Production

## Troubleshooting

### Backend nicht erreichbar

- Prüfen Sie ob der API-Server läuft (`http://localhost:8000`)
- Überprüfen Sie die Proxy-Konfiguration in `vite.config.js`

### WebSocket-Verbindung fehlgeschlagen

- Stellen Sie sicher dass der Backend-Server läuft
- Prüfen Sie die WebSocket-URL in `src/services/websocket.js`

### Broker-Verbindung fehlgeschlagen

- Überprüfen Sie Ihre API Credentials
- Verwenden Sie die richtige Base URL (Paper Trading)
- Prüfen Sie Alpaca API Status

## Screenshots

### Dashboard
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)

### Konfiguration
![Configuration](https://via.placeholder.com/800x400?text=Configuration+Screenshot)

### Live Trading
![Trading](https://via.placeholder.com/800x400?text=Trading+Screenshot)

## Lizenz

MIT License

## Support

Bei Fragen oder Problemen öffnen Sie ein Issue im Repository.
