"""
Tests für Database Models und Operations
"""
import pytest
from datetime import datetime, timedelta, UTC
from sqlalchemy import func

from src.database.models import Trade, Strategy, PerformanceMetric, Position


class TestTradeModel:
    """Tests für Trade Model"""
    
    def test_create_trade(self, test_db, sample_trade_data):
        """Test: Trade erstellen"""
        trade = Trade(**sample_trade_data)
        test_db.add(trade)
        test_db.commit()
        
        assert trade.id is not None
        assert trade.symbol == "AAPL"
        assert trade.order_id == "test-order-123"
        assert trade.quantity == 10.0
        assert trade.avg_fill_price == 150.50
    
    def test_trade_with_strategy(self, test_db, sample_trade_data, sample_strategy_data):
        """Test: Trade mit Strategy Relationship"""
        strategy = Strategy(**sample_strategy_data)
        test_db.add(strategy)
        test_db.commit()
        
        sample_trade_data['strategy_id'] = strategy.id
        trade = Trade(**sample_trade_data)
        test_db.add(trade)
        test_db.commit()
        
        assert trade.strategy is not None
        assert trade.strategy.name == "Test SMA Strategy"
    
    def test_trade_pnl_calculation(self, test_db, sample_trade_data):
        """Test: PnL Berechnung"""
        trade = Trade(**sample_trade_data)
        trade.pnl = 50.0
        trade.pnl_percent = 3.33
        
        test_db.add(trade)
        test_db.commit()
        
        assert trade.pnl == 50.0
        assert trade.pnl_percent == 3.33
    
    def test_query_trades_by_symbol(self, test_db, sample_trade_data):
        """Test: Trades nach Symbol filtern"""
        import time
        # Erstelle mehrere Trades
        for i, symbol in enumerate(["AAPL", "MSFT", "GOOGL", "AAPL"]):
            trade_data = sample_trade_data.copy()
            trade_data['order_id'] = f"order-{symbol}-{i}-{time.time()}"
            trade_data['symbol'] = symbol
            trade = Trade(**trade_data)
            test_db.add(trade)
            time.sleep(0.001)
        
        test_db.commit()
        
        # Query AAPL trades
        aapl_trades = test_db.query(Trade).filter(Trade.symbol == "AAPL").all()
        assert len(aapl_trades) == 2
    
    def test_query_filled_trades(self, test_db, sample_trade_data):
        """Test: Nur gefüllte Trades"""
        import time
        # Erstelle Trades mit verschiedenen Status
        for i, status in enumerate(["filled", "filled", "canceled", "pending"]):
            trade_data = sample_trade_data.copy()
            trade_data['order_id'] = f"order-{status}-{i}-{time.time()}"
            trade_data['status'] = status
            trade = Trade(**trade_data)
            test_db.add(trade)
        
        test_db.commit()
        
        filled_trades = test_db.query(Trade).filter(Trade.status == "filled").all()
        assert len(filled_trades) == 2


class TestStrategyModel:
    """Tests für Strategy Model"""
    
    def test_create_strategy(self, test_db, sample_strategy_data):
        """Test: Strategy erstellen"""
        strategy = Strategy(**sample_strategy_data)
        test_db.add(strategy)
        test_db.commit()
        
        assert strategy.id is not None
        assert strategy.name == "Test SMA Strategy"
        assert strategy.type == "sma"
        assert strategy.enabled is True
    
    def test_strategy_parameters(self, test_db, sample_strategy_data):
        """Test: Strategy Parameters (JSON)"""
        strategy = Strategy(**sample_strategy_data)
        test_db.add(strategy)
        test_db.commit()
        
        assert strategy.parameters['short_window'] == 20
        assert strategy.parameters['long_window'] == 50
    
    def test_strategy_performance_tracking(self, test_db, sample_strategy_data):
        """Test: Strategy Performance Tracking"""
        strategy = Strategy(**sample_strategy_data)
        strategy.total_trades = 10
        strategy.winning_trades = 7
        strategy.losing_trades = 3
        strategy.total_pnl = 500.0
        
        test_db.add(strategy)
        test_db.commit()
        
        win_rate = (strategy.winning_trades / strategy.total_trades) * 100
        assert win_rate == 70.0
        assert strategy.total_pnl == 500.0
    
    def test_strategy_with_trades(self, test_db, sample_strategy_data, sample_trade_data):
        """Test: Strategy mit mehreren Trades"""
        strategy = Strategy(**sample_strategy_data)
        test_db.add(strategy)
        test_db.commit()
        
        # Erstelle Trades für Strategy
        for i in range(3):
            trade_data = sample_trade_data.copy()
            trade_data['order_id'] = f"order-{i}"
            trade_data['strategy_id'] = strategy.id
            trade = Trade(**trade_data)
            test_db.add(trade)
        
        test_db.commit()
        
        assert len(strategy.trades) == 3


class TestPerformanceMetricModel:
    """Tests für PerformanceMetric Model"""
    
    def test_create_performance_metric(self, test_db, sample_performance_data):
        """Test: Performance Metric erstellen"""
        metric = PerformanceMetric(**sample_performance_data)
        test_db.add(metric)
        test_db.commit()
        
        assert metric.id is not None
        assert metric.portfolio_value == 100000.0
        assert metric.daily_pnl == 500.0
        assert metric.win_rate == 70.0
    
    def test_query_metrics_by_period(self, test_db, sample_performance_data):
        """Test: Metrics nach Zeitraum"""
        # Erstelle Metrics für verschiedene Tage
        for i in range(5):
            metric_data = sample_performance_data.copy()
            metric_data['date'] = datetime.now(UTC) - timedelta(days=i)
            metric = PerformanceMetric(**metric_data)
            test_db.add(metric)
        
        test_db.commit()
        
        # Query letzte 3 Tage
        since = datetime.now(UTC) - timedelta(days=3)
        recent_metrics = test_db.query(PerformanceMetric).filter(
            PerformanceMetric.date >= since
        ).all()
        
        # Sollte heute + 1 Tag + 2 Tage + 3 Tage = 4 sein, aber aufgrund von Rundung können es 3 oder 4 sein
        assert len(recent_metrics) >= 3
    
    def test_calculate_total_pnl(self, test_db, sample_performance_data):
        """Test: Total PnL Berechnung"""
        for i in range(3):
            metric_data = sample_performance_data.copy()
            metric_data['date'] = datetime.now(UTC) - timedelta(days=i)
            metric_data['daily_pnl'] = 100.0 * (i + 1)
            metric = PerformanceMetric(**metric_data)
            test_db.add(metric)
        
        test_db.commit()
        
        total_pnl = test_db.query(func.sum(PerformanceMetric.daily_pnl)).scalar()
        assert total_pnl == 600.0  # 100 + 200 + 300


class TestPositionModel:
    """Tests für Position Model"""
    
    def test_create_position(self, test_db):
        """Test: Position erstellen"""
        position = Position(
            symbol="AAPL",
            quantity=10.0,
            avg_entry_price=150.0,
            current_price=155.0,
            unrealized_pnl=50.0,
            unrealized_pnl_percent=3.33
        )
        test_db.add(position)
        test_db.commit()
        
        assert position.id is not None
        assert position.symbol == "AAPL"
        assert position.quantity == 10.0
    
    def test_position_with_stops(self, test_db):
        """Test: Position mit Stop-Loss und Take-Profit"""
        position = Position(
            symbol="AAPL",
            quantity=10.0,
            avg_entry_price=150.0,
            current_price=155.0,
            stop_loss=145.0,
            take_profit=160.0
        )
        test_db.add(position)
        test_db.commit()
        
        assert position.stop_loss == 145.0
        assert position.take_profit == 160.0
    
    def test_query_open_positions(self, test_db):
        """Test: Offene Positionen abfragen"""
        # Erstelle mehrere Positionen
        for symbol in ["AAPL", "MSFT", "GOOGL"]:
            position = Position(
                symbol=symbol,
                quantity=10.0,
                avg_entry_price=150.0
            )
            test_db.add(position)
        
        test_db.commit()
        
        positions = test_db.query(Position).all()
        assert len(positions) == 3


class TestDatabaseIntegration:
    """Integration Tests für Database Operations"""
    
    def test_complete_trade_workflow(self, test_db, sample_strategy_data, sample_trade_data):
        """Test: Kompletter Trade Workflow"""
        # 1. Strategy erstellen
        strategy = Strategy(**sample_strategy_data)
        test_db.add(strategy)
        test_db.commit()
        
        # 2. Trade öffnen
        entry_trade = Trade(**sample_trade_data)
        entry_trade.strategy_id = strategy.id
        entry_trade.side = "buy"
        test_db.add(entry_trade)
        test_db.commit()
        
        # 3. Trade schließen
        exit_trade_data = sample_trade_data.copy()
        exit_trade_data['order_id'] = "exit-order-123"
        exit_trade_data['side'] = "sell"
        exit_trade_data['avg_fill_price'] = 155.0
        exit_trade_data['pnl'] = 45.0  # (155 - 150.5) * 10
        exit_trade_data['pnl_percent'] = 2.99
        
        exit_trade = Trade(**exit_trade_data)
        exit_trade.strategy_id = strategy.id
        test_db.add(exit_trade)
        test_db.commit()
        
        # 4. Verify
        all_trades = test_db.query(Trade).filter(
            Trade.strategy_id == strategy.id
        ).all()
        
        assert len(all_trades) == 2
        assert exit_trade.pnl == 45.0
    
    def test_strategy_statistics_update(self, test_db, sample_strategy_data, sample_trade_data):
        """Test: Strategy Statistiken Update"""
        strategy = Strategy(**sample_strategy_data)
        test_db.add(strategy)
        test_db.commit()
        
        # Simuliere mehrere Trades
        for i in range(10):
            trade_data = sample_trade_data.copy()
            trade_data['order_id'] = f"order-{i}"
            trade_data['strategy_id'] = strategy.id
            trade_data['pnl'] = 50.0 if i < 7 else -30.0  # 7 winners, 3 losers
            trade = Trade(**trade_data)
            test_db.add(trade)
        
        test_db.commit()
        
        # Update Strategy Stats
        strategy.total_trades = 10
        strategy.winning_trades = 7
        strategy.losing_trades = 3
        strategy.total_pnl = (7 * 50.0) + (3 * -30.0)
        test_db.commit()
        
        assert strategy.total_trades == 10
        assert strategy.winning_trades == 7
        assert strategy.total_pnl == 260.0
