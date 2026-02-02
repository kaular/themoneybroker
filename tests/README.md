# Test Suite - TheMoneyBroker

Comprehensive test suite for the automated trading bot with **114 tests** and **53% code coverage**.

## 📊 Test Overview

| Test Module | Tests | Coverage | Description |
|------------|-------|----------|-------------|
| test_alerts.py | 7 | 51% | Alert/Notification system tests |
| test_api.py | 12 | - | REST API endpoint tests |
| test_api_simple.py | 3 | - | Basic API health checks |
| test_database.py | 17 | 78-96% | Database models & ORM tests |
| test_news.py | 15 | 44-89% | News feed & sentiment analysis tests |
| test_risk_manager.py | 17 | 87% | Risk management & position sizing tests |
| test_scanner.py | 12 | 49% | Growth stock scanner tests |
| test_stop_loss_manager.py | 23 | 72% | Stop-loss & take-profit tests |
| test_trading.py | 8 | 76-79% | Strategy & trading logic tests |

## 🚀 Running Tests

### Run All Tests
```bash
# PowerShell
.\run_tests.ps1

# Bash
./run_tests.sh

# Direct pytest
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

Coverage report is generated in `htmlcov/index.html`.

### Run Specific Tests
```bash
# Single test file
pytest tests/test_news.py -v

# Single test function
pytest tests/test_news.py::TestSentimentAnalyzer::test_bullish_sentiment -v

# Tests by marker
pytest -m asyncio  # All async tests
pytest -m unit     # Unit tests only
pytest -m integration  # Integration tests only
```

### Run Fast Tests Only
```bash
pytest -m "not slow"
```

## 📦 Test Categories

### Unit Tests
- **Alert Manager** - Multi-channel notification system
- **Sentiment Analyzer** - NLP-based news sentiment scoring
- **Risk Manager** - Position sizing & risk limits
- **Stop Loss Manager** - Automated stop-loss/take-profit
- **Growth Scanner** - Stock screening algorithm

### Integration Tests
- **API Endpoints** - FastAPI REST API testing
- **Database Operations** - SQLAlchemy ORM workflows
- **Trading Workflows** - End-to-end trade execution

### Mock Objects
All tests use `MockBroker` from `conftest.py` for isolated testing without real API calls.

## 🧪 Test Configuration

Configuration is in `pytest.ini`:
- **Test Discovery**: `tests/` directory
- **Coverage Source**: `src/` directory
- **Markers**: asyncio, slow, integration, unit
- **Asyncio Mode**: auto
- **Warnings**: Disabled for cleaner output

## 📈 Coverage Goals

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| sentiment_analyzer.py | 89% | 90%+ | ✅ High |
| risk_manager.py | 87% | 90%+ | ✅ High |
| base_broker.py | 87% | 90%+ | ✅ High |
| database/models.py | 96% | 95%+ | ✅ Excellent |
| stop_loss_manager.py | 72% | 80%+ | 🟡 Medium |
| news_monitor.py | 57% | 70%+ | 🟠 Medium |
| alerts/alert_manager.py | 51% | 70%+ | 🟠 Medium |
| growth_scanner.py | 49% | 60%+ | 🔴 Low |
| news_feed.py | 44% | 60%+ | 🔴 Low |
| backtester.py | 30% | 50%+ | 🔴 Low |

## 🔍 Key Test Cases

### News Feed System
- ✅ Bullish/bearish sentiment detection
- ✅ Negation handling ("not good" → negative)
- ✅ Intensifier boost ("very", "extremely")
- ✅ Headline confidence boost
- ✅ Batch analysis performance
- ✅ News score calculation
- ✅ Monitor start/stop functionality

### Alert System
- ✅ Multi-channel formatting (Email, Discord, Telegram)
- ✅ Priority levels & color coding
- ✅ Alert history tracking
- ✅ Convenience methods (trade_executed, moonshot_found)

### Risk Management
- ✅ Position size calculation
- ✅ Max position limits enforcement
- ✅ Daily loss limits & trading halt
- ✅ Buying power validation
- ✅ Risk/reward ratios

### Stop Loss Manager
- ✅ Fixed stop-loss triggers
- ✅ Percentage-based stops
- ✅ Trailing stop-loss updates
- ✅ Take-profit execution
- ✅ Multi-position monitoring

## 🐛 Known Issues

None! All 114 tests passing ✅

## 📝 Adding New Tests

1. Create test file in `tests/` directory
2. Use `@pytest.mark.asyncio` for async tests
3. Use `MockBroker` from `conftest.py` for broker interactions
4. Add custom markers in `pytest.ini` if needed
5. Run `pytest tests/ -v` to verify

Example:
```python
import pytest
from tests.conftest import MockBroker

@pytest.mark.asyncio
async def test_my_feature():
    broker = MockBroker()
    # Your test code here
    assert True
```

## 🔧 Debugging Tests

### Verbose Output
```bash
pytest tests/ -vv --tb=long
```

### Stop on First Failure
```bash
pytest tests/ -x
```

### Show Print Statements
```bash
pytest tests/ -s
```

### Run Last Failed Tests
```bash
pytest --lf
```

## 📊 CI/CD Integration

Tests run automatically on GitHub Actions:
- ✅ Python 3.10, 3.11, 3.12 matrix testing
- ✅ Code coverage reporting to Codecov
- ✅ Linting with flake8
- ✅ Security scanning with Bandit & Safety

See `.github/workflows/ci-cd.yml` for details.

## 🎯 Quality Metrics

- **Test Count**: 114
- **Pass Rate**: 100%
- **Code Coverage**: 53%
- **Execution Time**: ~3 seconds
- **Mock Coverage**: 100% (no real API calls)
- **Warnings**: 48 (deprecations, non-critical)

## 📚 Dependencies

Required packages (from `requirements.txt`):
- pytest==9.0.2
- pytest-asyncio==1.3.0
- pytest-cov==7.0.0
- coverage==7.13.2

## 🤝 Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure >60% coverage for new modules
3. Run full test suite before committing
4. Update this README with new test categories

---

**Last Updated**: 2026-02-01
**Total Tests**: 114
**Coverage**: 53%
**Status**: ✅ All Passing
