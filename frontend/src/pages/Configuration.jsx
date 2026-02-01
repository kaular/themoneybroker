import { useState } from 'react';
import { Shield, DollarSign, TrendingUp } from 'lucide-react';
import api from '../services/api';

const Configuration = () => {
  const [riskConfig, setRiskConfig] = useState({
    max_position_size: 10000,
    max_daily_loss: 500,
    max_open_positions: 5,
    risk_per_trade: 0.02
  });

  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(false);

    try {
      await api.configureRisk(riskConfig);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (error) {
      console.error('Fehler beim Speichern:', error);
      alert('Fehler: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setRiskConfig(prev => ({
      ...prev,
      [field]: parseFloat(value) || 0
    }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Konfiguration</h2>
        <p className="text-gray-600 mt-1">Risk Management und Trading-Parameter</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Risk Management */}
        <div className="card">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-red-50 rounded-lg">
              <Shield className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Risk Management</h3>
              <p className="text-sm text-gray-600">Risiko-Limits und Schutzmechanismen</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="label">
                <DollarSign className="w-4 h-4 inline mr-1" />
                Maximale Positionsgröße ($)
              </label>
              <input
                type="number"
                className="input"
                value={riskConfig.max_position_size}
                onChange={(e) => handleChange('max_position_size', e.target.value)}
                step="100"
                min="0"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Maximaler Wert einer einzelnen Position
              </p>
            </div>

            <div>
              <label className="label">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                Maximaler Tagesverlust ($)
              </label>
              <input
                type="number"
                className="input"
                value={riskConfig.max_daily_loss}
                onChange={(e) => handleChange('max_daily_loss', e.target.value)}
                step="10"
                min="0"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Trading wird gestoppt bei diesem Verlust
              </p>
            </div>

            <div>
              <label className="label">Max. Offene Positionen</label>
              <input
                type="number"
                className="input"
                value={riskConfig.max_open_positions}
                onChange={(e) => handleChange('max_open_positions', e.target.value)}
                min="1"
                max="20"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Anzahl gleichzeitig offener Positionen
              </p>
            </div>

            <div>
              <label className="label">Risiko pro Trade (%)</label>
              <input
                type="number"
                className="input"
                value={riskConfig.risk_per_trade * 100}
                onChange={(e) => handleChange('risk_per_trade', e.target.value / 100)}
                step="0.1"
                min="0.1"
                max="10"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Prozentsatz des Kapitals pro Trade
              </p>
            </div>
          </div>
        </div>

        {/* Summary */}
        <div className="card bg-blue-50 border border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-3">Zusammenfassung</h4>
          <div className="space-y-2 text-sm text-blue-800">
            <p>• Maximale Einzelposition: <strong>${riskConfig.max_position_size.toLocaleString()}</strong></p>
            <p>• Tägliches Risiko-Limit: <strong>${riskConfig.max_daily_loss.toLocaleString()}</strong></p>
            <p>• Maximale Positionen: <strong>{riskConfig.max_open_positions}</strong></p>
            <p>• Risiko pro Trade: <strong>{(riskConfig.risk_per_trade * 100).toFixed(1)}%</strong></p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <div>
            {success && (
              <p className="text-green-600 font-medium">
                ✓ Konfiguration erfolgreich gespeichert!
              </p>
            )}
          </div>
          <button
            type="submit"
            disabled={saving}
            className="btn btn-primary"
          >
            {saving ? 'Speichere...' : 'Konfiguration Speichern'}
          </button>
        </div>
      </form>

      {/* Warning */}
      <div className="card bg-yellow-50 border border-yellow-200">
        <h4 className="font-semibold text-yellow-900 mb-2">⚠️ Wichtig</h4>
        <p className="text-sm text-yellow-800">
          Diese Einstellungen sind kritisch für Ihr Risikomanagement. 
          Stellen Sie sicher, dass Sie die Auswirkungen verstehen, bevor Sie den Bot starten.
          Beginnen Sie immer mit kleinen Werten beim Testen.
        </p>
      </div>
    </div>
  );
};

export default Configuration;
