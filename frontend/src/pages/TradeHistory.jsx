import { useState, useEffect } from 'react';
import { History, TrendingUp, TrendingDown, DollarSign, Target, Filter } from 'lucide-react';
import { format } from 'date-fns';
import api from '../services/api';

const TradeHistory = () => {
  const [trades, setTrades] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [symbolFilter, setSymbolFilter] = useState('');

  useEffect(() => {
    fetchData();
  }, [symbolFilter]);

  const fetchData = async () => {
    try {
      const [tradesRes, statsRes] = await Promise.all([
        api.getTradeHistory(100, symbolFilter || null),
        api.getTradeStats()
      ]);
      
      setTrades(tradesRes.data.trades);
      setStats(statsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Fehler beim Laden der Trade-Historie:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Trade History</h2>
          <p className="text-gray-400">Vollständige Übersicht aller Trades</p>
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Gesamt Trades"
            value={stats.total_trades}
            icon={History}
            color="blue"
          />
          <StatCard
            title="Win Rate"
            value={`${stats.win_rate}%`}
            subtitle={`${stats.winning_trades} / ${stats.losing_trades}`}
            icon={Target}
            color="green"
          />
          <StatCard
            title="Total P&L"
            value={`$${stats.total_pnl.toLocaleString('de-DE', { minimumFractionDigits: 2 })}`}
            icon={stats.total_pnl >= 0 ? TrendingUp : TrendingDown}
            color={stats.total_pnl >= 0 ? 'green' : 'red'}
          />
          <StatCard
            title="Profit Factor"
            value={stats.profit_factor.toFixed(2)}
            subtitle={`Ø $${stats.avg_pnl_per_trade.toFixed(2)}/Trade`}
            icon={DollarSign}
            color="purple"
          />
        </div>
      )}

      {/* Filter */}
      <div className="card-glass">
        <div className="flex items-center space-x-4">
          <Filter className="w-5 h-5 text-primary-400" />
          <input
            type="text"
            placeholder="Symbol filtern (z.B. AAPL)"
            value={symbolFilter}
            onChange={(e) => setSymbolFilter(e.target.value.toUpperCase())}
            className="input flex-1"
          />
          {symbolFilter && (
            <button
              onClick={() => setSymbolFilter('')}
              className="btn btn-secondary"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Trades Table */}
      <div className="card-glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-800/50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Symbol
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Side
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  P&L
                </th>
                <th className="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700/50">
              {trades.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                    <History className="w-12 h-12 mx-auto mb-3 text-gray-600" />
                    <p>Keine Trades vorhanden</p>
                  </td>
                </tr>
              ) : (
                trades.map((trade) => (
                  <tr key={trade.id} className="hover:bg-gray-800/20 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {format(new Date(trade.submitted_at), 'dd.MM.yyyy HH:mm')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-semibold text-white">{trade.symbol}</span>
                      {trade.strategy_name && (
                        <span className="ml-2 text-xs text-gray-500">({trade.strategy_name})</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-lg ${
                        trade.side.toLowerCase() === 'buy' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {trade.side.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-300">
                      {trade.filled_qty || trade.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-300">
                      ${trade.avg_fill_price?.toFixed(2) || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-semibold text-white">
                      ${((trade.filled_qty || trade.quantity) * (trade.avg_fill_price || 0)).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      {trade.pnl !== null ? (
                        <span className={`font-bold ${trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                          {trade.pnl_percent !== null && (
                            <span className="text-xs ml-1">
                              ({trade.pnl_percent >= 0 ? '+' : ''}{trade.pnl_percent.toFixed(2)}%)
                            </span>
                          )}
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <StatusBadge status={trade.status} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, subtitle, icon: Icon, color }) => {
  const colorClasses = {
    blue: 'from-blue-600/20 to-blue-500/10 border-blue-500/30',
    green: 'from-green-600/20 to-emerald-500/10 border-green-500/30',
    red: 'from-red-600/20 to-rose-500/10 border-red-500/30',
    purple: 'from-purple-600/20 to-purple-500/10 border-purple-500/30',
  };

  const iconColorClasses = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    red: 'text-red-400',
    purple: 'text-purple-400',
  };

  return (
    <div className={`card-glass bg-gradient-to-br ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-gray-400 font-semibold">{title}</span>
        <Icon className={`w-5 h-5 ${iconColorClasses[color]}`} />
      </div>
      <div className="text-2xl font-bold text-white mb-1">{value}</div>
      {subtitle && <div className="text-xs text-gray-500">{subtitle}</div>}
    </div>
  );
};

const StatusBadge = ({ status }) => {
  const statusColors = {
    filled: 'bg-green-500/20 text-green-400',
    pending: 'bg-yellow-500/20 text-yellow-400',
    canceled: 'bg-gray-500/20 text-gray-400',
    rejected: 'bg-red-500/20 text-red-400',
    new: 'bg-blue-500/20 text-blue-400',
  };

  return (
    <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${statusColors[status] || statusColors.pending}`}>
      {status}
    </span>
  );
};

export default TradeHistory;
