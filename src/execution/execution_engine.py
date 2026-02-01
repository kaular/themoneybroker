"""
Order Execution Engine
Führt Trades basierend auf Signalen aus
"""
import logging
from typing import Optional, List
from datetime import datetime

from ..brokers import BaseBroker, OrderType, OrderSide, Order
from ..strategies import TradeSignal, Signal
from ..risk import RiskManager


class ExecutionEngine:
    """
    Execution Engine für automatischen Handel
    Verarbeitet Trading-Signale und führt Orders aus
    """
    
    def __init__(self, broker: BaseBroker, risk_manager: RiskManager):
        self.broker = broker
        self.risk_manager = risk_manager
        self.logger = logging.getLogger(__name__)
        self.executed_orders: List[Order] = []
    
    def execute_signal(
        self,
        signal: TradeSignal,
        order_type: OrderType = OrderType.MARKET
    ) -> Optional[Order]:
        """
        Führt ein Trading-Signal aus
        
        Args:
            signal: Das Trading-Signal
            order_type: Art der Order (Market, Limit, etc.)
        
        Returns:
            Die ausgeführte Order oder None bei Fehler
        """
        if signal.signal == Signal.HOLD:
            self.logger.debug(f"{signal.symbol}: HOLD Signal - keine Aktion")
            return None
        
        try:
            # Hole Account Info
            account_info = self.broker.get_account_info()
            
            # Prüfe ob wir handeln können
            if signal.signal == Signal.BUY:
                positions = self.broker.get_positions()
                can_trade, reason = self.risk_manager.can_open_position(
                    len(positions),
                    account_info
                )
                
                if not can_trade:
                    self.logger.warning(f"{signal.symbol}: Trade abgelehnt - {reason}")
                    return None
                
                # Berechne Position Size
                quantity = self.risk_manager.calculate_position_size(
                    account_info,
                    signal.price
                )
                
                if quantity <= 0:
                    self.logger.warning(f"{signal.symbol}: Quantity zu klein: {quantity}")
                    return None
                
                # Platziere Kauforder
                order = self.broker.place_order(
                    symbol=signal.symbol,
                    quantity=quantity,
                    side=OrderSide.BUY,
                    order_type=order_type
                )
                
                self.logger.info(
                    f"✓ KAUFORDER: {quantity} {signal.symbol} @ {signal.price:.2f} "
                    f"(Grund: {signal.reason})"
                )
                
            elif signal.signal == Signal.SELL:
                # Prüfe ob wir eine Position haben
                position = self.broker.get_position(signal.symbol)
                
                if not position:
                    self.logger.warning(f"{signal.symbol}: Keine Position zum Verkaufen")
                    return None
                
                # Verkaufe die gesamte Position
                quantity = abs(position.quantity)
                
                order = self.broker.place_order(
                    symbol=signal.symbol,
                    quantity=quantity,
                    side=OrderSide.SELL,
                    order_type=order_type
                )
                
                self.logger.info(
                    f"✓ VERKAUFSORDER: {quantity} {signal.symbol} @ {signal.price:.2f} "
                    f"(Grund: {signal.reason})"
                )
            
            self.executed_orders.append(order)
            return order
            
        except Exception as e:
            self.logger.error(f"Fehler beim Ausführen des Signals für {signal.symbol}: {e}")
            return None
    
    def monitor_positions(self):
        """
        Überwacht offene Positionen und prüft Stop-Loss/Take-Profit
        """
        try:
            positions = self.broker.get_positions()
            
            for position in positions:
                current_price = self.broker.get_market_price(position.symbol)
                
                should_close, reason = self.risk_manager.should_close_position(
                    position,
                    current_price
                )
                
                if should_close:
                    self.logger.info(
                        f"Position {position.symbol} wird geschlossen: {reason}"
                    )
                    
                    # Erstelle Verkaufssignal
                    signal = TradeSignal(
                        symbol=position.symbol,
                        signal=Signal.SELL,
                        strength=1.0,
                        price=current_price,
                        reason=reason
                    )
                    
                    self.execute_signal(signal)
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Überwachen der Positionen: {e}")
    
    def get_execution_summary(self) -> dict:
        """
        Gibt eine Zusammenfassung der ausgeführten Orders
        
        Returns:
            Dictionary mit Statistiken
        """
        total_orders = len(self.executed_orders)
        buy_orders = sum(1 for o in self.executed_orders if o.side == OrderSide.BUY)
        sell_orders = sum(1 for o in self.executed_orders if o.side == OrderSide.SELL)
        
        return {
            'total_orders': total_orders,
            'buy_orders': buy_orders,
            'sell_orders': sell_orders,
            'orders': self.executed_orders
        }
