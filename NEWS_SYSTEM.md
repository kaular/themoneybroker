# News Feed System - Quick Start Guide

## 🚀 Überblick

Das News Feed System bietet Real-time Finanznachrichten mit AI-basierter Sentiment-Analyse und automatischer Integration in den Growth Scanner.

## 📊 Features

### 1. **News Feed**
- Real-time News von Alpaca API
- Symbol-spezifische News
- Market-weite News (SPY, QQQ, DIA)
- Zeitbereich-Filter (1h bis 1 Woche)

### 2. **Sentiment Analysis**
- NLP mit 100+ Finanz-Keywords
- Score: -1.0 (sehr bearish) bis +1.0 (sehr bullish)
- Confidence Level (0-1)
- Emoji-Indikatoren: 🚀 📈 ➡️ 📉 💥

### 3. **News Score für Growth Scanner**
- Konvertiert Sentiment zu 0-100 Skala
- 15% des Growth Scanner Scores
- Boost für sehr bullische News
- Warnung bei bearish News

### 4. **Background Monitoring**
- Automatische Überwachung alle 5 Minuten
- Alerts bei wichtigen News
- WebSocket Notifications
- Deduplizierung (keine doppelten Alerts)

## 🔧 Setup

### Backend starten:
```bash
cd C:\Users\Arthur\themoneybroker
$env:PYTHONPATH="$PWD"
python api/main.py
```

### Frontend starten:
```bash
cd frontend
npm run dev
```

## 📡 API Endpoints

### News Feed initialisieren
```http
POST /news/initialize
```

### Aktuelle News abrufen
```http
GET /news/latest?symbols=TSLA,NVDA&limit=50&hours_back=24
```

### Symbol-spezifische News
```http
GET /news/symbol/TSLA?limit=20
```
Response enthält:
- `articles`: Liste aller Artikel mit Sentiment
- `sentiment_summary`: Aggregierte Statistik
- `news_score`: 0-100 Score für Scanner

### Market News
```http
GET /news/market?limit=50
```

### Sentiment-Analyse
```http
GET /news/sentiment/TSLA
```

### News Monitor starten
```http
POST /news/monitor/start?check_interval=300&symbols=TSLA,NVDA&min_confidence=0.7
```
Parameters:
- `check_interval`: Sekunden zwischen Checks (default: 300)
- `symbols`: Komma-getrennte Symbole (None = alle)
- `min_confidence`: Min. Confidence für Alerts (0-1)

### Monitor stoppen
```http
POST /news/monitor/stop
```

### Monitor Status
```http
GET /news/monitor/status
```

## 🎯 Growth Scanner Integration

Der Growth Scanner nutzt automatisch den News Score, wenn ein News Feed verfügbar ist:

```python
# Python Backend
from src.scanners import GrowthStockScanner
from src.news import NewsFeed

news_feed = NewsFeed(broker, alert_manager)
scanner = GrowthStockScanner(broker, news_feed=news_feed)

results = await scanner.scan_universe(min_score=60)
# Results enthalten jetzt news_score!
```

### Score-Gewichtung:
- 25% Revenue Growth
- 22% Relative Strength
- 18% Momentum
- 15% Volume
- **15% News Sentiment** ← Neu!
- 5% Sektor-Bonus

## 📈 Sentiment-Klassifizierung

### Positive Keywords (50+):
surge, soar, rally, breakthrough, bullish, outperform, strong, beat, exceed, accelerate, breakthrough, innovation, record, milestone, surge, boom, upgrade, optimistic, bullish, momentum, growth, profit, revenue, expansion, launch, partnership, acquisition, approval, success, breakthrough, revolutionary, disruptive, leader, dominant, competitive, efficient, productive, lucrative, profitable, upside, potential, opportunity, promising, favorable, positive, gains, winning, champion, stellar, robust, healthy, thriving

### Negative Keywords (50+):
plunge, crash, decline, lawsuit, bearish, underperform, weak, miss, warning, drop, fall, loss, deficit, debt, bankruptcy, recession, downturn, slump, collapse, failure, scandal, fraud, investigation, layoff, downgrade, pessimistic, bearish, risk, threat, concern, issue, problem, challenge, obstacle, delay, setback, shortfall, disappointment, negative, losses, losing, struggle, vulnerable, weak, fragile, unstable, volatile, uncertain, risky, dangerous

### Intensifiers:
very, extremely, significantly, substantially, dramatically, sharply, heavily, massive, huge, tremendous

### Negations:
not, no, never, without, lack, fails, unable

## 💡 Beispiele

### Sehr bullisch (Score > 70):
- "Tesla surges on record delivery numbers" → 🚀 Bullish (0.85)
- "Company announces breakthrough in AI technology" → 🚀 Bullish (0.90)

### Bullish (Score 50-70):
- "Stock rises after earnings beat" → 📈 Bullish (0.55)

### Neutral (Score 40-60):
- "Company announces quarterly results" → ➡️ Neutral (0.05)

### Bearish (Score 30-50):
- "Stock drops on weak guidance" → 📉 Bearish (-0.50)

### Sehr bearish (Score < 30):
- "Company stock plunges after lawsuit" → 💥 Bearish (-0.85)

## 🔔 Alerts

Automatische Alerts werden gesendet wenn:
- Confidence > 70%
- |Sentiment Score| > 0.6 (sehr bullish ODER sehr bearish)

Alert-Kanäle:
- Email (SMTP)
- Discord (Webhook)
- Telegram (Bot)
- Console (Logging)
- WebSocket (Real-time UI Updates)

## 🎨 Frontend Features

### News Feed Page (`/news`)
- Real-time News-Liste mit Sentiment
- Symbol-Filter & Suche
- Sentiment-Filter (Bullish/Bearish/Neutral)
- Zeitbereich-Filter
- Sentiment Summary Cards
- Monitor Start/Stop Buttons

### Growth Scanner Update
- Neue Spalte "News Sentiment"
- Farb-Codierung: Grün (>60), Rot (<40), Grau (neutral)
- Emoji-Indikatoren
- News Score in Scanner-Ergebnissen

## 🛠️ Technische Details

### News Monitor
- **Klasse**: `NewsMonitor`
- **Config**: `NewsMonitorConfig`
- **Loop**: Asyncio Task
- **Deduplizierung**: Set mit gesehenen Article IDs (max 1000)
- **Performance**: Cached IDs, nur neue Artikel verarbeitet

### Sentiment Analyzer
- **Klasse**: `SentimentAnalyzer`
- **Methode**: Keyword-basiertes NLP
- **Keywords**: 100+ Finanz-Begriffe
- **Features**: Negation-Handling, Intensifiers
- **Output**: Score, Label, Confidence, Keywords

### News Feed Manager
- **Klasse**: `NewsFeed`
- **API**: Alpaca News API
- **Caching**: Nein (immer fresh data)
- **Rate Limiting**: Berücksichtigt Alpaca Limits

## 🚨 Troubleshooting

### "News Feed not initialized"
```python
# Backend
POST /news/initialize
```

### "Broker not connected"
```python
# Erst Broker verbinden
POST /broker/connect
# Dann News initialisieren
POST /news/initialize
```

### Keine News gefunden
- Prüfe ob Symbole korrekt sind (Großbuchstaben)
- Prüfe Zeitbereich (hours_back)
- Manche Symbole haben wenig News

### Monitor startet nicht
- Prüfe ob News Feed initialisiert ist
- Prüfe Broker-Verbindung
- Prüfe Logs für Fehler

## 📊 Performance

- **News Fetch**: ~1-3s (abhängig von Anzahl)
- **Sentiment Analysis**: <100ms pro Artikel
- **Monitor Check**: ~2-5s alle 5 Minuten
- **Memory**: ~1MB pro 1000 gecachte IDs

## 🔮 Zukunft

Geplante Features:
- [ ] Multi-Source Integration (NewsAPI.org, Finnhub)
- [ ] Historical News Correlation
- [ ] News Impact auf Preis-Bewegungen
- [ ] Custom Keyword-Sets pro Sektor
- [ ] Machine Learning Sentiment Model
- [ ] News-basierte Trading Signale

## 📞 Support

Bei Fragen oder Problemen:
1. Logs prüfen: `logs/trading.log`
2. Monitor Status prüfen: `GET /news/monitor/status`
3. News Feed testen: `GET /news/latest?limit=5`
