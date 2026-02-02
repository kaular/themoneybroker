# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-02

### Added

#### News & Sentiment System
- **News Feed Module** (`src/news/`)
  - `news_feed.py`: Real-time news fetching from multiple sources (Alpaca, NewsAPI)
  - `sentiment_analyzer.py`: AI-powered sentiment analysis using transformers
  - `news_monitor.py`: Background monitoring service with alerts
  - Sentiment-based trading signals: Buy/Sell/Hold recommendations
- **News API Endpoints**
  - `GET /news/feed`: Fetch news for specific symbols or market-wide
  - `GET /news/sentiment/{symbol}`: Get sentiment analysis for a symbol
  - `GET /news/alerts`: Active news-based alerts
- **News Feed Frontend** (`frontend/src/pages/NewsFeed.jsx`)
  - Real-time news display with sentiment indicators
  - Color-coded sentiment badges (positive/negative/neutral)
  - Filter by symbol and time range
  - Direct links to news sources

#### Symbol Search & Discovery
- **Symbol Search Page** (`frontend/src/pages/SymbolSearch.jsx`)
  - Real-time symbol search across markets
  - Asset type filtering (stocks, crypto, forex)
  - Exchange information display
  - One-click symbol addition to watchlists

#### Enhanced Growth Scanner
- **Improved Performance Tracking**
  - Multi-timeframe analysis (daily, weekly, monthly)
  - Better error handling and data validation
  - Enhanced metrics calculation
  - API endpoints for scanner results

#### Testing & CI/CD
- **Comprehensive Test Suite**
  - Unit tests for news system, alerts, scanner
  - Integration tests for trading workflows
  - Test coverage reporting (coverage.xml)
  - Pytest configuration with parallel execution
- **GitHub Actions CI/CD** (`.github/workflows/`)
  - Automated testing on push/PR
  - Docker image building and publishing
  - Multi-platform support
- **Test Scripts**
  - `run_tests.ps1`: PowerShell test runner
  - `run_tests.sh`: Bash test runner
  - Test documentation in `tests/README.md`

#### Docker & Deployment
- **Docker Compose Setup**
  - Multi-service orchestration (backend, frontend, database)
  - Environment-based configuration
  - Volume management for data persistence
- **Frontend Dockerfile** with nginx
  - Production-optimized React build
  - Reverse proxy configuration
  - Static asset serving

#### Documentation
- `NEWS_SYSTEM.md`: News system architecture and usage
- `IMPLEMENTATION_COMPLETE.md`: Feature implementation status
- `docs/CI-CD.md`: CI/CD pipeline documentation

### Changed
- Updated alert manager with news-based alerts
- Enhanced backtesting module initialization
- Improved trade tracker with better error handling
- Updated API with new endpoints for news and search
- Refactored frontend layout and navigation

### Fixed
- Test configuration and fixture issues
- Database session management in tests
- Frontend API service error handling

## [1.0.0] - 2026-02-01

### Added

#### Database Integration
- **SQLAlchemy ORM Models** für vollständige Trade Persistence
  - `Trade` Model: Order History, P&L Tracking, Commission Tracking
  - `Strategy` Model: Strategy Configuration und Performance Metrics
  - `PerformanceMetric` Model: Daily/Weekly/Monthly Performance Tracking
  - `Position` Model: Current Open Positions mit Stop-Loss/Take-Profit
- **Database Module** (`src/database/`)
  - `db.py`: Database connection und session management
  - `trade_tracker.py`: Helper functions für automatisches Trade Tracking
  - SQLite Database: `data/trading.db` (development)
- **API Endpoints** für Trade History
  - `GET /trades/history`: Retrieve trade history mit filtering
  - `GET /trades/stats`: Win rate, profit factor, total P&L statistics
  - `GET /performance/metrics`: Time-series performance data

#### Stop-Loss & Take-Profit System
- **Stop-Loss Manager** (`src/risk/stop_loss_manager.py`)
  - Fixed Stop-Loss: Absolute price levels
  - Percentage Stop-Loss: Percentage from entry price
  - Trailing Stop-Loss: Dynamic stops that follow price movement
  - Take-Profit Targets: Fixed and percentage-based
  - Background Monitoring: Async task checks positions every 1 second
  - Automatic Order Execution: Places market orders when triggered
- **API Endpoints** für Stop-Loss Management
  - `POST /stop-loss/set`: Configure stop-loss for positions
  - `POST /take-profit/set`: Configure take-profit targets
  - `DELETE /stop-loss/{symbol}`: Remove stop-loss configuration
  - `GET /stop-loss/all`: Get all active stop configurations

#### Frontend Components
- **Trade History Page** (`frontend/src/pages/TradeHistory.jsx`)
  - Trade table mit sortierung und filtering
  - Statistics cards: Win Rate, Total P&L, Profit Factor
  - Export-ready data display
- **Stop-Loss Modal** (`frontend/src/components/StopLossModal.jsx`)
  - Interactive UI für Stop-Loss configuration
  - Support für alle 3 Stop types (Fixed, Percentage, Trailing)
  - Risk/Reward ratio calculator
  - Real-time price calculations
- **Enhanced Dashboard** (`frontend/src/pages/Dashboard.jsx`)
  - Stop-Loss/Take-Profit buttons auf Position cards
  - Integration mit StopLossModal

#### Test Suite
- **77 Tests** mit 100% Success Rate
  - Database Tests (17): Models, CRUD, Relationships, Aggregations
  - Stop-Loss Manager Tests (23): All stop types, trigger conditions, execution
  - Risk Manager Tests (17): Position sizing, risk limits, daily loss tracking
  - API Tests (15): Endpoints, error handling, validation
  - Trading Logic Tests (5): Strategy execution, order placement
- **Test Infrastructure** (`tests/`)
  - `conftest.py`: Shared fixtures, MockBroker, test database
  - In-memory SQLite für test isolation
  - Async test support für background tasks

### Changed

#### API Improvements
- **FastAPI Lifespan Events**: Migrated from deprecated `@app.on_event()` to modern lifespan context manager
- **Timezone-aware Datetimes**: All `datetime.utcnow()` replaced with `datetime.now(UTC)`
- **Error Messages**: German language support für better UX

#### Code Quality
- **SQLAlchemy 2.0 Compatibility**: Updated imports from `declarative_base`
- **Type Hints**: Improved type annotations across codebase
- **Deprecation Warnings**: Fixed all Python 3.12 deprecation warnings (84 → 0)

#### Risk Management
- **Position Size Calculation**: Enhanced with max position size limits
- **Daily Loss Tracking**: Improved tracking mit unrealized + realized P&L
- **Trading Halt**: Automatic trading suspension when risk limits exceeded

### Fixed

#### Bug Fixes
- **Order Attribute**: Fixed `order.id` vs `order_id` inconsistency in Stop-Loss Manager
- **Database Unique Constraints**: Fixed UNIQUE constraint violations mit timestamp-based IDs
- **MockBroker**: Implemented all abstract methods from BaseBroker
  - `get_market_price()`, `get_position()`, `get_order()`, `get_open_orders()`, `get_historical_data()`

#### Test Fixes
- **Risk Manager Tests**: Updated to use current API (AccountInfo objects)
- **Database Tests**: Fixed unique constraint issues with time-based order IDs
- **API Tests**: Added proper database isolation und localization support

### Technical Details

#### Dependencies Added
- `sqlalchemy==2.0.46` - ORM for database operations
- `greenlet==3.3.1` - Required for SQLAlchemy async support
- `pytest==9.0.2` - Testing framework
- `pytest-asyncio==1.3.0` - Async test support
- `httpx==0.26.0` - TestClient for FastAPI

#### Database Schema
```sql
-- Trades Table
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    order_id TEXT UNIQUE,
    symbol TEXT,
    side TEXT,
    order_type TEXT,
    quantity FLOAT,
    filled_qty FLOAT,
    avg_fill_price FLOAT,
    status TEXT,
    submitted_at DATETIME,
    filled_at DATETIME,
    pnl FLOAT,
    pnl_percent FLOAT,
    -- ... more fields
);

-- Strategies, PerformanceMetrics, Positions tables also created
```

#### Architecture
- **Database Layer**: SQLAlchemy ORM with SQLite (dev) / PostgreSQL (production ready)
- **API Layer**: FastAPI with async support, CORS enabled
- **Frontend**: React 18.2 with Vite, Tailwind CSS
- **Real-time**: WebSocket connections for live updates
- **Testing**: pytest with fixtures, mocks, and async support

### Performance
- **Test Suite**: Runs in ~1.0 seconds (77 tests)
- **Background Monitoring**: Stop-Loss checks every 1 second (configurable)
- **Database Queries**: Optimized with SQLAlchemy lazy loading

### Documentation
- **TEST_FINAL.md**: Complete test coverage report
- **TEST_RESULTS.md**: Test execution results and analysis
- **FEATURES.md**: Feature roadmap and implementation status
- **BROKER_APIS.md**: Broker integration documentation

### Statistics
- **Lines of Code**: 
  - Backend: ~3500 lines
  - Frontend: ~1200 lines
  - Tests: ~1800 lines
- **Test Coverage**: 77/77 tests passing (100%)
- **Warnings Fixed**: 84 deprecation warnings resolved
- **Features Implemented**: 15 major features from roadmap

### Migration Notes
- Database will be automatically initialized on first startup
- Existing configuration in `.env` remains compatible
- No breaking changes to existing API endpoints
- Frontend requires `npm install` for new dependencies

---

## [0.1.0] - Initial Release

### Initial Features
- Alpaca broker integration
- Basic SMA trading strategy
- Risk management system
- Simple execution engine
- Basic logging

---

**Legend:**
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` for vulnerability fixes
