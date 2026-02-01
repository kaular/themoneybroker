"""
Configuration Manager für Trading Bot
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Zentrale Konfigurationsklasse"""
    
    # Project paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    LOGS_DIR = BASE_DIR / "logs"
    CONFIG_DIR = BASE_DIR / "config"
    
    # Broker API Configuration
    BROKER_API_KEY: str = os.getenv("BROKER_API_KEY", "")
    BROKER_API_SECRET: str = os.getenv("BROKER_API_SECRET", "")
    BROKER_BASE_URL: str = os.getenv("BROKER_BASE_URL", "https://paper-api.alpaca.markets")
    
    # Trading Configuration
    TRADING_MODE: str = os.getenv("TRADING_MODE", "paper")  # paper or live
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE", "1000"))
    RISK_PERCENTAGE: float = float(os.getenv("RISK_PERCENTAGE", "0.02"))
    DEFAULT_SYMBOLS: list = os.getenv("DEFAULT_SYMBOLS", "AAPL,MSFT,GOOGL").split(",")
    
    # Risk Management
    MAX_DAILY_LOSS: float = float(os.getenv("MAX_DAILY_LOSS", "500"))
    MAX_OPEN_POSITIONS: int = int(os.getenv("MAX_OPEN_POSITIONS", "5"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/trading.log")
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """Validiert die Konfiguration und gibt Fehler zurück"""
        errors = []
        
        if not cls.BROKER_API_KEY or cls.BROKER_API_KEY == "your_api_key_here":
            errors.append("BROKER_API_KEY fehlt oder ist nicht gesetzt")
        
        if not cls.BROKER_API_SECRET or cls.BROKER_API_SECRET == "your_api_secret_here":
            errors.append("BROKER_API_SECRET fehlt oder ist nicht gesetzt")
        
        if not cls.BROKER_BASE_URL:
            errors.append("BROKER_BASE_URL fehlt")
        
        if cls.MAX_POSITION_SIZE <= 0:
            errors.append("MAX_POSITION_SIZE muss größer als 0 sein")
        
        if cls.RISK_PERCENTAGE <= 0 or cls.RISK_PERCENTAGE > 1:
            errors.append("RISK_PERCENTAGE muss zwischen 0 und 1 liegen")
        
        return (len(errors) == 0, errors)
    
    @classmethod
    def is_paper_trading(cls) -> bool:
        """Prüft ob Paper-Trading aktiviert ist"""
        return cls.TRADING_MODE.lower() == "paper"
    
    @classmethod
    def get_log_path(cls) -> Path:
        """Gibt den vollständigen Log-Pfad zurück"""
        log_path = cls.BASE_DIR / cls.LOG_FILE
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path


# Singleton instance
config = Config()
