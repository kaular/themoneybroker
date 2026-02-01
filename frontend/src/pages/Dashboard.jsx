import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Wallet, PieChart, Activity, ShoppingCart, Shield } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../services/api';
import StopLossModal from '../components/StopLossModal';

const Dashboard = ({ accountData }) => {
  const [positions, setPositions] = useState([]);
  const [orders, setOrders] = useState([]);
  const [account, setAccount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showStopLossModal, setShowStopLossModal] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000); // Alle 10 Sekunden
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [accountRes, positionsRes, ordersRes] = await Promise.all([
        api.getAccount().catch(() => ({ data: null })),
        api.getPositions().catch(() => ({ data: [] })),
        api.getOrders().catch(() => ({ data: [] }))
      ]);

      setAccount(accountRes.data);
      setPositions(positionsRes.data);
      setOrders(ordersRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Fehler beim Laden der Dashboard-Daten:', error);
      setLoading(false);
    }
  };

  const displayAccount = accountData || account;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Dashboard</h2>
          <p className="text-gray-400">Übersicht über Ihr Trading-Portfolio</p>
        </div>
        <div className="flex space-x-2">
          <div className="px-4 py-2 bg-primary-500/20 rounded-xl border border-primary-500/30">
            <span className="text-xs text-gray-400">Live Updates</span>
            <div className="flex items-center space-x-1 mt-1">
              <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse"></div>
              <span className="text-sm font-semibold text-primary-400">Aktiv</span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      {displayAccount && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Portfolio-Wert"
            value={`$${displayAccount.portfolio_value?.toLocaleString('de-DE', { minimumFractionDigits: 2 })}`}
            icon={DollarSign}
            color="blue"
          />
          <StatCard
            title="Bargeld"
            value={`$${displayAccount.cash?.toLocaleString('de-DE', { minimumFractionDigits: 2 })}`}
            icon={Wallet}
            color="green"
          />
          <StatCard
            title="Unrealisierter P&L"
            value={`$${displayAccount.unrealized_pnl?.toLocaleString('de-DE', { minimumFractionDigits: 2 })}`}
            icon={displayAccount.unrealized_pnl >= 0 ? TrendingUp : TrendingDown}
            color={displayAccount.unrealized_pnl >= 0 ? 'green' : 'red'}
            trend={displayAccount.unrealized_pnl >= 0 ? 'up' : 'down'}
          />
          <StatCard
            title="Realisierter P&L"
            value={`$${displayAccount.realized_pnl?.toLocaleString('de-DE', { minimumFractionDigits: 2 })}`}
            icon={displayAccount.realized_pnl >= 0 ? TrendingUp : TrendingDown}
            color={displayAccount.realized_pnl >= 0 ? 'green' : 'red'}
            trend={displayAccount.realized_pnl >= 0 ? 'up' : 'down'}
          />
        </div>
      )}

      {!displayAccount && (
        <div className="card-glass text-center py-16">
          <Activity className="w-16 h-16 text-primary-400 mx-auto mb-4 animate-float" />
          <h3 className="text-xl font-bold text-white mb-2">Keine Verbindung</h3>
          <p className="text-gray-400">
            Bitte verbinden Sie sich zuerst mit einem Broker in den Einstellungen.
          </p>
        </div>
      )}

      {/* Positions & Orders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Positions */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-bold text-white">Offene Positionen</h3>
              <p className="text-sm text-gray-400 mt-1">{positions.length} aktive Positionen</p>
            </div>
            <div className="px-3 py-1 bg-primary-500/20 rounded-lg border border-primary-500/30">
              <span className="text-sm font-bold text-primary-400">{positions.length}</span>
            </div>
          </div>
          
          {positions.length > 0 ? (
            <div className="space-y-3">
              {positions.map((position, index) => (
                <PositionCard 
                  key={index} 
                  position={position}
                  onSetStopLoss={(pos) => {
                    setSelectedPosition(pos);
                    setShowStopLossModal(true);
                  }}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 border-2 border-dashed border-gray-700 rounded-xl">
              <PieChart className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500">Keine offenen Positionen</p>
            </div>
          )}
        </div>

        {/* Recent Orders */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-bold text-white">Aktuelle Orders</h3>
              <p className="text-sm text-gray-400 mt-1">{orders.length} Orders</p>
            </div>
            <div className="px-3 py-1 bg-emerald-500/20 rounded-lg border border-emerald-500/30">
              <span className="text-sm font-bold text-emerald-400">{orders.length}</span>
            </div>
          </div>
          
          {orders.length > 0 ? (
            <div className="space-y-3">
              {orders.slice(0, 5).map((order, index) => (
                <OrderCard key={index} order={order} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 border-2 border-dashed border-gray-700 rounded-xl">
              <ShoppingCart className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-500">Keine offenen Orders</p>
            </div>
          )}
        </div>
      </div>

      {/* Stop-Loss Modal */}
      {showStopLossModal && selectedPosition && (
        <StopLossModal
          position={selectedPosition}
          onClose={() => {
            setShowStopLossModal(false);
            setSelectedPosition(null);
          }}
          onSuccess={() => {
            fetchDashboardData();
          }}
        />
      )}
    </div>
  );
};

const StatCard = ({ title, value, icon: Icon, color, trend }) => {
  const colorClasses = {
    blue: 'from-blue-600/20 to-cyan-600/20 border-blue-500/30 text-blue-400',
    green: 'from-green-600/20 to-emerald-600/20 border-green-500/30 text-green-400',
    red: 'from-red-600/20 to-rose-600/20 border-red-500/30 text-red-400',
  };

  return (
    <div className={`stat-card bg-gradient-to-br ${colorClasses[color]} border`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-semibold text-gray-400 mb-2">{title}</p>
          <p className="text-3xl font-bold text-white mb-1">{value}</p>
          {trend && (
            <div className={`flex items-center space-x-1 text-sm ${trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
              {trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              <span className="font-medium">{trend === 'up' ? 'Gewinn' : 'Verlust'}</span>
            </div>
          )}
        </div>
        <div className={`p-4 rounded-xl bg-gradient-to-br ${colorClasses[color]} backdrop-blur-sm`}>
          <Icon className="w-7 h-7" />
        </div>
      </div>
    </div>
  );
};

const PositionCard = ({ position, onSetStopLoss }) => {
  const pnlPercent = ((position.current_price - position.entry_price) / position.entry_price) * 100;
  const isProfit = position.unrealized_pnl >= 0;

  return (
    <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-xl border border-gray-600/30 hover:border-gray-500/50 transition-all duration-200">
      <div className="flex-1">
        <p className="font-bold text-white text-lg">{position.symbol}</p>
        <p className="text-sm text-gray-400 mt-1">
          {position.quantity} @ ${position.entry_price.toFixed(2)}
        </p>
      </div>
      <div className="text-right mr-4">
        <p className={`font-bold text-lg ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
          ${position.unrealized_pnl.toFixed(2)}
        </p>
        <p className={`text-sm font-semibold ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
          {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%
        </p>
      </div>
      <button
        onClick={() => onSetStopLoss(position)}
        className="btn btn-secondary flex items-center space-x-2 py-2 px-3"
        title="Stop-Loss/Take-Profit setzen"
      >
        <Shield className="w-4 h-4" />
        <span className="text-xs">SL/TP</span>
      </button>
    </div>
  );
};

const OrderCard = ({ order }) => {
  const statusColors = {
    pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    filled: 'bg-green-500/20 text-green-400 border-green-500/30',
    cancelled: 'bg-red-500/20 text-red-400 border-red-500/30',
  };

  return (
    <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-xl border border-gray-600/30 hover:border-gray-500/50 transition-all duration-200">
      <div>
        <p className="font-bold text-white text-lg">{order.symbol}</p>
        <p className="text-sm text-gray-400 mt-1">
          {order.side.toUpperCase()} {order.quantity} @ {order.order_type}
        </p>
      </div>
      <span className={`px-3 py-1.5 text-xs font-bold rounded-lg border ${statusColors[order.status] || 'bg-gray-700/50 text-gray-400 border-gray-600/30'}`}>
        {order.status}
      </span>
    </div>
  );
};

export default Dashboard;
