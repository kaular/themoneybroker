"""
Trade Tracking Helper
Speichert Trades automatisch in die Database
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from .models import Trade
from ..brokers.base_broker import Order


def save_trade(
    db: Session,
    order: Order,
    strategy_id: Optional[int] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    extra_data: Optional[Dict[str, Any]] = None
) -> Trade:
    """
    Speichert einen Trade in die Database
    
    Args:
        db: Database Session
        order: Order Object vom Broker
        strategy_id: Optional Strategy ID
        stop_loss: Optional Stop Loss Price
        take_profit: Optional Take Profit Price
        extra_data: Optional zusätzliche Metadaten
    
    Returns:
        Trade: Gespeicherter Trade
    """
    # Hole order_id (kann .id oder .order_id sein)
    order_id = getattr(order, 'id', None) or getattr(order, 'order_id', None)
    
    trade = Trade(
        order_id=order_id,
        symbol=order.symbol,
        side=order.side.value if hasattr(order.side, 'value') else str(order.side),
        order_type=getattr(order, 'type', getattr(order, 'order_type', 'market')).value if hasattr(getattr(order, 'type', getattr(order, 'order_type', 'market')), 'value') else str(getattr(order, 'type', getattr(order, 'order_type', 'market'))),
        quantity=order.quantity,
        filled_qty=getattr(order, 'filled_qty', None) or getattr(order, 'filled_quantity', 0.0),
        avg_fill_price=getattr(order, 'filled_avg_price', None) or getattr(order, 'average_fill_price', None),
        limit_price=getattr(order, 'limit_price', None),
        status=order.status.value if hasattr(order.status, 'value') else str(order.status),
        submitted_at=getattr(order, 'submitted_at', None) or datetime.utcnow(),
        filled_at=getattr(order, 'filled_at', None),
        commission=0.0,  # Wird später vom Broker aktualisiert
        total_value=(getattr(order, 'filled_qty', None) or getattr(order, 'filled_quantity', 0.0)) * (getattr(order, 'filled_avg_price', None) or getattr(order, 'average_fill_price', 0.0)) if (getattr(order, 'filled_avg_price', None) or getattr(order, 'average_fill_price', None)) and (getattr(order, 'filled_qty', None) or getattr(order, 'filled_quantity', None)) else None,
        strategy_id=strategy_id,
        stop_loss=stop_loss,
        take_profit=take_profit,
        extra_data=extra_data
    )
    
    db.add(trade)
    db.commit()
    db.refresh(trade)
    
    return trade


def update_trade_status(
    db: Session,
    order_id: str,
    status: str,
    filled_qty: Optional[float] = None,
    filled_price: Optional[float] = None,
    filled_at: Optional[datetime] = None
) -> Optional[Trade]:
    """
    Updated Trade Status (z.B. filled, canceled)
    
    Args:
        db: Database Session
        order_id: Order ID
        status: Neuer Status
        filled_qty: Gefüllte Menge
        filled_price: Durchschnitts-Füllpreis
        filled_at: Zeitpunkt der Füllung
    
    Returns:
        Trade: Updated Trade oder None
    """
    trade = db.query(Trade).filter(Trade.order_id == order_id).first()
    
    if not trade:
        return None
    
    trade.status = status
    
    if filled_qty is not None:
        trade.filled_qty = filled_qty
    
    if filled_price is not None:
        trade.avg_fill_price = filled_price
        if trade.filled_qty:
            trade.total_value = trade.filled_qty * filled_price
    
    if filled_at is not None:
        trade.filled_at = filled_at
    
    db.commit()
    db.refresh(trade)
    
    return trade


def calculate_trade_pnl(
    db: Session,
    order_id: str,
    exit_price: float
) -> Optional[Trade]:
    """
    Berechnet PnL für einen geschlossenen Trade
    
    Args:
        db: Database Session
        order_id: Order ID des Entry Trades
        exit_price: Exit Preis
    
    Returns:
        Trade: Updated Trade mit PnL
    """
    trade = db.query(Trade).filter(Trade.order_id == order_id).first()
    
    if not trade or not trade.avg_fill_price:
        return None
    
    # Berechne PnL
    if trade.side.lower() == "buy":
        pnl = (exit_price - trade.avg_fill_price) * trade.filled_qty
    else:  # sell/short
        pnl = (trade.avg_fill_price - exit_price) * trade.filled_qty
    
    pnl_percent = (pnl / (trade.avg_fill_price * trade.filled_qty)) * 100 if trade.avg_fill_price else 0
    
    trade.pnl = pnl
    trade.pnl_percent = pnl_percent
    
    db.commit()
    db.refresh(trade)
    
    return trade


def get_open_trades(db: Session, symbol: Optional[str] = None) -> list:
    """
    Holt alle offenen Trades
    
    Args:
        db: Database Session
        symbol: Optional Symbol Filter
    
    Returns:
        list: Liste von offenen Trades
    """
    query = db.query(Trade).filter(
        Trade.status.in_(["pending", "new", "partially_filled", "accepted"])
    )
    
    if symbol:
        query = query.filter(Trade.symbol == symbol)
    
    return query.all()
