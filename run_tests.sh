#!/bin/bash

# Test Runner Script for TheMoneyBroker
# Runs all tests with coverage and generates reports

set -e  # Exit on error

echo "🧪 Starting Test Suite..."
echo "========================="

# Set Python path
export PYTHONPATH=$(pwd)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test Backend
echo -e "\n${YELLOW}📦 Testing Backend...${NC}"
pytest tests/ -v \
    --cov=src \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml \
    --maxfail=3 \
    --tb=short

# Check test exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend tests passed!${NC}"
else
    echo -e "${RED}❌ Backend tests failed!${NC}"
    exit 1
fi

# Show coverage summary
echo -e "\n${YELLOW}📊 Coverage Summary:${NC}"
coverage report --skip-empty

# Check coverage threshold
coverage report --fail-under=60 --skip-empty
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Coverage threshold met (>60%)${NC}"
else
    echo -e "${RED}⚠️  Coverage below 60%${NC}"
fi

# Run linting
echo -e "\n${YELLOW}🔍 Running Linting...${NC}"
flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

echo -e "\n${GREEN}✅ All checks passed!${NC}"
echo -e "\n📝 Coverage report available at: htmlcov/index.html"
