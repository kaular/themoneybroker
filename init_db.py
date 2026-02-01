"""
Database Initialization Script
Erstellt alle Tabellen und initial Daten
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db

if __name__ == "__main__":
    print("🚀 Initialisiere Trading Database...")
    init_db()
    print("✅ Database Setup abgeschlossen!")
    print("\nTabellen erstellt:")
    print("  - trades (Trade History)")
    print("  - strategies (Strategy Configs)")
    print("  - performance_metrics (Performance Tracking)")
    print("  - positions (Current Positions)")
