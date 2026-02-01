"""
Growth Stock Scanner
Identifiziert Aktien mit hohem Wachstumspotenzial (wie NVIDIA 2014)
"""

import asyncio
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GrowthScore:
    """Growth Stock Score mit Details"""
    symbol: str
    score: float  # 0-100
    revenue_growth: Optional[float] = None
    relative_strength: Optional[float] = None
    momentum_score: Optional[float] = None
    volume_increase: Optional[float] = None
    price_change_30d: Optional[float] = None
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    reason: str = ""


class GrowthStockScanner:
    """
    Scannt nach High-Growth Stocks mit Moonshot-Potenzial
    
    Kriterien (angelehnt an NVIDIA 2014):
    - Hohe Revenue Growth (>30% p.a.)
    - Starkes Momentum (Relative Strength)
    - Steigendes Volumen (Institutional Interest)
    - Small/Mid Cap (<50B Market Cap)
    - Technologie-Sektor bevorzugt
    """
    
    def __init__(self, broker):
        self.broker = broker
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Sektor-Prioritäten (wie NVIDIA im AI-Boom)
        self.megatrend_sectors = {
            'AI_INFRASTRUCTURE': 1.5,      # Höchste Priorität
            'QUANTUM_COMPUTING': 1.4,
            'ROBOTICS': 1.3,
            'BIOTECH': 1.3,
            'CLEAN_ENERGY': 1.2,
            'SPACE': 1.2,
            'SEMICONDUCTORS': 1.4,
            'CLOUD_INFRASTRUCTURE': 1.3,
        }
        
    async def scan_universe(
        self, 
        symbols: Optional[List[str]] = None,
        min_score: float = 60.0,
        max_market_cap: float = 50_000_000_000  # 50B max
    ) -> List[GrowthScore]:
        """
        Scannt eine Liste von Symbolen oder das gesamte Universum
        
        Args:
            symbols: Liste von Ticker-Symbolen (None = alle)
            min_score: Minimaler Growth Score (0-100)
            max_market_cap: Maximale Market Cap in USD
            
        Returns:
            Liste von GrowthScore Objekten, sortiert nach Score
        """
        if symbols is None:
            # Hole alle verfügbaren Symbole (US-Aktien)
            symbols = await self._get_screening_universe()
        
        self.logger.info(f"Scanning {len(symbols)} symbols for growth opportunities...")
        
        results = []
        for symbol in symbols:
            try:
                score = await self._calculate_growth_score(symbol)
                
                # Filter nach Market Cap und Score
                if score and score.score >= min_score:
                    if score.market_cap and score.market_cap <= max_market_cap:
                        results.append(score)
                        
            except Exception as e:
                self.logger.debug(f"Error scanning {symbol}: {e}")
                continue
        
        # Sortiere nach Score
        results.sort(key=lambda x: x.score, reverse=True)
        
        self.logger.info(f"Found {len(results)} growth candidates (score >= {min_score})")
        return results
    
    async def _get_screening_universe(self) -> List[str]:
        """
        Holt eine Liste von Aktien für das Screening
        Fokus auf US Tech Stocks, Small/Mid Caps
        """
        # TODO: Integration mit Alpaca Asset API
        # Für jetzt: Vordefinierte Liste von interessanten Symbolen
        
        # Tech Small/Mid Caps
        tech_universe = [
            # AI/ML Infrastructure
            'PLTR', 'AI', 'SNOW', 'PATH', 'IONQ', 'RGTI',
            # Semiconductors
            'ARM', 'ASML', 'MRVL', 'MPWR', 'CRUS',
            # Cloud/SaaS
            'DDOG', 'NET', 'CRWD', 'ZS', 'DOCN',
            # Biotech
            'CRSP', 'EDIT', 'NTLA', 'BEAM', 'VRTX',
            # Clean Energy
            'ENPH', 'SEDG', 'RUN', 'FSLR', 'PLUG',
            # Space
            'RKLB', 'SPIR', 'ASTS',
            # Robotics
            'TSLA', 'RIVN', 'JOBY',
            # Quantum
            'IONQ', 'RGTI', 'QBTS',
            # Cybersecurity
            'CRWD', 'PANW', 'ZS', 'OKTA',
        ]
        
        return list(set(tech_universe))  # Remove duplicates
    
    async def _calculate_growth_score(self, symbol: str) -> Optional[GrowthScore]:
        """
        Berechnet Growth Score für ein Symbol (0-100)
        
        Score-Komponenten:
        - 30%: Revenue Growth
        - 25%: Relative Strength (vs Market)
        - 20%: Momentum (Price Change)
        - 15%: Volume Increase
        - 10%: Sektor-Bonus
        """
        try:
            # Hole Preis-Daten (30 Tage)
            bars = await self._get_historical_bars(symbol, days=30)
            if not bars or len(bars) < 20:
                return None
            
            # Berechne technische Metriken
            price_change_30d = self._calculate_price_change(bars)
            relative_strength = await self._calculate_relative_strength(symbol, bars)
            volume_increase = self._calculate_volume_trend(bars)
            momentum_score = self._calculate_momentum(bars)
            
            # Hole Fundamental-Daten (simuliert - später via API)
            revenue_growth = await self._estimate_revenue_growth(symbol)
            sector = await self._get_sector(symbol)
            market_cap = await self._get_market_cap(symbol)
            
            # Berechne Gesamt-Score
            score = 0.0
            reasons = []
            
            # 1. Revenue Growth (30 Punkte)
            if revenue_growth:
                rev_score = min(30, (revenue_growth / 50) * 30)  # 50% growth = volle Punkte
                score += rev_score
                if revenue_growth > 30:
                    reasons.append(f"Revenue +{revenue_growth:.0f}%")
            
            # 2. Relative Strength (25 Punkte)
            if relative_strength:
                rs_score = min(25, (relative_strength / 40) * 25)  # 40% outperformance = voll
                score += rs_score
                if relative_strength > 20:
                    reasons.append(f"Outperforming market by {relative_strength:.0f}%")
            
            # 3. Momentum (20 Punkte)
            if momentum_score:
                mom_score = min(20, (momentum_score / 50) * 20)  # 50% gain = voll
                score += mom_score
                if price_change_30d and price_change_30d > 20:
                    reasons.append(f"Strong momentum +{price_change_30d:.0f}%")
            
            # 4. Volume Increase (15 Punkte)
            if volume_increase:
                vol_score = min(15, (volume_increase / 100) * 15)  # 100% increase = voll
                score += vol_score
                if volume_increase > 50:
                    reasons.append(f"Volume surge +{volume_increase:.0f}%")
            
            # 5. Sektor-Bonus (10 Punkte)
            sector_multiplier = 1.0
            if sector:
                for trend_sector, multiplier in self.megatrend_sectors.items():
                    if trend_sector.lower() in sector.lower():
                        sector_multiplier = multiplier
                        score += 10
                        reasons.append(f"Megatrend sector: {sector}")
                        break
            
            # Sektor-Multiplikator anwenden
            score *= sector_multiplier
            score = min(100, score)  # Cap bei 100
            
            return GrowthScore(
                symbol=symbol,
                score=round(score, 2),
                revenue_growth=revenue_growth,
                relative_strength=relative_strength,
                momentum_score=momentum_score,
                volume_increase=volume_increase,
                price_change_30d=price_change_30d,
                sector=sector,
                market_cap=market_cap,
                reason=" | ".join(reasons) if reasons else "Growth candidate"
            )
            
        except Exception as e:
            self.logger.debug(f"Error calculating score for {symbol}: {e}")
            return None
    
    async def _get_historical_bars(self, symbol: str, days: int = 30) -> List[Dict]:
        """Holt historische Preis-Daten"""
        try:
            end_date = datetime.now(UTC)
            start_date = end_date - timedelta(days=days)
            
            # Nutze Broker API (Alpaca)
            bars = await asyncio.to_thread(
                self.broker.api.get_bars,
                symbol,
                '1Day',
                start=start_date.isoformat(),
                end=end_date.isoformat()
            )
            
            return [
                {
                    'close': float(bar.c),
                    'volume': int(bar.v),
                    'timestamp': bar.t
                }
                for bar in bars
            ]
            
        except Exception as e:
            self.logger.debug(f"Error fetching bars for {symbol}: {e}")
            return []
    
    def _calculate_price_change(self, bars: List[Dict]) -> Optional[float]:
        """Berechnet prozentuale Preisänderung"""
        if len(bars) < 2:
            return None
        
        first_price = bars[0]['close']
        last_price = bars[-1]['close']
        
        return ((last_price - first_price) / first_price) * 100
    
    async def _calculate_relative_strength(
        self, 
        symbol: str, 
        bars: List[Dict]
    ) -> Optional[float]:
        """
        Berechnet Relative Strength vs SPY (S&P 500)
        Positiv = Outperformance, Negativ = Underperformance
        """
        try:
            # Hole SPY Daten für gleichen Zeitraum
            spy_bars = await self._get_historical_bars('SPY', days=30)
            
            if not spy_bars or len(spy_bars) < 2:
                return None
            
            # Berechne Performance
            stock_performance = self._calculate_price_change(bars)
            spy_performance = self._calculate_price_change(spy_bars)
            
            if stock_performance is None or spy_performance is None:
                return None
            
            # Relative Strength = Stock Performance - Market Performance
            return stock_performance - spy_performance
            
        except Exception as e:
            self.logger.debug(f"Error calculating RS for {symbol}: {e}")
            return None
    
    def _calculate_volume_trend(self, bars: List[Dict]) -> Optional[float]:
        """Berechnet Volumen-Trend (prozentuale Änderung)"""
        if len(bars) < 10:
            return None
        
        # Vergleiche letzten 5 Tage mit vorherigen 5 Tagen
        recent_volume = sum(bar['volume'] for bar in bars[-5:]) / 5
        older_volume = sum(bar['volume'] for bar in bars[-10:-5]) / 5
        
        if older_volume == 0:
            return None
        
        return ((recent_volume - older_volume) / older_volume) * 100
    
    def _calculate_momentum(self, bars: List[Dict]) -> Optional[float]:
        """
        Berechnet Momentum Score
        Kombiniert kurzfristige und mittelfristige Trends
        """
        if len(bars) < 10:
            return None
        
        # Kurzfristig: Letzte 5 Tage
        short_term = ((bars[-1]['close'] - bars[-5]['close']) / bars[-5]['close']) * 100
        
        # Mittelfristig: Letzte 20 Tage (wenn vorhanden)
        if len(bars) >= 20:
            mid_term = ((bars[-1]['close'] - bars[-20]['close']) / bars[-20]['close']) * 100
            momentum = (short_term * 0.6) + (mid_term * 0.4)
        else:
            momentum = short_term
        
        return momentum
    
    async def _estimate_revenue_growth(self, symbol: str) -> Optional[float]:
        """
        Schätzt Revenue Growth (später via Fundamental API)
        Für jetzt: Placeholder mit realistischen Werten
        """
        # TODO: Integration mit Financial Data API (AlphaVantage, FinancialModelingPrep)
        # Für Development: Simuliere basierend auf Preis-Momentum
        
        bars = await self._get_historical_bars(symbol, days=90)
        if not bars or len(bars) < 60:
            return None
        
        # Nutze Preis-Momentum als Proxy (nicht perfekt, aber Annäherung)
        price_change = self._calculate_price_change(bars)
        
        if price_change and price_change > 0:
            # Revenue Growth ist oft 30-50% des Price Momentum bei Growth Stocks
            estimated_growth = price_change * 0.4
            return min(150, max(0, estimated_growth))  # Cap zwischen 0-150%
        
        return None
    
    async def _get_sector(self, symbol: str) -> Optional[str]:
        """Holt Sektor-Information"""
        # TODO: Integration mit Asset API
        # Placeholder: Mapping bekannter Symbole
        
        sector_map = {
            'PLTR': 'AI_INFRASTRUCTURE',
            'IONQ': 'QUANTUM_COMPUTING',
            'RGTI': 'QUANTUM_COMPUTING',
            'ARM': 'SEMICONDUCTORS',
            'TSLA': 'ROBOTICS',
            'CRSP': 'BIOTECH',
            'RKLB': 'SPACE',
        }
        
        return sector_map.get(symbol, 'TECHNOLOGY')
    
    async def _get_market_cap(self, symbol: str) -> Optional[float]:
        """Holt Market Cap"""
        # TODO: Integration mit Asset API
        # Placeholder: Schätzung basierend auf Preis
        
        try:
            bars = await self._get_historical_bars(symbol, days=1)
            if bars:
                # Sehr grobe Schätzung (für Demo)
                # In Realität: shares_outstanding * price
                return bars[-1]['close'] * 1_000_000_000  # Placeholder
        except:
            pass
        
        return None
    
    def get_top_picks(
        self, 
        results: List[GrowthScore], 
        count: int = 10
    ) -> List[GrowthScore]:
        """
        Gibt die Top N Growth Stocks zurück
        """
        return results[:count]
    
    def format_report(self, results: List[GrowthScore]) -> str:
        """
        Formatiert Scan-Ergebnisse als Text-Report
        """
        if not results:
            return "No growth stocks found matching criteria."
        
        report = "=" * 80 + "\n"
        report += "GROWTH STOCK SCANNER REPORT\n"
        report += f"Scan Date: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        report += f"Stocks Found: {len(results)}\n"
        report += "=" * 80 + "\n\n"
        
        for i, stock in enumerate(results[:20], 1):  # Top 20
            report += f"{i}. {stock.symbol} - Score: {stock.score:.1f}/100\n"
            
            if stock.price_change_30d:
                report += f"   📈 30-Day Change: {stock.price_change_30d:+.1f}%\n"
            
            if stock.revenue_growth:
                report += f"   💰 Est. Revenue Growth: {stock.revenue_growth:.1f}%\n"
            
            if stock.relative_strength:
                report += f"   💪 Relative Strength: {stock.relative_strength:+.1f}% vs Market\n"
            
            if stock.volume_increase:
                report += f"   📊 Volume Trend: {stock.volume_increase:+.1f}%\n"
            
            if stock.sector:
                report += f"   🏢 Sector: {stock.sector}\n"
            
            if stock.reason:
                report += f"   ✅ {stock.reason}\n"
            
            report += "\n"
        
        return report
