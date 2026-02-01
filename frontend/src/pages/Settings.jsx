import { useState } from 'react';
import { Wifi, Key, Server } from 'lucide-react';
import api from '../services/api';

const Settings = ({ botStatus }) => {
  const [brokerConfig, setBrokerConfig] = useState({
    api_key: '',
    api_secret: '',
    base_url: 'https://paper-api.alpaca.markets'
  });

  const [connecting, setConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState(null);

  const handleConnect = async (e) => {
    e.preventDefault();
    setConnecting(true);
    setConnectionStatus(null);

    try {
      const response = await api.connectBroker(brokerConfig);
      setConnectionStatus({ success: true, message: 'Erfolgreich verbunden!', data: response.data });
    } catch (error) {
      setConnectionStatus({ 
        success: false, 
        message: error.response?.data?.detail || 'Verbindung fehlgeschlagen'
      });
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await api.disconnectBroker();
      setConnectionStatus({ success: true, message: 'Verbindung getrennt' });
    } catch (error) {
      console.error('Fehler beim Trennen:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Einstellungen</h2>
        <p className="text-gray-600 mt-1">Broker-Verbindung und System-Konfiguration</p>
      </div>

      {/* Broker Connection */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-primary-50 rounded-lg">
            <Wifi className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Broker-Verbindung</h3>
            <p className="text-sm text-gray-600">Alpaca Trading API Konfiguration</p>
          </div>
        </div>

        {/* Connection Status */}
        {botStatus.connected && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-green-900">✓ Verbunden</p>
                <p className="text-sm text-green-700">Broker-Verbindung ist aktiv</p>
              </div>
              <button
                onClick={handleDisconnect}
                className="btn btn-danger"
              >
                Trennen
              </button>
            </div>
          </div>
        )}

        {!botStatus.connected && (
          <form onSubmit={handleConnect} className="space-y-4">
            <div>
              <label className="label">
                <Key className="w-4 h-4 inline mr-1" />
                API Key
              </label>
              <input
                type="password"
                className="input font-mono"
                value={brokerConfig.api_key}
                onChange={(e) => setBrokerConfig({ ...brokerConfig, api_key: e.target.value })}
                placeholder="PK..."
                required
              />
            </div>

            <div>
              <label className="label">
                <Key className="w-4 h-4 inline mr-1" />
                API Secret
              </label>
              <input
                type="password"
                className="input font-mono"
                value={brokerConfig.api_secret}
                onChange={(e) => setBrokerConfig({ ...brokerConfig, api_secret: e.target.value })}
                placeholder="..."
                required
              />
            </div>

            <div>
              <label className="label">
                <Server className="w-4 h-4 inline mr-1" />
                Base URL
              </label>
              <select
                className="input"
                value={brokerConfig.base_url}
                onChange={(e) => setBrokerConfig({ ...brokerConfig, base_url: e.target.value })}
              >
                <option value="https://paper-api.alpaca.markets">Paper Trading</option>
                <option value="https://api.alpaca.markets">Live Trading ⚠️</option>
              </select>
              <p className="mt-1 text-sm text-gray-500">
                Verwenden Sie Paper Trading zum Testen!
              </p>
            </div>

            {connectionStatus && (
              <div className={`p-4 rounded-lg ${
                connectionStatus.success 
                  ? 'bg-green-50 border border-green-200' 
                  : 'bg-red-50 border border-red-200'
              }`}>
                <p className={`font-medium ${
                  connectionStatus.success ? 'text-green-900' : 'text-red-900'
                }`}>
                  {connectionStatus.message}
                </p>
                {connectionStatus.data?.account && (
                  <div className="mt-2 text-sm text-green-800 space-y-1">
                    <p>Portfolio: ${connectionStatus.data.account.portfolio_value.toLocaleString()}</p>
                    <p>Bargeld: ${connectionStatus.data.account.cash.toLocaleString()}</p>
                  </div>
                )}
              </div>
            )}

            <button
              type="submit"
              disabled={connecting}
              className="btn btn-primary w-full"
            >
              {connecting ? 'Verbinde...' : 'Mit Broker verbinden'}
            </button>
          </form>
        )}
      </div>

      {/* API Keys Info */}
      <div className="card bg-blue-50 border border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-3">📚 API Keys erhalten</h4>
        <div className="text-sm text-blue-800 space-y-2">
          <p>1. Erstellen Sie einen Account bei <a href="https://alpaca.markets" target="_blank" rel="noopener noreferrer" className="underline">alpaca.markets</a></p>
          <p>2. Navigieren Sie zu "Paper Trading"</p>
          <p>3. Generieren Sie Ihre API Keys</p>
          <p>4. Verwenden Sie die Paper Trading URL für Tests</p>
        </div>
      </div>

      {/* Security Warning */}
      <div className="card bg-yellow-50 border border-yellow-200">
        <h4 className="font-semibold text-yellow-900 mb-2">🔒 Sicherheitshinweise</h4>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>• API Keys werden nur im Browser gespeichert</li>
          <li>• Niemals API Keys mit anderen teilen</li>
          <li>• Verwenden Sie immer Paper Trading zum Testen</li>
          <li>• Beschränken Sie API-Berechtigungen auf Trading</li>
        </ul>
      </div>
    </div>
  );
};

export default Settings;
