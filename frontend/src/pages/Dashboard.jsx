import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Wallet, PieChart, Activity, ShoppingCart, Shield, XCircle } from 'lucide-react';
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
  const [showSellModal, setShowSellModal] = useState(false);
  const [positionToSell, setPositionToSell] = useState(null);
  const [selling, setSelling] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000); // Alle 10 Sekunden
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [accountRes, positionsRes, ordersRes] = await Promise.all([
        api.getAccount().catch((err) => {
          console.error('Account error:', err);
          return { data: null };
        }),
        api.getPositions().catch((err) => {
          console.error('Positions error:', err);
          return { data: [] };
        }),
        api.getOrders().catch((err) => {
          console.error('Orders error:', err);
          return { data: [] };
        })
      ]);

      console.log('Dashboard data loaded:', { account: accountRes.data, positions: positionsRes.data.length, orders: ordersRes.data.length });

      // Nur aktualisieren, wenn die Daten vorhanden sind
      if (accountRes.data) {
        setAccount(accountRes.data);
      }
      setPositions(positionsRes.data || []);
      setOrders(ordersRes.data || []);
    } catch (error) {
      console.error('Fehler beim Laden der Dashboard-Daten:', error);
    } finally {
      setLoading(false);
    }
  };

  const sellPosition = async (position) => {
    setPositionToSell(position);
    setShowSellModal(true);
  };

  const confirmSell = async () => {
    if (!positionToSell) return;
    
    setSelling(true);
    const symbol = positionToSell.symbol;
    const quantity = positionToSell.quantity;

    try {
      console.log('Verkaufe Position:', positionToSell);
      
      const response = await api.post('/orders', {
        symbol: symbol,
        quantity: quantity,
        side: 'sell',
        order_type: 'market'
      });

      console.log('Verkauf erfolgreich:', response.data);
      
      // Modal schließen
      setShowSellModal(false);
      setPositionToSell(null);
      
      // Daten neu laden
      fetchDashboardData();
      
      // Erfolgs-Alert nach dem Schließen des Modals
      setTimeout(() => {
        alert(`✅ Verkaufsorder für ${quantity} ${symbol} Aktien wurde platziert!`);
      }, 200);
    } catch (error) {
      console.error('Fehler beim Verkauf:', error);
      alert(`❌ Fehler beim Verkauf: ${error.response?.data?.detail || error.message}`);
      // Modal bleibt bei Fehler offen
    } finally {
      setSelling(false);
    }
  };

  const displayAccount = accountData || account;

  // Berechne den tatsächlichen Aktien-Wert aus den Positionen
  const calculatePositionsValue = () => {
    if (!positions || positions.length === 0) return 0;
    return positions.reduce((total, pos) => total + (pos.quantity * pos.current_price), 0);
  };

  const positionsValue = calculatePositionsValue();

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

      {/* Gesamtwert Header */}
      {displayAccount && (
        <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-2xl shadow-2xl p-8 border border-blue-500/30">
          <div className="text-center">
            <p className="text-sm font-semibold text-gray-400 mb-2 uppercase tracking-wide">Gesamtwert Portfolio</p>
            <h1 className="text-6xl font-bold text-white mb-2">
              ${(displayAccount.portfolio_value ?? 0).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </h1>
            <div className="flex items-center justify-center gap-4 mt-4">
              <div className="text-center">
                <p className="text-xs text-gray-400">Bargeld</p>
                <p className="text-lg font-semibold text-green-400">
                  ${(displayAccount.cash ?? 0).toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="w-px h-8 bg-gray-600"></div>
              <div className="text-center">
                <p className="text-xs text-gray-400">Unrealisiert P&L</p>
                <p className={`text-lg font-semibold ${(displayAccount.unrealized_pnl ?? 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {(displayAccount.unrealized_pnl ?? 0) >= 0 ? '+' : ''}${(displayAccount.unrealized_pnl ?? 0).toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      {displayAccount && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Aktien-Wert"
            value={`$${positionsValue.toLocaleString('de-DE', { minimumFractionDigits: 2 })}`}
            icon={PieChart}
            color="blue"
            subtitle="Wert der gekauften Aktien"
          />
          <StatCard
            title="Verfügbares Cash"
            value={`$${(displayAccount.cash ?? 0).toLocaleString('de-DE', { minimumFractionDigits: 2 })}`}
            icon={Wallet}
            color="green"
            subtitle="Zum Investieren verfügbar"
          />
          <StatCard
            title="Realisierter P&L"
            value={`$${(displayAccount.realized_pnl ?? 0).toLocaleString('de-DE', { minimumFractionDigits: 2 })}`}
            icon={(displayAccount.realized_pnl ?? 0) >= 0 ? TrendingUp : TrendingDown}
            color={(displayAccount.realized_pnl ?? 0) >= 0 ? 'green' : 'red'}
            trend={(displayAccount.realized_pnl ?? 0) >= 0 ? 'up' : 'down'}
          />
          <StatCard
            title="Unrealisierter P&L"
            value={`$${(displayAccount.unrealized_pnl ?? 0).toLocaleString('de-DE', { minimumFractionDigits: 2 })}`}
            icon={(displayAccount.unrealized_pnl ?? 0) >= 0 ? TrendingUp : TrendingDown}
            color={(displayAccount.unrealized_pnl ?? 0) >= 0 ? 'green' : 'red'}
            trend={(displayAccount.unrealized_pnl ?? 0) >= 0 ? 'up' : 'down'}
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
                  onSell={sellPosition}
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

      {/* Sell Confirmation Modal */}
      {showSellModal && positionToSell && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-xl shadow-2xl p-6 max-w-md w-full mx-4 border border-gray-700">
            <h3 className="text-2xl font-bold text-white mb-4">Position verkaufen</h3>
            
            <div className="bg-gray-700/50 rounded-lg p-4 mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-400">Symbol:</span>
                <span className="text-white font-bold text-lg">{positionToSell.symbol}</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-400">Menge:</span>
                <span className="text-white font-semibold">{positionToSell.quantity} Stück</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-400">Aktueller Preis:</span>
                <span className="text-white font-semibold">${positionToSell.current_price.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">Geschätzter Wert:</span>
                <span className="text-white font-bold">${(positionToSell.quantity * positionToSell.current_price).toFixed(2)}</span>
              </div>
            </div>

            <p className="text-gray-300 mb-6">
              Möchten Sie wirklich <span className="font-bold text-white">{positionToSell.quantity} Aktien</span> von{' '}
              <span className="font-bold text-white">{positionToSell.symbol}</span> zum Marktpreis verkaufen?
            </p>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowSellModal(false);
                  setPositionToSell(null);
                }}
                disabled={selling}
                className="flex-1 px-4 py-3 bg-gray-700 text-white rounded-lg font-semibold hover:bg-gray-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Abbrechen
              </button>
              <button
                onClick={confirmSell}
                disabled={selling}
                className="flex-1 px-4 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {selling ? 'Verkaufe...' : 'Verkaufen'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const StatCard = ({ title, value, icon: Icon, color, trend, subtitle }) => {
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
          {subtitle && (
            <p className="text-xs text-gray-400 mt-1">{subtitle}</p>
          )}
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

const PositionCard = ({ position, onSetStopLoss, onSell }) => {
  const pnlPercent = ((position.current_price - position.entry_price) / position.entry_price) * 100;
  const pnlPerShare = position.current_price - position.entry_price;
  const isProfit = position.unrealized_pnl >= 0;

  return (
    <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-xl border border-gray-600/30 hover:border-gray-500/50 transition-all duration-200">
      <div className="flex-1">
        <p className="font-bold text-white text-lg">{position.symbol}</p>
        <p className="text-sm text-gray-400 mt-1">
          {position.quantity} Stück
        </p>
      </div>
      
      <div className="flex flex-col items-end mr-4">
        <div className="text-sm text-gray-400 mb-1">
          <span className="font-medium">Gekauft:</span> ${position.entry_price.toFixed(2)}
        </div>
        <div className="text-sm text-white font-medium">
          <span className="text-gray-400">Aktuell:</span> ${position.current_price.toFixed(2)}
        </div>
        <div className={`text-xs mt-1 font-medium ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
          {pnlPerShare >= 0 ? '+' : ''}${pnlPerShare.toFixed(2)} pro Aktie
        </div>
      </div>
      
      <div className="text-right mr-4">
        <p className={`font-bold text-lg ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
          ${position.unrealized_pnl.toFixed(2)}
        </p>
        <p className={`text-sm font-semibold ${isProfit ? 'text-green-400' : 'text-red-400'}`}>
          {pnlPercent >= 0 ? '+' : ''}{pnlPercent.toFixed(2)}%
        </p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => onSell(position)}
          className="bg-red-600 hover:bg-red-700 text-white flex items-center space-x-2 py-2 px-3 rounded-lg transition-all duration-200"
          title="Position verkaufen"
        >
          <XCircle className="w-4 h-4" />
          <span className="text-xs font-semibold">Verkaufen</span>
        </button>
        <button
          onClick={() => onSetStopLoss(position)}
          className="btn btn-secondary flex items-center space-x-2 py-2 px-3"
          title="Stop-Loss/Take-Profit setzen"
        >
          <Shield className="w-4 h-4" />
          <span className="text-xs">SL/TP</span>
        </button>
      </div>
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
