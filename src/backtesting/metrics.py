"""
Performance Metrics Calculator for Backtesting

Calculates all key trading metrics:
- Sharpe Ratio
- Max Drawdown
- Win Rate
- Profit Factor
- Calmar Ratio
- Sortino Ratio
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime


@dataclass
class TradeMetrics:
    """Metrics for a single trade"""
    entry_date: datetime
    exit_date: datetime
    symbol: str
    entry_price: float
    exit_price: float
    shares: int
    pnl: float
    pnl_percent: float
    holding_days: int
    win: bool


class PerformanceMetrics:
    """
    Calculate comprehensive performance metrics from backtest results
    """
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe Ratio
        
        Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns
        
        Args:
            returns: List of daily/periodic returns
            risk_free_rate: Annual risk-free rate (default 2%)
        
        Returns:
            Sharpe ratio (annualized)
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        if std_return == 0:
            return 0.0
        
        # Annualize (assuming daily returns)
        sharpe = (mean_return * 252 - risk_free_rate) / (std_return * np.sqrt(252))
        return sharpe
    
    @staticmethod
    def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sortino Ratio (like Sharpe but only uses downside deviation)
        
        Args:
            returns: List of daily/periodic returns
            risk_free_rate: Annual risk-free rate
        
        Returns:
            Sortino ratio (annualized)
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        
        # Only negative returns for downside deviation
        downside_returns = returns_array[returns_array < 0]
        if len(downside_returns) == 0:
            return float('inf')  # No downside = infinite Sortino
        
        downside_std = np.std(downside_returns)
        if downside_std == 0:
            return 0.0
        
        # Annualize
        sortino = (mean_return * 252 - risk_free_rate) / (downside_std * np.sqrt(252))
        return sortino
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> Dict:
        """
        Calculate maximum drawdown
        
        Max Drawdown = largest peak-to-trough decline
        
        Args:
            equity_curve: List of portfolio values over time
        
        Returns:
            Dict with max_drawdown, max_drawdown_percent, peak, trough
        """
        if not equity_curve or len(equity_curve) < 2:
            return {
                'max_drawdown': 0.0,
                'max_drawdown_percent': 0.0,
                'peak': 0.0,
                'trough': 0.0,
                'peak_date': None,
                'trough_date': None
            }
        
        equity_array = np.array(equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        
        max_dd_idx = np.argmin(drawdown)
        max_dd_percent = drawdown[max_dd_idx]
        
        # Find peak before this trough
        peak_idx = np.argmax(equity_array[:max_dd_idx+1]) if max_dd_idx > 0 else 0
        
        return {
            'max_drawdown': equity_array[peak_idx] - equity_array[max_dd_idx],
            'max_drawdown_percent': abs(max_dd_percent),
            'peak': equity_array[peak_idx],
            'trough': equity_array[max_dd_idx],
            'peak_index': int(peak_idx),
            'trough_index': int(max_dd_idx)
        }
    
    @staticmethod
    def calculate_win_rate(trades: List[TradeMetrics]) -> Dict:
        """
        Calculate win rate and related metrics
        
        Args:
            trades: List of TradeMetrics objects
        
        Returns:
            Dict with win_rate, wins, losses, avg_win, avg_loss
        """
        if not trades:
            return {
                'win_rate': 0.0,
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'avg_win_percent': 0.0,
                'avg_loss_percent': 0.0
            }
        
        wins = [t for t in trades if t.win]
        losses = [t for t in trades if not t.win]
        
        avg_win = np.mean([t.pnl for t in wins]) if wins else 0.0
        avg_loss = np.mean([t.pnl for t in losses]) if losses else 0.0
        avg_win_pct = np.mean([t.pnl_percent for t in wins]) if wins else 0.0
        avg_loss_pct = np.mean([t.pnl_percent for t in losses]) if losses else 0.0
        
        return {
            'win_rate': len(wins) / len(trades) if trades else 0.0,
            'total_trades': len(trades),
            'wins': len(wins),
            'losses': len(losses),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_win_percent': avg_win_pct,
            'avg_loss_percent': avg_loss_pct
        }
    
    @staticmethod
    def calculate_profit_factor(trades: List[TradeMetrics]) -> float:
        """
        Calculate Profit Factor
        
        Profit Factor = Gross Profit / Gross Loss
        
        Args:
            trades: List of TradeMetrics objects
        
        Returns:
            Profit factor (>1 = profitable, <1 = losing)
        """
        if not trades:
            return 0.0
        
        gross_profit = sum(t.pnl for t in trades if t.win)
        gross_loss = abs(sum(t.pnl for t in trades if not t.win))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    @staticmethod
    def calculate_calmar_ratio(returns: List[float], equity_curve: List[float]) -> float:
        """
        Calculate Calmar Ratio
        
        Calmar = Annual Return / Max Drawdown
        
        Args:
            returns: List of returns
            equity_curve: List of portfolio values
        
        Returns:
            Calmar ratio (higher is better)
        """
        if not returns or not equity_curve:
            return 0.0
        
        # Calculate annual return
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        days = len(equity_curve)
        annual_return = (1 + total_return) ** (252 / days) - 1
        
        # Get max drawdown
        dd = PerformanceMetrics.calculate_max_drawdown(equity_curve)
        max_dd_pct = dd['max_drawdown_percent']
        
        if max_dd_pct == 0:
            return float('inf') if annual_return > 0 else 0.0
        
        return annual_return / max_dd_pct
    
    @staticmethod
    def calculate_expectancy(trades: List[TradeMetrics]) -> float:
        """
        Calculate expectancy (average $ per trade)
        
        Expectancy = (Win Rate * Avg Win) - (Loss Rate * Avg Loss)
        
        Args:
            trades: List of TradeMetrics objects
        
        Returns:
            Expected value per trade
        """
        if not trades:
            return 0.0
        
        metrics = PerformanceMetrics.calculate_win_rate(trades)
        win_rate = metrics['win_rate']
        loss_rate = 1 - win_rate
        avg_win = metrics['avg_win']
        avg_loss = abs(metrics['avg_loss'])
        
        return (win_rate * avg_win) - (loss_rate * avg_loss)
    
    @staticmethod
    def calculate_all_metrics(trades: List[TradeMetrics], equity_curve: List[float], 
                            returns: List[float], initial_capital: float) -> Dict:
        """
        Calculate all performance metrics at once
        
        Args:
            trades: List of completed trades
            equity_curve: Portfolio value over time
            returns: Daily returns
            initial_capital: Starting capital
        
        Returns:
            Dict with all metrics
        """
        win_metrics = PerformanceMetrics.calculate_win_rate(trades)
        dd_metrics = PerformanceMetrics.calculate_max_drawdown(equity_curve)
        
        final_value = equity_curve[-1] if equity_curve else initial_capital
        total_return = (final_value - initial_capital) / initial_capital
        
        # Calculate annualized return
        days = len(equity_curve)
        annual_return = (1 + total_return) ** (252 / days) - 1 if days > 0 else 0.0
        
        return {
            # Overall Performance
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_percent': total_return * 100,
            'annual_return': annual_return,
            'annual_return_percent': annual_return * 100,
            
            # Trade Statistics
            'total_trades': win_metrics['total_trades'],
            'wins': win_metrics['wins'],
            'losses': win_metrics['losses'],
            'win_rate': win_metrics['win_rate'],
            'win_rate_percent': win_metrics['win_rate'] * 100,
            
            # Win/Loss Metrics
            'avg_win': win_metrics['avg_win'],
            'avg_loss': win_metrics['avg_loss'],
            'avg_win_percent': win_metrics['avg_win_percent'],
            'avg_loss_percent': win_metrics['avg_loss_percent'],
            
            # Risk Metrics
            'sharpe_ratio': PerformanceMetrics.calculate_sharpe_ratio(returns),
            'sortino_ratio': PerformanceMetrics.calculate_sortino_ratio(returns),
            'max_drawdown': dd_metrics['max_drawdown'],
            'max_drawdown_percent': dd_metrics['max_drawdown_percent'] * 100,
            'calmar_ratio': PerformanceMetrics.calculate_calmar_ratio(returns, equity_curve),
            
            # Profitability
            'profit_factor': PerformanceMetrics.calculate_profit_factor(trades),
            'expectancy': PerformanceMetrics.calculate_expectancy(trades),
            
            # Holding Periods
            'avg_holding_days': np.mean([t.holding_days for t in trades]) if trades else 0.0,
            'max_holding_days': max([t.holding_days for t in trades]) if trades else 0,
            'min_holding_days': min([t.holding_days for t in trades]) if trades else 0,
        }
