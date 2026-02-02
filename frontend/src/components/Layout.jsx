import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Settings, 
  TrendingUp, 
  ShoppingCart, 
  Sliders,
  Play,
  Square,
  Wifi,
  WifiOff,
  History,
  Rocket,
  Clock,
  Newspaper,
  PieChart,
  Search
} from 'lucide-react';
import clsx from 'clsx';

const Layout = ({ children, botStatus, onStartBot, onStopBot, accountData }) => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Symbol Suche', href: '/symbols', icon: Search },
    { name: 'Growth Scanner', href: '/scanner', icon: Rocket },
    { name: 'Portfolio 70/30', href: '/portfolio', icon: PieChart },
    { name: 'Backtesting', href: '/backtest', icon: Clock },
    { name: 'News Feed', href: '/news', icon: Newspaper },
    { name: 'Konfiguration', href: '/configuration', icon: Settings },
    { name: 'Strategien', href: '/strategies', icon: TrendingUp },
    { name: 'Orders', href: '/orders', icon: ShoppingCart },
    { name: 'Trade History', href: '/history', icon: History },
    { name: 'Einstellungen', href: '/settings', icon: Sliders },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="bg-gray-800/40 backdrop-blur-xl shadow-2xl border-b border-gray-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-glow">
                <span className="text-2xl">💰</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold glow-text">
                  TheMoneyBroker
                </h1>
                <p className="text-xs text-gray-400">Automated Trading Bot</p>
              </div>
            </div>

            {/* Status Indicators */}
            <div className="flex items-center space-x-6">
              {/* Connection Status */}
              <div className="flex items-center space-x-2 px-3 py-2 bg-gray-700/30 rounded-lg backdrop-blur-sm">
                {botStatus.connected ? (
                  <>
                    <Wifi className="w-5 h-5 text-green-400 animate-pulse" />
                    <span className="text-sm text-gray-200 font-medium">Verbunden</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="w-5 h-5 text-red-400" />
                    <span className="text-sm text-gray-400">Getrennt</span>
                  </>
                )}
              </div>

              {/* Portfolio Value */}
              {accountData && (
                <div className="px-4 py-2 bg-gradient-to-r from-primary-600/20 to-emerald-600/20 rounded-lg border border-primary-500/30">
                  <div className="text-xs text-gray-400">Portfolio</div>
                  <div className="text-lg font-bold text-primary-400">
                    ${accountData.portfolio_value?.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                  </div>
                </div>
              )}

              {/* Bot Control */}
              {botStatus.connected && (
                <div>
                  {botStatus.running ? (
                    <button
                      onClick={onStopBot}
                      className="flex items-center space-x-2 btn btn-danger"
                    >
                      <Square className="w-4 h-4 fill-current" />
                      <span>Stop Bot</span>
                    </button>
                  ) : (
                    <button
                      onClick={onStartBot}
                      className="flex items-center space-x-2 btn btn-success"
                      disabled={!botStatus.has_risk_manager}
                    >
                      <Play className="w-4 h-4 fill-current" />
                      <span>Start Bot</span>
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="w-72 bg-gray-800/20 backdrop-blur-xl border-r border-gray-700/50">
          <nav className="mt-8 px-4 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'group flex items-center px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-200',
                    isActive
                      ? 'bg-gradient-to-r from-primary-600/20 to-emerald-600/20 text-primary-400 border border-primary-500/30 shadow-lg'
                      : 'text-gray-400 hover:bg-gray-700/30 hover:text-gray-200'
                  )}
                >
                  <Icon
                    className={clsx(
                      'mr-3 flex-shrink-0 h-5 w-5 transition-transform group-hover:scale-110',
                      isActive
                        ? 'text-primary-400'
                        : 'text-gray-500 group-hover:text-primary-400'
                    )}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Bot Status Card */}
          <div className="mt-8 mx-4 p-5 card-glass">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 flex items-center">
              <div className="w-2 h-2 bg-primary-500 rounded-full mr-2 animate-pulse"></div>
              Bot Status
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Status</span>
                <span className={clsx(
                  'text-sm font-bold px-3 py-1 rounded-lg',
                  botStatus.running 
                    ? 'text-green-400 bg-green-500/20' 
                    : 'text-gray-400 bg-gray-700/30'
                )}>
                  {botStatus.running ? '🟢 Aktiv' : '⚪ Inaktiv'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Strategien</span>
                <span className="text-sm font-bold text-primary-400 bg-primary-500/20 px-3 py-1 rounded-lg">
                  {botStatus.strategies_count}
                </span>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10 py-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
