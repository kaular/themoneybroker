"""
Pytest Fixtures und Konfiguration
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.models import Base, Trade, Strategy, PerformanceMetric, Position
from src.brokers.base_broker import BaseBroker, Order, OrderSide, OrderType, OrderStatus, Position as BrokerPosition, AccountInfo
from typing import List, Optional


@pytest.fixture(scope="function")
def test_db():
    """Test Database (In-Memory SQLite)"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_trade_data():
    """Sample Trade Data"""
    return {
        "order_id": "test-order-123",
        "symbol": "AAPL",
        "side": "buy",
        "order_type": "market",
        "quantity": 10.0,
        "filled_qty": 10.0,
        "avg_fill_price": 150.50,
        "status": "filled",
        "submitted_at": datetime.now(UTC),
        "filled_at": datetime.now(UTC),
        "total_value": 1505.0
    }


@pytest.fixture
def sample_strategy_data():
    """Sample Strategy Data"""
    return {
        "name": "Test SMA Strategy",
        "type": "sma",
        "description": "Test strategy for unit tests",
        "parameters": {
            "short_window": 20,
            "long_window": 50
        },
        "enabled": True,
        "max_position_size": 10000.0,
        "risk_per_trade": 0.02
    }


@pytest.fixture
def sample_performance_data():
    """Sample Performance Metrics Data"""
    return {
        "date": datetime.now(UTC),
        "period_type": "daily",
        "portfolio_value": 100000.0,
        "cash": 50000.0,
        "equity": 50000.0,
        "daily_pnl": 500.0,
        "daily_pnl_percent": 0.5,
        "total_pnl": 5000.0,
        "trades_count": 10,
        "winning_trades": 7,
        "losing_trades": 3,
        "win_rate": 70.0,
        "max_drawdown": -2.5,
        "sharpe_ratio": 1.8,
        "profit_factor": 2.33
    }


@pytest.fixture
def mock_order():
    """Mock Order Object"""
    order = Order()
    order.id = "mock-order-123"
    order.symbol = "AAPL"
    order.side = OrderSide.BUY
    order.type = OrderType.MARKET
    order.quantity = 10
    order.filled_qty = 10
    order.filled_avg_price = 150.50
    order.status = OrderStatus.FILLED
    order.submitted_at = datetime.utcnow()
    order.filled_at = datetime.utcnow()
    return order


@pytest.fixture
def mock_position():
    """Mock Position Object"""
    class MockPosition:
        def __init__(self):
            self.symbol = "AAPL"
            self.qty = 10
            self.side = "long"
            self.avg_entry_price = 150.00
            self.current_price = 155.00
            self.market_value = 1550.00
            self.cost_basis = 1500.00
            self.unrealized_pnl = 50.00
            self.unrealized_pnl_percent = 3.33
    
    return MockPosition()


class MockBroker(BaseBroker):
    """Mock Broker for Testing"""
    
    def __init__(self):
        super().__init__("test-key", "test-secret", "https://test.broker.com")
        self._connected = False
        self.positions = []
        self.orders = []
        self.mock_prices = {"AAPL": 150.0, "MSFT": 300.0, "GOOGL": 2800.0}
    
    def connect(self) -> bool:
        self._connected = True
        return True
    
    def disconnect(self) -> bool:
        self._connected = False
        return True
    
    def get_account_info(self) -> AccountInfo:
        return AccountInfo(
            cash=100000.0,
            portfolio_value=100000.0,
            buying_power=100000.0,
            equity=100000.0,
            unrealized_pnl=0.0,
            realized_pnl=0.0
        )
    
    def get_positions(self) -> List[Position]:
        return self.positions
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Einzelne Position abrufen"""
        for pos in self.positions:
            if pos.symbol == symbol:
                return pos
        return None
    
    def place_order(
        self,
        symbol: str,
        quantity: float,
        side: OrderSide,
        order_type: OrderType,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Order:
        order = Order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            order_type=order_type,
            status=OrderStatus.FILLED,
            order_id=f"mock-{len(self.orders)}",
            filled_quantity=quantity,
            average_fill_price=limit_price or self.mock_prices.get(symbol, 150.0),
            limit_price=limit_price,
            stop_price=stop_price,
            created_at=datetime.now(UTC),
            filled_at=datetime.now(UTC)
        )
        self.orders.append(order)
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        self.orders = [o for o in self.orders if o.order_id != order_id]
        return True
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Order-Status abrufen"""
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None
    
    def get_open_orders(self) -> List[Order]:
        """Alle offenen Orders abrufen"""
        return [o for o in self.orders if o.status == OrderStatus.PENDING]
    
    def get_market_price(self, symbol: str) -> float:
        """Aktuellen Marktpreis abrufen"""
        return self.mock_prices.get(symbol, 150.0)
    
    def get_historical_data(self, symbol: str, start_date, end_date, timeframe: str = "1D"):
        """Historische Kursdaten abrufen"""
        import pandas as pd
        return pd.DataFrame({
            'close': [150.0, 151.0, 152.0],
            'volume': [1000000, 1100000, 1050000]
        })
    
    def get_orders(self, status=None):
        """Legacy method for compatibility"""
        if status:
            return [o for o in self.orders if o.status == status]
        return self.orders
    
    def get_quote(self, symbol: str):
        """Legacy method for compatibility"""
        class MockQuote:
            def __init__(self, sym):
                self.symbol = sym
                self.bid = 150.0
                self.ask = 150.10
                self.last = 150.05
        return MockQuote(symbol)


@pytest.fixture
def mock_broker():
    """Mock Broker Fixture"""
    return MockBroker()
