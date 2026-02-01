import { useState } from 'react';
import { TrendingUp, Play, Clock, Target, Award, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../services/api';

const Backtesting = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [config, setConfig] = useState({
    strategy_type: 'sma',
    start_date: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    initial_capital: 10000,
    symbols: ['SPY', 'QQQ', 'AAPL'],
    parameters: { short_window: 20, long_window: 50 },
    commission: 0,
    slippage: 0.001,
    max_positions: 5,
    position_size_pct: 0.2
  });
  const [showTrades, setShowTrades] = useState(false);
  
  const runBacktest = async () => {
    setLoading(true);
    setResult(null);
    
    try {
      const response = await api.post('/backtest/run', {
        ...config,
        symbols: config.symbols.split(',').map(s => s.trim())
      });
      setResult(response.data);
    } catch (error) {
      alert('Backtest failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const loadPreset = (preset) => {
    setConfig({
      ...preset,
      symbols: preset.symbols.join(', '),
      start_date: new Date(preset.start_date).toISOString().split('T')[0],
      end_date: new Date(preset.end_date).toISOString().split('T')[0]
    });
  };
  
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };
  
  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };
  
  const getMetricColor = (value, threshold) => {
    if (value >= threshold) return 'text-green-400';
    if (value >= threshold * 0.5) return 'text-yellow-400';
    return 'text-red-400';
  };
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold glow-text mb-2">Backtesting Lab</h2>
          <p className="text-gray-400">Test strategies with historical data before risking real capital</p>
        </div>
      </div>
      
      {/* Configuration Panel */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Target className="w-5 h-5 text-primary-400" />
          Backtest Configuration
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Strategy Type */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Strategy</label>
            <select 
              value={config.strategy_type}
              onChange={(e) => setConfig({...config, strategy_type: e.target.value})}
              className="input w-full"
            >
              <option value="sma">SMA Crossover</option>
              <option value="growth_scanner">Growth Scanner</option>
            </select>
          </div>
          
          {/* Start Date */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Start Date</label>
            <input 
              type="date"
              value={config.start_date}
              onChange={(e) => setConfig({...config, start_date: e.target.value})}
              className="input w-full"
            />
          </div>
          
          {/* End Date */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">End Date</label>
            <input 
              type="date"
              value={config.end_date}
              onChange={(e) => setConfig({...config, end_date: e.target.value})}
              className="input w-full"
            />
          </div>
          
          {/* Initial Capital */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Initial Capital ($)</label>
            <input 
              type="number"
              value={config.initial_capital}
              onChange={(e) => setConfig({...config, initial_capital: parseFloat(e.target.value)})}
              className="input w-full"
            />
          </div>
          
          {/* Symbols */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-400 mb-2">Symbols (comma-separated)</label>
            <input 
              type="text"
              value={config.symbols}
              onChange={(e) => setConfig({...config, symbols: e.target.value})}
              placeholder="SPY, QQQ, AAPL"
              className="input w-full"
            />
          </div>
          
          {/* Max Positions */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Max Positions</label>
            <input 
              type="number"
              value={config.max_positions}
              onChange={(e) => setConfig({...config, max_positions: parseInt(e.target.value)})}
              className="input w-full"
            />
          </div>
          
          {/* Position Size */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Position Size (%)</label>
            <input 
              type="number"
              step="0.01"
              value={config.position_size_pct * 100}
              onChange={(e) => setConfig({...config, position_size_pct: parseFloat(e.target.value) / 100})}
              className="input w-full"
            />
          </div>
          
          {/* Commission */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Commission ($)</label>
            <input 
              type="number"
              step="0.01"
              value={config.commission}
              onChange={(e) => setConfig({...config, commission: parseFloat(e.target.value)})}
              className="input w-full"
            />
          </div>
        </div>
        
        <div className="flex gap-3 mt-6">
          <button 
            onClick={runBacktest}
            disabled={loading}
            className="btn btn-primary flex items-center gap-2"
          >
            {loading ? (
              <>
                <Clock className="w-4 h-4 animate-spin" />
                Running Backtest...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Backtest
              </>
            )}
          </button>
        </div>
      </div>
      
      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Metrics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Total Return */}
            <div className="glass-card p-4 bg-gradient-to-br from-green-900/20 to-green-600/5 border-green-500/30">
              <div className="text-sm text-gray-400 mb-1">Total Return</div>
              <div className={`text-2xl font-bold ${getMetricColor(result.metrics.total_return_percent, 10)}`}>
                {formatPercent(result.metrics.total_return_percent)}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {formatCurrency(result.metrics.initial_capital)} → {formatCurrency(result.metrics.final_value)}
              </div>
            </div>
            
            {/* Sharpe Ratio */}
            <div className="glass-card p-4">
              <div className="text-sm text-gray-400 mb-1">Sharpe Ratio</div>
              <div className={`text-2xl font-bold ${getMetricColor(result.metrics.sharpe_ratio, 1)}`}>
                {result.metrics.sharpe_ratio.toFixed(2)}
              </div>
              <div className="text-xs text-gray-400 mt-1">Risk-adjusted return</div>
            </div>
            
            {/* Max Drawdown */}
            <div className="glass-card p-4 bg-gradient-to-br from-red-900/20 to-red-600/5 border-red-500/30">
              <div className="text-sm text-gray-400 mb-1">Max Drawdown</div>
              <div className="text-2xl font-bold text-red-400">
                -{result.metrics.max_drawdown_percent.toFixed(2)}%
              </div>
              <div className="text-xs text-gray-400 mt-1">Largest decline</div>
            </div>
            
            {/* Win Rate */}
            <div className="glass-card p-4">
              <div className="text-sm text-gray-400 mb-1">Win Rate</div>
              <div className={`text-2xl font-bold ${getMetricColor(result.metrics.win_rate_percent, 50)}`}>
                {result.metrics.win_rate_percent.toFixed(1)}%
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {result.metrics.wins}W / {result.metrics.losses}L
              </div>
            </div>
            
            {/* Profit Factor */}
            <div className="glass-card p-4">
              <div className="text-sm text-gray-400 mb-1">Profit Factor</div>
              <div className={`text-2xl font-bold ${getMetricColor(result.metrics.profit_factor, 1.5)}`}>
                {result.metrics.profit_factor === Infinity ? '∞' : result.metrics.profit_factor.toFixed(2)}
              </div>
              <div className="text-xs text-gray-400 mt-1">Gross profit / loss</div>
            </div>
            
            {/* Total Trades */}
            <div className="glass-card p-4">
              <div className="text-sm text-gray-400 mb-1">Total Trades</div>
              <div className="text-2xl font-bold text-blue-400">{result.metrics.total_trades}</div>
              <div className="text-xs text-gray-400 mt-1">
                Avg hold: {result.metrics.avg_holding_days.toFixed(1)} days
              </div>
            </div>
            
            {/* Annual Return */}
            <div className="glass-card p-4">
              <div className="text-sm text-gray-400 mb-1">Annual Return</div>
              <div className={`text-2xl font-bold ${getMetricColor(result.metrics.annual_return_percent, 15)}`}>
                {formatPercent(result.metrics.annual_return_percent)}
              </div>
              <div className="text-xs text-gray-400 mt-1">Annualized</div>
            </div>
            
            {/* Expectancy */}
            <div className="glass-card p-4">
              <div className="text-sm text-gray-400 mb-1">Expectancy</div>
              <div className={`text-2xl font-bold ${result.metrics.expectancy >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatCurrency(result.metrics.expectancy)}
              </div>
              <div className="text-xs text-gray-400 mt-1">Per trade</div>
            </div>
          </div>
          
          {/* Equity Curve Chart */}
          <div className="glass-card p-6">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary-400" />
              Equity Curve
            </h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={result.equity_curve}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#9CA3AF"
                    tick={{fontSize: 12}}
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis 
                    stroke="#9CA3AF"
                    tick={{fontSize: 12}}
                    tickFormatter={(value) => `$${(value/1000).toFixed(1)}k`}
                  />
                  <Tooltip 
                    contentStyle={{backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px'}}
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value) => [formatCurrency(value), 'Portfolio Value']}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#10B981" 
                    strokeWidth={2}
                    dot={false}
                    name="Portfolio Value"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          {/* Trades List */}
          {result.trades && result.trades.length > 0 && (
            <div className="glass-card">
              <button 
                onClick={() => setShowTrades(!showTrades)}
                className="w-full p-4 flex justify-between items-center hover:bg-gray-800/50 transition-colors"
              >
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <Award className="w-5 h-5 text-primary-400" />
                  Trade History ({result.trades.length} shown)
                </h3>
                {showTrades ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>
              
              {showTrades && (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="border-t border-b border-gray-700">
                      <tr>
                        <th className="text-left p-3 font-semibold text-gray-400">Symbol</th>
                        <th className="text-left p-3 font-semibold text-gray-400">Entry</th>
                        <th className="text-left p-3 font-semibold text-gray-400">Exit</th>
                        <th className="text-right p-3 font-semibold text-gray-400">Shares</th>
                        <th className="text-right p-3 font-semibold text-gray-400">Entry Price</th>
                        <th className="text-right p-3 font-semibold text-gray-400">Exit Price</th>
                        <th className="text-right p-3 font-semibold text-gray-400">P/L</th>
                        <th className="text-right p-3 font-semibold text-gray-400">Days</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.trades.map((trade, idx) => (
                        <tr key={idx} className="border-b border-gray-700/50 hover:bg-gray-800/50">
                          <td className="p-3 font-bold">{trade.symbol}</td>
                          <td className="p-3 text-sm text-gray-400">
                            {new Date(trade.entry_date).toLocaleDateString()}
                          </td>
                          <td className="p-3 text-sm text-gray-400">
                            {new Date(trade.exit_date).toLocaleDateString()}
                          </td>
                          <td className="p-3 text-right">{trade.shares}</td>
                          <td className="p-3 text-right">{formatCurrency(trade.entry_price)}</td>
                          <td className="p-3 text-right">{formatCurrency(trade.exit_price)}</td>
                          <td className="p-3 text-right">
                            <div className={trade.win ? 'text-green-400' : 'text-red-400'}>
                              <div className="font-medium">{formatCurrency(trade.pnl)}</div>
                              <div className="text-xs">{formatPercent(trade.pnl_percent)}</div>
                            </div>
                          </td>
                          <td className="p-3 text-right text-gray-400">{trade.holding_days}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      
      {/* Info Box */}
      <div className="glass-card p-4 bg-blue-900/10 border-blue-500/30">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5" />
          <div>
            <h4 className="font-bold text-blue-400 mb-1">About Backtesting</h4>
            <p className="text-sm text-gray-300">
              Backtesting simulates your strategy on historical data to estimate performance. 
              Past results don't guarantee future performance. Consider slippage, commissions, 
              and market conditions. Use walk-forward analysis to avoid overfitting.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Backtesting;
