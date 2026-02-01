import { useState, useEffect } from 'react';
import { TrendingUp, PieChart, RefreshCw, Target, Rocket, Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import api from '../services/api';

const HybridPortfolio = () => {
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const [summary, setSummary] = useState(null);
  const [positions, setPositions] = useState([]);
  const [rebalanceCheck, setRebalanceCheck] = useState(null);
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'core', 'satellite'
  
  useEffect(() => {
    checkInitialization();
  }, []);
  
  const checkInitialization = async () => {
    try {
      const response = await api.get('/portfolio/summary');
      setInitialized(true);
      setSummary(response.data);
      loadPositions('all');
    } catch (error) {
      setInitialized(false);
    }
  };
  
  const initializePortfolio = async () => {
    setLoading(true);
    try {
      await api.post('/portfolio/initialize');
      setInitialized(true);
      await loadSummary();
      await loadPositions('all');
    } catch (error) {
      alert('Portfolio initialization failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const loadSummary = async () => {
    try {
      const response = await api.get('/portfolio/summary');
      setSummary(response.data);
    } catch (error) {
      console.error('Failed to load summary:', error);
    }
  };
  
  const loadPositions = async (type) => {
    setLoading(true);
    try {
      const params = type !== 'all' ? `?position_type=${type}` : '';
      const response = await api.get(`/portfolio/positions${params}`);
      setPositions(response.data.positions);
      setActiveTab(type);
    } catch (error) {
      console.error('Failed to load positions:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const checkRebalancing = async () => {
    setLoading(true);
    try {
      const response = await api.get('/portfolio/rebalance/check');
      setRebalanceCheck(response.data);
    } catch (error) {
      alert('Rebalance check failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const executeRebalancing = async () => {
    if (!confirm('Execute portfolio rebalancing? This will submit market orders.')) return;
    
    setLoading(true);
    try {
      const response = await api.post('/portfolio/rebalance/execute');
      alert(`Rebalancing complete!\n${response.data.success_count} successful, ${response.data.failed_count} failed`);
      await loadSummary();
      await loadPositions(activeTab);
      setRebalanceCheck(null);
    } catch (error) {
      alert('Rebalancing failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const updateSatellite = async () => {
    setLoading(true);
    try {
      const response = await api.post('/portfolio/satellite/update');
      alert(`Satellite updated!\n+${response.data.summary.added_count} added\n-${response.data.summary.removed_count} removed\n=${response.data.summary.kept_count} kept`);
      await loadSummary();
      await loadPositions(activeTab);
    } catch (error) {
      alert('Satellite update failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };
  
  const formatPercent = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };
  
  if (!initialized) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold glow-text mb-2">Hybrid Portfolio</h2>
            <p className="text-gray-400">70/30 Core-Satellite Strategy</p>
          </div>
        </div>
        
        <div className="glass-card p-8 text-center">
          <PieChart className="w-16 h-16 text-primary-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold mb-2">Portfolio Not Initialized</h3>
          <p className="text-gray-400 mb-6">Initialize the Hybrid Portfolio Manager to start tracking your 70/30 Core-Satellite strategy.</p>
          <button 
            onClick={initializePortfolio}
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Initializing...' : 'Initialize Portfolio'}
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold glow-text mb-2">Hybrid Portfolio</h2>
          <p className="text-gray-400">70% Core (Stable) / 30% Satellite (Moonshots)</p>
        </div>
        
        <div className="flex gap-3">
          <button 
            onClick={() => { loadSummary(); loadPositions(activeTab); }}
            disabled={loading}
            className="btn btn-secondary"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button 
            onClick={updateSatellite}
            disabled={loading}
            className="btn btn-primary"
          >
            <Rocket className="w-4 h-4" />
            Update Satellite
          </button>
          <button 
            onClick={checkRebalancing}
            disabled={loading}
            className="btn btn-success"
          >
            <Target className="w-4 h-4" />
            Check Rebalance
          </button>
        </div>
      </div>
      
      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Total Value */}
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Total Value</span>
              <PieChart className="w-5 h-5 text-primary-400" />
            </div>
            <div className="text-2xl font-bold">{formatCurrency(summary.total_value)}</div>
            <div className={`text-sm mt-1 ${summary.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {summary.total_pnl >= 0 ? '+' : ''}{formatCurrency(summary.total_pnl)}
            </div>
          </div>
          
          {/* Core Portfolio */}
          <div className="glass-card p-6 bg-gradient-to-br from-blue-900/20 to-blue-600/5 border-blue-500/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Core (70%)</span>
              <Shield className="w-5 h-5 text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-blue-400">{formatCurrency(summary.core.value)}</div>
            <div className="flex justify-between items-center mt-2">
              <span className="text-xs text-gray-400">{formatPercent(summary.core.allocation)} actual</span>
              <span className="text-xs">{summary.core.positions_count} positions</span>
            </div>
            <div className={`text-sm mt-1 ${summary.core.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {summary.core.pnl >= 0 ? '+' : ''}{formatCurrency(summary.core.pnl)}
            </div>
          </div>
          
          {/* Satellite Portfolio */}
          <div className="glass-card p-6 bg-gradient-to-br from-purple-900/20 to-purple-600/5 border-purple-500/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Satellite (30%)</span>
              <Rocket className="w-5 h-5 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-purple-400">{formatCurrency(summary.satellite.value)}</div>
            <div className="flex justify-between items-center mt-2">
              <span className="text-xs text-gray-400">{formatPercent(summary.satellite.allocation)} actual</span>
              <span className="text-xs">{summary.satellite.positions_count} positions</span>
            </div>
            <div className={`text-sm mt-1 ${summary.satellite.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {summary.satellite.pnl >= 0 ? '+' : ''}{formatCurrency(summary.satellite.pnl)}
            </div>
          </div>
          
          {/* Allocation Status */}
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Allocation Status</span>
              <Target className="w-5 h-5 text-emerald-400" />
            </div>
            <div className="space-y-2">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-blue-400">Core</span>
                  <span>{formatPercent(summary.core.allocation)}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full transition-all"
                    style={{ width: `${summary.core.allocation * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-purple-400">Satellite</span>
                  <span>{formatPercent(summary.satellite.allocation)}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-purple-500 to-purple-400 h-2 rounded-full transition-all"
                    style={{ width: `${summary.satellite.allocation * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Rebalance Alert */}
      {rebalanceCheck && rebalanceCheck.needs_rebalancing && (
        <div className="glass-card p-4 bg-yellow-900/20 border-yellow-500/30">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-bold text-yellow-400 mb-1">Rebalancing Needed</h4>
              <p className="text-sm text-gray-300 mb-3">
                Portfolio has {rebalanceCheck.actions_count} rebalancing action{rebalanceCheck.actions_count !== 1 ? 's' : ''} to bring allocation back to target.
              </p>
              <div className="flex gap-3">
                <button onClick={executeRebalancing} disabled={loading} className="btn btn-warning text-sm py-1 px-3">
                  Execute Rebalancing
                </button>
                <button onClick={() => setRebalanceCheck(null)} className="btn btn-secondary text-sm py-1 px-3">
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {rebalanceCheck && !rebalanceCheck.needs_rebalancing && (
        <div className="glass-card p-4 bg-green-900/20 border-green-500/30">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <div>
              <h4 className="font-bold text-green-400">Portfolio Balanced</h4>
              <p className="text-sm text-gray-300">No rebalancing needed at this time.</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-gray-700">
        <button 
          onClick={() => loadPositions('all')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'all' 
              ? 'text-primary-400 border-b-2 border-primary-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          All Positions
        </button>
        <button 
          onClick={() => loadPositions('core')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'core' 
              ? 'text-blue-400 border-b-2 border-blue-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Shield className="w-4 h-4 inline mr-1" />
          Core
        </button>
        <button 
          onClick={() => loadPositions('satellite')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'satellite' 
              ? 'text-purple-400 border-b-2 border-purple-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Rocket className="w-4 h-4 inline mr-1" />
          Satellite
        </button>
      </div>
      
      {/* Positions Table */}
      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left p-4 font-semibold text-gray-400">Symbol</th>
              <th className="text-left p-4 font-semibold text-gray-400">Type</th>
              <th className="text-right p-4 font-semibold text-gray-400">Shares</th>
              <th className="text-right p-4 font-semibold text-gray-400">Avg Entry</th>
              <th className="text-right p-4 font-semibold text-gray-400">Value</th>
              <th className="text-right p-4 font-semibold text-gray-400">Weight</th>
              <th className="text-right p-4 font-semibold text-gray-400">Target</th>
              <th className="text-right p-4 font-semibold text-gray-400">P/L</th>
            </tr>
          </thead>
          <tbody>
            {positions.length === 0 ? (
              <tr>
                <td colSpan="8" className="text-center p-8 text-gray-400">
                  No positions found
                </td>
              </tr>
            ) : (
              positions.map((position) => (
                <tr key={position.symbol} className="border-b border-gray-700/50 hover:bg-gray-800/50 transition-colors">
                  <td className="p-4">
                    <span className="font-bold">{position.symbol}</span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      position.type === 'core' 
                        ? 'bg-blue-900/30 text-blue-400 border border-blue-500/30' 
                        : 'bg-purple-900/30 text-purple-400 border border-purple-500/30'
                    }`}>
                      {position.type === 'core' ? '🛡️ Core' : '🚀 Satellite'}
                    </span>
                  </td>
                  <td className="p-4 text-right">{position.shares}</td>
                  <td className="p-4 text-right">{formatCurrency(position.average_entry)}</td>
                  <td className="p-4 text-right font-medium">{formatCurrency(position.current_value)}</td>
                  <td className="p-4 text-right">{formatPercent(position.current_weight)}</td>
                  <td className="p-4 text-right text-gray-400">{formatPercent(position.target_weight)}</td>
                  <td className="p-4 text-right">
                    <div className={position.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}>
                      <div className="font-medium">{formatCurrency(position.unrealized_pnl)}</div>
                      <div className="text-xs">({position.unrealized_pnl_percent.toFixed(2)}%)</div>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default HybridPortfolio;
