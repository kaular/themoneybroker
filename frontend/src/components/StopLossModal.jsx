import { useState } from 'react';
import { Shield, Target, TrendingUp, X } from 'lucide-react';
import api from '../services/api';

const StopLossModal = ({ position, onClose, onSuccess }) => {
  const [config, setConfig] = useState({
    stopType: 'percentage',
    stopPrice: '',
    stopPercentage: '2',
    trailingPercentage: '',
    takeProfitPrice: '',
    takeProfitPercentage: '5'
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      // Set Stop-Loss
      const stopLossData = {
        symbol: position.symbol,
        stop_type: config.stopType,
        stop_price: config.stopPrice ? parseFloat(config.stopPrice) : null,
        stop_percentage: config.stopPercentage ? parseFloat(config.stopPercentage) : null,
        trailing_percentage: config.trailingPercentage ? parseFloat(config.trailingPercentage) : null,
        entry_price: parseFloat(position.avg_entry_price)
      };

      await api.setStopLoss(stopLossData);

      // Set Take-Profit if provided
      if (config.takeProfitPrice || config.takeProfitPercentage) {
        const takeProfitData = {
          symbol: position.symbol,
          take_profit_price: config.takeProfitPrice ? parseFloat(config.takeProfitPrice) : null,
          take_profit_percentage: config.takeProfitPercentage ? parseFloat(config.takeProfitPercentage) : null
        };
        await api.setTakeProfit(takeProfitData);
      }

      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('Fehler beim Setzen von Stop-Loss/Take-Profit:', error);
      alert('Fehler: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
    }
  };

  const calculateStopPrice = () => {
    if (!config.stopPercentage || !position.avg_entry_price) return '-';
    const entryPrice = parseFloat(position.avg_entry_price);
    const stopPercent = parseFloat(config.stopPercentage) / 100;
    return (entryPrice * (1 - stopPercent)).toFixed(2);
  };

  const calculateTakeProfitPrice = () => {
    if (!config.takeProfitPercentage || !position.avg_entry_price) return '-';
    const entryPrice = parseFloat(position.avg_entry_price);
    const tpPercent = parseFloat(config.takeProfitPercentage) / 100;
    return (entryPrice * (1 + tpPercent)).toFixed(2);
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-2xl shadow-2xl border border-gray-700 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div>
            <h3 className="text-xl font-bold text-white">Stop-Loss & Take-Profit</h3>
            <p className="text-sm text-gray-400 mt-1">{position.symbol} - {position.qty} Shares @ ${parseFloat(position.avg_entry_price).toFixed(2)}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Stop-Loss Section */}
          <div className="card-glass">
            <div className="flex items-center space-x-3 mb-4">
              <Shield className="w-5 h-5 text-red-400" />
              <h4 className="text-lg font-semibold text-white">Stop-Loss</h4>
            </div>

            {/* Stop Type */}
            <div className="mb-4">
              <label className="label">Stop-Loss Typ</label>
              <select
                value={config.stopType}
                onChange={(e) => setConfig({ ...config, stopType: e.target.value })}
                className="input"
              >
                <option value="percentage">Prozentual</option>
                <option value="fixed">Fester Preis</option>
                <option value="trailing">Trailing Stop</option>
              </select>
            </div>

            {/* Percentage Stop */}
            {config.stopType === 'percentage' && (
              <div>
                <label className="label">Stop-Loss Prozent (%)</label>
                <input
                  type="number"
                  step="0.1"
                  value={config.stopPercentage}
                  onChange={(e) => setConfig({ ...config, stopPercentage: e.target.value })}
                  className="input"
                  placeholder="z.B. 2"
                />
                <p className="text-sm text-gray-500 mt-2">
                  Stop-Preis: ${calculateStopPrice()}
                </p>
              </div>
            )}

            {/* Fixed Stop */}
            {config.stopType === 'fixed' && (
              <div>
                <label className="label">Stop-Loss Preis ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={config.stopPrice}
                  onChange={(e) => setConfig({ ...config, stopPrice: e.target.value })}
                  className="input"
                  placeholder={`z.B. ${(parseFloat(position.avg_entry_price) * 0.98).toFixed(2)}`}
                />
              </div>
            )}

            {/* Trailing Stop */}
            {config.stopType === 'trailing' && (
              <div>
                <label className="label">Trailing Prozent (%)</label>
                <input
                  type="number"
                  step="0.1"
                  value={config.trailingPercentage}
                  onChange={(e) => setConfig({ ...config, trailingPercentage: e.target.value })}
                  className="input"
                  placeholder="z.B. 3"
                />
                <p className="text-sm text-gray-400 mt-2">
                  💡 Stop-Loss folgt dem Preis mit {config.trailingPercentage || '0'}% Abstand
                </p>
              </div>
            )}
          </div>

          {/* Take-Profit Section */}
          <div className="card-glass">
            <div className="flex items-center space-x-3 mb-4">
              <Target className="w-5 h-5 text-green-400" />
              <h4 className="text-lg font-semibold text-white">Take-Profit</h4>
            </div>

            <div className="space-y-4">
              <div>
                <label className="label">Take-Profit Prozent (%) - Optional</label>
                <input
                  type="number"
                  step="0.1"
                  value={config.takeProfitPercentage}
                  onChange={(e) => setConfig({ ...config, takeProfitPercentage: e.target.value })}
                  className="input"
                  placeholder="z.B. 5"
                />
                <p className="text-sm text-gray-500 mt-2">
                  Take-Profit Preis: ${calculateTakeProfitPrice()}
                </p>
              </div>

              <div>
                <label className="label">Take-Profit Preis ($) - Optional</label>
                <input
                  type="number"
                  step="0.01"
                  value={config.takeProfitPrice}
                  onChange={(e) => setConfig({ ...config, takeProfitPrice: e.target.value })}
                  className="input"
                  placeholder={`z.B. ${(parseFloat(position.avg_entry_price) * 1.05).toFixed(2)}`}
                />
              </div>
            </div>
          </div>

          {/* Risk/Reward Info */}
          <div className="bg-primary-500/10 border border-primary-500/30 rounded-xl p-4">
            <div className="flex items-start space-x-3">
              <TrendingUp className="w-5 h-5 text-primary-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-primary-400 mb-1">Risk/Reward Ratio</p>
                <p className="text-xs text-gray-400">
                  {config.stopPercentage && config.takeProfitPercentage ? (
                    <>
                      Risiko: {config.stopPercentage}% | Gewinn: {config.takeProfitPercentage}% | 
                      R/R: 1:{(parseFloat(config.takeProfitPercentage) / parseFloat(config.stopPercentage)).toFixed(2)}
                    </>
                  ) : (
                    'Geben Sie Stop-Loss und Take-Profit ein, um das Verhältnis zu sehen'
                  )}
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 btn btn-secondary"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 btn btn-primary"
            >
              {saving ? 'Wird gesetzt...' : 'Stop-Loss/TP setzen'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StopLossModal;
