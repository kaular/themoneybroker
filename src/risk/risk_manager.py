"""
Risk Manager
Verwaltet Risiko und Position Sizing
"""
import logging
from typing import Optional
from dataclasses import dataclass

from ..brokers import AccountInfo, Position


@dataclass
class RiskLimits:
    """Risiko-Limits"""
    max_position_size: float
    max_daily_loss: float
    max_open_positions: int
    risk_per_trade: float  # Als Prozentsatz des Kapitals


class RiskManager:
    """
    Risk Management System
    Überwacht und limitiert Handelsrisiken
    """
    
    def __init__(self, limits: RiskLimits):
        self.limits = limits
        self.logger = logging.getLogger(__name__)
        self.daily_pnl = 0.0
        self.trading_halted = False
    
    def calculate_position_size(
        self,
        account_info: AccountInfo,
        entry_price: float,
        stop_loss_price: Optional[float] = None
    ) -> float:
        """
        Berechnet die optimale Positionsgröße basierend auf Risiko
        
        Args:
            account_info: Account-Informationen
            entry_price: Einstiegspreis
            stop_loss_price: Stop-Loss Preis (optional)
        
        Returns:
            Anzahl Aktien/Kontrakte
        """
        # Basis-Berechnung: Risiko pro Trade
        risk_amount = account_info.equity * self.limits.risk_per_trade
        
        if stop_loss_price:
            # Mit Stop-Loss: Risiko = Differenz zum Entry * Quantity
            risk_per_unit = abs(entry_price - stop_loss_price)
            if risk_per_unit > 0:
                quantity = risk_amount / risk_per_unit
            else:
                quantity = 0
        else:
            # Ohne Stop-Loss: Nutze max Position Size
            quantity = min(
                self.limits.max_position_size,
                risk_amount / entry_price
            )
        
        # Limitiere auf Buying Power
        max_quantity = account_info.buying_power / entry_price
        quantity = min(quantity, max_quantity)
        
        # Limitiere auf max Position Size
        value = quantity * entry_price
        if value > self.limits.max_position_size:
            quantity = self.limits.max_position_size / entry_price
        
        self.logger.debug(
            f"Position Size berechnet: {quantity:.2f} Einheiten "
            f"@ {entry_price:.2f} = {quantity * entry_price:.2f}"
        )
        
        return max(0, int(quantity))
    
    def can_open_position(
        self,
        current_positions: int,
        account_info: AccountInfo
    ) -> tuple[bool, str]:
        """
        Prüft ob eine neue Position eröffnet werden kann
        
        Args:
            current_positions: Anzahl offener Positionen
            account_info: Account-Informationen
        
        Returns:
            (bool, reason) - True wenn erlaubt, sonst False mit Grund
        """
        if self.trading_halted:
            return False, "Trading wurde gestoppt (Risiko-Limit erreicht)"
        
        # Check max positions
        if current_positions >= self.limits.max_open_positions:
            return False, f"Max. Positionen erreicht ({self.limits.max_open_positions})"
        
        # Check daily loss limit
        total_pnl = account_info.unrealized_pnl + account_info.realized_pnl
        if abs(total_pnl) >= self.limits.max_daily_loss:
            self.trading_halted = True
            self.logger.warning(f"Tägliches Verlust-Limit erreicht: {total_pnl:.2f}")
            return False, f"Tägliches Verlust-Limit erreicht: {total_pnl:.2f}"
        
        # Check buying power
        if account_info.buying_power <= 0:
            return False, "Keine Kaufkraft verfügbar"
        
        return True, "OK"
    
    def should_close_position(
        self,
        position: Position,
        current_price: float,
        stop_loss_pct: float = 0.02,
        take_profit_pct: float = 0.05
    ) -> tuple[bool, str]:
        """
        Prüft ob eine Position geschlossen werden sollte
        
        Args:
            position: Die Position
            current_price: Aktueller Preis
            stop_loss_pct: Stop-Loss Prozentsatz
            take_profit_pct: Take-Profit Prozentsatz
        
        Returns:
            (bool, reason) - True wenn schließen, sonst False
        """
        pnl_pct = (current_price - position.entry_price) / position.entry_price
        
        # Stop Loss
        if pnl_pct <= -stop_loss_pct:
            return True, f"Stop-Loss ausgelöst: {pnl_pct*100:.2f}%"
        
        # Take Profit
        if pnl_pct >= take_profit_pct:
            return True, f"Take-Profit erreicht: {pnl_pct*100:.2f}%"
        
        return False, "Position halten"
    
    def update_daily_pnl(self, account_info: AccountInfo):
        """Aktualisiert das tägliche PnL"""
        self.daily_pnl = account_info.unrealized_pnl + account_info.realized_pnl
    
    def reset_daily_limits(self):
        """Setzt tägliche Limits zurück (z.B. am Handelsstart)"""
        self.daily_pnl = 0.0
        self.trading_halted = False
        self.logger.info("Tägliche Limits zurückgesetzt")
    
    def halt_trading(self, reason: str):
        """Stoppt das Trading"""
        self.trading_halted = True
        self.logger.critical(f"TRADING GESTOPPT: {reason}")
    
    def resume_trading(self):
        """Setzt das Trading fort"""
        self.trading_halted = False
        self.logger.info("Trading fortgesetzt")
