import { useState, useEffect } from 'react';
import { Play, RefreshCw, TrendingUp, Award, Zap, Target } from 'lucide-react';
import api from '../services/api';

export default function GrowthScanner() {
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState([]);
  const [scanStats, setScanStats] = useState(null);
  const [minScore, setMinScore] = useState(40);
  const [customSymbols, setCustomSymbols] = useState('');
  const [error, setError] = useState(null);

  const runScan = async () => {
    setScanning(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        min_score: minScore,
        max_results: 20
      });
      
      if (customSymbols.trim()) {
        params.append('symbols', customSymbols);
      }
      
      const response = await api.get(`/scanner/scan?${params}`);
      
      setResults(response.data.results);
      setScanStats({
        scan_time: response.data.scan_time,
        total_scanned: response.data.total_scanned,
        matches_found: response.data.matches_found
      });
    } catch (err) {
      console.error('Scanner error:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Scanner Fehler';
      setError(errorMsg);
    } finally {
      setScanning(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 75) return 'text-blue-600 bg-blue-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-gray-600 bg-gray-100';
  };

  const getScoreEmoji = (score) => {
    if (score >= 90) return '🚀';
    if (score >= 75) return '⭐';
    if (score >= 60) return '📈';
    return '📊';
  };

  const formatNumber = (num) => {
    if (!num) return 'N/A';
    return num > 0 ? `+${num.toFixed(1)}%` : `${num.toFixed(1)}%`;
  };

  const formatMarketCap = (mc) => {
    if (!mc) return 'N/A';
    if (mc >= 1e12) return `$${(mc / 1e12).toFixed(1)}T`;
    if (mc >= 1e9) return `$${(mc / 1e9).toFixed(1)}B`;
    if (mc >= 1e6) return `$${(mc / 1e6).toFixed(1)}M`;
    return `$${mc.toFixed(0)}`;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Growth Stock Scanner</h1>
          <p className="text-gray-600 mt-1">Finde die nächste NVIDIA - Stocks mit 10x-100x Potenzial 🚀</p>
        </div>
        <button
          onClick={runScan}
          disabled={scanning}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 shadow-lg"
        >
          {scanning ? (
            <>
              <RefreshCw className="w-5 h-5 animate-spin" />
              Scanning...
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              Start Scan
            </>
          )}
        </button>
      </div>

      {/* Scan Configuration */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold mb-4">Scan Konfiguration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Min. Growth Score ({minScore})
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={minScore}
              onChange={(e) => setMinScore(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0 (Alle)</span>
              <span>50 (OK)</span>
              <span>100 (Top)</span>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Spezifische Symbole (optional)
            </label>
            <input
              type="text"
              value={customSymbols}
              onChange={(e) => setCustomSymbols(e.target.value)}
              placeholder="z.B. PLTR,IONQ,ARM,TSLA"
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Leer lassen für komplettes Universe (~50 Stocks)</p>
          </div>
        </div>
      </div>

      {/* Scan Stats */}
      {scanStats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Total Gescannt</p>
                <p className="text-3xl font-bold mt-1">{scanStats.total_scanned}</p>
              </div>
              <Target className="w-12 h-12 text-blue-200" />
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Matches Gefunden</p>
                <p className="text-3xl font-bold mt-1">{scanStats.matches_found}</p>
              </div>
              <Award className="w-12 h-12 text-green-200" />
            </div>
          </div>
          
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Scan Zeit</p>
                <p className="text-3xl font-bold mt-1">{new Date(scanStats.scan_time).toLocaleTimeString()}</p>
              </div>
              <Zap className="w-12 h-12 text-purple-200" />
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium">⚠️ {error}</p>
          {error.includes('nicht verbunden') && (
            <p className="text-red-600 text-sm mt-2">
              💡 Gehe zur <a href="/configuration" className="underline font-semibold">Configuration</a> Seite und verbinde zuerst deinen Broker.
            </p>
          )}
        </div>
      )}

      {/* Results Table */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 bg-gradient-to-r from-gray-50 to-gray-100 border-b">
            <h2 className="text-xl font-bold text-gray-900">
              Growth Stock Kandidaten ({results.length})
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Sortiert nach Growth Score - Höhere Scores = Höheres Potenzial
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b-2 border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    30D Change
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rel. Strength
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Revenue Growth
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    News Sentiment
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sektor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Grund
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {results.map((stock, index) => (
                  <tr key={stock.symbol} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{index < 3 ? ['🥇', '🥈', '🥉'][index] : '📊'}</span>
                        <span className="text-gray-900 font-medium">#{index + 1}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-lg font-bold text-blue-600">{stock.symbol}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{getScoreEmoji(stock.score)}</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-bold ${getScoreColor(stock.score)}`}>
                          {stock.score.toFixed(1)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`font-semibold ${stock.price_change_30d > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatNumber(stock.price_change_30d)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`font-semibold ${stock.relative_strength > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatNumber(stock.relative_strength)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-purple-600 font-semibold">
                        {formatNumber(stock.revenue_growth)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {stock.news_score !== null && stock.news_score !== undefined ? (
                        <div className="flex items-center gap-1">
                          <span className="text-xl">
                            {stock.news_score > 70 ? '🚀' : stock.news_score > 50 ? '📈' : stock.news_score < 40 ? '📉' : '➡️'}
                          </span>
                          <span className={`font-semibold ${
                            stock.news_score > 60 ? 'text-green-600' : 
                            stock.news_score < 40 ? 'text-red-600' : 
                            'text-gray-600'
                          }`}>
                            {stock.news_score.toFixed(0)}
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">N/A</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-full font-medium">
                        {stock.sector || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-600 max-w-xs truncate" title={stock.reason}>
                        {stock.reason || 'Growth candidate'}
                      </p>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!scanning && results.length === 0 && !error && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Bereit zum Scannen</h3>
          <p className="text-gray-600 mb-6">
            Klicke auf "Start Scan" um Growth Stocks mit Moonshot-Potenzial zu finden
          </p>
          <div className="bg-blue-50 rounded-lg p-4 max-w-2xl mx-auto text-left">
            <h4 className="font-semibold text-blue-900 mb-2">💡 Was der Scanner findet:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>AI Infrastructure:</strong> PLTR, AI, SNOW</li>
              <li>• <strong>Quantum Computing:</strong> IONQ, RGTI</li>
              <li>• <strong>Semiconductors:</strong> ARM, ASML, MRVL</li>
              <li>• <strong>Robotics:</strong> TSLA, RIVN, JOBY</li>
              <li>• <strong>Biotech:</strong> CRSP, EDIT, BEAM</li>
              <li>• <strong>Space:</strong> RKLB, ASTS</li>
            </ul>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <div className="text-3xl">💡</div>
          <div>
            <h3 className="font-bold text-amber-900 mb-2">Wie funktioniert der Scanner?</h3>
            <p className="text-amber-800 text-sm mb-3">
              Der Growth Stock Scanner analysiert Aktien nach dem "NVIDIA-Prinzip" - findet Unternehmen mit 
              explosivem Wachstum in Zukunftsmärkten.
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div className="bg-white rounded p-2">
                <div className="font-bold text-amber-900">30%</div>
                <div className="text-amber-700">Revenue Growth</div>
              </div>
              <div className="bg-white rounded p-2">
                <div className="font-bold text-amber-900">25%</div>
                <div className="text-amber-700">Relative Strength</div>
              </div>
              <div className="bg-white rounded p-2">
                <div className="font-bold text-amber-900">20%</div>
                <div className="text-amber-700">Momentum</div>
              </div>
              <div className="bg-white rounded p-2">
                <div className="font-bold text-amber-900">25%</div>
                <div className="text-amber-700">Volume + Sektor</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
