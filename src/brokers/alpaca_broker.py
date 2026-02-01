"""
Alpaca Broker Implementation
Integration mit Alpaca Trading API
"""
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide as AlpacaOrderSide, TimeInForce, OrderType as AlpacaOrderType
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from typing import List, Optional, Any
from datetime import datetime
import logging

from .base_broker import (
    BaseBroker, Order, Position, AccountInfo,
    OrderType, OrderSide, OrderStatus
)


class AlpacaBroker(BaseBroker):
    """Alpaca Trading API Integration"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str):
        super().__init__(api_key, api_secret, base_url)
        self.trading_client: Optional[TradingClient] = None
        self.data_client: Optional[StockHistoricalDataClient] = None
        self.logger = logging.getLogger(__name__)
        self.paper = 'paper' in base_url
    
    def connect(self) -> bool:
        """Verbindung zu Alpaca herstellen"""
        try:
            self.trading_client = TradingClient(
                api_key=self.api_key,
                secret_key=self.api_secret,
                paper=self.paper
            )
            self.data_client = StockHistoricalDataClient(
                api_key=self.api_key,
                secret_key=self.api_secret
            )
            # Test connection
            self.trading_client.get_account()
            self._connected = True
            self.logger.info("Erfolgreich mit Alpaca verbunden")
            return True
        except Exception as e:
            self.logger.error(f"Verbindung zu Alpaca fehlgeschlagen: {e}")
            self._connected = False
            return False
    
    def disconnect(self) -> bool:
        """Verbindung trennen"""
        self._connected = False
        self.trading_client = None
        self.data_client = None
        self.logger.info("Verbindung zu Alpaca getrennt")
        return True
    
    def get_account_info(self) -> AccountInfo:
        """Account-Informationen abrufen"""
        if not self.trading_client:
            raise RuntimeError("Nicht verbunden")
        
        account = self.trading_client.get_account()
        return AccountInfo(
            cash=float(account.cash),
            portfolio_value=float(account.portfolio_value),
            buying_power=float(account.buying_power),
            equity=float(account.equity),
            unrealized_pnl=float(account.unrealized_plpc if hasattr(account, 'unrealized_plpc') else 0),
            realized_pnl=float(0)
        )
    
    def get_positions(self) -> List[Position]:
        """Alle Positionen abrufen"""
        if not self.trading_client:
            raise RuntimeError("Nicht verbunden")
        
        positions = []
        for pos in self.trading_client.get_all_positions():
            positions.append(Position(
                symbol=pos.symbol,
                quantity=float(pos.qty),
                entry_price=float(pos.avg_entry_price),
                current_price=float(pos.current_price),
                unrealized_pnl=float(pos.unrealized_pl),
                side="long" if float(pos.qty) > 0 else "short"
            ))
        return positions
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Einzelne Position abrufen"""
        if not self.trading_client:
            raise RuntimeError("Nicht verbunden")
        
        try:
            pos = self.trading_client.get_open_position(symbol)
            return Position(
                symbol=pos.symbol,
                quantity=float(pos.qty),
                entry_price=float(pos.avg_entry_price),
                current_price=float(pos.current_price),
                unrealized_pnl=float(pos.unrealized_pl),
                side="long" if float(pos.qty) > 0 else "short"
            )
        except Exception:
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
        """Order platzieren"""
        if not self.trading_client:
            raise RuntimeError("Nicht verbunden")
        
        # Convert side
        alpaca_side = AlpacaOrderSide.BUY if side == OrderSide.BUY else AlpacaOrderSide.SELL
        
        # Create order request based on type
        if order_type == OrderType.MARKET:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=alpaca_side,
                time_in_force=TimeInForce.GTC
            )
        elif order_type == OrderType.LIMIT and limit_price:
            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=alpaca_side,
                time_in_force=TimeInForce.GTC,
                limit_price=limit_price
            )
        elif order_type == OrderType.STOP and stop_price:
            order_data = StopOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=alpaca_side,
                time_in_force=TimeInForce.GTC,
                stop_price=stop_price
            )
        else:
            raise ValueError(f"Invalid order type or missing price parameters")
        
        alpaca_order = self.trading_client.submit_order(order_data)
        
        self.logger.info(f"Order platziert: {side.value} {quantity} {symbol} @ {order_type.value}")
        
        return self._convert_alpaca_order(alpaca_order)
    
    def cancel_order(self, order_id: str) -> bool:
        """Order stornieren"""
        if not self.trading_client:
            raise RuntimeError("Nicht verbunden")
        
        try:
            self.trading_client.cancel_order_by_id(order_id)
            self.logger.info(f"Order {order_id} storniert")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Stornieren von Order {order_id}: {e}")
            return False
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Order-Status abrufen"""
        if not self.trading_client:
            raise RuntimeError("Nicht verbunden")
        
        try:
            alpaca_order = self.trading_client.get_order_by_id(order_id)
            return self._convert_alpaca_order(alpaca_order)
        except Exception:
            return None
    
    def get_open_orders(self) -> List[Order]:
        """Alle offenen Orders abrufen"""
        if not self.trading_client:
            raise RuntimeError("Nicht verbunden")
        
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus
        
        request_params = GetOrdersRequest(
            status=QueryOrderStatus.OPEN
        )
        orders = []
        for alpaca_order in self.trading_client.get_orders(filter=request_params):
            orders.append(self._convert_alpaca_order(alpaca_order))
        return orders
    
    def get_market_price(self, symbol: str) -> float:
        """Aktuellen Marktpreis abrufen"""
        if not self.data_client:
            raise RuntimeError("Nicht verbunden")
        
        try:
            from alpaca.data.requests import StockLatestTradeRequest
            request_params = StockLatestTradeRequest(symbol_or_symbols=symbol)
            latest_trade = self.data_client.get_stock_latest_trade(request_params)
            return float(latest_trade[symbol].price)
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen des Preises für {symbol}: {e}")
            raise
    
    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframe: str = "1D"
    ) -> Any:
        """Historische Daten abrufen"""
        if not self.data_client:
            raise RuntimeError("Nicht verbunden")
        
        # Map timeframe string to TimeFrame enum
        timeframe_map = {
            "1Min": TimeFrame.Minute,
            "5Min": TimeFrame.Hour,  # Use Hour as proxy
            "1H": TimeFrame.Hour,
            "1D": TimeFrame.Day,
            "1W": TimeFrame.Week,
            "1M": TimeFrame.Month
        }
        
        tf = timeframe_map.get(timeframe, TimeFrame.Day)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=tf,
            start=start_date,
            end=end_date
        )
        
        bars = self.data_client.get_stock_bars(request_params)
        return bars.df
    
    def _convert_alpaca_order(self, alpaca_order) -> Order:
        """Konvertiert Alpaca Order zu unserem Order Model"""
        status_map = {
            'new': OrderStatus.PENDING,
            'partially_filled': OrderStatus.PARTIALLY_FILLED,
            'filled': OrderStatus.FILLED,
            'canceled': OrderStatus.CANCELLED,
            'rejected': OrderStatus.REJECTED,
        }
        
        return Order(
            symbol=alpaca_order.symbol,
            quantity=float(alpaca_order.qty),
            side=OrderSide.BUY if alpaca_order.side == 'buy' else OrderSide.SELL,
            order_type=OrderType(alpaca_order.type),
            status=status_map.get(alpaca_order.status, OrderStatus.PENDING),
            order_id=alpaca_order.id,
            filled_quantity=float(alpaca_order.filled_qty or 0),
            average_fill_price=float(alpaca_order.filled_avg_price or 0),
            limit_price=float(alpaca_order.limit_price) if alpaca_order.limit_price else None,
            stop_price=float(alpaca_order.stop_price) if alpaca_order.stop_price else None,
            created_at=alpaca_order.created_at,
            filled_at=alpaca_order.filled_at
        )
