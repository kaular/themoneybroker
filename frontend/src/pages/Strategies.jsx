import { useState, useEffect } from 'react';
import { Plus, TrendingUp, Settings as SettingsIcon, ToggleLeft, ToggleRight } from 'lucide-react';
import api from '../services/api';

const Strategies = () => {
  const [strategies, setStrategies] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const response = await api.getStrategies();
      setStrategies(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Fehler beim Laden der Strategien:', error);
      setLoading(false);
    }
  };

  const handleAddStrategy = async (strategyData) => {
    try {
      await api.addStrategy(strategyData);
      await fetchStrategies();
      setShowAddModal(false);
    } catch (error) {
      console.error('Fehler beim Hinzufügen der Strategie:', error);
      alert('Fehler: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Trading-Strategien</h2>
          <p className="text-gray-600 mt-1">Verwalten Sie Ihre automatischen Trading-Strategien</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Strategie hinzufügen</span>
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : strategies.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {strategies.map((strategy, index) => (
            <StrategyCard key={index} strategy={strategy} />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Keine Strategien</h3>
          <p className="text-gray-600 mb-4">
            Fügen Sie Ihre erste Trading-Strategie hinzu, um zu beginnen.
          </p>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn btn-primary inline-flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Strategie hinzufügen</span>
          </button>
        </div>
      )}

      {showAddModal && (
        <AddStrategyModal
          onClose={() => setShowAddModal(false)}
          onAdd={handleAddStrategy}
        />
      )}
    </div>
  );
};

const StrategyCard = ({ strategy }) => {
  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-50 rounded-lg">
            <TrendingUp className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{strategy.name}</h3>
            <p className="text-sm text-gray-600">SMA Crossover</p>
          </div>
        </div>
        {strategy.enabled ? (
          <ToggleRight className="w-8 h-8 text-green-600" />
        ) : (
          <ToggleLeft className="w-8 h-8 text-gray-400" />
        )}
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Kurzer Zeitraum:</span>
          <span className="font-medium text-gray-900">
            {strategy.parameters?.short_window || 20} Tage
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Langer Zeitraum:</span>
          <span className="font-medium text-gray-900">
            {strategy.parameters?.long_window || 50} Tage
          </span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <button className="btn btn-secondary flex-1 text-sm">
            <SettingsIcon className="w-4 h-4 inline mr-1" />
            Bearbeiten
          </button>
          <button className="btn btn-danger flex-1 text-sm">
            Entfernen
          </button>
        </div>
      </div>
    </div>
  );
};

const AddStrategyModal = ({ onClose, onAdd }) => {
  const [formData, setFormData] = useState({
    name: 'SMA Crossover',
    type: 'sma',
    short_window: 20,
    long_window: 50,
    enabled: true
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onAdd({
      name: formData.name,
      type: formData.type,
      parameters: {
        short_window: parseInt(formData.short_window),
        long_window: parseInt(formData.long_window)
      },
      enabled: formData.enabled
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Strategie hinzufügen</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Name</label>
              <input
                type="text"
                className="input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="label">Strategie-Typ</label>
              <select
                className="input"
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              >
                <option value="sma">SMA Crossover</option>
              </select>
            </div>

            <div>
              <label className="label">Kurzer Zeitraum (Tage)</label>
              <input
                type="number"
                className="input"
                value={formData.short_window}
                onChange={(e) => setFormData({ ...formData, short_window: e.target.value })}
                min="5"
                max="100"
                required
              />
            </div>

            <div>
              <label className="label">Langer Zeitraum (Tage)</label>
              <input
                type="number"
                className="input"
                value={formData.long_window}
                onChange={(e) => setFormData({ ...formData, long_window: e.target.value })}
                min="10"
                max="200"
                required
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="enabled"
                checked={formData.enabled}
                onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                className="mr-2"
              />
              <label htmlFor="enabled" className="text-sm text-gray-700">
                Strategie aktivieren
              </label>
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
                Hinzufügen
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Strategies;
