# Broker API Integration - Übersicht

Sammlung von Brokern mit API-Zugang für automatisierten Handel.

## 🌟 Empfohlene Broker (Gut dokumentiert & Developer-freundlich)

### 1. **Alpaca Markets** ⭐⭐⭐⭐⭐
- **Region:** USA
- **Asset-Klassen:** Aktien, ETFs, Crypto
- **API:** REST + WebSocket
- **Dokumentation:** https://alpaca.markets/docs/
- **Python SDK:** ✅ `alpaca-trade-api`
- **Paper Trading:** ✅ Kostenlos
- **Kosten:** Kommissionsfrei
- **Besonderheiten:**
  - Sehr developer-freundlich
  - Ausgezeichnete Dokumentation
  - Market Data API inklusive
  - Ideal für Anfänger

**Implementierungsstatus:** ✅ Bereits implementiert

---

### 2. **Interactive Brokers (IBKR)** ⭐⭐⭐⭐
- **Region:** Global
- **Asset-Klassen:** Aktien, Options, Futures, Forex, Bonds, CFDs
- **API:** TWS API, Client Portal API, IB Gateway
- **Dokumentation:** https://www.interactivebrokers.com/en/trading/ib-api.php
- **Python SDK:** ✅ `ib_insync`, `ibapi`
- **Paper Trading:** ✅ Verfügbar
- **Kosten:** Variable Kommissionen
- **Besonderheiten:**
  - Größte Asset-Auswahl
  - Globale Märkte
  - Professionelle Features
  - Komplexere Integration

**Empfohlene Library:** `ib_insync`

---

### 3. **Trading212** ⭐⭐⭐⭐
- **Region:** EU, UK
- **Asset-Klassen:** Aktien, ETFs, CFDs, Forex, Crypto
- **API:** REST API (Beta/auf Anfrage)
- **Dokumentation:** https://trading212.com/
- **Python SDK:** ❌ Community-Lösungen verfügbar
- **Paper Trading:** ✅ Demo-Account
- **Kosten:** Kommissionsfrei (Aktien/ETFs)
- **Besonderheiten:**
  - Sehr populär in Europa
  - API-Zugang limitiert/auf Anfrage
  - Gute Mobile App
  - Deutscher Support

**Status:** API nicht öffentlich verfügbar - Kontakt zu Trading212 erforderlich

---

### 4. **TD Ameritrade (Schwab)** ⭐⭐⭐⭐
- **Region:** USA
- **Asset-Klassen:** Aktien, Options, ETFs, Mutual Funds
- **API:** REST API
- **Dokumentation:** https://developer.tdameritrade.com/
- **Python SDK:** ✅ `td-ameritrade-python-api`
- **Paper Trading:** ✅ Paper Money Account
- **Kosten:** Kommissionsfrei (Aktien)
- **Besonderheiten:**
  - Thinkorswim Integration
  - Gute Market Data
  - OAuth2 Authentifizierung

**Hinweis:** Wird zu Schwab migriert (2024-2026)

---

### 5. **OANDA** ⭐⭐⭐⭐
- **Region:** Global (außer USA für Retail)
- **Asset-Klassen:** Forex, CFDs, Metalle
- **API:** REST + Streaming API
- **Dokumentation:** https://developer.oanda.com/
- **Python SDK:** ✅ `oandapyV20`
- **Paper Trading:** ✅ Demo-Account
- **Kosten:** Spreads
- **Besonderheiten:**
  - Spezialist für Forex
  - Ausgezeichnete API
  - Sehr gute Dokumentation
  - Sub-Pip Pricing

---

### 6. **Binance** ⭐⭐⭐⭐
- **Region:** Global (mit Einschränkungen)
- **Asset-Klassen:** Crypto, Futures, Options
- **API:** REST + WebSocket
- **Dokumentation:** https://binance-docs.github.io/apidocs/
- **Python SDK:** ✅ `python-binance`
- **Paper Trading:** ✅ Testnet
- **Kosten:** 0.1% Trading Fee
- **Besonderheiten:**
  - Größte Crypto Exchange
  - Sehr schnelle API
  - Hohe Liquidität
  - Margin Trading

---

### 7. **Kraken** ⭐⭐⭐⭐
- **Region:** Global
- **Asset-Klassen:** Crypto, Futures
- **API:** REST + WebSocket
- **Dokumentation:** https://docs.kraken.com/rest/
- **Python SDK:** ✅ `krakenex`, `python-kraken-sdk`
- **Paper Trading:** ❌ (nur mit echtem Geld)
- **Kosten:** 0.16-0.26% Maker/Taker
- **Besonderheiten:**
  - Reguliert & sicher
  - Gute EU-Abdeckung
  - Staking verfügbar

---

## 🏦 Weitere Broker mit API

### 8. **eToro** ⭐⭐⭐
- **Region:** Global
- **Asset-Klassen:** Aktien, Crypto, CFDs, Forex
- **API:** Teilweise verfügbar (Partner-Programm)
- **Paper Trading:** ✅ Demo-Account
- **Besonderheiten:** Social Trading, Copy Trading
- **Status:** API sehr limitiert

---

### 9. **DEGIRO** ⭐⭐
- **Region:** EU
- **Asset-Klassen:** Aktien, ETFs, Options, Futures
- **API:** ❌ Keine offizielle API
- **Besonderheiten:** Sehr günstig, aber keine API
- **Alternative:** Inoffizielle Python-Libraries (nicht empfohlen)

---

### 10. **Saxo Bank** ⭐⭐⭐⭐
- **Region:** Global
- **Asset-Klassen:** Aktien, Forex, CFDs, Futures, Options, Bonds
- **API:** OpenAPI
- **Dokumentation:** https://www.developer.saxo/
- **Paper Trading:** ✅ Simulation
- **Kosten:** Professional Pricing
- **Besonderheiten:** Professionelle Plattform, hohe Standards

---

### 11. **Coinbase Pro** ⭐⭐⭐⭐
- **Region:** USA, EU
- **Asset-Klassen:** Crypto
- **API:** REST + WebSocket
- **Dokumentation:** https://docs.cloud.coinbase.com/
- **Python SDK:** ✅ `coinbase-advanced-py`
- **Paper Trading:** ❌
- **Besonderheiten:** Sehr populär, gute Liquidität

---

### 12. **Dukascopy** ⭐⭐⭐
- **Region:** EU, Schweiz
- **Asset-Klassen:** Forex, CFDs, Binäre Optionen
- **API:** JForex API, REST API
- **Dokumentation:** https://www.dukascopy.com/
- **Paper Trading:** ✅ Demo
- **Besonderheiten:** Schweizer Bank, ECN Trading

---

### 13. **IG Markets** ⭐⭐⭐
- **Region:** UK, EU, Global
- **Asset-Klassen:** CFDs, Spread Betting, Forex
- **API:** REST API
- **Dokumentation:** https://labs.ig.com/
- **Python SDK:** Community-Libraries
- **Paper Trading:** ✅ Demo
- **Besonderheiten:** Großer CFD Broker

---

### 14. **Bitfinex** ⭐⭐⭐
- **Region:** Global
- **Asset-Klassen:** Crypto
- **API:** REST + WebSocket
- **Dokumentation:** https://docs.bitfinex.com/
- **Python SDK:** ✅ `bitfinex-api-py`
- **Paper Trading:** ❌
- **Besonderheiten:** Margin Trading, Lending

---

### 15. **FTX** ⚠️
- **Status:** INSOLVENT (November 2022)
- **Hinweis:** Nicht mehr verfügbar

---

### 16. **Bybit** ⭐⭐⭐⭐
- **Region:** Global
- **Asset-Klassen:** Crypto Derivatives, Spot
- **API:** REST + WebSocket
- **Dokumentation:** https://bybit-exchange.github.io/docs/
- **Python SDK:** ✅ `pybit`
- **Paper Trading:** ✅ Testnet
- **Besonderheiten:** Hohe Leverage, gute API

---

### 17. **Robinhood** ⭐⭐
- **Region:** USA
- **Asset-Klassen:** Aktien, Options, Crypto
- **API:** ❌ Keine offizielle API
- **Besonderheiten:** Sehr populär, aber keine API
- **Alternative:** Inoffizielle Libraries (gegen ToS)

---

### 18. **Plus500** ⭐⭐
- **Region:** Global
- **Asset-Klassen:** CFDs
- **API:** ❌ Keine API verfügbar
- **Besonderheiten:** Nur WebTrader/App

---

### 19. **XTB** ⭐⭐⭐
- **Region:** EU, Global
- **Asset-Klassen:** CFDs, Forex, Aktien
- **API:** xStation API
- **Dokumentation:** http://developers.xstore.pro/
- **Python SDK:** Community-Lösungen
- **Paper Trading:** ✅ Demo
- **Besonderheiten:** Gute EU-Präsenz

---

### 20. **Questrade** ⭐⭐⭐
- **Region:** Kanada
- **Asset-Klassen:** Aktien, Options, ETFs
- **API:** REST API
- **Dokumentation:** https://www.questrade.com/api
- **Python SDK:** Community-Libraries
- **Paper Trading:** ✅
- **Besonderheiten:** Größter Discount Broker in Kanada

---

## 🌍 Regionale Spezialisten

### Deutschland/EU
- **Trading212** - Sehr populär, API limitiert
- **DEGIRO** - Keine offizielle API
- **Scalable Capital** - Keine API
- **Trade Republic** - Keine API
- **Consorsbank** - Keine API

### UK
- **IG Markets** - API verfügbar
- **Saxo Bank** - Professionelle API
- **Hargreaves Lansdown** - Keine API

### Schweiz
- **Dukascopy** - JForex API
- **Swissquote** - API für institutionelle Kunden

---

## 📊 Vergleichstabelle

| Broker | Region | API | Paper Trading | Python SDK | Empfehlung |
|--------|--------|-----|---------------|------------|------------|
| Alpaca | USA | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| IBKR | Global | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| TD Ameritrade | USA | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ |
| OANDA | Global | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ |
| Binance | Global | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ |
| Kraken | Global | ✅ | ❌ | ✅ | ⭐⭐⭐⭐ |
| Trading212 | EU | ⚠️ | ✅ | ❌ | ⭐⭐⭐ |
| Saxo Bank | Global | ✅ | ✅ | ⚠️ | ⭐⭐⭐⭐ |
| Coinbase Pro | USA/EU | ✅ | ❌ | ✅ | ⭐⭐⭐⭐ |
| Bybit | Global | ✅ | ✅ | ✅ | ⭐⭐⭐⭐ |

---

## 🛠️ Integration in TheMoneyBroker

### Bereits implementiert:
- ✅ Alpaca Markets

### Einfach zu integrieren:
1. **OANDA** - Ähnliche API-Struktur
2. **Binance** - Gute Python-Library
3. **TD Ameritrade** - Gut dokumentiert

### Mittlerer Aufwand:
1. **Interactive Brokers** - Komplexere API
2. **Saxo Bank** - Professional Features
3. **Bybit** - Crypto Derivatives

### Schwierig/Eingeschränkt:
1. **Trading212** - API-Zugang limitiert
2. **DEGIRO** - Keine offizielle API
3. **Robinhood** - Gegen ToS

---

## 💡 Empfehlungen

### Für Anfänger:
- **Alpaca** - Perfekt zum Lernen
- **Binance** (Testnet) - Für Crypto

### Für europäische Trader:
- **Interactive Brokers** - Beste Gesamtoption
- **OANDA** - Für Forex
- **Trading212** - Wenn API-Zugang möglich

### Für professionelles Trading:
- **Interactive Brokers** - Umfassendste Lösung
- **Saxo Bank** - Professional Grade
- **OANDA** - Forex Spezialist

### Für Crypto:
- **Binance** - Größte Exchange
- **Kraken** - Sicher & reguliert
- **Bybit** - Derivatives

---

## 📝 Nächste Schritte für Integration

1. **Broker auswählen** basierend auf:
   - Ihrer Region
   - Gewünschten Asset-Klassen
   - API-Verfügbarkeit
   - Kosten

2. **Account erstellen:**
   - Zuerst Paper/Demo-Account
   - API-Credentials generieren
   - Rate Limits prüfen

3. **Integration entwickeln:**
   - `BaseBroker` Interface implementieren
   - SDK/Library einbinden
   - Tests schreiben

4. **Testen:**
   - Paper Trading ausgiebig testen
   - Risk Management validieren
   - Erst dann Live-Trading

---

## ⚠️ Wichtige Hinweise

- **Regulierung:** Prüfen Sie ob der Broker in Ihrer Region zugelassen ist
- **API-Limits:** Beachten Sie Rate Limits
- **Kosten:** Prüfen Sie API-Gebühren und Handelskosten
- **Sicherheit:** Verwenden Sie API-Keys nur mit notwendigen Rechten
- **Testing:** IMMER erst Paper Trading verwenden
- **Backup:** Haben Sie einen Backup-Broker

---

## 📚 Weitere Ressourcen

- [Alpaca Docs](https://alpaca.markets/docs/)
- [IBKR API](https://www.interactivebrokers.com/en/trading/ib-api.php)
- [OANDA API](https://developer.oanda.com/)
- [Binance API](https://binance-docs.github.io/apidocs/)

---

**Stand:** Februar 2026
**Letzte Aktualisierung:** 01.02.2026
