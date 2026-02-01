"""
SQLAlchemy Models für Trading Database
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, UTC

Base = declarative_base()


class Trade(Base):
    """Trade History Model"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Order Information
    order_id = Column(String, unique=True, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    side = Column(String, nullable=False)  # buy/sell
    order_type = Column(String, nullable=False)  # market/limit
    
    # Quantities & Prices
    quantity = Column(Float, nullable=False)
    filled_qty = Column(Float, default=0.0)
    avg_fill_price = Column(Float)
    limit_price = Column(Float, nullable=True)
    
    # Status & Timestamps
    status = Column(String, nullable=False)  # pending/filled/canceled/rejected
    submitted_at = Column(DateTime, default=datetime.utcnow)
    filled_at = Column(DateTime, nullable=True)
    
    # Financial Data
    commission = Column(Float, default=0.0)
    total_value = Column(Float)  # filled_qty * avg_fill_price
    
    # Strategy & Risk
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    
    # PnL (wird bei Exit berechnet)
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="trades")
    
    def __repr__(self):
        return f"<Trade {self.symbol} {self.side} {self.quantity}@{self.avg_fill_price}>"


class Strategy(Base):
    """Trading Strategy Configuration"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Strategy Info
    name = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)  # sma/rsi/macd/custom
    description = Column(Text, nullable=True)
    
    # Configuration
    parameters = Column(JSON, nullable=False)  # Strategy-specific params
    enabled = Column(Boolean, default=True)
    
    # Risk Management
    max_position_size = Column(Float, nullable=True)
    risk_per_trade = Column(Float, nullable=True)
    
    # Performance
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_trade_at = Column(DateTime, nullable=True)
    
    # Relationships
    trades = relationship("Trade", back_populates="strategy")
    
    def __repr__(self):
        return f"<Strategy {self.name} ({self.type})>"


class PerformanceMetric(Base):
    """Daily/Period Performance Metrics"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time Period
    date = Column(DateTime, index=True, nullable=False)
    period_type = Column(String, nullable=False)  # daily/weekly/monthly
    
    # Portfolio Metrics
    portfolio_value = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    equity = Column(Float, nullable=False)
    
    # Performance
    daily_pnl = Column(Float, default=0.0)
    daily_pnl_percent = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    
    # Trade Statistics
    trades_count = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    
    # Risk Metrics
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    
    # Position Info
    open_positions = Column(Integer, default=0)
    largest_position = Column(Float, nullable=True)
    
    # Metadata
    extra_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PerformanceMetric {self.date} PnL: {self.daily_pnl}>"


class Position(Base):
    """Current Open Positions (Snapshot)"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    symbol = Column(String, index=True, nullable=False)
    quantity = Column(Float, nullable=False)
    avg_entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    
    # PnL
    unrealized_pnl = Column(Float, default=0.0)
    unrealized_pnl_percent = Column(Float, default=0.0)
    
    # Risk Management
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    
    # Strategy
    strategy_id = Column(Integer, ForeignKey('strategies.id'), nullable=True)
    
    # Timestamps
    opened_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    extra_data = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<Position {self.symbol} {self.quantity}@{self.avg_entry_price}>"
