"""
Base Strategy Class
Abstrakte Basisklasse für Trading-Strategien
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd


class Signal(Enum):
    """Trading-Signale"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class TradeSignal:
    """Trade-Signal mit Zusatzinformationen"""
    symbol: str
    signal: Signal
    strength: float  # 0.0 - 1.0
    price: float
    quantity: Optional[float] = None
    reason: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseStrategy(ABC):
    """
    Abstrakte Basisklasse für Trading-Strategien
    Alle Strategien müssen diese Methoden implementieren
    """
    
    def __init__(self, name: str, parameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.parameters = parameters or {}
        self.enabled = True
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame, symbol: str) -> TradeSignal:
        """
        Analysiert Marktdaten und generiert ein Trading-Signal
        
        Args:
            data: DataFrame mit OHLCV-Daten
            symbol: Symbol des zu analysierenden Assets
        
        Returns:
            TradeSignal mit Handelsentscheidung
        """
        pass
    
    @abstractmethod
    def get_required_data_length(self) -> int:
        """
        Gibt die Mindestanzahl an Datenpoints zurück, die für die Analyse benötigt werden
        
        Returns:
            Anzahl benötigter Perioden
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validiert ob die Daten für die Analyse ausreichend sind
        
        Args:
            data: DataFrame mit Marktdaten
        
        Returns:
            True wenn Daten valide sind
        """
        if data is None or data.empty:
            return False
        
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            return False
        
        if len(data) < self.get_required_data_length():
            return False
        
        return True
    
    def enable(self):
        """Aktiviert die Strategie"""
        self.enabled = True
    
    def disable(self):
        """Deaktiviert die Strategie"""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Prüft ob die Strategie aktiviert ist"""
        return self.enabled
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Holt einen Parameter aus der Konfiguration"""
        return self.parameters.get(key, default)
    
    def set_parameter(self, key: str, value: Any):
        """Setzt einen Parameter"""
        self.parameters[key] = value
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
