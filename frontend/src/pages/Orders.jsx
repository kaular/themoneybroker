import { useState, useEffect } from 'react';
import { ShoppingCart, X, Plus } from 'lucide-react';
import api from '../services/api';

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [showPlaceOrder, setShowPlaceOrder] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
    const interval = setInterval(fetchOrders, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.getOrders();
      setOrders(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Fehler beim Laden der Orders:', error);
      setLoading(false);
    }
  };

  const handleCancelOrder = async (orderId) => {
    if (confirm('Order wirklich stornieren?')) {
      try {
        await api.cancelOrder(orderId);
        await fetchOrders();
      } catch (error) {
        console.error('Fehler beim Stornieren:', error);
        alert('Fehler: ' + (error.response?.data?.detail || error.message));
      }
    }
  };

  const handlePlaceOrder = async (orderData) => {
    try {
      await api.placeOrder(orderData);
      await fetchOrders();
      setShowPlaceOrder(false);
    } catch (error) {
      console.error('Fehler beim Platzieren der Order:', error);
      alert('Fehler: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Orders</h2>
          <p className="text-gray-600 mt-1">Übersicht und Verwaltung Ihrer Orders</p>
        </div>
        <button
          onClick={() => setShowPlaceOrder(true)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Manuelle Order</span>
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : orders.length > 0 ? (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Seite
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Menge
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Typ
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ausgeführt
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Aktionen
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {orders.map((order) => (
                  <tr key={order.order_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{order.symbol}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        order.side === 'buy' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {order.side.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {order.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {order.order_type.toUpperCase()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={order.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {order.filled_quantity} / {order.quantity}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <button
                        onClick={() => handleCancelOrder(order.order_id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="card text-center py-12">
          <ShoppingCart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Keine Orders</h3>
          <p className="text-gray-600">
            Sie haben aktuell keine offenen Orders.
          </p>
        </div>
      )}

      {showPlaceOrder && (
        <PlaceOrderModal
          onClose={() => setShowPlaceOrder(false)}
          onSubmit={handlePlaceOrder}
        />
      )}
    </div>
  );
};

const StatusBadge = ({ status }) => {
  const statusConfig = {
    pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Ausstehend' },
    filled: { bg: 'bg-green-100', text: 'text-green-800', label: 'Ausgeführt' },
    partially_filled: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Teilweise' },
    cancelled: { bg: 'bg-red-100', text: 'text-red-800', label: 'Storniert' },
    rejected: { bg: 'bg-red-100', text: 'text-red-800', label: 'Abgelehnt' },
  };

  const config = statusConfig[status] || statusConfig.pending;

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded ${config.bg} ${config.text}`}>
      {config.label}
    </span>
  );
};

const PlaceOrderModal = ({ onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    symbol: 'AAPL',
    quantity: 10,
    side: 'buy',
    order_type: 'market',
    limit_price: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const orderData = {
      ...formData,
      quantity: parseFloat(formData.quantity),
      limit_price: formData.limit_price ? parseFloat(formData.limit_price) : null
    };
    onSubmit(orderData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Manuelle Order platzieren</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Symbol</label>
              <input
                type="text"
                className="input"
                value={formData.symbol}
                onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                placeholder="z.B. AAPL"
                required
              />
            </div>

            <div>
              <label className="label">Menge</label>
              <input
                type="number"
                className="input"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                min="1"
                required
              />
            </div>

            <div>
              <label className="label">Seite</label>
              <select
                className="input"
                value={formData.side}
                onChange={(e) => setFormData({ ...formData, side: e.target.value })}
              >
                <option value="buy">Kaufen</option>
                <option value="sell">Verkaufen</option>
              </select>
            </div>

            <div>
              <label className="label">Order-Typ</label>
              <select
                className="input"
                value={formData.order_type}
                onChange={(e) => setFormData({ ...formData, order_type: e.target.value })}
              >
                <option value="market">Market</option>
                <option value="limit">Limit</option>
              </select>
            </div>

            {formData.order_type === 'limit' && (
              <div>
                <label className="label">Limit-Preis</label>
                <input
                  type="number"
                  className="input"
                  value={formData.limit_price}
                  onChange={(e) => setFormData({ ...formData, limit_price: e.target.value })}
                  step="0.01"
                  min="0"
                  required
                />
              </div>
            )}

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
              <p className="text-sm text-yellow-800">
                ⚠️ Diese Order wird sofort an den Broker übermittelt.
              </p>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                type="button"
                onClick={onClose}
                className="btn btn-secondary flex-1"
              >
                Abbrechen
              </button>
              <button
                type="submit"
                className="btn btn-primary flex-1"
              >
                Order platzieren
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Orders;
