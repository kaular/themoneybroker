import { useState, useEffect } from 'react';
import { Search, TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';
import api from '../services/api';

export default function SymbolSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [allSymbols, setAllSymbols] = useState([]);
  const [topGainers, setTopGainers] = useState([]);
  const [topLosers, setTopLosers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [orderModal, setOrderModal] = useState(false);
  const [orderData, setOrderData] = useState({
    side: 'buy',
    quantity: 1,
    order_type: 'market',
    limit_price: null
  });

  // Vordefinierte beliebte US-Symbole (alle gut handelbar auf Alpaca)
  const popularSymbols = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
    'AMD', 'INTC', 'PLTR', 'SNOW', 'CRWD', 'NET', 'DDOG', 'ZS',
    'PANW', 'OKTA', 'SHOP', 'SQ', 'PYPL', 'ADBE', 'CRM', 'NOW',
    'UBER', 'LYFT', 'RIVN', 'SOFI', 'HOOD', 'BA', 'DIS', 'V'
  ];

  // Lade alle Symbole beim Start
  useEffect(() => {
    loadAllSymbols();
  }, []);

  const loadAllSymbols = async () => {
    setLoading(true);
    try {
      // Hole Quotes für alle Symbole
      const results = await Promise.all(
        popularSymbols.map(async (symbol) => {
          try {
            const response = await api.get(`/api/quote/${symbol}`);
            return {
              symbol,
              price: response.data.price,
              change: response.data.change,
              change_percent: response.data.change_percent,
              volume: response.data.volume
            };
          } catch (error) {
            return null;
          }
        })
      );

      const validResults = results.filter(r => r !== null);
      setAllSymbols(validResults);
      setSearchResults(validResults);

      // Sortiere für Top Gainers/Losers
      const sortedByChange = [...validResults].sort((a, b) => 
        (b.change_percent || 0) - (a.change_percent || 0)
      );
      
      setTopGainers(sortedByChange.slice(0, 5));
      setTopLosers(sortedByChange.slice(-5).reverse());
    } catch (error) {
      console.error('Load error:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchSymbols = (query) => {
    if (!query || query.length < 1) {
      setSearchResults(allSymbols);
      return;
    }

    const filtered = allSymbols.filter(stock => 
      stock.symbol.toLowerCase().includes(query.toLowerCase())
    );

    setSearchResults(filtered);
  };

  const openOrderModal = (symbol, side) => {
    setSelectedSymbol(symbol);
    setOrderData({ ...orderData, side });
    setOrderModal(true);
  };

  const placeOrder = async () => {
    try {
      await api.post('/api/orders', {
        symbol: selectedSymbol,
        quantity: parseFloat(orderData.quantity),
        side: orderData.side,
        order_type: orderData.order_type,
        limit_price: orderData.order_type === 'limit' ? parseFloat(orderData.limit_price) : null
      });

      alert(`${orderData.side.toUpperCase()} Order für ${selectedSymbol} platziert!`);
      setOrderModal(false);
      setOrderData({
        side: 'buy',
        quantity: 1,
        order_type: 'market',
        limit_price: null
      });
    } catch (error) {
      alert(`Fehler: ${error.response?.data?.detail || error.message}`);
    }
  };

  const formatPrice = (price) => {
    if (!price) return 'N/A';
    return `$${parseFloat(price).toFixed(2)}`;
  };

  const formatVolume = (volume) => {
    if (!volume) return 'N/A';
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(1)}B`;
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(1)}M`;
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(1)}K`;
    return volume.toString();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Symbol Suche</h1>
          <p className="text-gray-600 mt-1">Suche nach Aktien und platziere Orders</p>
        </div>
        <button
          onClick={loadAllSymbols}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Lädt...' : 'Aktualisieren'}
        </button>
      </div>

      {/* Top Gainers & Losers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Top Gainers */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-green-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6" />
            🔥 Top Gainers (24h)
          </h2>
          <div className="space-y-2">
            {topGainers.map((stock, idx) => (
              <div key={stock.symbol} className="flex items-center justify-between bg-white rounded-lg p-3">
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold text-gray-400">#{idx + 1}</span>
                  <span className="font-bold text-gray-900">{stock.symbol}</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900">${stock.price?.toFixed(2)}</div>
                  <div className="text-green-600 font-bold text-sm">
                    +{stock.change_percent?.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Losers */}
        <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-red-800 mb-4 flex items-center gap-2">
            <TrendingDown className="w-6 h-6" />
            📉 Top Losers (24h)
          </h2>
          <div className="space-y-2">
            {topLosers.map((stock, idx) => (
              <div key={stock.symbol} className="flex items-center justify-between bg-white rounded-lg p-3">
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold text-gray-400">#{idx + 1}</span>
                  <span className="font-bold text-gray-900">{stock.symbol}</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-900">${stock.price?.toFixed(2)}</div>
                  <div className="text-red-600 font-bold text-sm">
                    {stock.change_percent?.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              searchSymbols(e.target.value);
            }}
            placeholder="Symbol suchen (z.B. AAPL, TSLA, NVDA)..."
            className="w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
          />
        </div>
        {loading && (
          <p className="text-gray-500 text-sm mt-2">Suche läuft...</p>
        )}
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b">
            <h2 className="text-lg font-semibold">Verfügbare Symbole ({searchResults.length})</h2>
            {searchQuery && (
              <p className="text-sm text-gray-600 mt-1">Gefiltert nach: "{searchQuery}"</p>
            )}
          </div>
          
          <div className="divide-y">
            {searchResults.map((result) => (
              <div key={result.symbol} className="p-6 hover:bg-gray-50 transition">
                <div className="flex items-center justify-between">
                  {/* Symbol Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-xl font-bold text-gray-900">{result.symbol}</h3>
                      {result.change_percent !== null && (
                        <span className={`flex items-center gap-1 px-2 py-1 rounded text-sm font-medium ${
                          result.change_percent >= 0 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {result.change_percent >= 0 ? (
                            <TrendingUp className="w-4 h-4" />
                          ) : (
                            <TrendingDown className="w-4 h-4" />
                          )}
                          {result.change_percent >= 0 ? '+' : ''}{result.change_percent?.toFixed(2)}%
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-6 mt-2 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-4 h-4" />
                        <span className="font-semibold">{formatPrice(result.price)}</span>
                      </div>
                      
                      {result.change !== null && (
                        <div className={result.change >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {result.change >= 0 ? '+' : ''}{result.change?.toFixed(2)}
                        </div>
                      )}
                      
                      <div className="flex items-center gap-1">
                        <Activity className="w-4 h-4" />
                        <span>Vol: {formatVolume(result.volume)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => openOrderModal(result.symbol, 'buy')}
                      className="px-6 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition"
                    >
                      Buy
                    </button>
                    <button
                      onClick={() => openOrderModal(result.symbol, 'sell')}
                      className="px-6 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition"
                    >
                      Sell
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {loading && !allSymbols.length && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-500 text-lg">Lade Symbole...</p>
        </div>
      )}

      {/* Order Modal */}
      {orderModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-4">
              {orderData.side === 'buy' ? '🟢 Buy' : '🔴 Sell'} {selectedSymbol}
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                <input
                  type="number"
                  value={orderData.quantity}
                  onChange={(e) => setOrderData({ ...orderData, quantity: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  min="1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Order Type</label>
                <select
                  value={orderData.order_type}
                  onChange={(e) => setOrderData({ ...orderData, order_type: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="market">Market</option>
                  <option value="limit">Limit</option>
                </select>
              </div>

              {orderData.order_type === 'limit' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Limit Price</label>
                  <input
                    type="number"
                    value={orderData.limit_price || ''}
                    onChange={(e) => setOrderData({ ...orderData, limit_price: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    step="0.01"
                  />
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setOrderModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Abbrechen
              </button>
              <button
                onClick={placeOrder}
                className={`flex-1 px-4 py-2 rounded-lg text-white font-semibold ${
                  orderData.side === 'buy'
                    ? 'bg-green-600 hover:bg-green-700'
                    : 'bg-red-600 hover:bg-red-700'
                }`}
              >
                Order platzieren
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
