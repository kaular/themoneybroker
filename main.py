"""
TheMoneyBroker - Automatisierter Trading Bot
Main Application
"""
import time
import sys
from datetime import datetime, timedelta
from typing import List

from src.utils import config, setup_logger
from src.brokers import AlpacaBroker
from src.strategies import SMAStrategy, Signal
from src.risk import RiskManager, RiskLimits
from src.execution import ExecutionEngine


class TradingBot:
    """Hauptklasse für den Trading Bot"""
    
    def __init__(self):
        # Setup Logger
        self.logger = setup_logger(
            name="TradingBot",
            log_level=config.LOG_LEVEL,
            log_file=config.get_log_path()
        )
        
        self.logger.info("=" * 60)
        self.logger.info("TheMoneyBroker - Trading Bot startet...")
        self.logger.info("=" * 60)
        
        # Validiere Konfiguration
        is_valid, errors = config.validate()
        if not is_valid:
            self.logger.error("❌ Ungültige Konfiguration! Folgende Fehler gefunden:")
            for error in errors:
                self.logger.error(f"   • {error}")
            self.logger.error("\nBitte korrigieren Sie die .env Datei und starten Sie neu.")
            sys.exit(1)
        
        # Trading Mode
        mode = "PAPER TRADING" if config.is_paper_trading() else "⚠️  LIVE TRADING ⚠️"
        self.logger.info(f"Modus: {mode}")
        
        # Initialisiere Komponenten
        self.broker = None
        self.risk_manager = None
        self.execution_engine = None
        self.strategies: List = []
        
        self._setup_components()
    
    def _setup_components(self):
        """Initialisiert alle Komponenten"""
        try:
            # Broker
            self.logger.info("Verbinde mit Broker...")
            self.broker = AlpacaBroker(
                api_key=config.BROKER_API_KEY,
                api_secret=config.BROKER_API_SECRET,
                base_url=config.BROKER_BASE_URL
            )
            
            if not self.broker.connect():
                raise RuntimeError("Broker-Verbindung fehlgeschlagen")
            
            # Account Info
            account = self.broker.get_account_info()
            self.logger.info(f"✓ Verbunden! Portfolio-Wert: ${account.portfolio_value:,.2f}")
            self.logger.info(f"  Bargeld: ${account.cash:,.2f}")
            self.logger.info(f"  Kaufkraft: ${account.buying_power:,.2f}")
            
            # Risk Manager
            self.logger.info("Initialisiere Risk Manager...")
            risk_limits = RiskLimits(
                max_position_size=config.MAX_POSITION_SIZE,
                max_daily_loss=config.MAX_DAILY_LOSS,
                max_open_positions=config.MAX_OPEN_POSITIONS,
                risk_per_trade=config.RISK_PERCENTAGE
            )
            self.risk_manager = RiskManager(risk_limits)
            
            # Execution Engine
            self.logger.info("Initialisiere Execution Engine...")
            self.execution_engine = ExecutionEngine(self.broker, self.risk_manager)
            
            # Strategien
            self.logger.info("Lade Trading-Strategien...")
            self.strategies.append(
                SMAStrategy(
                    name="SMA 20/50 Crossover",
                    short_window=20,
                    long_window=50
                )
            )
            self.logger.info(f"✓ {len(self.strategies)} Strategie(n) geladen")
            
            self.logger.info("✓ Alle Komponenten initialisiert")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Komponenten-Initialisierung: {e}")
            sys.exit(1)
    
    def analyze_markets(self):
        """Analysiert die Märkte und generiert Signale"""
        self.logger.info("-" * 60)
        self.logger.info("Analysiere Märkte...")
        
        symbols = config.DEFAULT_SYMBOLS
        
        for symbol in symbols:
            try:
                # Hole historische Daten
                end_date = datetime.now()
                start_date = end_date - timedelta(days=100)
                
                data = self.broker.get_historical_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    timeframe="1Day"
                )
                
                if data is None or data.empty:
                    self.logger.warning(f"{symbol}: Keine Daten verfügbar")
                    continue
                
                # Analysiere mit allen Strategien
                for strategy in self.strategies:
                    if not strategy.is_enabled():
                        continue
                    
                    signal = strategy.analyze(data, symbol)
                    
                    if signal.signal != Signal.HOLD:
                        self.logger.info(
                            f"📊 {symbol}: {signal.signal.value.upper()} Signal "
                            f"(Stärke: {signal.strength:.2%}, Strategie: {strategy.name})"
                        )
                        
                        # Führe Signal aus
                        order = self.execution_engine.execute_signal(signal)
                        
                        if order:
                            self.logger.info(f"   Order ID: {order.order_id}")
                    
            except Exception as e:
                self.logger.error(f"Fehler bei Analyse von {symbol}: {e}")
    
    def monitor_positions(self):
        """Überwacht offene Positionen"""
        try:
            positions = self.broker.get_positions()
            
            if positions:
                self.logger.info(f"📊 {len(positions)} offene Position(en):")
                for pos in positions:
                    pnl_pct = (pos.unrealized_pnl / (pos.quantity * pos.entry_price)) * 100
                    self.logger.info(
                        f"   {pos.symbol}: {pos.quantity} @ ${pos.entry_price:.2f} "
                        f"(Aktuell: ${pos.current_price:.2f}, "
                        f"PnL: ${pos.unrealized_pnl:,.2f} [{pnl_pct:+.2f}%])"
                    )
                
                # Prüfe Stop-Loss / Take-Profit
                self.execution_engine.monitor_positions()
            
        except Exception as e:
            self.logger.error(f"Fehler beim Überwachen der Positionen: {e}")
    
    def print_summary(self):
        """Gibt eine Zusammenfassung aus"""
        try:
            account = self.broker.get_account_info()
            positions = self.broker.get_positions()
            orders = self.execution_engine.get_execution_summary()
            
            self.logger.info("=" * 60)
            self.logger.info("ZUSAMMENFASSUNG")
            self.logger.info("=" * 60)
            self.logger.info(f"Portfolio-Wert: ${account.portfolio_value:,.2f}")
            self.logger.info(f"Bargeld: ${account.cash:,.2f}")
            self.logger.info(f"Unrealisierter PnL: ${account.unrealized_pnl:,.2f}")
            self.logger.info(f"Realisierter PnL: ${account.realized_pnl:,.2f}")
            self.logger.info(f"Offene Positionen: {len(positions)}")
            self.logger.info(f"Ausgeführte Orders: {orders['total_orders']}")
            self.logger.info(f"  - Käufe: {orders['buy_orders']}")
            self.logger.info(f"  - Verkäufe: {orders['sell_orders']}")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Zusammenfassung: {e}")
    
    def run_once(self):
        """Führt einen Trading-Zyklus aus"""
        try:
            self.logger.info(f"🔄 Trading-Zyklus: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Aktualisiere Risk Manager
            account = self.broker.get_account_info()
            self.risk_manager.update_daily_pnl(account)
            
            # Überwache Positionen
            self.monitor_positions()
            
            # Analysiere Märkte
            self.analyze_markets()
            
            # Zusammenfassung
            self.print_summary()
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            self.logger.error(f"Fehler im Trading-Zyklus: {e}")
    
    def run(self, interval_seconds: int = 300):
        """
        Startet den Trading Bot im Loop
        
        Args:
            interval_seconds: Intervall zwischen Analysen in Sekunden (Standard: 5 Minuten)
        """
        self.logger.info(f"Bot läuft mit {interval_seconds}s Intervall. Strg+C zum Beenden.")
        
        try:
            while True:
                self.run_once()
                
                self.logger.info(f"⏸️  Warte {interval_seconds} Sekunden...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Bot wird beendet...")
            self.shutdown()
    
    def shutdown(self):
        """Fährt den Bot sauber herunter"""
        try:
            self.print_summary()
            
            if self.broker:
                self.broker.disconnect()
            
            self.logger.info("✓ Bot erfolgreich beendet")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Herunterfahren: {e}")


def main():
    """Main Entry Point"""
    bot = TradingBot()
    
    # Einmaliger Durchlauf oder kontinuierlich
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        bot.run_once()
        bot.shutdown()
    else:
        # Standard: Läuft kontinuierlich alle 5 Minuten
        bot.run(interval_seconds=300)


if __name__ == "__main__":
    main()
