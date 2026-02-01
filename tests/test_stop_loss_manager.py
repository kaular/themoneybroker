"""
Tests für Stop-Loss Manager
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.risk.stop_loss_manager import StopLossManager, StopLossConfig, StopType


class TestStopLossConfig:
    """Tests für StopLossConfig"""
    
    def test_create_config(self):
        """Test: Config erstellen"""
        config = StopLossConfig(
            symbol="AAPL",
            stop_type=StopType.PERCENTAGE,
            stop_percentage=2.0
        )
        
        assert config.symbol == "AAPL"
        assert config.stop_type == StopType.PERCENTAGE
        assert config.stop_percentage == 2.0
    
    def test_trailing_config(self):
        """Test: Trailing Stop Config"""
        config = StopLossConfig(
            symbol="AAPL",
            stop_type=StopType.TRAILING,
            trailing_percentage=3.0
        )
        
        assert config.stop_type == StopType.TRAILING
        assert config.trailing_percentage == 3.0
        assert config.highest_price is None


class TestStopLossManager:
    """Tests für StopLossManager"""
    
    @pytest.fixture
    def manager(self, mock_broker):
        """Stop-Loss Manager Fixture"""
        return StopLossManager(broker=mock_broker, check_interval=0.1)
    
    def test_manager_initialization(self, manager):
        """Test: Manager Initialisierung"""
        assert manager.broker is not None
        assert manager.check_interval == 0.1
        assert manager.is_monitoring is False
        assert len(manager.stop_configs) == 0
    
    def test_set_fixed_stop_loss(self, manager):
        """Test: Fixed Stop-Loss setzen"""
        manager.set_stop_loss(
            symbol="AAPL",
            stop_type=StopType.FIXED,
            stop_price=145.0,
            entry_price=150.0
        )
        
        assert "AAPL" in manager.stop_configs
        config = manager.stop_configs["AAPL"]
        assert config.stop_type == StopType.FIXED
        assert config.stop_price == 145.0
        assert config.entry_price == 150.0
    
    def test_set_percentage_stop_loss(self, manager):
        """Test: Percentage Stop-Loss setzen"""
        manager.set_stop_loss(
            symbol="AAPL",
            stop_type=StopType.PERCENTAGE,
            stop_percentage=2.0,
            entry_price=150.0
        )
        
        config = manager.stop_configs["AAPL"]
        assert config.stop_type == StopType.PERCENTAGE
        assert config.stop_percentage == 2.0
    
    def test_set_trailing_stop_loss(self, manager):
        """Test: Trailing Stop-Loss setzen"""
        manager.set_stop_loss(
            symbol="AAPL",
            stop_type=StopType.TRAILING,
            trailing_percentage=3.0,
            entry_price=150.0
        )
        
        config = manager.stop_configs["AAPL"]
        assert config.stop_type == StopType.TRAILING
        assert config.trailing_percentage == 3.0
    
    def test_set_take_profit(self, manager):
        """Test: Take-Profit setzen"""
        manager.set_take_profit(
            symbol="AAPL",
            take_profit_price=160.0
        )
        
        config = manager.stop_configs["AAPL"]
        assert config.take_profit_price == 160.0
    
    def test_set_take_profit_percentage(self, manager):
        """Test: Take-Profit mit Prozent"""
        manager.set_stop_loss(
            symbol="AAPL",
            stop_type=StopType.FIXED,
            stop_price=145.0,
            entry_price=150.0
        )
        
        manager.set_take_profit(
            symbol="AAPL",
            take_profit_percentage=5.0
        )
        
        config = manager.stop_configs["AAPL"]
        assert config.take_profit_percentage == 5.0
    
    def test_remove_stop_loss(self, manager):
        """Test: Stop-Loss entfernen"""
        manager.set_stop_loss(
            symbol="AAPL",
            stop_type=StopType.FIXED,
            stop_price=145.0
        )
        
        assert "AAPL" in manager.stop_configs
        
        manager.remove_stop_loss("AAPL")
        assert "AAPL" not in manager.stop_configs
    
    def test_should_trigger_fixed_stop_loss_long(self, manager):
        """Test: Fixed Stop-Loss Trigger (Long Position)"""
        config = StopLossConfig(
            symbol="AAPL",
            stop_type=StopType.FIXED,
            stop_price=145.0
        )
        config.entry_price = 150.0
        
        # Preis über Stop -> Kein Trigger
        assert not manager._should_trigger_stop_loss(config, 146.0, "long")
        
        # Preis unter Stop -> Trigger
        assert manager._should_trigger_stop_loss(config, 144.0, "long")
        
        # Preis genau am Stop -> Trigger
        assert manager._should_trigger_stop_loss(config, 145.0, "long")
    
    def test_should_trigger_fixed_stop_loss_short(self, manager):
        """Test: Fixed Stop-Loss Trigger (Short Position)"""
        config = StopLossConfig(
            symbol="AAPL",
            stop_type=StopType.FIXED,
            stop_price=155.0
        )
        config.entry_price = 150.0
        
        # Preis unter Stop -> Kein Trigger
        assert not manager._should_trigger_stop_loss(config, 154.0, "short")
        
        # Preis über Stop -> Trigger
        assert manager._should_trigger_stop_loss(config, 156.0, "short")
    
    def test_should_trigger_percentage_stop_loss(self, manager):
        """Test: Percentage Stop-Loss Trigger"""
        config = StopLossConfig(
            symbol="AAPL",
            stop_type=StopType.PERCENTAGE,
            stop_percentage=2.0
        )
        config.entry_price = 150.0
        
        # Berechne Stop-Preis: 150 * (1 - 0.02) = 147.0
        assert not manager._should_trigger_stop_loss(config, 148.0, "long")
        assert manager._should_trigger_stop_loss(config, 146.0, "long")
    
    def test_update_trailing_stop_long(self, manager):
        """Test: Trailing Stop Update (Long)"""
        config = StopLossConfig(
            symbol="AAPL",
            stop_type=StopType.TRAILING,
            trailing_percentage=3.0
        )
        config.entry_price = 150.0
        
        # Initialer Preis
        manager._update_trailing_stop(config, 152.0, "long")
        assert config.highest_price == 152.0
        assert config.stop_price == 152.0 * 0.97  # 3% trailing
        
        # Preis steigt -> Stop steigt
        manager._update_trailing_stop(config, 155.0, "long")
        assert config.highest_price == 155.0
        assert config.stop_price == 155.0 * 0.97
        
        # Preis fällt -> Stop bleibt
        old_stop = config.stop_price
        manager._update_trailing_stop(config, 153.0, "long")
        assert config.stop_price == old_stop
    
    def test_update_trailing_stop_short(self, manager):
        """Test: Trailing Stop Update (Short)"""
        config = StopLossConfig(
            symbol="AAPL",
            stop_type=StopType.TRAILING,
            trailing_percentage=3.0
        )
        config.entry_price = 150.0
        
        # Initialer Preis
        manager._update_trailing_stop(config, 148.0, "short")
        assert config.lowest_price == 148.0
        assert config.stop_price == 148.0 * 1.03  # 3% trailing
        
        # Preis fällt -> Stop fällt
        manager._update_trailing_stop(config, 145.0, "short")
        assert config.lowest_price == 145.0
        assert config.stop_price == 145.0 * 1.03
    
    def test_should_trigger_take_profit_long(self, manager):
        """Test: Take-Profit Trigger (Long)"""
        config = StopLossConfig(
            symbol="AAPL",
            stop_type=StopType.FIXED,
            take_profit_price=160.0
        )
        config.entry_price = 150.0
        
        # Preis unter TP -> Kein Trigger
        assert not manager._should_trigger_take_profit(config, 159.0, "long")
        
        # Preis über TP -> Trigger
        assert manager._should_trigger_take_profit(config, 161.0, "long")
    
    def test_should_trigger_take_profit_percentage(self, manager):
        """Test: Take-Profit Percentage Trigger"""
        config = StopLossConfig(
            symbol="AAPL",
            stop_type=StopType.FIXED,
            take_profit_percentage=5.0
        )
        config.entry_price = 150.0
        
        # TP Price = 150 * 1.05 = 157.5
        assert not manager._should_trigger_take_profit(config, 157.0, "long")
        assert manager._should_trigger_take_profit(config, 158.0, "long")
    
    @pytest.mark.asyncio
    async def test_execute_stop_loss(self, manager, mock_broker):
        """Test: Stop-Loss Ausführung"""
        # Setup
        manager.set_stop_loss(
            symbol="AAPL",
            stop_type=StopType.FIXED,
            stop_price=145.0
        )
        
        # Execute Stop-Loss
        await manager._execute_stop_loss("AAPL", 10.0, "long", 144.0)
        
        # Verify Order platziert
        assert len(mock_broker.orders) == 1
        order = mock_broker.orders[0]
        assert order.symbol == "AAPL"
        assert order.quantity == 10.0
        
        # Verify Config entfernt
        assert "AAPL" not in manager.stop_configs
    
    @pytest.mark.asyncio
    async def test_execute_take_profit(self, manager, mock_broker):
        """Test: Take-Profit Ausführung"""
        # Setup
        manager.set_take_profit(
            symbol="AAPL",
            take_profit_price=160.0
        )
        
        # Execute Take-Profit
        await manager._execute_take_profit("AAPL", 10.0, "long", 161.0)
        
        # Verify Order platziert
        assert len(mock_broker.orders) == 1
        order = mock_broker.orders[0]
        assert order.symbol == "AAPL"
        assert order.quantity == 10.0
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, manager):
        """Test: Monitoring Start/Stop"""
        assert not manager.is_monitoring
        
        # Start
        await manager.start_monitoring()
        assert manager.is_monitoring
        assert manager.monitor_task is not None
        
        # Stop
        await manager.stop_monitoring()
        assert not manager.is_monitoring
    
    def test_get_stop_config(self, manager):
        """Test: Config abrufen"""
        manager.set_stop_loss(
            symbol="AAPL",
            stop_type=StopType.FIXED,
            stop_price=145.0
        )
        
        config = manager.get_stop_config("AAPL")
        assert config is not None
        assert config.symbol == "AAPL"
        
        # Nicht existierendes Symbol
        assert manager.get_stop_config("MSFT") is None
    
    def test_get_all_stops(self, manager):
        """Test: Alle Stops abrufen"""
        # Setze mehrere Stops
        manager.set_stop_loss("AAPL", StopType.FIXED, stop_price=145.0)
        manager.set_stop_loss("MSFT", StopType.TRAILING, trailing_percentage=3.0)
        manager.set_stop_loss("GOOGL", StopType.PERCENTAGE, stop_percentage=2.0)
        
        all_stops = manager.get_all_stops()
        assert len(all_stops) == 3
        assert "AAPL" in all_stops
        assert "MSFT" in all_stops
        assert "GOOGL" in all_stops


class TestStopLossIntegration:
    """Integration Tests für Stop-Loss System"""
    
    @pytest.mark.asyncio
    async def test_complete_stop_loss_workflow(self, mock_broker):
        """Test: Kompletter Stop-Loss Workflow"""
        manager = StopLossManager(broker=mock_broker, check_interval=0.1)
        
        # 1. Position öffnen (simuliert)
        mock_broker.positions = [mock_broker.get_quote("AAPL")]
        
        # 2. Stop-Loss setzen
        manager.set_stop_loss(
            symbol="AAPL",
            stop_type=StopType.PERCENTAGE,
            stop_percentage=2.0,
            entry_price=150.0
        )
        
        # 3. Take-Profit setzen
        manager.set_take_profit(
            symbol="AAPL",
            take_profit_percentage=5.0
        )
        
        # 4. Verify Config
        config = manager.get_stop_config("AAPL")
        assert config.stop_percentage == 2.0
        assert config.take_profit_percentage == 5.0
        
        # 5. Simulate Stop-Loss Trigger
        await manager._execute_stop_loss("AAPL", 10.0, "long", 146.0)
        
        # 6. Verify Exit Order
        assert len(mock_broker.orders) == 1
        assert mock_broker.orders[0].symbol == "AAPL"
    
    @pytest.mark.asyncio
    async def test_trailing_stop_profit_protection(self, mock_broker):
        """Test: Trailing Stop schützt Gewinne"""
        manager = StopLossManager(broker=mock_broker, check_interval=0.1)
        
        # Setup Trailing Stop
        manager.set_stop_loss(
            symbol="AAPL",
            stop_type=StopType.TRAILING,
            trailing_percentage=3.0,
            entry_price=150.0
        )
        
        config = manager.get_stop_config("AAPL")
        
        # Preis steigt auf 160
        manager._update_trailing_stop(config, 160.0, "long")
        stop_at_160 = config.stop_price
        assert stop_at_160 == 160.0 * 0.97  # 155.2
        
        # Preis steigt weiter auf 165
        manager._update_trailing_stop(config, 165.0, "long")
        stop_at_165 = config.stop_price
        assert stop_at_165 == 165.0 * 0.97  # 160.05
        assert stop_at_165 > stop_at_160
        
        # Preis fällt auf 162 -> Stop bleibt bei 160.05
        manager._update_trailing_stop(config, 162.0, "long")
        assert config.stop_price == stop_at_165
        
        # Preis fällt auf 160 -> Trigger!
        assert manager._should_trigger_stop_loss(config, 160.0, "long")
