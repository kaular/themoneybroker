"""
FastAPI Backend für Trading Bot UI
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, UTC
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import asyncio
import json
import logging

from src.brokers import AlpacaBroker, OrderType, OrderSide
from src.strategies import SMAStrategy
from src.risk import RiskManager, RiskLimits, StopLossManager, StopType
from src.execution import ExecutionEngine
from src.utils import config, setup_logger
from src.database import init_db, get_db
from src.database.models import Trade, Strategy, PerformanceMetric
from src.database.trade_tracker import save_trade, update_trade_status
from src.scanners import GrowthStockScanner
from src.portfolio import HybridPortfolio

# Logger
logger = setup_logger("API", config.LOG_LEVEL)

# Lifespan Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("API shutting down")

# FastAPI App
app = FastAPI(
    title="TheMoneyBroker API",
    description="Trading Bot Control & Configuration API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS für React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Bot State
class BotState:
    def __init__(self):
        self.broker: Optional[AlpacaBroker] = None
        self.risk_manager: Optional[RiskManager] = None
        self.stop_loss_manager: Optional[StopLossManager] = None
        self.execution_engine: Optional[ExecutionEngine] = None
        self.portfolio_manager: Optional[HybridPortfolio] = None
        self.strategies: List = []
        self.is_running = False
        self.connected = False
        self.ws_connections: List[WebSocket] = []

bot_state = BotState()


# Pydantic Models
class BrokerConfig(BaseModel):
    api_key: str
    api_secret: str
    base_url: str


class RiskConfig(BaseModel):
    max_position_size: float
    max_daily_loss: float
    max_open_positions: int
    risk_per_trade: float


class StrategyConfig(BaseModel):
    name: str
    type: str
    parameters: Dict[str, Any]
    enabled: bool = True


class OrderRequest(BaseModel):
    symbol: str
    quantity: float
    side: str  # "buy" or "sell"
    order_type: str = "market"
    limit_price: Optional[float] = None


class StopLossRequest(BaseModel):
    symbol: str
    stop_type: str  # "fixed", "trailing", "percentage"
    stop_price: Optional[float] = None
    stop_percentage: Optional[float] = None
    trailing_percentage: Optional[float] = None
    entry_price: Optional[float] = None


class TakeProfitRequest(BaseModel):
    symbol: str
    take_profit_price: Optional[float] = None
    take_profit_percentage: Optional[float] = None


# WebSocket Manager
async def broadcast_update(data: dict):
    """Sendet Updates an alle verbundenen WebSocket Clients"""
    dead_connections = []
    for connection in bot_state.ws_connections:
        try:
            await connection.send_json(data)
        except:
            dead_connections.append(connection)
    
    # Entferne tote Verbindungen
    for conn in dead_connections:
        bot_state.ws_connections.remove(conn)


# API Endpoints

@app.get("/")
async def root():
    """API Health Check"""
    return {
        "status": "online",
        "name": "TheMoneyBroker API",
        "version": "1.0.0",
        "bot_running": bot_state.is_running,
        "broker_connected": bot_state.connected
    }


@app.post("/broker/connect")
async def connect_broker(config_data: BrokerConfig):
    """Verbindet mit dem Broker"""
    try:
        bot_state.broker = AlpacaBroker(
            api_key=config_data.api_key,
            api_secret=config_data.api_secret,
            base_url=config_data.base_url
        )
        
        if bot_state.broker.connect():
            bot_state.connected = True
            account = bot_state.broker.get_account_info()
            
            # Initialisiere Stop-Loss Manager
            bot_state.stop_loss_manager = StopLossManager(
                broker=bot_state.broker,
                check_interval=1.0  # Prüfe alle 1 Sekunde
            )
            # Starte Monitoring
            await bot_state.stop_loss_manager.start_monitoring()
            logger.info("Stop-Loss Manager initialisiert und gestartet")
            
            await broadcast_update({
                "type": "broker_connected",
                "data": {
                    "portfolio_value": float(account.portfolio_value),
                    "cash": float(account.cash)
                }
            })
            
            return {
                "success": True,
                "message": "Broker verbunden",
                "account": {
                    "portfolio_value": float(account.portfolio_value),
                    "cash": float(account.cash),
                    "buying_power": float(account.buying_power)
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Verbindung fehlgeschlagen")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/broker/disconnect")
async def disconnect_broker():
    """Trennt die Broker-Verbindung"""
    if bot_state.broker:
        bot_state.broker.disconnect()
        bot_state.connected = False
        await broadcast_update({"type": "broker_disconnected"})
        return {"success": True, "message": "Broker getrennt"}
    return {"success": False, "message": "Kein Broker verbunden"}


@app.get("/account")
async def get_account():
    """Holt Account-Informationen"""
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker nicht verbunden")
    
    try:
        account = bot_state.broker.get_account_info()
        return {
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "buying_power": float(account.buying_power),
            "equity": float(account.equity),
            "unrealized_pnl": float(account.unrealized_pnl),
            "realized_pnl": float(account.realized_pnl)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/positions")
async def get_positions():
    """Holt alle Positionen"""
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker nicht verbunden")
    
    try:
        positions = bot_state.broker.get_positions()
        return [{
            "symbol": pos.symbol,
            "quantity": float(pos.quantity),
            "entry_price": float(pos.entry_price),
            "current_price": float(pos.current_price),
            "unrealized_pnl": float(pos.unrealized_pnl),
            "side": pos.side
        } for pos in positions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders")
async def get_orders():
    """Holt alle Orders"""
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker nicht verbunden")
    
    try:
        orders = bot_state.broker.get_open_orders()
        return [{
            "order_id": order.order_id,
            "symbol": order.symbol,
            "quantity": float(order.quantity),
            "side": order.side.value,
            "order_type": order.order_type.value,
            "status": order.status.value,
            "filled_quantity": float(order.filled_quantity)
        } for order in orders]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orders")
async def place_order(order_req: OrderRequest, db: Session = Depends(get_db)):
    """Platziert eine neue Order und speichert sie in der Database"""
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker nicht verbunden")
    
    try:
        side = OrderSide.BUY if order_req.side.lower() == "buy" else OrderSide.SELL
        order_type = OrderType.MARKET if order_req.order_type.lower() == "market" else OrderType.LIMIT
        
        order = bot_state.broker.place_order(
            symbol=order_req.symbol,
            quantity=order_req.quantity,
            side=side,
            order_type=order_type,
            limit_price=order_req.limit_price
        )
        
        # Speichere Trade in Database
        try:
            trade = save_trade(
                db=db,
                order=order,
                extra_data={"source": "manual"}
            )
            logger.info(f"Trade saved to database: {trade.order_id}")
        except Exception as db_error:
            logger.error(f"Failed to save trade to database: {db_error}")
        
        await broadcast_update({
            "type": "order_placed",
            "data": {
                "symbol": order.symbol,
                "side": order.side.value,
                "quantity": float(order.quantity)
            }
        })
        
        return {
            "success": True,
            "order_id": order.order_id,
            "status": order.status.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/orders/{order_id}")
async def cancel_order(order_id: str):
    """Storniert eine Order"""
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker nicht verbunden")
    
    try:
        success = bot_state.broker.cancel_order(order_id)
        if success:
            await broadcast_update({"type": "order_cancelled", "order_id": order_id})
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/risk/configure")
async def configure_risk(risk_config: RiskConfig):
    """Konfiguriert Risk Management"""
    try:
        limits = RiskLimits(
            max_position_size=risk_config.max_position_size,
            max_daily_loss=risk_config.max_daily_loss,
            max_open_positions=risk_config.max_open_positions,
            risk_per_trade=risk_config.risk_per_trade
        )
        bot_state.risk_manager = RiskManager(limits)
        
        return {"success": True, "message": "Risk Management konfiguriert"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/strategies")
async def get_strategies():
    """Holt alle Strategien"""
    return [{
        "name": s.name,
        "enabled": s.is_enabled(),
        "parameters": s.parameters
    } for s in bot_state.strategies]


@app.post("/strategies")
async def add_strategy(strategy_config: StrategyConfig):
    """Fügt eine neue Strategie hinzu"""
    try:
        if strategy_config.type == "sma":
            strategy = SMAStrategy(
                name=strategy_config.name,
                parameters=strategy_config.parameters
            )
            if not strategy_config.enabled:
                strategy.disable()
            
            bot_state.strategies.append(strategy)
            
            return {"success": True, "message": f"Strategie '{strategy_config.name}' hinzugefügt"}
        else:
            raise HTTPException(status_code=400, detail="Unbekannter Strategie-Typ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/bot/start")
async def start_bot():
    """Startet den Trading Bot"""
    if not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker nicht verbunden")
    
    if not bot_state.risk_manager:
        raise HTTPException(status_code=400, detail="Risk Manager nicht konfiguriert")
    
    bot_state.is_running = True
    await broadcast_update({"type": "bot_started"})
    
    return {"success": True, "message": "Bot gestartet"}


@app.post("/bot/stop")
async def stop_bot():
    """Stoppt den Trading Bot"""
    bot_state.is_running = False
    await broadcast_update({"type": "bot_stopped"})
    
    return {"success": True, "message": "Bot gestoppt"}


@app.get("/bot/status")
async def get_bot_status():
    """Holt den Bot-Status"""
    return {
        "running": bot_state.is_running,
        "connected": bot_state.connected,
        "strategies_count": len(bot_state.strategies),
        "has_risk_manager": bot_state.risk_manager is not None
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket für Live-Updates"""
    await websocket.accept()
    bot_state.ws_connections.append(websocket)
    logger.info(f"WebSocket verbunden. Aktive Verbindungen: {len(bot_state.ws_connections)}")
    
    try:
        while True:
            # Sende periodische Updates
            if bot_state.connected and bot_state.broker:
                try:
                    account = bot_state.broker.get_account_info()
                    positions = bot_state.broker.get_positions()
                    
                    await websocket.send_json({
                        "type": "update",
                        "timestamp": datetime.now().isoformat(),
                        "data": {
                            "account": {
                                "portfolio_value": float(account.portfolio_value),
                                "unrealized_pnl": float(account.unrealized_pnl),
                                "realized_pnl": float(account.realized_pnl)
                            },
                            "positions_count": len(positions),
                            "bot_running": bot_state.is_running
                        }
                    })
                except:
                    pass
            
            await asyncio.sleep(5)  # Update alle 5 Sekunden
            
    except WebSocketDisconnect:
        bot_state.ws_connections.remove(websocket)
        logger.info(f"WebSocket getrennt. Aktive Verbindungen: {len(bot_state.ws_connections)}")


# ==========================================
# TRADE HISTORY & ANALYTICS ENDPOINTS
# ==========================================

@app.get("/trades/history")
async def get_trade_history(
    limit: int = 100,
    symbol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get trade history with optional filtering"""
    query = db.query(Trade).order_by(Trade.submitted_at.desc())
    
    if symbol:
        query = query.filter(Trade.symbol == symbol)
    
    trades = query.limit(limit).all()
    
    return {
        "trades": [
            {
                "id": t.id,
                "order_id": t.order_id,
                "symbol": t.symbol,
                "side": t.side,
                "quantity": t.quantity,
                "filled_qty": t.filled_qty,
                "avg_fill_price": t.avg_fill_price,
                "status": t.status,
                "submitted_at": t.submitted_at.isoformat() if t.submitted_at else None,
                "filled_at": t.filled_at.isoformat() if t.filled_at else None,
                "pnl": t.pnl,
                "pnl_percent": t.pnl_percent,
                "strategy_name": t.strategy.name if t.strategy else None
            }
            for t in trades
        ],
        "total": len(trades)
    }


@app.get("/trades/stats")
async def get_trade_stats(db: Session = Depends(get_db)):
    """Get overall trading statistics"""
    from sqlalchemy import func
    
    # Total trades
    total_trades = db.query(func.count(Trade.id)).filter(Trade.status == "filled").scalar()
    
    # Win/Loss
    winning_trades = db.query(func.count(Trade.id)).filter(
        Trade.status == "filled",
        Trade.pnl > 0
    ).scalar()
    
    losing_trades = db.query(func.count(Trade.id)).filter(
        Trade.status == "filled",
        Trade.pnl < 0
    ).scalar()
    
    # Total PnL
    total_pnl = db.query(func.sum(Trade.pnl)).filter(Trade.status == "filled").scalar() or 0
    
    # Win Rate
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Average Trade
    avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
    
    return {
        "total_trades": total_trades or 0,
        "winning_trades": winning_trades or 0,
        "losing_trades": losing_trades or 0,
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "avg_pnl_per_trade": round(avg_pnl, 2),
        "profit_factor": round(
            abs(db.query(func.sum(Trade.pnl)).filter(Trade.pnl > 0).scalar() or 0) / 
            abs(db.query(func.sum(Trade.pnl)).filter(Trade.pnl < 0).scalar() or 1),
            2
        )
    }


@app.get("/performance/metrics")
async def get_performance_metrics(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get performance metrics for last N days"""
    since = datetime.now(UTC) - timedelta(days=days)
    
    metrics = db.query(PerformanceMetric).filter(
        PerformanceMetric.date >= since
    ).order_by(PerformanceMetric.date.asc()).all()
    
    return {
        "metrics": [
            {
                "date": m.date.isoformat(),
                "portfolio_value": m.portfolio_value,
                "daily_pnl": m.daily_pnl,
                "daily_pnl_percent": m.daily_pnl_percent,
                "total_pnl": m.total_pnl,
                "trades_count": m.trades_count,
                "win_rate": m.win_rate,
                "max_drawdown": m.max_drawdown
            }
            for m in metrics
        ],
        "total_records": len(metrics)
    }


# ==========================================
# STOP-LOSS & TAKE-PROFIT ENDPOINTS
# ==========================================

@app.post("/stop-loss/set")
async def set_stop_loss(request: StopLossRequest):
    """Setzt Stop-Loss für eine Position"""
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker nicht verbunden")
    
    if not bot_state.stop_loss_manager:
        raise HTTPException(status_code=400, detail="Stop-Loss Manager nicht initialisiert")
    
    try:
        # Parse Stop Type
        stop_type_map = {
            "fixed": StopType.FIXED,
            "trailing": StopType.TRAILING,
            "percentage": StopType.PERCENTAGE
        }
        stop_type = stop_type_map.get(request.stop_type.lower(), StopType.FIXED)
        
        # Setze Stop-Loss
        bot_state.stop_loss_manager.set_stop_loss(
            symbol=request.symbol,
            stop_type=stop_type,
            stop_price=request.stop_price,
            stop_percentage=request.stop_percentage,
            trailing_percentage=request.trailing_percentage,
            entry_price=request.entry_price
        )
        
        return {
            "success": True,
            "message": f"Stop-Loss gesetzt für {request.symbol}",
            "config": {
                "symbol": request.symbol,
                "stop_type": request.stop_type,
                "stop_price": request.stop_price,
                "stop_percentage": request.stop_percentage,
                "trailing_percentage": request.trailing_percentage
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/take-profit/set")
async def set_take_profit(request: TakeProfitRequest):
    """Setzt Take-Profit für eine Position"""
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker nicht verbunden")
    
    if not bot_state.stop_loss_manager:
        raise HTTPException(status_code=400, detail="Stop-Loss Manager nicht initialisiert")
    
    try:
        bot_state.stop_loss_manager.set_take_profit(
            symbol=request.symbol,
            take_profit_price=request.take_profit_price,
            take_profit_percentage=request.take_profit_percentage
        )
        
        return {
            "success": True,
            "message": f"Take-Profit gesetzt für {request.symbol}",
            "config": {
                "symbol": request.symbol,
                "take_profit_price": request.take_profit_price,
                "take_profit_percentage": request.take_profit_percentage
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/stop-loss/{symbol}")
async def remove_stop_loss(symbol: str):
    """Entfernt Stop-Loss für eine Position"""
    if not bot_state.stop_loss_manager:
        raise HTTPException(status_code=400, detail="Stop-Loss Manager nicht initialisiert")
    
    try:
        bot_state.stop_loss_manager.remove_stop_loss(symbol)
        return {"success": True, "message": f"Stop-Loss entfernt für {symbol}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stop-loss/all")
async def get_all_stops():
    """Holt alle aktiven Stop-Loss/Take-Profit Configs"""
    if not bot_state.stop_loss_manager:
        return {"stops": []}
    
    try:
        stops = bot_state.stop_loss_manager.get_all_stops()
        
        return {
            "stops": [
                {
                    "symbol": config.symbol,
                    "stop_type": config.stop_type.value,
                    "stop_price": config.stop_price,
                    "stop_percentage": config.stop_percentage,
                    "trailing_percentage": config.trailing_percentage,
                    "take_profit_price": config.take_profit_price,
                    "take_profit_percentage": config.take_profit_percentage,
                    "entry_price": config.entry_price,
                    "highest_price": config.highest_price,
                    "lowest_price": config.lowest_price
                }
                for symbol, config in stops.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GROWTH STOCK SCANNER ENDPOINTS
# ============================================================================

@app.get("/scanner/scan")
async def scan_growth_stocks(
    min_score: float = 60.0,
    max_results: int = 20,
    symbols: Optional[str] = None  # Comma-separated list
):
    """
    Scannt nach Growth Stocks mit hohem Potenzial
    
    Parameters:
    - min_score: Minimaler Growth Score (0-100)
    - max_results: Maximale Anzahl Ergebnisse
    - symbols: Optional - spezifische Symbole (komma-getrennt)
    """
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker not connected")
    
    try:
        # Erstelle Scanner
        scanner = GrowthStockScanner(bot_state.broker)
        
        # Parse Symbole
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        # Führe Scan aus
        results = await scanner.scan_universe(
            symbols=symbol_list,
            min_score=min_score
        )
        
        # Limitiere Ergebnisse
        top_picks = scanner.get_top_picks(results, count=max_results)
        
        return {
            "scan_time": datetime.now(UTC).isoformat(),
            "total_scanned": len(symbol_list) if symbol_list else "universe",
            "matches_found": len(results),
            "results": [
                {
                    "symbol": stock.symbol,
                    "score": stock.score,
                    "revenue_growth": stock.revenue_growth,
                    "relative_strength": stock.relative_strength,
                    "momentum_score": stock.momentum_score,
                    "volume_increase": stock.volume_increase,
                    "price_change_30d": stock.price_change_30d,
                    "sector": stock.sector,
                    "market_cap": stock.market_cap,
                    "reason": stock.reason
                }
                for stock in top_picks
            ]
        }
    
    except Exception as e:
        logger.error(f"Scanner error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scanner/report")
async def get_scanner_report(
    min_score: float = 70.0,
    symbols: Optional[str] = None
):
    """
    Generiert einen formatierten Scan-Report
    """
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker not connected")
    
    try:
        scanner = GrowthStockScanner(bot_state.broker)
        
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        results = await scanner.scan_universe(
            symbols=symbol_list,
            min_score=min_score
        )
        
        report = scanner.format_report(results)
        
        return {
            "report": report,
            "results_count": len(results)
        }
    
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scanner/top-picks/{count}")
async def get_top_picks(count: int = 10, min_score: float = 65.0):
    """
    Holt die Top N Growth Stock Picks
    """
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker not connected")
    
    try:
        scanner = GrowthStockScanner(bot_state.broker)
        results = await scanner.scan_universe(min_score=min_score)
        top_picks = scanner.get_top_picks(results, count=count)
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "count": len(top_picks),
            "picks": [
                {
                    "rank": i + 1,
                    "symbol": stock.symbol,
                    "score": stock.score,
                    "price_change_30d": stock.price_change_30d,
                    "relative_strength": stock.relative_strength,
                    "sector": stock.sector,
                    "reason": stock.reason
                }
                for i, stock in enumerate(top_picks)
            ]
        }
    
    except Exception as e:
        logger.error(f"Top picks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# PORTFOLIO ENDPOINTS (70/30 Core-Satellite)
# ================================

@app.post("/portfolio/initialize")
async def initialize_portfolio():
    """
    Initialize Hybrid Portfolio Manager
    """
    if not bot_state.broker or not bot_state.connected:
        raise HTTPException(status_code=400, detail="Broker not connected")
    
    if not bot_state.risk_manager:
        raise HTTPException(status_code=400, detail="Risk Manager not initialized")
    
    try:
        # Create scanner for satellite positions
        scanner = GrowthStockScanner(bot_state.broker)
        
        # Initialize portfolio manager
        bot_state.portfolio_manager = HybridPortfolio(
            broker=bot_state.broker,
            scanner=scanner,
            risk_manager=bot_state.risk_manager
        )
        
        await bot_state.portfolio_manager.initialize()
        
        return {
            "status": "initialized",
            "timestamp": datetime.now(UTC).isoformat(),
            "message": "Hybrid Portfolio Manager initialized successfully"
        }
    
    except Exception as e:
        logger.error(f"Portfolio initialization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/summary")
async def get_portfolio_summary():
    """
    Get portfolio summary with core/satellite breakdown
    """
    if not bot_state.portfolio_manager:
        raise HTTPException(status_code=400, detail="Portfolio Manager not initialized")
    
    try:
        summary = await bot_state.portfolio_manager.get_portfolio_summary()
        return summary
    
    except Exception as e:
        logger.error(f"Portfolio summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/positions")
async def get_portfolio_positions(position_type: Optional[str] = None):
    """
    Get portfolio positions (all, core, or satellite)
    
    Args:
        position_type: 'core', 'satellite', or None for all
    """
    if not bot_state.portfolio_manager:
        raise HTTPException(status_code=400, detail="Portfolio Manager not initialized")
    
    try:
        if position_type == 'core':
            positions = await bot_state.portfolio_manager.get_core_positions()
        elif position_type == 'satellite':
            positions = await bot_state.portfolio_manager.get_satellite_positions()
        else:
            positions = await bot_state.portfolio_manager.get_all_positions()
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "position_type": position_type or "all",
            "count": len(positions),
            "positions": [
                {
                    "symbol": p.symbol,
                    "type": p.portfolio_type.value,
                    "target_weight": p.target_weight,
                    "current_weight": p.current_weight,
                    "current_value": p.current_value,
                    "shares": p.shares,
                    "average_entry": p.average_entry,
                    "unrealized_pnl": p.unrealized_pnl,
                    "unrealized_pnl_percent": p.unrealized_pnl_percent,
                    "last_rebalance": p.last_rebalance.isoformat()
                }
                for p in positions
            ]
        }
    
    except Exception as e:
        logger.error(f"Portfolio positions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/rebalance/check")
async def check_rebalancing():
    """
    Check if portfolio needs rebalancing
    """
    if not bot_state.portfolio_manager:
        raise HTTPException(status_code=400, detail="Portfolio Manager not initialized")
    
    try:
        needs_rebalancing = await bot_state.portfolio_manager.check_rebalancing_needed()
        actions = []
        
        if needs_rebalancing:
            actions = await bot_state.portfolio_manager.get_rebalancing_actions()
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "needs_rebalancing": needs_rebalancing,
            "actions_count": len(actions),
            "actions": [
                {
                    "symbol": a.symbol,
                    "action": a.action,
                    "shares": a.shares,
                    "reason": a.reason,
                    "urgency": a.urgency
                }
                for a in actions
            ]
        }
    
    except Exception as e:
        logger.error(f"Rebalancing check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/rebalance/execute")
async def execute_rebalancing():
    """
    Execute portfolio rebalancing
    """
    if not bot_state.portfolio_manager:
        raise HTTPException(status_code=400, detail="Portfolio Manager not initialized")
    
    try:
        # Get actions
        actions = await bot_state.portfolio_manager.get_rebalancing_actions()
        
        if not actions:
            return {
                "status": "no_action_needed",
                "message": "Portfolio is balanced, no actions required"
            }
        
        # Execute rebalancing
        results = await bot_state.portfolio_manager.execute_rebalancing(actions)
        
        return {
            "status": "completed",
            "timestamp": datetime.now(UTC).isoformat(),
            "total_actions": results['total_actions'],
            "success_count": len(results['success']),
            "failed_count": len(results['failed']),
            "success": results['success'],
            "failed": results['failed']
        }
    
    except Exception as e:
        logger.error(f"Rebalancing execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/portfolio/satellite/update")
async def update_satellite_positions():
    """
    Update satellite positions with fresh Growth Scanner picks
    """
    if not bot_state.portfolio_manager:
        raise HTTPException(status_code=400, detail="Portfolio Manager not initialized")
    
    try:
        actions = await bot_state.portfolio_manager.update_satellite_positions()
        
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "added": actions['added'],
            "kept": actions['kept'],
            "removed": actions['removed'],
            "summary": {
                "added_count": len(actions['added']),
                "kept_count": len(actions['kept']),
                "removed_count": len(actions['removed'])
            }
        }
    
    except Exception as e:
        logger.error(f"Satellite update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Old startup event removed - now using lifespan
# @app.on_event("startup") was deprecated

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
