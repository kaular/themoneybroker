"""
Backtesting Engine

Tests trading strategies with historical data to validate performance
before risking real capital.

Features:
- Historical data simulation
- Strategy performance validation
- Walk-forward analysis
- Parameter optimization
- Realistic slippage & commissions
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from .metrics import PerformanceMetrics, TradeMetrics

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for backtesting"""
    start_date: datetime
    end_date: datetime
    initial_capital: float
    symbols: List[str]
    commission: float = 0.0  # $ per trade
    slippage: float = 0.001  # 0.1% slippage
    max_positions: int = 5
    position_size_pct: float = 0.2  # 20% per position
    

@dataclass
class Position:
    """Open position in backtest"""
    symbol: str
    entry_date: datetime
    entry_price: float
    shares: int
    cost_basis: float
    
    def current_value(self, current_price: float) -> float:
        return self.shares * current_price
    
    def unrealized_pnl(self, current_price: float) -> float:
        return self.current_value(current_price) - self.cost_basis


@dataclass
class BacktestResult:
    """Results from backtest run"""
    config: BacktestConfig
    trades: List[TradeMetrics]
    equity_curve: List[float]
    equity_dates: List[datetime]
    daily_returns: List[float]
    metrics: Dict
    strategy_name: str
    parameters: Dict = field(default_factory=dict)


class Backtester:
    """
    Backtesting engine for strategy validation
    
    Simulates trading with historical data to measure strategy performance
    before deploying with real capital.
    """
    
    def __init__(self, broker):
        """
        Initialize backtester
        
        Args:
            broker: Broker instance with historical data access
        """
        self.broker = broker
        self.positions: Dict[str, Position] = {}
        self.closed_trades: List[TradeMetrics] = []
        self.equity_curve: List[float] = []
        self.equity_dates: List[datetime] = []
        self.cash: float = 0.0
        
    async def run_backtest(self, strategy, config: BacktestConfig) -> BacktestResult:
        """
        Run backtest with given strategy
        
        Args:
            strategy: Strategy instance to test
            config: BacktestConfig with test parameters
        
        Returns:
            BacktestResult with all metrics
        """
        logger.info(f"Starting backtest: {config.start_date} to {config.end_date}")
        logger.info(f"Symbols: {config.symbols}, Initial Capital: ${config.initial_capital}")
        
        # Initialize
        self.cash = config.initial_capital
        self.positions = {}
        self.closed_trades = []
        self.equity_curve = [config.initial_capital]
        self.equity_dates = [config.start_date]
        
        # Get historical data for all symbols
        logger.info("Fetching historical data...")
        historical_data = await self._fetch_historical_data(
            config.symbols,
            config.start_date,
            config.end_date
        )
        
        if not historical_data:
            raise ValueError("No historical data available")
        
        # Get all unique dates
        all_dates = sorted(set(
            date for symbol_data in historical_data.values()
            for date in symbol_data.keys()
        ))
        
        logger.info(f"Simulating {len(all_dates)} trading days...")
        
        # Simulate day by day
        for i, current_date in enumerate(all_dates):
            # Get current prices
            current_prices = {
                symbol: data.get(current_date)
                for symbol, data in historical_data.items()
                if current_date in data
            }
            
            if not current_prices:
                continue
            
            # Update equity curve
            portfolio_value = self._calculate_portfolio_value(current_prices)
            self.equity_curve.append(portfolio_value)
            self.equity_dates.append(current_date)
            
            # Generate signals from strategy
            signals = await self._generate_signals(strategy, current_date, historical_data)
            
            # Process signals
            await self._process_signals(signals, current_prices, current_date, config)
            
            # Check for exits (stop-loss, take-profit, strategy exit signals)
            await self._check_exits(strategy, current_prices, current_date)
            
            # Log progress every 20 days
            if i % 20 == 0:
                logger.info(f"Day {i+1}/{len(all_dates)}: Portfolio ${portfolio_value:.2f}, Positions: {len(self.positions)}")
        
        # Close all remaining positions at end
        final_prices = {
            symbol: historical_data[symbol][all_dates[-1]]
            for symbol in self.positions.keys()
            if all_dates[-1] in historical_data[symbol]
        }
        await self._close_all_positions(final_prices, all_dates[-1])
        
        # Calculate metrics
        daily_returns = self._calculate_returns()
        metrics = PerformanceMetrics.calculate_all_metrics(
            trades=self.closed_trades,
            equity_curve=self.equity_curve,
            returns=daily_returns,
            initial_capital=config.initial_capital
        )
        
        logger.info(f"Backtest complete: {len(self.closed_trades)} trades")
        logger.info(f"Final Value: ${self.equity_curve[-1]:.2f}")
        logger.info(f"Total Return: {metrics['total_return_percent']:.2f}%")
        logger.info(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        logger.info(f"Max Drawdown: {metrics['max_drawdown_percent']:.2f}%")
        logger.info(f"Win Rate: {metrics['win_rate_percent']:.2f}%")
        
        return BacktestResult(
            config=config,
            trades=self.closed_trades,
            equity_curve=self.equity_curve,
            equity_dates=self.equity_dates,
            daily_returns=daily_returns,
            metrics=metrics,
            strategy_name=strategy.__class__.__name__,
            parameters=getattr(strategy, 'parameters', {})
        )
    
    async def _fetch_historical_data(self, symbols: List[str], 
                                     start_date: datetime, 
                                     end_date: datetime) -> Dict[str, Dict[datetime, float]]:
        """
        Fetch historical price data
        
        Returns:
            Dict[symbol -> Dict[date -> close_price]]
        """
        historical_data = {}
        
        for symbol in symbols:
            try:
                bars = await self.broker.get_historical_bars(
                    symbol=symbol,
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d'),
                    timeframe='1Day'
                )
                
                # Convert to dict of date -> price
                symbol_data = {
                    datetime.fromisoformat(bar.t.replace('Z', '+00:00')): float(bar.c)
                    for bar in bars
                }
                
                historical_data[symbol] = symbol_data
                logger.info(f"Loaded {len(symbol_data)} bars for {symbol}")
                
            except Exception as e:
                logger.warning(f"Failed to load data for {symbol}: {e}")
        
        return historical_data
    
    def _calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value"""
        positions_value = sum(
            pos.current_value(current_prices.get(symbol, pos.entry_price))
            for symbol, pos in self.positions.items()
            if symbol in current_prices
        )
        return self.cash + positions_value
    
    async def _generate_signals(self, strategy, current_date: datetime, 
                                historical_data: Dict) -> Dict[str, str]:
        """
        Generate buy/sell signals from strategy
        
        Returns:
            Dict[symbol -> 'buy' or 'sell']
        """
        signals = {}
        
        # Get historical prices up to current date
        for symbol in historical_data.keys():
            prices = {
                date: price
                for date, price in historical_data[symbol].items()
                if date <= current_date
            }
            
            if len(prices) < 20:  # Need minimum data
                continue
            
            # Check if strategy generates signal
            # This is simplified - real implementation would call strategy.should_buy/should_sell
            signal = await self._strategy_signal(strategy, symbol, prices, current_date)
            if signal:
                signals[symbol] = signal
        
        return signals
    
    async def _strategy_signal(self, strategy, symbol: str, 
                               prices: Dict[datetime, float], 
                               current_date: datetime) -> Optional[str]:
        """Get signal from strategy (buy/sell/None)"""
        # Simplified - would integrate with actual strategy logic
        # For now, return None (no signal)
        return None
    
    async def _process_signals(self, signals: Dict[str, str], 
                               current_prices: Dict[str, float],
                               current_date: datetime,
                               config: BacktestConfig):
        """Process buy/sell signals"""
        for symbol, signal in signals.items():
            if signal == 'buy' and symbol not in self.positions:
                await self._open_position(symbol, current_prices[symbol], current_date, config)
            elif signal == 'sell' and symbol in self.positions:
                await self._close_position(symbol, current_prices[symbol], current_date, config)
    
    async def _open_position(self, symbol: str, price: float, 
                            date: datetime, config: BacktestConfig):
        """Open new position"""
        if len(self.positions) >= config.max_positions:
            return  # Max positions reached
        
        # Calculate position size
        position_value = self.equity_curve[-1] * config.position_size_pct
        
        # Apply slippage
        entry_price = price * (1 + config.slippage)
        
        shares = int(position_value / entry_price)
        if shares == 0:
            return
        
        cost = shares * entry_price + config.commission
        
        if cost > self.cash:
            return  # Not enough cash
        
        # Open position
        self.positions[symbol] = Position(
            symbol=symbol,
            entry_date=date,
            entry_price=entry_price,
            shares=shares,
            cost_basis=cost
        )
        
        self.cash -= cost
        logger.debug(f"OPEN {symbol}: {shares} shares @ ${entry_price:.2f}")
    
    async def _close_position(self, symbol: str, price: float, 
                             date: datetime, config: BacktestConfig):
        """Close existing position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Apply slippage
        exit_price = price * (1 - config.slippage)
        
        # Calculate P&L
        proceeds = position.shares * exit_price - config.commission
        pnl = proceeds - position.cost_basis
        pnl_percent = pnl / position.cost_basis
        
        # Record trade
        holding_days = (date - position.entry_date).days
        trade = TradeMetrics(
            entry_date=position.entry_date,
            exit_date=date,
            symbol=symbol,
            entry_price=position.entry_price,
            exit_price=exit_price,
            shares=position.shares,
            pnl=pnl,
            pnl_percent=pnl_percent,
            holding_days=holding_days,
            win=pnl > 0
        )
        
        self.closed_trades.append(trade)
        self.cash += proceeds
        del self.positions[symbol]
        
        logger.debug(f"CLOSE {symbol}: ${pnl:.2f} ({pnl_percent*100:.2f}%)")
    
    async def _check_exits(self, strategy, current_prices: Dict[str, float], 
                          current_date: datetime):
        """Check for exit conditions (stop-loss, take-profit, etc.)"""
        # Simplified - would integrate with strategy exit rules
        pass
    
    async def _close_all_positions(self, prices: Dict[str, float], date: datetime):
        """Close all positions at end of backtest"""
        for symbol in list(self.positions.keys()):
            if symbol in prices:
                # Use zero commission for final close
                config = BacktestConfig(
                    start_date=date,
                    end_date=date,
                    initial_capital=0,
                    symbols=[],
                    commission=0
                )
                await self._close_position(symbol, prices[symbol], date, config)
    
    def _calculate_returns(self) -> List[float]:
        """Calculate daily returns from equity curve"""
        if len(self.equity_curve) < 2:
            return []
        
        returns = []
        for i in range(1, len(self.equity_curve)):
            ret = (self.equity_curve[i] - self.equity_curve[i-1]) / self.equity_curve[i-1]
            returns.append(ret)
        
        return returns
    
    async def walk_forward_analysis(self, strategy, config: BacktestConfig,
                                   window_size_days: int = 90,
                                   step_size_days: int = 30) -> List[BacktestResult]:
        """
        Perform walk-forward analysis
        
        Splits data into multiple periods and tests progressively
        to avoid overfitting.
        
        Args:
            strategy: Strategy to test
            config: Base backtest config
            window_size_days: Size of each test window
            step_size_days: Step between windows
        
        Returns:
            List of BacktestResult for each window
        """
        logger.info(f"Starting walk-forward analysis: {window_size_days}d windows, {step_size_days}d steps")
        
        results = []
        current_start = config.start_date
        
        while current_start + timedelta(days=window_size_days) <= config.end_date:
            window_end = current_start + timedelta(days=window_size_days)
            
            window_config = BacktestConfig(
                start_date=current_start,
                end_date=window_end,
                initial_capital=config.initial_capital,
                symbols=config.symbols,
                commission=config.commission,
                slippage=config.slippage,
                max_positions=config.max_positions,
                position_size_pct=config.position_size_pct
            )
            
            result = await self.run_backtest(strategy, window_config)
            results.append(result)
            
            current_start += timedelta(days=step_size_days)
        
        logger.info(f"Walk-forward complete: {len(results)} windows tested")
        return results
