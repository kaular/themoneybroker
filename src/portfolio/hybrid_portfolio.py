"""
Hybrid Portfolio Manager - 70/30 Core-Satellite Strategy

Core (70%): Stable, dividend-paying stocks and blue chips
Satellite (30%): High-risk moonshot opportunities from Growth Scanner

Features:
- Automatic rebalancing
- Separate risk limits per bucket
- Performance attribution
- Tax-loss harvesting opportunities
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class PortfolioType(Enum):
    """Portfolio bucket types"""
    CORE = "core"
    SATELLITE = "satellite"


@dataclass
class PortfolioAllocation:
    """Portfolio allocation details"""
    symbol: str
    portfolio_type: PortfolioType
    target_weight: float  # Target % of total portfolio
    current_weight: float  # Current % of total portfolio
    current_value: float  # Current USD value
    shares: int
    average_entry: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    last_rebalance: datetime


@dataclass
class RebalanceAction:
    """Rebalancing trade action"""
    symbol: str
    action: str  # 'buy' or 'sell'
    shares: int
    reason: str
    urgency: str  # 'low', 'medium', 'high'


class HybridPortfolio:
    """
    Hybrid Portfolio Manager with Core-Satellite Strategy
    
    Allocation:
    - Core (70%): VOO, SCHD, AAPL, MSFT, etc. - Low volatility, dividends
    - Satellite (30%): Growth Scanner picks - High-risk moonshots
    
    Rebalancing triggers:
    - Deviation >5% from target allocation
    - Quarterly scheduled rebalancing
    - Position hits stop-loss or take-profit
    """
    
    # Core holdings with target weights (out of 70% total)
    CORE_HOLDINGS = {
        'VOO': 0.30,   # S&P 500 ETF - 30% of core = 21% of total
        'SCHD': 0.20,  # Dividend ETF - 20% of core = 14% of total
        'AAPL': 0.15,  # Apple - 15% of core = 10.5% of total
        'MSFT': 0.15,  # Microsoft - 15% of core = 10.5% of total
        'NVDA': 0.10,  # Nvidia - 10% of core = 7% of total
        'GOOGL': 0.10, # Google - 10% of core = 7% of total
    }
    
    def __init__(self, broker, scanner, risk_manager):
        """
        Initialize Hybrid Portfolio Manager
        
        Args:
            broker: Broker instance for trading
            scanner: GrowthStockScanner instance for satellite picks
            risk_manager: RiskManager instance for position sizing
        """
        self.broker = broker
        self.scanner = scanner
        self.risk_manager = risk_manager
        
        self.core_allocation = 0.70  # 70% in core
        self.satellite_allocation = 0.30  # 30% in satellite
        
        self.rebalance_threshold = 0.05  # Rebalance if >5% deviation
        self.rebalance_interval_days = 90  # Quarterly rebalancing
        
        self.last_rebalance = None
        self.positions: Dict[str, PortfolioAllocation] = {}
        
        # Satellite-specific settings
        self.satellite_max_positions = 10  # Max 10 moonshot positions
        self.satellite_max_per_position = 0.05  # Max 5% total portfolio per satellite
        self.satellite_min_score = 75.0  # Minimum scanner score for satellite
        
    async def initialize(self):
        """Initialize portfolio from current broker positions"""
        logger.info("Initializing Hybrid Portfolio Manager...")
        
        try:
            # Get current account info
            account = await self.broker.get_account()
            positions = await self.broker.get_positions()
            
            total_value = float(account.portfolio_value)
            
            # Classify existing positions
            for position in positions:
                symbol = position.symbol
                current_value = float(position.market_value)
                current_weight = current_value / total_value
                
                # Determine if core or satellite
                portfolio_type = (
                    PortfolioType.CORE if symbol in self.CORE_HOLDINGS
                    else PortfolioType.SATELLITE
                )
                
                # Get target weight
                if portfolio_type == PortfolioType.CORE:
                    core_weight = self.CORE_HOLDINGS.get(symbol, 0)
                    target_weight = core_weight * self.core_allocation
                else:
                    # Satellite positions equally weighted
                    target_weight = self.satellite_allocation / self.satellite_max_positions
                
                allocation = PortfolioAllocation(
                    symbol=symbol,
                    portfolio_type=portfolio_type,
                    target_weight=target_weight,
                    current_weight=current_weight,
                    current_value=current_value,
                    shares=int(position.qty),
                    average_entry=float(position.avg_entry_price),
                    unrealized_pnl=float(position.unrealized_pl),
                    unrealized_pnl_percent=float(position.unrealized_plpc) * 100,
                    last_rebalance=datetime.now()
                )
                
                self.positions[symbol] = allocation
            
            logger.info(f"Portfolio initialized with {len(self.positions)} positions")
            logger.info(f"Core positions: {self._get_core_count()}")
            logger.info(f"Satellite positions: {self._get_satellite_count()}")
            
        except Exception as e:
            logger.error(f"Error initializing portfolio: {e}")
            raise
    
    def _get_core_count(self) -> int:
        """Get number of core positions"""
        return sum(1 for p in self.positions.values() 
                  if p.portfolio_type == PortfolioType.CORE)
    
    def _get_satellite_count(self) -> int:
        """Get number of satellite positions"""
        return sum(1 for p in self.positions.values() 
                  if p.portfolio_type == PortfolioType.SATELLITE)
    
    async def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary with allocation breakdown"""
        account = await self.broker.get_account()
        total_value = float(account.portfolio_value)
        
        core_value = sum(p.current_value for p in self.positions.values()
                        if p.portfolio_type == PortfolioType.CORE)
        satellite_value = sum(p.current_value for p in self.positions.values()
                             if p.portfolio_type == PortfolioType.SATELLITE)
        
        core_pnl = sum(p.unrealized_pnl for p in self.positions.values()
                      if p.portfolio_type == PortfolioType.CORE)
        satellite_pnl = sum(p.unrealized_pnl for p in self.positions.values()
                           if p.portfolio_type == PortfolioType.SATELLITE)
        
        return {
            'total_value': total_value,
            'core': {
                'value': core_value,
                'allocation': core_value / total_value if total_value > 0 else 0,
                'target_allocation': self.core_allocation,
                'pnl': core_pnl,
                'positions_count': self._get_core_count()
            },
            'satellite': {
                'value': satellite_value,
                'allocation': satellite_value / total_value if total_value > 0 else 0,
                'target_allocation': self.satellite_allocation,
                'pnl': satellite_pnl,
                'positions_count': self._get_satellite_count()
            },
            'total_pnl': core_pnl + satellite_pnl,
            'last_rebalance': self.last_rebalance
        }
    
    async def check_rebalancing_needed(self) -> bool:
        """Check if portfolio needs rebalancing"""
        # Check time-based rebalancing
        if self.last_rebalance:
            days_since_rebalance = (datetime.now() - self.last_rebalance).days
            if days_since_rebalance >= self.rebalance_interval_days:
                logger.info(f"Quarterly rebalancing due ({days_since_rebalance} days since last)")
                return True
        
        # Check allocation deviation
        summary = await self.get_portfolio_summary()
        core_deviation = abs(summary['core']['allocation'] - self.core_allocation)
        satellite_deviation = abs(summary['satellite']['allocation'] - self.satellite_allocation)
        
        if core_deviation > self.rebalance_threshold:
            logger.info(f"Core allocation deviation: {core_deviation:.2%} > {self.rebalance_threshold:.2%}")
            return True
        
        if satellite_deviation > self.rebalance_threshold:
            logger.info(f"Satellite allocation deviation: {satellite_deviation:.2%} > {self.rebalance_threshold:.2%}")
            return True
        
        return False
    
    async def get_rebalancing_actions(self) -> List[RebalanceAction]:
        """Calculate rebalancing actions needed"""
        actions = []
        
        account = await self.broker.get_account()
        total_value = float(account.portfolio_value)
        
        # Get current prices
        symbols = list(self.positions.keys()) + list(self.CORE_HOLDINGS.keys())
        bars = await self.broker.get_latest_bars(list(set(symbols)))
        prices = {symbol: float(bar.c) for symbol, bar in bars.items()}
        
        # Calculate target values for core holdings
        for symbol, core_weight in self.CORE_HOLDINGS.items():
            target_value = total_value * self.core_allocation * core_weight
            
            if symbol in self.positions:
                current_value = self.positions[symbol].current_value
                value_diff = target_value - current_value
            else:
                value_diff = target_value
            
            if abs(value_diff) > 100:  # Only if difference > $100
                price = prices.get(symbol)
                if not price:
                    continue
                
                shares = int(abs(value_diff) / price)
                if shares > 0:
                    action = RebalanceAction(
                        symbol=symbol,
                        action='buy' if value_diff > 0 else 'sell',
                        shares=shares,
                        reason=f"Core rebalancing: ${value_diff:+.2f} from target",
                        urgency='medium'
                    )
                    actions.append(action)
        
        return actions
    
    async def execute_rebalancing(self, actions: List[RebalanceAction]) -> Dict:
        """Execute rebalancing trades"""
        results = {
            'success': [],
            'failed': [],
            'total_actions': len(actions)
        }
        
        logger.info(f"Executing {len(actions)} rebalancing actions...")
        
        for action in actions:
            try:
                if action.action == 'buy':
                    order = await self.broker.submit_order(
                        symbol=action.symbol,
                        qty=action.shares,
                        side='buy',
                        type='market',
                        time_in_force='day'
                    )
                    logger.info(f"Rebalance BUY: {action.shares} {action.symbol} - {action.reason}")
                    results['success'].append({
                        'symbol': action.symbol,
                        'action': 'buy',
                        'shares': action.shares,
                        'order_id': order.id
                    })
                
                elif action.action == 'sell':
                    order = await self.broker.submit_order(
                        symbol=action.symbol,
                        qty=action.shares,
                        side='sell',
                        type='market',
                        time_in_force='day'
                    )
                    logger.info(f"Rebalance SELL: {action.shares} {action.symbol} - {action.reason}")
                    results['success'].append({
                        'symbol': action.symbol,
                        'action': 'sell',
                        'shares': action.shares,
                        'order_id': order.id
                    })
                
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Failed to execute {action.action} {action.symbol}: {e}")
                results['failed'].append({
                    'symbol': action.symbol,
                    'action': action.action,
                    'error': str(e)
                })
        
        # Update last rebalance time
        if results['success']:
            self.last_rebalance = datetime.now()
        
        logger.info(f"Rebalancing complete: {len(results['success'])} success, {len(results['failed'])} failed")
        return results
    
    async def update_satellite_positions(self, scanner_results: List = None) -> Dict:
        """
        Update satellite positions with Growth Scanner picks
        
        Args:
            scanner_results: Optional pre-scanned results. If None, will scan.
        
        Returns:
            Dict with added/removed positions
        """
        logger.info("Updating satellite positions...")
        
        # Scan for moonshot candidates if not provided
        if scanner_results is None:
            scanner_results = await self.scanner.scan_universe(
                min_score=self.satellite_min_score,
                max_market_cap=50_000_000_000  # Max $50B market cap
            )
        
        # Get top picks
        top_picks = sorted(scanner_results, key=lambda x: x.score, reverse=True)
        top_picks = top_picks[:self.satellite_max_positions]
        
        account = await self.broker.get_account()
        total_value = float(account.portfolio_value)
        
        # Calculate position size for each satellite
        position_value = total_value * self.satellite_max_per_position
        
        actions = {
            'added': [],
            'kept': [],
            'removed': []
        }
        
        # Get current satellite holdings
        current_satellites = [
            p.symbol for p in self.positions.values()
            if p.portfolio_type == PortfolioType.SATELLITE
        ]
        
        # Determine which to add
        for pick in top_picks:
            if pick.symbol not in current_satellites:
                # New satellite position
                actions['added'].append({
                    'symbol': pick.symbol,
                    'score': pick.score,
                    'reason': pick.reason,
                    'target_value': position_value
                })
            else:
                actions['kept'].append(pick.symbol)
        
        # Determine which to remove
        top_symbols = {pick.symbol for pick in top_picks}
        for symbol in current_satellites:
            if symbol not in top_symbols:
                actions['removed'].append(symbol)
        
        logger.info(f"Satellite update: +{len(actions['added'])} -{len(actions['removed'])} ={len(actions['kept'])}")
        return actions
    
    async def get_all_positions(self) -> List[PortfolioAllocation]:
        """Get all portfolio positions"""
        return list(self.positions.values())
    
    async def get_core_positions(self) -> List[PortfolioAllocation]:
        """Get core portfolio positions"""
        return [p for p in self.positions.values() 
                if p.portfolio_type == PortfolioType.CORE]
    
    async def get_satellite_positions(self) -> List[PortfolioAllocation]:
        """Get satellite portfolio positions"""
        return [p for p in self.positions.values() 
                if p.portfolio_type == PortfolioType.SATELLITE]
