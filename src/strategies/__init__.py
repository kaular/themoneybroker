"""Strategies Package"""
from .base_strategy import BaseStrategy, TradeSignal, Signal
from .sma_strategy import SMAStrategy

__all__ = [
    'BaseStrategy', 'TradeSignal', 'Signal',
    'SMAStrategy'
]
