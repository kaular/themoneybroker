# TheMoneyBroker - Automated Trading Bot

Ein automatisiertes Trading-System zur Interaktion mit Broker-APIs und automatischer Trade-Ausführung.

## Features

- 🔌 Modulare Broker-API Integration
- 📊 Flexibles Trading-Strategy Framework
- ⚡ Automatische Order-Ausführung
- 🛡️ Risk Management System
- 📝 Umfassendes Logging & Monitoring
- 🔐 Sichere Credential-Verwaltung

## Installation

1. Repository klonen:
```bash
git clone <your-repo-url>
cd themoneybroker
```

2. Virtual Environment erstellen:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Dependencies installieren:
```bash
pip install -r requirements.txt
```

4. Konfiguration einrichten:
```bash
copy .env.example .env
```

5. `.env` mit Ihren API-Credentials ausfüllen

## Konfiguration

Erstellen Sie eine `.env` Datei mit folgenden Parametern:

```env
# Broker API Credentials
BROKER_API_KEY=your_api_key_here
BROKER_API_SECRET=your_api_secret_here
BROKER_BASE_URL=https://api.broker.com

# Trading Configuration
TRADING_MODE=paper  # paper oder live
MAX_POSITION_SIZE=1000
RISK_PERCENTAGE=0.02

# Logging
LOG_LEVEL=INFO
```

## Verwendung

### Trading Bot starten:
```bash
python main.py
```

### Eigene Trading-Strategie implementieren:

```python
from src.strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def analyze(self, market_data):
        # Ihre Analyse-Logik
        return signal
    
    def generate_signals(self, data):
        # Signal-Generierung
        return signals
```

## Projekt-Struktur

```
themoneybroker/
├── src/
│   ├── brokers/          # Broker-API Integrationen
│   ├── strategies/       # Trading-Strategien
│   ├── execution/        # Order-Execution Engine
│   ├── risk/            # Risk Management
│   └── utils/           # Utility-Funktionen
├── config/              # Konfigurationsdateien
├── logs/                # Log-Dateien
├── tests/               # Unit-Tests
├── main.py             # Haupt-Anwendung
└── requirements.txt    # Python Dependencies
```

## Unterstützte Broker

- Interactive Brokers (geplant)
- Alpaca Trading (geplant)
- Trading212 (geplant)
- Weitere können hinzugefügt werden

## Sicherheitshinweise

⚠️ **WICHTIG**: 
- Starten Sie immer im Paper-Trading Modus
- Testen Sie Strategien ausgiebig vor Live-Trading
- Verwenden Sie niemals mehr Kapital als Sie bereit sind zu verlieren
- Speichern Sie API-Keys niemals im Code

## Lizenz

MIT License

## Disclaimer

Diese Software dient nur zu Bildungszwecken. Der Handel mit Finanzinstrumenten birgt erhebliche Risiken. Verwenden Sie diese Software auf eigenes Risiko.
