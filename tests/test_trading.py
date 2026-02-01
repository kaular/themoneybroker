"""
Test Suite für Trading Bot
"""
import pytest
from datetime import datetime, timedelta
import pandas as pd

from src.strategies import SMAStrategy, Signal
from src.risk import RiskManager, RiskLimits
from src.brokers import AccountInfo, Position


class TestSMAStrategy:
    """Tests für SMA Strategy"""
    
    def test_strategy_initialization(self):
        strategy = SMAStrategy(short_window=10, long_window=20)
        assert strategy.name == "SMA Crossover"
        assert strategy.get_parameter('short_window') == 10
        assert strategy.get_parameter('long_window') == 20
    
    def test_golden_cross(self):
        """Test Golden Cross (Buy Signal)"""
        strategy = SMAStrategy(short_window=2, long_window=3)
        
        # Erstelle Test-Daten mit Golden Cross
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 105, 110, 115, 120, 125],
            'high': [101, 102, 103, 104, 105, 106, 111, 116, 121, 126],
            'low': [99, 100, 101, 102, 103, 104, 109, 114, 119, 124],
            'close': [100, 101, 102, 103, 104, 105, 110, 115, 120, 125],
            'volume': [1000] * 10
        }, index=dates)
        
        signal = strategy.analyze(data, 'TEST')
        
        assert signal.symbol == 'TEST'
        assert signal.price > 0


class TestRiskManager:
    """Tests für Risk Manager"""
    
    def test_position_size_calculation(self):
        limits = RiskLimits(
            max_position_size=10000,
            max_daily_loss=500,
            max_open_positions=5,
            risk_per_trade=0.02
        )
        risk_manager = RiskManager(limits)
        
        account = AccountInfo(
            cash=10000,
            portfolio_value=10000,
            buying_power=10000,
            equity=10000
        )
        
        position_size = risk_manager.calculate_position_size(account, 100)
        
        assert position_size > 0
        assert position_size * 100 <= limits.max_position_size
    
    def test_can_open_position_max_positions(self):
        limits = RiskLimits(
            max_position_size=10000,
            max_daily_loss=500,
            max_open_positions=3,
            risk_per_trade=0.02
        )
        risk_manager = RiskManager(limits)
        
        account = AccountInfo(
            cash=10000,
            portfolio_value=10000,
            buying_power=10000,
            equity=10000
        )
        
        # Sollte erlaubt sein
        can_trade, reason = risk_manager.can_open_position(2, account)
        assert can_trade is True
        
        # Sollte abgelehnt werden (max erreicht)
        can_trade, reason = risk_manager.can_open_position(3, account)
        assert can_trade is False
    
    def test_should_close_position_stop_loss(self):
        limits = RiskLimits(
            max_position_size=10000,
            max_daily_loss=500,
            max_open_positions=5,
            risk_per_trade=0.02
        )
        risk_manager = RiskManager(limits)
        
        position = Position(
            symbol='TEST',
            quantity=10,
            entry_price=100,
            current_price=95,
            unrealized_pnl=-50
        )
        
        # Stop Loss sollte auslösen bei 3% Verlust
        should_close, reason = risk_manager.should_close_position(
            position,
            current_price=97,
            stop_loss_pct=0.02
        )
        
        assert should_close is True
        assert "Stop-Loss" in reason


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
