"""
Simple Moving Average Crossover Strategy
Beispiel-Implementierung einer Trading-Strategie
"""
import pandas as pd
import logging
from typing import Optional, Dict, Any

from .base_strategy import BaseStrategy, TradeSignal, Signal


class SMAStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategie
    
    Kauft wenn der kurze SMA den langen SMA von unten kreuzt (Golden Cross)
    Verkauft wenn der kurze SMA den langen SMA von oben kreuzt (Death Cross)
    """
    
    def __init__(
        self,
        name: str = "SMA Crossover",
        short_window: int = 20,
        long_window: int = 50,
        parameters: Optional[Dict[str, Any]] = None
    ):
        default_params = {
            'short_window': short_window,
            'long_window': long_window
        }
        if parameters:
            default_params.update(parameters)
        
        super().__init__(name, default_params)
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, data: pd.DataFrame, symbol: str) -> TradeSignal:
        """
        Analysiert die Daten mit SMA Crossover
        
        Args:
            data: DataFrame mit OHLCV-Daten
            symbol: Symbol
        
        Returns:
            TradeSignal
        """
        if not self.validate_data(data):
            return TradeSignal(
                symbol=symbol,
                signal=Signal.HOLD,
                strength=0.0,
                price=data['close'].iloc[-1] if not data.empty else 0.0,
                reason="Unzureichende Daten"
            )
        
        short_window = self.get_parameter('short_window', 20)
        long_window = self.get_parameter('long_window', 50)
        
        # Berechne SMAs
        data = data.copy()
        data['sma_short'] = data['close'].rolling(window=short_window).mean()
        data['sma_long'] = data['close'].rolling(window=long_window).mean()
        
        # Hole aktuelle und vorherige Werte
        current_short = data['sma_short'].iloc[-1]
        current_long = data['sma_long'].iloc[-1]
        prev_short = data['sma_short'].iloc[-2]
        prev_long = data['sma_long'].iloc[-2]
        current_price = data['close'].iloc[-1]
        
        # Check für Crossover
        signal = Signal.HOLD
        strength = 0.0
        reason = "Kein klares Signal"
        
        # Golden Cross (Kaufsignal)
        if prev_short <= prev_long and current_short > current_long:
            signal = Signal.BUY
            strength = min(1.0, abs(current_short - current_long) / current_long)
            reason = f"Golden Cross: SMA{short_window} kreuzt SMA{long_window} nach oben"
            self.logger.info(f"{symbol}: {reason}")
        
        # Death Cross (Verkaufssignal)
        elif prev_short >= prev_long and current_short < current_long:
            signal = Signal.SELL
            strength = min(1.0, abs(current_short - current_long) / current_long)
            reason = f"Death Cross: SMA{short_window} kreuzt SMA{long_window} nach unten"
            self.logger.info(f"{symbol}: {reason}")
        
        return TradeSignal(
            symbol=symbol,
            signal=signal,
            strength=strength,
            price=current_price,
            reason=reason,
            metadata={
                'sma_short': current_short,
                'sma_long': current_long,
                'short_window': short_window,
                'long_window': long_window
            }
        )
    
    def get_required_data_length(self) -> int:
        """Benötigt mindestens long_window + 1 Datenpunkte"""
        long_window = self.get_parameter('long_window', 50)
        return long_window + 1
