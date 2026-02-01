"""
Stop-Loss & Take-Profit Manager
Überwacht offene Positionen und führt automatisch Exit-Orders aus
"""
import logging
import asyncio
from typing import Dict, Optional, Callable
from datetime import datetime
from enum import Enum

from ..brokers.base_broker import BaseBroker, OrderSide, OrderType


class StopType(Enum):
    """Stop-Loss Typen"""
    FIXED = "fixed"  # Fester Stop-Loss Preis
    TRAILING = "trailing"  # Trailing Stop (folgt dem Preis)
    PERCENTAGE = "percentage"  # Stop-Loss als Prozent


class StopLossConfig:
    """Stop-Loss Konfiguration für eine Position"""
    def __init__(
        self,
        symbol: str,
        stop_type: StopType,
        stop_price: Optional[float] = None,
        stop_percentage: Optional[float] = None,
        trailing_percentage: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        take_profit_percentage: Optional[float] = None
    ):
        self.symbol = symbol
        self.stop_type = stop_type
        self.stop_price = stop_price
        self.stop_percentage = stop_percentage
        self.trailing_percentage = trailing_percentage
        self.take_profit_price = take_profit_price
        self.take_profit_percentage = take_profit_percentage
        
        # Tracking für Trailing Stop
        self.highest_price = None
        self.lowest_price = None
        self.entry_price = None


class StopLossManager:
    """
    Stop-Loss & Take-Profit Manager
    
    Features:
    - Fixed Stop-Loss
    - Trailing Stop-Loss
    - Take-Profit Targets
    - Partial Exit Support
    """
    
    def __init__(self, broker: BaseBroker, check_interval: float = 1.0):
        """
        Args:
            broker: Broker Instance
            check_interval: Wie oft Positionen geprüft werden (in Sekunden)
        """
        self.broker = broker
        self.check_interval = check_interval
        self.logger = logging.getLogger(__name__)
        
        # Position Tracking
        self.stop_configs: Dict[str, StopLossConfig] = {}
        self.position_quantities: Dict[str, float] = {}
        
        # Monitoring
        self.is_monitoring = False
        self.monitor_task = None
        
        # Callbacks
        self.on_stop_loss_triggered: Optional[Callable] = None
        self.on_take_profit_triggered: Optional[Callable] = None
    
    def set_stop_loss(
        self,
        symbol: str,
        stop_type: StopType,
        stop_price: Optional[float] = None,
        stop_percentage: Optional[float] = None,
        trailing_percentage: Optional[float] = None,
        entry_price: Optional[float] = None
    ):
        """
        Setzt Stop-Loss für eine Position
        
        Args:
            symbol: Symbol
            stop_type: Art des Stop-Loss
            stop_price: Fester Stop-Loss Preis
            stop_percentage: Stop-Loss als Prozent vom Entry
            trailing_percentage: Trailing Stop Prozentsatz
            entry_price: Entry Preis (für Berechnungen)
        """
        config = StopLossConfig(
            symbol=symbol,
            stop_type=stop_type,
            stop_price=stop_price,
            stop_percentage=stop_percentage,
            trailing_percentage=trailing_percentage
        )
        config.entry_price = entry_price
        
        self.stop_configs[symbol] = config
        self.logger.info(f"Stop-Loss gesetzt für {symbol}: {stop_type.value}")
    
    def set_take_profit(
        self,
        symbol: str,
        take_profit_price: Optional[float] = None,
        take_profit_percentage: Optional[float] = None
    ):
        """
        Setzt Take-Profit für eine Position
        
        Args:
            symbol: Symbol
            take_profit_price: Fester Take-Profit Preis
            take_profit_percentage: Take-Profit als Prozent
        """
        if symbol in self.stop_configs:
            self.stop_configs[symbol].take_profit_price = take_profit_price
            self.stop_configs[symbol].take_profit_percentage = take_profit_percentage
        else:
            config = StopLossConfig(
                symbol=symbol,
                stop_type=StopType.FIXED,
                take_profit_price=take_profit_price,
                take_profit_percentage=take_profit_percentage
            )
            self.stop_configs[symbol] = config
        
        self.logger.info(f"Take-Profit gesetzt für {symbol}")
    
    def remove_stop_loss(self, symbol: str):
        """Entfernt Stop-Loss für eine Position"""
        if symbol in self.stop_configs:
            del self.stop_configs[symbol]
            self.logger.info(f"Stop-Loss entfernt für {symbol}")
    
    async def start_monitoring(self):
        """Startet das kontinuierliche Monitoring"""
        if self.is_monitoring:
            self.logger.warning("Monitoring läuft bereits")
            return
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        self.logger.info("Stop-Loss Monitoring gestartet")
    
    async def stop_monitoring(self):
        """Stoppt das Monitoring"""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stop-Loss Monitoring gestoppt")
    
    async def _monitor_loop(self):
        """Haupt-Monitoring Loop"""
        while self.is_monitoring:
            try:
                await self._check_positions()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Fehler im Monitoring Loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_positions(self):
        """Prüft alle Positionen auf Stop-Loss/Take-Profit"""
        try:
            positions = self.broker.get_positions()
            
            for position in positions:
                symbol = position.symbol
                
                if symbol not in self.stop_configs:
                    continue
                
                config = self.stop_configs[symbol]
                current_price = float(position.current_price)
                quantity = float(position.qty)
                side = position.side  # "long" or "short"
                
                # Update Position Quantity
                self.position_quantities[symbol] = quantity
                
                # Entry Price setzen falls noch nicht vorhanden
                if config.entry_price is None:
                    config.entry_price = float(position.avg_entry_price)
                
                # Update Trailing Stop
                if config.stop_type == StopType.TRAILING:
                    self._update_trailing_stop(config, current_price, side)
                
                # Prüfe Stop-Loss
                if self._should_trigger_stop_loss(config, current_price, side):
                    await self._execute_stop_loss(symbol, quantity, side, current_price)
                
                # Prüfe Take-Profit
                elif self._should_trigger_take_profit(config, current_price, side):
                    await self._execute_take_profit(symbol, quantity, side, current_price)
        
        except Exception as e:
            self.logger.error(f"Fehler beim Prüfen der Positionen: {e}")
    
    def _update_trailing_stop(self, config: StopLossConfig, current_price: float, side: str):
        """Updated Trailing Stop-Loss"""
        if side.lower() == "long":
            # Long Position: Track highest price
            if config.highest_price is None or current_price > config.highest_price:
                config.highest_price = current_price
                
                # Update Stop-Loss
                if config.trailing_percentage:
                    config.stop_price = config.highest_price * (1 - config.trailing_percentage / 100)
        
        else:  # Short Position
            # Short Position: Track lowest price
            if config.lowest_price is None or current_price < config.lowest_price:
                config.lowest_price = current_price
                
                # Update Stop-Loss
                if config.trailing_percentage:
                    config.stop_price = config.lowest_price * (1 + config.trailing_percentage / 100)
    
    def _should_trigger_stop_loss(self, config: StopLossConfig, current_price: float, side: str) -> bool:
        """Prüft ob Stop-Loss ausgelöst werden soll"""
        if config.stop_price is None:
            # Berechne Stop-Loss aus Prozent
            if config.stop_percentage and config.entry_price:
                if side.lower() == "long":
                    config.stop_price = config.entry_price * (1 - config.stop_percentage / 100)
                else:
                    config.stop_price = config.entry_price * (1 + config.stop_percentage / 100)
            else:
                return False
        
        # Prüfe Trigger
        if side.lower() == "long":
            return current_price <= config.stop_price
        else:  # Short
            return current_price >= config.stop_price
    
    def _should_trigger_take_profit(self, config: StopLossConfig, current_price: float, side: str) -> bool:
        """Prüft ob Take-Profit ausgelöst werden soll"""
        # Berechne Take-Profit Preis falls nötig
        tp_price = config.take_profit_price
        
        if tp_price is None and config.take_profit_percentage and config.entry_price:
            if side.lower() == "long":
                tp_price = config.entry_price * (1 + config.take_profit_percentage / 100)
            else:
                tp_price = config.entry_price * (1 - config.take_profit_percentage / 100)
        
        if tp_price is None:
            return False
        
        # Prüfe Trigger
        if side.lower() == "long":
            return current_price >= tp_price
        else:  # Short
            return current_price <= tp_price
    
    async def _execute_stop_loss(self, symbol: str, quantity: float, side: str, current_price: float):
        """Führt Stop-Loss Order aus"""
        self.logger.warning(f"🛑 Stop-Loss triggered für {symbol} @ ${current_price:.2f}")
        
        try:
            # Exit Position
            exit_side = OrderSide.SELL if side.lower() == "long" else OrderSide.BUY
            
            order = self.broker.place_order(
                symbol=symbol,
                quantity=quantity,
                side=exit_side,
                order_type=OrderType.MARKET
            )
            
            self.logger.info(f"Stop-Loss Order ausgeführt: {order.order_id}")
            
            # Entferne Config
            self.remove_stop_loss(symbol)
            
            # Callback
            if self.on_stop_loss_triggered:
                await self.on_stop_loss_triggered(symbol, quantity, current_price)
        
        except Exception as e:
            self.logger.error(f"Fehler beim Ausführen der Stop-Loss Order: {e}")
    
    async def _execute_take_profit(self, symbol: str, quantity: float, side: str, current_price: float):
        """Führt Take-Profit Order aus"""
        self.logger.info(f"🎯 Take-Profit triggered für {symbol} @ ${current_price:.2f}")
        
        try:
            # Exit Position
            exit_side = OrderSide.SELL if side.lower() == "long" else OrderSide.BUY
            
            order = self.broker.place_order(
                symbol=symbol,
                quantity=quantity,
                side=exit_side,
                order_type=OrderType.MARKET
            )
            
            self.logger.info(f"Take-Profit Order ausgeführt: {order.id}")
            
            # Entferne Config
            self.remove_stop_loss(symbol)
            
            # Callback
            if self.on_take_profit_triggered:
                await self.on_take_profit_triggered(symbol, quantity, current_price)
        
        except Exception as e:
            self.logger.error(f"Fehler beim Ausführen der Take-Profit Order: {e}")
    
    def get_stop_config(self, symbol: str) -> Optional[StopLossConfig]:
        """Holt Stop-Loss Config für ein Symbol"""
        return self.stop_configs.get(symbol)
    
    def get_all_stops(self) -> Dict[str, StopLossConfig]:
        """Holt alle Stop-Loss Configs"""
        return self.stop_configs.copy()
