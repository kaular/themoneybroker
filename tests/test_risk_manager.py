"""
Tests für Risk Manager
"""
import pytest
from src.risk.risk_manager import RiskManager, RiskLimits


class TestRiskLimits:
    """Tests für RiskLimits"""
    
    def test_create_risk_limits(self):
        """Test: RiskLimits erstellen"""
        limits = RiskLimits(
            max_position_size=10000.0,
            max_daily_loss=500.0,
            max_open_positions=5,
            risk_per_trade=0.02
        )
        
        assert limits.max_position_size == 10000.0
        assert limits.max_daily_loss == 500.0
        assert limits.max_open_positions == 5
        assert limits.risk_per_trade == 0.02


class TestRiskManager:
    """Tests für RiskManager"""
    
    @pytest.fixture
    def risk_limits(self):
        """Risk Limits Fixture"""
        return RiskLimits(
            max_position_size=10000.0,
            max_daily_loss=500.0,
            max_open_positions=5,
            risk_per_trade=0.02
        )
    
    @pytest.fixture
    def risk_manager(self, risk_limits):
        """Risk Manager Fixture"""
        return RiskManager(risk_limits)
    
    def test_risk_manager_initialization(self, risk_manager, risk_limits):
        """Test: Risk Manager Initialisierung"""
        assert risk_manager.limits == risk_limits
        assert risk_manager.daily_pnl == 0.0
        assert risk_manager.trading_halted is False
    
    def test_can_open_position_under_limit(self, risk_manager):
        """Test: Position öffnen unter Limit"""
        from src.brokers import AccountInfo
        account = AccountInfo(cash=100000, portfolio_value=100000, buying_power=100000, equity=100000)
        can_open, msg = risk_manager.can_open_position(3, account)
        assert can_open is True
        assert msg == "OK"
    
    def test_can_open_position_at_limit(self, risk_manager):
        """Test: Position öffnen am Limit"""
        from src.brokers import AccountInfo
        account = AccountInfo(cash=100000, portfolio_value=100000, buying_power=100000, equity=100000)
        can_open, msg = risk_manager.can_open_position(5, account)
        assert can_open is False
        assert "Max. Positionen" in msg
    
    def test_can_open_position_over_limit(self, risk_manager):
        """Test: Position öffnen über Limit"""
        from src.brokers import AccountInfo
        account = AccountInfo(cash=100000, portfolio_value=100000, buying_power=100000, equity=100000)
        can_open, msg = risk_manager.can_open_position(6, account)
        assert can_open is False
    
    def test_check_daily_loss_within_limit(self, risk_manager):
        """Test: Daily Loss innerhalb Limit"""
        from src.brokers import AccountInfo
        account = AccountInfo(cash=99700, portfolio_value=99700, buying_power=99700, equity=99700, unrealized_pnl=-300.0)
        can_open, _ = risk_manager.can_open_position(0, account)
        assert can_open is True
    
    def test_check_daily_loss_at_limit(self, risk_manager):
        """Test: Daily Loss am Limit"""
        from src.brokers import AccountInfo
        account = AccountInfo(cash=99500, portfolio_value=99500, buying_power=99500, equity=99500, unrealized_pnl=-500.0)
        can_open, msg = risk_manager.can_open_position(0, account)
        assert can_open is False
        assert "Verlust-Limit" in msg
    
    def test_check_daily_loss_exceeded(self, risk_manager):
        """Test: Daily Loss überschritten"""
        from src.brokers import AccountInfo
        account = AccountInfo(cash=99400, portfolio_value=99400, buying_power=99400, equity=99400, unrealized_pnl=-600.0)
        can_open, msg = risk_manager.can_open_position(0, account)
        assert can_open is False
    
    def test_calculate_position_size_basic(self, risk_manager):
        """Test: Position Size Berechnung"""
        from src.brokers import AccountInfo
        account = AccountInfo(cash=100000, portfolio_value=100000, buying_power=100000, equity=100000)
        entry_price = 150.0
        stop_loss_price = 145.0
        
        position_size = risk_manager.calculate_position_size(
            account,
            entry_price,
            stop_loss_price
        )
        
        # Risk per trade = 2% of 100k = 2000
        # Risk per share = 150 - 145 = 5
        # Shares would be 400, but limited by max_position_size (10000)
        # 10000 / 150 = 66
        assert position_size == 66
    
    def test_calculate_position_size_with_max_limit(self, risk_manager):
        """Test: Position Size mit Max Limit"""
        from src.brokers import AccountInfo
        account = AccountInfo(cash=100000, portfolio_value=100000, buying_power=100000, equity=100000)
        entry_price = 10.0
        stop_loss_price = 9.5
        
        position_size = risk_manager.calculate_position_size(
            account,
            entry_price,
            stop_loss_price
        )
        
        # Risk = 2000, Risk per share = 0.5
        # Shares = 2000 / 0.5 = 4000
        # But limited by max_position_size (10000) / entry_price (10) = 1000
        assert position_size == 1000
    
    def test_calculate_position_size_zero_risk(self, risk_manager):
        """Test: Position Size bei null Risiko"""
        from src.brokers import AccountInfo
        account = AccountInfo(cash=100000, portfolio_value=100000, buying_power=100000, equity=100000)
        position_size = risk_manager.calculate_position_size(
            account,
            150.0,
            150.0  # Stop = Entry
        )
        
        assert position_size == 0
    
    def test_update_daily_pnl(self, risk_manager):
        """Test: Daily PnL Tracking"""
        assert risk_manager.daily_pnl == 0.0
        
        risk_manager.daily_pnl = -100.0
        assert risk_manager.daily_pnl == -100.0
    
    def test_reset_daily_limits(self, risk_manager):
        """Test: Daily Limits Reset"""
        risk_manager.trading_halted = True
        risk_manager.daily_pnl = -300.0
        
        risk_manager.reset_daily_limits()
        assert risk_manager.trading_halted is False
        assert risk_manager.daily_pnl == 0.0
    
    def test_trading_halted_after_loss_limit(self, risk_manager):
        """Test: Trading wird gestoppt nach Verlust-Limit"""
        from src.brokers import AccountInfo
        # Erste Prüfung mit hohem Verlust
        account = AccountInfo(cash=99400, portfolio_value=99400, buying_power=99400, equity=99400, unrealized_pnl=-600.0)
        can_open, msg = risk_manager.can_open_position(0, account)
        
        assert can_open is False
        assert risk_manager.trading_halted is True
        
        # Zweite Prüfung - Trading bleibt gestoppt
        account2 = AccountInfo(cash=100000, portfolio_value=100000, buying_power=100000, equity=100000)
        can_open2, msg2 = risk_manager.can_open_position(0, account2)
        assert can_open2 is False
        assert "gestoppt" in msg2
    
    def test_no_buying_power(self, risk_manager):
        """Test: Keine Position bei fehlender Kaufkraft"""
        from src.brokers import AccountInfo
        account = AccountInfo(cash=0, portfolio_value=100000, buying_power=0, equity=100000)
        can_open, msg = risk_manager.can_open_position(0, account)
        assert can_open is False
        assert "Kaufkraft" in msg


class TestRiskManagementIntegration:
    """Integration Tests für Risk Management"""
    
    def test_complete_risk_workflow(self):
        """Test: Kompletter Risk Management Workflow"""
        from src.brokers import AccountInfo
        # Setup
        limits = RiskLimits(
            max_position_size=10000.0,
            max_daily_loss=500.0,
            max_open_positions=3,
            risk_per_trade=0.02
        )
        risk_manager = RiskManager(limits)
        
        account = AccountInfo(cash=50000, portfolio_value=50000, buying_power=50000, equity=50000)
        
        # 1. Erste Position berechnen
        entry_price = 100.0
        stop_loss = 98.0
        position_size = risk_manager.calculate_position_size(
            account,
            entry_price,
            stop_loss
        )
        
        # Risk = 1000 (2% of 50k), Risk per share = 2, Shares would be 500
        # But limited by max_position_size (10000) / entry_price (100) = 100
        assert position_size == 100
        
        # Position öffnen prüfen
        can_open, _ = risk_manager.can_open_position(0, account)
        assert can_open is True
        
        # 2. Zweite Position
        can_open, _ = risk_manager.can_open_position(1, account)
        assert can_open is True
        
        # 3. Dritte Position - Am Limit
        can_open, _ = risk_manager.can_open_position(3, account)
        assert can_open is False
        
        # 4. Simuliere Verlust
        account_loss = AccountInfo(cash=49500, portfolio_value=49500, buying_power=49500, equity=49500, unrealized_pnl=-500.0)
        can_open, msg = risk_manager.can_open_position(0, account_loss)
        assert can_open is False
        assert risk_manager.trading_halted is True
        
        # 5. Neuer Tag - Reset
        risk_manager.reset_daily_limits()
        assert risk_manager.trading_halted is False
        can_open, _ = risk_manager.can_open_position(0, account)
        assert can_open is True
    
    def test_position_sizing_with_different_stop_distances(self):
        """Test: Position Sizing mit verschiedenen Stop Distanzen"""
        from src.brokers import AccountInfo
        limits = RiskLimits(
            max_position_size=10000.0,
            max_daily_loss=1000.0,
            max_open_positions=5,
            risk_per_trade=0.01  # 1%
        )
        risk_manager = RiskManager(limits)
        
        account = AccountInfo(cash=100000, portfolio_value=100000, buying_power=100000, equity=100000)
        entry_price = 100.0
        
        # Enger Stop (1% Distanz)
        tight_stop = 99.0
        size_tight = risk_manager.calculate_position_size(
            account, entry_price, tight_stop
        )
        # Risk = 1000, Risk per share = 1, Shares would be 1000
        # But limited by max_position_size (10000) / entry_price (100) = 100
        assert size_tight == 100
        
        # Weiter Stop (5% Distanz)
        wide_stop = 95.0
        size_wide = risk_manager.calculate_position_size(
            account, entry_price, wide_stop
        )
        # Risk = 1000, Risk per share = 5, Shares would be 200
        # Also limited by max_position_size = 100
        assert size_wide == 100
        
        # Sehr weiter Stop (10% Distanz)
        very_wide_stop = 90.0
        size_very_wide = risk_manager.calculate_position_size(
            account, entry_price, very_wide_stop
        )
        # Risk = 1000, Risk per share = 10, Shares = 100
        # Limited by max_position_size = 100
        assert size_very_wide == 100
