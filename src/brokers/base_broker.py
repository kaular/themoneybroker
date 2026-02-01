"""
Base Broker Interface
Abstrakte Basisklasse für alle Broker-Integrationen
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderType(Enum):
    """Order-Typen"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Order-Seiten"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order-Status"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Position:
    """Position Model"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    side: str = "long"


@dataclass
class Order:
    """Order Model"""
    symbol: str
    quantity: float
    side: OrderSide
    order_type: OrderType
    status: OrderStatus
    order_id: Optional[str] = None
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    created_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None


@dataclass
class AccountInfo:
    """Account Information"""
    cash: float
    portfolio_value: float
    buying_power: float
    equity: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0


class BaseBroker(ABC):
    """
    Abstrakte Basisklasse für Broker-Integrationen
    Alle Broker müssen diese Methoden implementieren
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self._connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Verbindung zum Broker herstellen"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Verbindung zum Broker trennen"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> AccountInfo:
        """Account-Informationen abrufen"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Alle offenen Positionen abrufen"""
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Position]:
        """Einzelne Position abrufen"""
        pass
    
    @abstractmethod
    def place_order(
        self,
        symbol: str,
        quantity: float,
        side: OrderSide,
        order_type: OrderType,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Order:
        """Order platzieren"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Order stornieren"""
        pass
    
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """Order-Status abrufen"""
        pass
    
    @abstractmethod
    def get_open_orders(self) -> List[Order]:
        """Alle offenen Orders abrufen"""
        pass
    
    @abstractmethod
    def get_market_price(self, symbol: str) -> float:
        """Aktuellen Marktpreis abrufen"""
        pass
    
    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1D"
    ) -> Any:
        """Historische Kursdaten abrufen"""
        pass
    
    def is_connected(self) -> bool:
        """Prüft ob die Verbindung besteht"""
        return self._connected
