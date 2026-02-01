"""
Test Growth Stock Scanner
"""

import pytest
import asyncio
from datetime import datetime, UTC
from src.scanners import GrowthStockScanner
from tests.conftest import MockBroker


@pytest.mark.asyncio
async def test_scanner_initialization():
    """Test Scanner Initialisierung"""
    broker = MockBroker()
    scanner = GrowthStockScanner(broker)
    
    assert scanner.broker == broker
    assert len(scanner.megatrend_sectors) > 0


@pytest.mark.asyncio
async def test_get_screening_universe():
    """Test Universe Retrieval"""
    broker = MockBroker()
    scanner = GrowthStockScanner(broker)
    
    universe = await scanner._get_screening_universe()
    
    assert len(universe) > 0
    assert 'PLTR' in universe  # AI Stock
    assert 'IONQ' in universe  # Quantum Stock
    assert 'TSLA' in universe  # Robotics


@pytest.mark.asyncio
async def test_calculate_growth_score():
    """Test Growth Score Berechnung"""
    broker = MockBroker()
    broker.mock_prices = {
        'AAPL': 150.0,
        'SPY': 450.0
    }
    scanner = GrowthStockScanner(broker)
    
    score = await scanner._calculate_growth_score('AAPL')
    
    # Score sollte berechnet werden
    assert score is not None
    assert 0 <= score.score <= 100
    assert score.symbol == 'AAPL'


@pytest.mark.asyncio
async def test_scan_universe_with_filters():
    """Test Universe Scan mit Filtern"""
    broker = MockBroker()
    broker.mock_prices = {
        'AAPL': 150.0,
        'MSFT': 300.0,
        'GOOGL': 140.0,
    }
    scanner = GrowthStockScanner(broker)
    
    # Scanne nur spezifische Symbole
    results = await scanner.scan_universe(
        symbols=['AAPL', 'MSFT', 'GOOGL'],
        min_score=0.0  # Alle akzeptieren für Test
    )
    
    assert len(results) > 0
    # Ergebnisse sollten nach Score sortiert sein
    for i in range(len(results) - 1):
        assert results[i].score >= results[i + 1].score


@pytest.mark.asyncio
async def test_top_picks():
    """Test Top Picks Auswahl"""
    broker = MockBroker()
    scanner = GrowthStockScanner(broker)
    
    # Erstelle Mock-Ergebnisse
    from src.scanners.growth_scanner import GrowthScore
    mock_results = [
        GrowthScore(symbol='STOCK1', score=95.0, reason="High growth"),
        GrowthScore(symbol='STOCK2', score=85.0, reason="Good momentum"),
        GrowthScore(symbol='STOCK3', score=75.0, reason="Decent"),
        GrowthScore(symbol='STOCK4', score=65.0, reason="OK"),
    ]
    
    top_3 = scanner.get_top_picks(mock_results, count=3)
    
    assert len(top_3) == 3
    assert top_3[0].symbol == 'STOCK1'
    assert top_3[0].score == 95.0


@pytest.mark.asyncio
async def test_format_report():
    """Test Report Formatierung"""
    broker = MockBroker()
    scanner = GrowthStockScanner(broker)
    
    from src.scanners.growth_scanner import GrowthScore
    results = [
        GrowthScore(
            symbol='NVDA',
            score=92.5,
            revenue_growth=120.0,
            relative_strength=45.0,
            price_change_30d=35.0,
            volume_increase=80.0,
            sector='AI_INFRASTRUCTURE',
            reason="Megatrend leader"
        )
    ]
    
    report = scanner.format_report(results)
    
    assert 'NVDA' in report
    assert '92.5' in report
    assert 'Score' in report
    assert len(report) > 100  # Sollte substantieller Text sein


@pytest.mark.asyncio
async def test_price_change_calculation():
    """Test Preisänderungs-Berechnung"""
    broker = MockBroker()
    scanner = GrowthStockScanner(broker)
    
    bars = [
        {'close': 100.0, 'volume': 1000000, 'timestamp': datetime.now(UTC)},
        {'close': 105.0, 'volume': 1100000, 'timestamp': datetime.now(UTC)},
        {'close': 110.0, 'volume': 1200000, 'timestamp': datetime.now(UTC)},
    ]
    
    change = scanner._calculate_price_change(bars)
    
    assert change is not None
    assert abs(change - 10.0) < 0.1  # 100 -> 110 = 10% change


@pytest.mark.asyncio
async def test_volume_trend_calculation():
    """Test Volumen-Trend Berechnung"""
    broker = MockBroker()
    scanner = GrowthStockScanner(broker)
    
    bars = [
        {'close': 100.0, 'volume': 1000000, 'timestamp': datetime.now(UTC)},
        {'close': 101.0, 'volume': 1000000, 'timestamp': datetime.now(UTC)},
        {'close': 102.0, 'volume': 1000000, 'timestamp': datetime.now(UTC)},
        {'close': 103.0, 'volume': 1000000, 'timestamp': datetime.now(UTC)},
        {'close': 104.0, 'volume': 1000000, 'timestamp': datetime.now(UTC)},
        {'close': 105.0, 'volume': 1500000, 'timestamp': datetime.now(UTC)},  # Volumen steigt
        {'close': 106.0, 'volume': 1500000, 'timestamp': datetime.now(UTC)},
        {'close': 107.0, 'volume': 1500000, 'timestamp': datetime.now(UTC)},
        {'close': 108.0, 'volume': 1500000, 'timestamp': datetime.now(UTC)},
        {'close': 109.0, 'volume': 1500000, 'timestamp': datetime.now(UTC)},
    ]
    
    volume_increase = scanner._calculate_volume_trend(bars)
    
    assert volume_increase is not None
    assert volume_increase > 0  # Volumen ist gestiegen


@pytest.mark.asyncio
async def test_momentum_calculation():
    """Test Momentum Score"""
    broker = MockBroker()
    scanner = GrowthStockScanner(broker)
    
    # Aufwärtstrend
    bars = [
        {'close': 100.0 + i, 'volume': 1000000, 'timestamp': datetime.now(UTC)}
        for i in range(20)
    ]
    
    momentum = scanner._calculate_momentum(bars)
    
    assert momentum is not None
    assert momentum > 0  # Positiver Momentum bei Aufwärtstrend


@pytest.mark.asyncio
async def test_sector_identification():
    """Test Sektor-Identifikation"""
    broker = MockBroker()
    scanner = GrowthStockScanner(broker)
    
    sector_pltr = await scanner._get_sector('PLTR')
    sector_ionq = await scanner._get_sector('IONQ')
    
    assert sector_pltr == 'AI_INFRASTRUCTURE'
    assert sector_ionq == 'QUANTUM_COMPUTING'


@pytest.mark.asyncio
async def test_empty_universe():
    """Test mit leerem Universe"""
    broker = MockBroker()
    scanner = GrowthStockScanner(broker)
    
    results = await scanner.scan_universe(
        symbols=[],  # Leere Liste
        min_score=0.0
    )
    
    assert len(results) == 0


@pytest.mark.asyncio
async def test_high_score_filter():
    """Test dass nur hohe Scores zurückgegeben werden"""
    broker = MockBroker()
    broker.mock_prices = {
        'AAPL': 150.0,
        'MSFT': 300.0,
    }
    scanner = GrowthStockScanner(broker)
    
    # Sehr hoher min_score - sollte weniger Ergebnisse geben
    results = await scanner.scan_universe(
        symbols=['AAPL', 'MSFT'],
        min_score=90.0  # Sehr hoch
    )
    
    # Alle Ergebnisse sollten Score >= 90 haben
    for result in results:
        assert result.score >= 90.0
