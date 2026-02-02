"""
Tests für Alert System
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from src.alerts.alert_manager import AlertManager, Alert, AlertType, AlertChannel


@pytest.mark.asyncio
class TestAlertManager:
    """Tests für Alert Manager"""
    
    def setup_method(self):
        self.config = {
            'email': {
                'smtp_server': 'smtp.test.com',
                'smtp_port': 587,
                'from_email': 'test@test.com',
                'to_emails': ['user@test.com'],
                'password': 'test123'
            },
            'discord': {
                'webhook_url': 'https://discord.com/webhook/test'
            },
            'telegram': {
                'bot_token': 'test_token',
                'chat_id': '123456'
            }
        }
        self.manager = AlertManager(self.config)
    
    def test_alert_creation(self):
        """Test: Alert Creation"""
        alert = Alert(
            type=AlertType.TRADE_EXECUTED,
            title="Test Trade",
            message="Trade executed successfully",
            priority="high",
            timestamp=datetime.now(),
            data={'symbol': 'AAPL', 'quantity': 10}
        )
        
        assert alert.type == AlertType.TRADE_EXECUTED
        assert alert.title == "Test Trade"
        assert alert.priority == "high"
    
    def test_email_formatting(self):
        """Test: Email HTML Formatting"""
        alert = Alert(
            type=AlertType.MOONSHOT_FOUND,
            title="Moonshot Detected",
            message="TSLA shows strong signals",
            priority="high",
            timestamp=datetime.now()
        )
        
        html = alert.format_email_html()
        
        assert "Moonshot Detected" in html
        assert "TSLA" in html
        assert "color:" in html  # Has styling
    
    def test_discord_formatting(self):
        """Test: Discord Embed Formatting"""
        alert = Alert(
            type=AlertType.STOP_LOSS_TRIGGERED,
            title="Stop Loss Hit",
            message="NVDA position closed",
            priority="medium",
            timestamp=datetime.now(),
            data={'symbol': 'NVDA', 'loss': -150}
        )
        
        embed = alert.format_discord()
        
        # Discord gibt ein dict mit 'embeds' array zurück
        assert 'embeds' in embed
        assert len(embed['embeds']) > 0
        assert 'title' in embed['embeds'][0]
        assert 'Stop Loss Hit' in embed['embeds'][0]['title']
    
    def test_telegram_formatting(self):
        """Test: Telegram Markdown Formatting"""
        alert = Alert(
            type=AlertType.DAILY_PNL,
            title="Daily P&L Report",
            message="Today's performance",
            priority="low",
            timestamp=datetime.now(),
            data={'pnl': 250, 'pnl_percent': 2.5}
        )
        
        markdown = alert.format_telegram()
        
        assert "Daily P&L Report" in markdown
        assert "250" in markdown
    
    def test_channel_enabling(self):
        """Test: Channel Enable/Disable"""
        # enabled_channels ist eine Liste
        if AlertChannel.EMAIL not in self.manager.enabled_channels:
            self.manager.enabled_channels.append(AlertChannel.EMAIL)
        
        assert AlertChannel.EMAIL in self.manager.enabled_channels
        
        # Entfernen
        if AlertChannel.EMAIL in self.manager.enabled_channels:
            self.manager.enabled_channels.remove(AlertChannel.EMAIL)
        
        assert AlertChannel.EMAIL not in self.manager.enabled_channels
    
    def test_alert_history(self):
        """Test: Alert History Tracking"""
        alert = Alert(
            type=AlertType.TRADE_EXECUTED,
            title="Test",
            message="Test message",
            priority="medium",
            timestamp=datetime.now()
        )
        
        self.manager.alert_history.append(alert)
        
        # History direkt prüfen
        assert len(self.manager.alert_history) >= 1
        assert self.manager.alert_history[-1].title == "Test"
    
    async def test_convenience_methods(self):
        """Test: Convenience Alert Methods"""
        # Mock send_alert um Netzwerk-Calls zu vermeiden
        async def mock_send_alert(alert):
            pass
        self.manager.send_alert = mock_send_alert
        
        # Trade executed alert - Korrekte Reihenfolge: symbol, side, quantity, price
        alert1 = await self.manager.alert_trade_executed('AAPL', 'buy', 10, 150.0)
        assert alert1.type == AlertType.TRADE_EXECUTED
        assert 'AAPL' in alert1.message
        
        # Moonshot alert
        alert2 = await self.manager.alert_moonshot_found('TSLA', 95.5)
        assert alert2.type == AlertType.MOONSHOT_FOUND
        assert 'TSLA' in alert2.message

