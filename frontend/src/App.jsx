import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Configuration from './pages/Configuration';
import Strategies from './pages/Strategies';
import Orders from './pages/Orders';
import Settings from './pages/Settings';
import TradeHistory from './pages/TradeHistory';
import GrowthScanner from './pages/GrowthScanner';
import HybridPortfolio from './pages/HybridPortfolio';
import Backtesting from './pages/Backtesting';
import api from './services/api';
import wsService from './services/websocket';

function App() {
  const [botStatus, setBotStatus] = useState({
    running: false,
    connected: false,
    strategies_count: 0,
    has_risk_manager: false
  });

  const [accountData, setAccountData] = useState(null);

  useEffect(() => {
    // Hole initialen Bot-Status
    fetchBotStatus();

    // WebSocket verbinden
    wsService.connect();

    // WebSocket Event Listeners
    wsService.on('update', (data) => {
      if (data.data && data.data.account) {
        setAccountData(data.data.account);
      }
    });

    wsService.on('bot_started', () => {
      setBotStatus(prev => ({ ...prev, running: true }));
    });

    wsService.on('bot_stopped', () => {
      setBotStatus(prev => ({ ...prev, running: false }));
    });

    wsService.on('broker_connected', () => {
      setBotStatus(prev => ({ ...prev, connected: true }));
      fetchBotStatus();
    });

    wsService.on('broker_disconnected', () => {
      setBotStatus(prev => ({ ...prev, connected: false }));
    });

    return () => {
      wsService.disconnect();
    };
  }, []);

  const fetchBotStatus = async () => {
    try {
      const response = await api.getBotStatus();
      setBotStatus(response.data);
    } catch (error) {
      console.error('Fehler beim Laden des Bot-Status:', error);
    }
  };

  const handleStartBot = async () => {
    try {
      await api.startBot();
      setBotStatus(prev => ({ ...prev, running: true }));
    } catch (error) {
      console.error('Fehler beim Starten des Bots:', error);
      alert('Fehler beim Starten: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleStopBot = async () => {
    try {
      await api.stopBot();
      setBotStatus(prev => ({ ...prev, running: false }));
    } catch (error) {
      console.error('Fehler beim Stoppen des Bots:', error);
    }
  };

  return (
    <Router>
      <Layout 
        botStatus={botStatus} 
        onStartBot={handleStartBot}
        onStopBot={handleStopBot}
        accountData={accountData}
      >
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard accountData={accountData} />} />
          <Route path="/scanner" element={<GrowthScanner />} />
          <Route path="/portfolio" element={<HybridPortfolio />} />
          <Route path="/backtest" element={<Backtesting />} />
          <Route path="/configuration" element={<Configuration />} />
          <Route path="/strategies" element={<Strategies />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/history" element={<TradeHistory />} />
          <Route path="/settings" element={<Settings botStatus={botStatus} />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
