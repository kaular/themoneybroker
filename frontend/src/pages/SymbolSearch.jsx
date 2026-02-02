import { useState, useEffect } from 'react';
import { Search, TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ComposedChart, Customized } from 'recharts';
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
  const [quote, setQuote] = useState(null);
  const [loadingQuote, setLoadingQuote] = useState(false);
  const [showChartModal, setShowChartModal] = useState(false);
  const [chartSymbol, setChartSymbol] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [chartLoading, setChartLoading] = useState(false);
  const [chartError, setChartError] = useState(null);
  const [chartType, setChartType] = useState('line');
  const [chartTimeframe, setChartTimeframe] = useState('1D');
  const [chartDays, setChartDays] = useState(180);
  const [chartStartDate, setChartStartDate] = useState('');
  const [chartEndDate, setChartEndDate] = useState('');
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

  const companyNames = {
    AAPL: 'Apple Inc.',
    MSFT: 'Microsoft Corporation',
    GOOGL: 'Alphabet Inc.',
    AMZN: 'Amazon.com, Inc.',
    TSLA: 'Tesla, Inc.',
    NVDA: 'NVIDIA Corporation',
    META: 'Meta Platforms, Inc.',
    NFLX: 'Netflix, Inc.',
    AMD: 'Advanced Micro Devices, Inc.',
    INTC: 'Intel Corporation',
    PLTR: 'Palantir Technologies Inc.',
    SNOW: 'Snowflake Inc.',
    CRWD: 'CrowdStrike Holdings, Inc.',
    NET: 'Cloudflare, Inc.',
    DDOG: 'Datadog, Inc.',
    ZS: 'Zscaler, Inc.',
    PANW: 'Palo Alto Networks, Inc.',
    OKTA: 'Okta, Inc.',
    SHOP: 'Shopify Inc.',
    SQ: 'Block, Inc.',
    PYPL: 'PayPal Holdings, Inc.',
    ADBE: 'Adobe Inc.',
    CRM: 'Salesforce, Inc.',
    NOW: 'ServiceNow, Inc.',
    UBER: 'Uber Technologies, Inc.',
    LYFT: 'Lyft, Inc.',
    RIVN: 'Rivian Automotive, Inc.',
    SOFI: 'SoFi Technologies, Inc.',
    HOOD: 'Robinhood Markets, Inc.',
    BA: 'The Boeing Company',
    DIS: 'The Walt Disney Company',
    V: 'Visa Inc.'
  };

  const getCompanyName = (symbol) => companyNames[symbol] || symbol;

  const openChart = async (symbol) => {
    if (!symbol) return;
    setChartSymbol(symbol);
    setShowChartModal(true);
    await loadChartData(symbol, chartTimeframe, chartDays);
  };

  const loadChartData = async (symbol, timeframe, days) => {
    setChartLoading(true);
    setChartError(null);
    try {
      const response = await api.get(`/market/history/${symbol}`, {
        params: { timeframe, days }
      });
      setChartData(response.data.data || []);
    } catch (error) {
      console.error('Fehler beim Laden der Chart-Daten:', error);
      setChartError(error.response?.data?.detail || error.message);
      setChartData([]);
    } finally {
      setChartLoading(false);
    }
  };

  // Lade Symbole schrittweise beim Start
  useEffect(() => {
    loadSymbolsProgressively();
  }, []);

  const loadSymbolsProgressively = async () => {
    setLoading(true);
    
    // Lade zuerst die wichtigsten 10 Symbole
    const prioritySymbols = popularSymbols.slice(0, 10);
    await loadSymbolBatch(prioritySymbols);
    
    setLoading(false);
    
    // Lade die restlichen Symbole im Hintergrund
    const remainingSymbols = popularSymbols.slice(10);
    await loadSymbolBatch(remainingSymbols, true);
  };

  const loadSymbolBatch = async (symbols, isBackground = false) => {
    const results = await Promise.all(
      symbols.map(async (symbol) => {
        try {
          const response = await api.get(`/api/quote/${symbol}`);
          // Hole auch Quote-Daten (Bid/Ask) für Spread
          let quoteData = null;
          try {
            const quoteResponse = await api.get(`/quote/${symbol}`);
            quoteData = quoteResponse.data;
          } catch (e) {
            console.log(`Quote data not available for ${symbol}`);
          }
          return {
            symbol,
            name: getCompanyName(symbol),
            price: response.data.price,
            change: response.data.change,
            change_percent: response.data.change_percent,
            volume: response.data.volume,
            bid: quoteData?.bid,
            ask: quoteData?.ask,
            spread: quoteData?.spread,
            spread_percent: quoteData?.spread_percent
          };
        } catch (error) {
          return null;
        }
      })
    );

    const validResults = results.filter(r => r !== null);
    
    // Füge die neuen Ergebnisse hinzu
    setAllSymbols(prev => {
      const combined = [...prev, ...validResults];
      // Sortiere für Top Gainers/Losers
      const sortedByChange = [...combined].sort((a, b) => 
        (b.change_percent || 0) - (a.change_percent || 0)
      );
      
      setTopGainers(sortedByChange.slice(0, 5));
      setTopLosers(sortedByChange.slice(-5).reverse());
      
      return combined;
    });
    
    setSearchResults(prev => [...prev, ...validResults]);
  };

  const loadAllSymbols = async () => {
    setLoading(true);
    try {
      // Hole Quotes für alle Symbole
      const results = await Promise.all(
        popularSymbols.map(async (symbol) => {
          try {
            const response = await api.get(`/api/quote/${symbol}`);
            // Hole auch Quote-Daten (Bid/Ask) für Spread
            let quoteData = null;
            try {
              const quoteResponse = await api.get(`/quote/${symbol}`);
              quoteData = quoteResponse.data;
            } catch (e) {
              console.log(`Quote data not available for ${symbol}`);
            }
            return {
              symbol,
              name: getCompanyName(symbol),
              price: response.data.price,
              change: response.data.change,
              change_percent: response.data.change_percent,
              volume: response.data.volume,
              bid: quoteData?.bid,
              ask: quoteData?.ask,
              spread: quoteData?.spread,
              spread_percent: quoteData?.spread_percent
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

  const openOrderModal = async (symbol, side) => {
    setSelectedSymbol(symbol);
    setOrderData({ ...orderData, side });
    setOrderModal(true);
    
    // Lade Quote (Bid/Ask)
    setLoadingQuote(true);
    try {
      const response = await api.get(`/quote/${symbol}`);
      setQuote(response.data);
    } catch (error) {
      console.error('Fehler beim Laden der Quote:', error);
      setQuote(null);
    } finally {
      setLoadingQuote(false);
    }
  };

  const placeOrder = async () => {
    try {
      await api.post('/orders', {
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

  const formatChartDate = (value) => new Date(value).toLocaleString();

  const calculateDaysBetween = (start, end) => {
    if (!start || !end) return null;
    const startDate = new Date(start);
    const endDate = new Date(end);
    if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) return null;
    const diffMs = endDate.getTime() - startDate.getTime();
    if (diffMs <= 0) return null;
    return Math.ceil(diffMs / (1000 * 60 * 60 * 24));
  };

  const Candlestick = ({ yAxisMap, offset, data, width }) => {
    if (!yAxisMap || !offset || !width || !data?.length) return null;
    const yAxis = Object.values(yAxisMap)[0];
    if (!yAxis) return null;

    const plotWidth = width - offset.left - offset.right;
    const step = plotWidth / data.length;
    const candleWidth = Math.max(3, Math.min(12, step * 0.6));

    return (
      <g>
        {data.map((d, index) => {
          const x = offset.left + step * index + step / 2;
          const open = yAxis.scale(d.open) + offset.top;
          const close = yAxis.scale(d.close) + offset.top;
          const high = yAxis.scale(d.high) + offset.top;
          const low = yAxis.scale(d.low) + offset.top;
          const isUp = d.close >= d.open;
          const color = isUp ? '#16A34A' : '#DC2626';
          const bodyY = Math.min(open, close);
          const bodyH = Math.max(1, Math.abs(close - open));

          return (
            <g key={`${d.time}-${index}`}>
              <line x1={x} x2={x} y1={high} y2={low} stroke={color} strokeWidth={1} />
              <rect
                x={x - candleWidth / 2}
                y={bodyY}
                width={candleWidth}
                height={bodyH}
                fill={color}
                stroke={color}
              />
            </g>
          );
        })}
      </g>
    );
  };

  const CandleTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;
    const data = payload[0]?.payload;
    if (!data) return null;
    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow p-3 text-sm">
        <div className="font-semibold mb-1">{formatChartDate(label)}</div>
        <div>Open: ${data.open.toFixed(2)}</div>
        <div>High: ${data.high.toFixed(2)}</div>
        <div>Low: ${data.low.toFixed(2)}</div>
        <div>Close: ${data.close.toFixed(2)}</div>
      </div>
    );
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
                  <div>
                    <div className="font-bold text-gray-900">{stock.name}</div>
                    <div className="text-xs text-gray-500">{stock.symbol}</div>
                  </div>
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
                  <div>
                    <div className="font-bold text-gray-900">{stock.name}</div>
                    <div className="text-xs text-gray-500">{stock.symbol}</div>
                  </div>
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
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">{result.name}</h3>
                        <p className="text-sm text-gray-500">{result.symbol}</p>
                      </div>
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
                      
                      {result.spread !== null && result.spread !== undefined && (
                        <div className="flex items-center gap-1 text-blue-600">
                          <span className="text-gray-500">Spread:</span>
                          <span className="font-medium">${result.spread?.toFixed(4)} ({result.spread_percent?.toFixed(3)}%)</span>
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
                      onClick={() => openChart(result.symbol)}
                      className="px-4 py-2 bg-gray-900 text-white rounded-lg font-semibold hover:bg-gray-800 transition"
                      title="Chart öffnen"
                    >
                      Chart
                    </button>
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
          <div className="bg-white text-gray-900 rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-4">
              {orderData.side === 'buy' ? '🟢 Buy' : '🔴 Sell'} {getCompanyName(selectedSymbol)} ({selectedSymbol})
            </h2>
            
            {/* Quote Info */}
            {loadingQuote ? (
              <div className="bg-gray-100 rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-600">Lade Preisinformationen...</p>
              </div>
            ) : quote ? (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600 font-medium">Bid (Verkauf)</p>
                    <p className="text-lg font-bold text-red-600">${quote.bid.toFixed(2)}</p>
                    <p className="text-xs text-gray-500">{quote.bid_size} Stück</p>
                  </div>
                  <div>
                    <p className="text-gray-600 font-medium">Ask (Kauf)</p>
                    <p className="text-lg font-bold text-green-600">${quote.ask.toFixed(2)}</p>
                    <p className="text-xs text-gray-500">{quote.ask_size} Stück</p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-blue-200">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-600">Spread:</span>
                    <span className="font-semibold text-gray-900">
                      ${quote.spread.toFixed(4)} ({quote.spread_percent.toFixed(3)}%)
                    </span>
                  </div>
                </div>
                <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded">
                  <p className="text-xs text-yellow-800">
                    💡 Bei Market Order zahlst du ca. <strong>${orderData.side === 'buy' ? quote.ask.toFixed(2) : quote.bid.toFixed(2)}</strong>
                  </p>
                </div>
              </div>
            ) : null}
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                <input
                  type="number"
                  value={orderData.quantity}
                  onChange={(e) => setOrderData({ ...orderData, quantity: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
                  min="1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Order Type</label>
                <select
                  value={orderData.order_type}
                  onChange={(e) => setOrderData({ ...orderData, order_type: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
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
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900"
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

      {/* Chart Modal */}
      {showChartModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold">{getCompanyName(chartSymbol)} ({chartSymbol})</h2>
                <p className="text-sm text-gray-500">{chartDays} Tage • {chartTimeframe}</p>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <select
                    value={chartTimeframe}
                    onChange={(e) => {
                      const value = e.target.value;
                      setChartTimeframe(value);
                      if (chartSymbol) {
                        loadChartData(chartSymbol, value, chartDays);
                      }
                    }}
                    className="px-2 py-1 border border-gray-300 rounded text-sm bg-white text-gray-900"
                  >
                    <option value="1S">1s</option>
                    <option value="1D">1D</option>
                    <option value="1H">1H</option>
                    <option value="1Min">1Min</option>
                    <option value="1M">1M</option>
                  </select>
                  <select
                    value={chartDays}
                    onChange={(e) => {
                      const value = parseInt(e.target.value, 10);
                      setChartDays(value);
                      setChartStartDate('');
                      setChartEndDate('');
                      if (chartSymbol) {
                        loadChartData(chartSymbol, chartTimeframe, value);
                      }
                    }}
                    className="px-2 py-1 border border-gray-300 rounded text-sm bg-white text-gray-900"
                  >
                    <option value={1}>1 Tag</option>
                    <option value={7}>1 Woche</option>
                    <option value={30}>1 Monat</option>
                    <option value={90}>90 Tage</option>
                    <option value={180}>180 Tage</option>
                    <option value={365}>1 Jahr</option>
                    <option value={1825}>5 Jahre</option>
                    <option value={3650}>10 Jahre</option>
                  </select>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="date"
                    value={chartStartDate}
                    onChange={(e) => {
                      const value = e.target.value;
                      setChartStartDate(value);
                      const days = calculateDaysBetween(value, chartEndDate);
                      if (days && chartSymbol) {
                        setChartDays(days);
                        loadChartData(chartSymbol, chartTimeframe, days);
                      }
                    }}
                    className="px-2 py-1 border border-gray-300 rounded text-sm bg-white text-gray-900"
                  />
                  <span className="text-sm text-gray-500">bis</span>
                  <input
                    type="date"
                    value={chartEndDate}
                    onChange={(e) => {
                      const value = e.target.value;
                      setChartEndDate(value);
                      const days = calculateDaysBetween(chartStartDate, value);
                      if (days && chartSymbol) {
                        setChartDays(days);
                        loadChartData(chartSymbol, chartTimeframe, days);
                      }
                    }}
                    className="px-2 py-1 border border-gray-300 rounded text-sm bg-white text-gray-900"
                  />
                </div>
                <div className="flex rounded-lg border border-gray-300 overflow-hidden">
                  <button
                    onClick={() => setChartType('line')}
                    className={`px-3 py-1 text-sm ${chartType === 'line' ? 'bg-gray-900 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
                  >
                    Line
                  </button>
                  <button
                    onClick={() => setChartType('candlestick')}
                    className={`px-3 py-1 text-sm ${chartType === 'candlestick' ? 'bg-gray-900 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}
                  >
                    Candlestick
                  </button>
                </div>
                <button
                  onClick={() => setShowChartModal(false)}
                  className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 bg-white text-gray-900"
                >
                  Schließen
                </button>
              </div>
            </div>

            {chartLoading ? (
              <div className="h-64 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : chartError ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                {chartError}
              </div>
            ) : chartData.length > 0 ? (
              <div className="h-96">
                <ResponsiveContainer width="100%" height="100%">
                  {chartType === 'line' ? (
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="time" tickFormatter={formatChartDate} />
                      <YAxis domain={['auto', 'auto']} />
                      <Tooltip
                        labelFormatter={(value) => formatChartDate(value)}
                        formatter={(value) => [`$${parseFloat(value).toFixed(2)}`, 'Close']}
                      />
                      <Line type="monotone" dataKey="close" stroke="#2563EB" strokeWidth={2} dot={false} />
                    </LineChart>
                  ) : (
                    <ComposedChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" tickFormatter={formatChartDate} />
                      <YAxis domain={['auto', 'auto']} />
                      <Tooltip content={<CandleTooltip />} />
                      <Customized component={<Candlestick />} />
                    </ComposedChart>
                  )}
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-gray-600">
                Keine Chart-Daten verfügbar.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
