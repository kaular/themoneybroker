import axios from 'axios';

const API_BASE_URL = '/api';

class ApiClient {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Generic HTTP methods
  async get(url, config = {}) {
    return this.client.get(url, config);
  }

  async post(url, data, config = {}) {
    return this.client.post(url, data, config);
  }

  async put(url, data, config = {}) {
    return this.client.put(url, data, config);
  }

  async delete(url, config = {}) {
    return this.client.delete(url, config);
  }

  // Broker APIs
  async connectBroker(config) {
    return this.client.post('/broker/connect', config);
  }

  async disconnectBroker() {
    return this.client.post('/broker/disconnect');
  }

  // Account APIs
  async getAccount() {
    return this.client.get('/account');
  }

  async getPositions() {
    return this.client.get('/positions');
  }

  async getOrders() {
    return this.client.get('/orders');
  }

  async placeOrder(orderData) {
    return this.client.post('/orders', orderData);
  }

  async cancelOrder(orderId) {
    return this.client.delete(`/orders/${orderId}`);
  }

  // Risk Management
  async configureRisk(riskConfig) {
    return this.client.post('/risk/configure', riskConfig);
  }

  // Strategies
  async getStrategies() {
    return this.client.get('/strategies');
  }

  async addStrategy(strategyConfig) {
    return this.client.post('/strategies', strategyConfig);
  }

  // Trade History & Analytics
  async getTradeHistory(limit = 100, symbol = null) {
    const params = { limit };
    if (symbol) params.symbol = symbol;
    return this.client.get('/trades/history', { params });
  }

  async getTradeStats() {
    return this.client.get('/trades/stats');
  }

  async getPerformanceMetrics(days = 30) {
    return this.client.get('/performance/metrics', { params: { days } });
  }

  // Stop-Loss & Take-Profit
  async setStopLoss(config) {
    return this.client.post('/stop-loss/set', config);
  }

  async setTakeProfit(config) {
    return this.client.post('/take-profit/set', config);
  }

  async removeStopLoss(symbol) {
    return this.client.delete(`/stop-loss/${symbol}`);
  }

  async getAllStops() {
    return this.client.get('/stop-loss/all');
  }

  // Bot Control
  async startBot() {
    return this.client.post('/bot/start');
  }

  async stopBot() {
    return this.client.post('/bot/stop');
  }

  async getBotStatus() {
    return this.client.get('/bot/status');
  }

  // Health Check
  async healthCheck() {
    return this.client.get('/');
  }
}

export default new ApiClient();
