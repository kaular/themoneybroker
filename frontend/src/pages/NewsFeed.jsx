import { useState, useEffect } from 'react';
import { Newspaper, RefreshCw, TrendingUp, TrendingDown, Minus, ExternalLink, Search, Filter, Bell, BellOff, Play, Square } from 'lucide-react';
import api from '../services/api';

const NewsFeed = () => {
  const [loading, setLoading] = useState(false);
  const [articles, setArticles] = useState([]);
  const [sentiment, setSentiment] = useState(null);
  const [filterSymbol, setFilterSymbol] = useState('');
  const [filterSentiment, setFilterSentiment] = useState('all'); // 'all', 'bullish', 'bearish'
  const [hoursBack, setHoursBack] = useState(24);
  const [monitorStatus, setMonitorStatus] = useState({ running: false, stats: null });
  const [monitorConfig, setMonitorConfig] = useState({
    check_interval: 300,
    symbols: '',
    min_confidence: 0.7
  });
  
  useEffect(() => {
    loadNews();
    checkMonitorStatus();
    
    // Poll monitor status every 30 seconds
    const interval = setInterval(checkMonitorStatus, 30000);
    return () => clearInterval(interval);
  }, []);
  
  const loadNews = async (symbols = null) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: 50,
        hours_back: hoursBack
      });
      
      if (symbols) {
        params.append('symbols', symbols);
      }
      
      const response = await api.get(`/news/latest?${params}`);
      setArticles(response.data.articles);
      
      // Calculate sentiment summary
      calculateSentiment(response.data.articles);
    } catch (error) {
      console.error('Failed to load news:', error);
      alert('Failed to load news: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const loadSymbolNews = async (symbol) => {
    if (!symbol) {
      loadNews();
      return;
    }
    
    setLoading(true);
    try {
      const response = await api.get(`/news/symbol/${symbol}?limit=50`);
      setArticles(response.data.articles);
      setSentiment(response.data.sentiment_summary);
    } catch (error) {
      console.error('Failed to load symbol news:', error);
      alert('Failed to load news: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const calculateSentiment = (articlesData) => {
    const withSentiment = articlesData.filter(a => a.sentiment);
    if (withSentiment.length === 0) {
      setSentiment(null);
      return;
    }
    
    const bullish = withSentiment.filter(a => a.sentiment.label === 'bullish').length;
    const bearish = withSentiment.filter(a => a.sentiment.label === 'bearish').length;
    const neutral = withSentiment.filter(a => a.sentiment.label === 'neutral').length;
    
    const avgScore = withSentiment.reduce((sum, a) => sum + a.sentiment.score, 0) / withSentiment.length;
    
    setSentiment({
      overall_sentiment: avgScore > 0.3 ? 'bullish' : avgScore < -0.3 ? 'bearish' : 'neutral',
      sentiment_score: avgScore,
      bullish_count: bullish,
      bearish_count: bearish,
      neutral_count: neutral,
      total_articles: withSentiment.length,
      bullish_pct: (bullish / withSentiment.length) * 100,
      bearish_pct: (bearish / withSentiment.length) * 100
    });
  };
  
  const handleSearch = () => {
    if (filterSymbol.trim()) {
      loadSymbolNews(filterSymbol.trim().toUpperCase());
    } else {
      loadNews();
    }
  };
  
  const checkMonitorStatus = async () => {
    try {
      const response = await api.get('/news/monitor/status');
      setMonitorStatus(response.data);
    } catch (error) {
      console.error('Failed to check monitor status:', error);
    }
  };
  
  const startMonitor = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        check_interval: monitorConfig.check_interval,
        min_confidence: monitorConfig.min_confidence
      });
      
      if (monitorConfig.symbols.trim()) {
        params.append('symbols', monitorConfig.symbols.trim());
      }
      
      await api.post(`/news/monitor/start?${params}`);
      await checkMonitorStatus();
      alert('News Monitor started successfully! You will receive alerts for important news.');
    } catch (error) {
      console.error('Failed to start monitor:', error);
      alert('Failed to start monitor: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const stopMonitor = async () => {
    setLoading(true);
    try {
      await api.post('/news/monitor/stop');
      await checkMonitorStatus();
      alert('News Monitor stopped.');
    } catch (error) {
      console.error('Failed to stop monitor:', error);
      alert('Failed to stop monitor: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  const getSentimentColor = (label) => {
    if (label === 'bullish') return 'text-green-400';
    if (label === 'bearish') return 'text-red-400';
    return 'text-gray-400';
  };
  
  const getSentimentBg = (label) => {
    if (label === 'bullish') return 'bg-green-900/30 border-green-500/30';
    if (label === 'bearish') return 'bg-red-900/30 border-red-500/30';
    return 'bg-gray-900/30 border-gray-500/30';
  };
  
  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000); // seconds
    
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };
  
  const filteredArticles = articles.filter(article => {
    if (filterSentiment === 'all') return true;
    return article.sentiment && article.sentiment.label === filterSentiment;
  });
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold glow-text mb-2">News Feed</h2>
          <p className="text-gray-400">Real-time financial news with AI sentiment analysis</p>
        </div>
        
        <div className="flex gap-3">
          <button 
            onClick={() => handleSearch()}
            disabled={loading}
            className="btn btn-secondary flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          
          {monitorStatus.running ? (
            <button 
              onClick={stopMonitor}
              disabled={loading}
              className="btn bg-red-600 hover:bg-red-700 text-white flex items-center gap-2"
            >
              <Square className="w-4 h-4" />
              Stop Monitor
            </button>
          ) : (
            <button 
              onClick={startMonitor}
              disabled={loading}
              className="btn btn-primary flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Start Monitor
            </button>
          )}
        </div>
      </div>
      
      {/* Monitor Status */}
      {monitorStatus.running && monitorStatus.stats && (
        <div className="glass-card p-4 border border-green-500/30 bg-green-900/10">
          <div className="flex items-center gap-3">
            <Bell className="w-5 h-5 text-green-400 animate-pulse" />
            <div className="flex-1">
              <div className="flex items-center gap-4 text-sm">
                <span className="text-green-400 font-semibold">News Monitor Active</span>
                <span className="text-gray-400">
                  Checking every {monitorStatus.stats.check_interval}s
                </span>
                <span className="text-gray-400">
                  Monitoring: {monitorStatus.stats.monitoring_symbols}
                </span>
                <span className="text-gray-400">
                  Articles seen: {monitorStatus.stats.seen_articles}
                </span>
              </div>
            </div>
            <BellOff className="w-5 h-5 text-gray-400 cursor-pointer hover:text-red-400" onClick={stopMonitor} title="Stop Monitor" />
          </div>
        </div>
      )}
      
      {/* Search & Filters */}
      <div className="glass-card p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Symbol Search */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-400 mb-2">Search Symbol</label>
            <div className="flex gap-2">
              <input 
                type="text"
                value={filterSymbol}
                onChange={(e) => setFilterSymbol(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="e.g., AAPL, TSLA, or leave empty for all"
                className="input flex-1"
              />
              <button onClick={handleSearch} disabled={loading} className="btn btn-primary">
                <Search className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          {/* Sentiment Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Sentiment</label>
            <select 
              value={filterSentiment}
              onChange={(e) => setFilterSentiment(e.target.value)}
              className="input w-full"
            >
              <option value="all">All Sentiment</option>
              <option value="bullish">Bullish Only</option>
              <option value="bearish">Bearish Only</option>
              <option value="neutral">Neutral Only</option>
            </select>
          </div>
          
          {/* Time Range */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Time Range</label>
            <select 
              value={hoursBack}
              onChange={(e) => setHoursBack(parseInt(e.target.value))}
              className="input w-full"
            >
              <option value="1">Last Hour</option>
              <option value="6">Last 6 Hours</option>
              <option value="24">Last 24 Hours</option>
              <option value="72">Last 3 Days</option>
              <option value="168">Last Week</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Sentiment Summary */}
      {sentiment && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Overall Sentiment */}
          <div className={`glass-card p-4 border ${getSentimentBg(sentiment.overall_sentiment)}`}>
            <div className="text-sm text-gray-400 mb-1">Overall Sentiment</div>
            <div className={`text-2xl font-bold ${getSentimentColor(sentiment.overall_sentiment)}`}>
              {sentiment.overall_sentiment.toUpperCase()}
            </div>
            <div className="text-sm text-gray-400 mt-1">
              Score: {sentiment.sentiment_score.toFixed(2)}
            </div>
          </div>
          
          {/* Bullish Count */}
          <div className="glass-card p-4 border bg-green-900/20 border-green-500/30">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-green-400" />
              <span className="text-sm text-gray-400">Bullish</span>
            </div>
            <div className="text-2xl font-bold text-green-400">
              {sentiment.bullish_count}
            </div>
            <div className="text-sm text-gray-400 mt-1">
              {sentiment.bullish_pct.toFixed(1)}%
            </div>
          </div>
          
          {/* Bearish Count */}
          <div className="glass-card p-4 border bg-red-900/20 border-red-500/30">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="w-5 h-5 text-red-400" />
              <span className="text-sm text-gray-400">Bearish</span>
            </div>
            <div className="text-2xl font-bold text-red-400">
              {sentiment.bearish_count}
            </div>
            <div className="text-sm text-gray-400 mt-1">
              {sentiment.bearish_pct.toFixed(1)}%
            </div>
          </div>
          
          {/* Neutral Count */}
          <div className="glass-card p-4">
            <div className="flex items-center gap-2 mb-2">
              <Minus className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-400">Neutral</span>
            </div>
            <div className="text-2xl font-bold text-gray-400">
              {sentiment.neutral_count}
            </div>
            <div className="text-sm text-gray-400 mt-1">
              {((sentiment.neutral_count / sentiment.total_articles) * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      )}
      
      {/* News Articles */}
      <div className="space-y-3">
        {loading ? (
          <div className="glass-card p-8 text-center">
            <RefreshCw className="w-8 h-8 animate-spin text-primary-400 mx-auto mb-3" />
            <p className="text-gray-400">Loading news...</p>
          </div>
        ) : filteredArticles.length === 0 ? (
          <div className="glass-card p-8 text-center">
            <Newspaper className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400">No news articles found</p>
          </div>
        ) : (
          filteredArticles.map((article) => (
            <div 
              key={article.id}
              className={`glass-card p-5 hover:bg-gray-800/50 transition-colors border ${
                article.sentiment ? getSentimentBg(article.sentiment.label) : ''
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {article.sentiment && (
                      <span className="text-2xl">{article.sentiment.emoji}</span>
                    )}
                    <h3 className="text-lg font-bold flex-1">{article.headline}</h3>
                  </div>
                  
                  {/* Metadata */}
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span>{article.source}</span>
                    <span>•</span>
                    <span>{formatTime(article.created_at)}</span>
                    {article.symbols && article.symbols.length > 0 && (
                      <>
                        <span>•</span>
                        <div className="flex gap-1">
                          {article.symbols.map((symbol, idx) => (
                            <span key={idx} className="px-2 py-0.5 bg-primary-900/30 text-primary-400 rounded text-xs font-medium">
                              {symbol}
                            </span>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                </div>
                
                {/* Sentiment Badge */}
                {article.sentiment && (
                  <div className={`px-3 py-1 rounded ${getSentimentBg(article.sentiment.label)}`}>
                    <div className={`text-sm font-bold ${getSentimentColor(article.sentiment.label)}`}>
                      {article.sentiment.label.toUpperCase()}
                    </div>
                    <div className="text-xs text-gray-400">
                      {(article.sentiment.confidence * 100).toFixed(0)}% conf.
                    </div>
                  </div>
                )}
              </div>
              
              {/* Summary */}
              <p className="text-gray-300 mb-3 leading-relaxed">{article.summary}</p>
              
              {/* Footer */}
              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-500">
                  by {article.author}
                </div>
                <a 
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-sm text-primary-400 hover:text-primary-300 transition-colors"
                >
                  Read Full Article
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default NewsFeed;
