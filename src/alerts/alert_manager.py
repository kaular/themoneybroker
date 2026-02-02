"""
Alert Manager - Multi-Channel Notification System

Supports:
- Email alerts
- Discord webhooks
- Telegram bot
- SMS (Twilio)
- Browser push notifications

Alert Types:
- Trade executed
- Scanner moonshot found
- Portfolio rebalance needed
- Stop-loss triggered
- Take-profit hit
- Risk limit reached
- Daily P/L thresholds
"""

import asyncio
import logging
import smtplib
import requests
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of alerts"""
    TRADE_EXECUTED = "trade_executed"
    MOONSHOT_FOUND = "moonshot_found"
    REBALANCE_NEEDED = "rebalance_needed"
    STOP_LOSS_TRIGGERED = "stop_loss_triggered"
    TAKE_PROFIT_HIT = "take_profit_hit"
    RISK_LIMIT = "risk_limit"
    DAILY_PNL = "daily_pnl"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    ERROR = "error"


class AlertChannel(Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    SMS = "sms"
    BROWSER = "browser"
    CONSOLE = "console"


@dataclass
class Alert:
    """Alert message"""
    type: AlertType
    title: str
    message: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    timestamp: datetime
    data: Dict = None
    
    def format_email_html(self) -> str:
        """Format alert as HTML email"""
        priority_colors = {
            'low': '#3B82F6',      # Blue
            'medium': '#F59E0B',   # Yellow
            'high': '#EF4444',     # Red
            'critical': '#DC2626'  # Dark Red
        }
        
        color = priority_colors.get(self.priority, '#6B7280')
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f3f4f6;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
              <div style="background-color: {color}; padding: 20px; color: white;">
                <h2 style="margin: 0;">🔔 {self.title}</h2>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">{self.priority.upper()} Priority</p>
              </div>
              <div style="padding: 20px;">
                <p style="font-size: 16px; line-height: 1.6; color: #374151;">{self.message}</p>
                <div style="margin-top: 20px; padding: 15px; background-color: #f9fafb; border-radius: 6px;">
                  <p style="margin: 0; font-size: 14px; color: #6b7280;">
                    <strong>Time:</strong> {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                  </p>
                  <p style="margin: 5px 0 0 0; font-size: 14px; color: #6b7280;">
                    <strong>Type:</strong> {self.type.value}
                  </p>
                </div>
                {self._format_data_html()}
              </div>
              <div style="padding: 15px 20px; background-color: #f3f4f6; text-align: center; font-size: 12px; color: #6b7280;">
                TheMoneyBroker Trading Bot Alert System
              </div>
            </div>
          </body>
        </html>
        """
        return html
    
    def _format_data_html(self) -> str:
        """Format additional data as HTML"""
        if not self.data:
            return ""
        
        items = []
        for key, value in self.data.items():
            items.append(f"<li><strong>{key}:</strong> {value}</li>")
        
        return f"""
        <div style="margin-top: 15px; padding: 15px; border-left: 3px solid #3B82F6; background-color: #eff6ff;">
          <p style="margin: 0 0 10px 0; font-weight: bold; color: #1e40af;">Details:</p>
          <ul style="margin: 0; padding-left: 20px; color: #374151;">
            {''.join(items)}
          </ul>
        </div>
        """
    
    def format_discord(self) -> Dict:
        """Format alert for Discord webhook"""
        priority_colors = {
            'low': 0x3B82F6,
            'medium': 0xF59E0B,
            'high': 0xEF4444,
            'critical': 0xDC2626
        }
        
        embed = {
            "title": f"🔔 {self.title}",
            "description": self.message,
            "color": priority_colors.get(self.priority, 0x6B7280),
            "timestamp": self.timestamp.isoformat(),
            "fields": [
                {
                    "name": "Priority",
                    "value": self.priority.upper(),
                    "inline": True
                },
                {
                    "name": "Type",
                    "value": self.type.value,
                    "inline": True
                }
            ],
            "footer": {
                "text": "TheMoneyBroker Alert System"
            }
        }
        
        # Add data fields
        if self.data:
            for key, value in self.data.items():
                embed["fields"].append({
                    "name": key,
                    "value": str(value),
                    "inline": True
                })
        
        return {"embeds": [embed]}
    
    def format_telegram(self) -> str:
        """Format alert for Telegram"""
        priority_emoji = {
            'low': 'ℹ️',
            'medium': '⚠️',
            'high': '🚨',
            'critical': '🔴'
        }
        
        emoji = priority_emoji.get(self.priority, '📢')
        
        text = f"{emoji} **{self.title}**\n\n"
        text += f"{self.message}\n\n"
        text += f"🕐 {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"📊 Type: {self.type.value}\n"
        text += f"⚡ Priority: {self.priority.upper()}\n"
        
        if self.data:
            text += "\n📋 **Details:**\n"
            for key, value in self.data.items():
                text += f"  • {key}: {value}\n"
        
        return text


class AlertManager:
    """
    Alert Manager - Multi-channel notification system
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize Alert Manager
        
        Args:
            config: Dict with channel configurations
                {
                    'email': {'smtp_server': ..., 'from': ..., 'to': ...},
                    'discord': {'webhook_url': ...},
                    'telegram': {'bot_token': ..., 'chat_id': ...}
                }
        """
        self.config = config or {}
        self.alert_history: List[Alert] = []
        self.enabled_channels: List[AlertChannel] = [AlertChannel.CONSOLE]
        
        # Configure channels based on config
        if 'email' in self.config and self.config['email'].get('enabled'):
            self.enabled_channels.append(AlertChannel.EMAIL)
        
        if 'discord' in self.config and self.config['discord'].get('enabled'):
            self.enabled_channels.append(AlertChannel.DISCORD)
        
        if 'telegram' in self.config and self.config['telegram'].get('enabled'):
            self.enabled_channels.append(AlertChannel.TELEGRAM)
        
        logger.info(f"Alert Manager initialized with channels: {[c.value for c in self.enabled_channels]}")
    
    async def send_alert(self, alert: Alert, channels: Optional[List[AlertChannel]] = None):
        """
        Send alert through specified channels
        
        Args:
            alert: Alert to send
            channels: List of channels to use (default: all enabled)
        """
        if channels is None:
            channels = self.enabled_channels
        
        # Add to history
        self.alert_history.append(alert)
        
        # Limit history size
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        # Send through each channel
        tasks = []
        for channel in channels:
            if channel == AlertChannel.EMAIL:
                tasks.append(self._send_email(alert))
            elif channel == AlertChannel.DISCORD:
                tasks.append(self._send_discord(alert))
            elif channel == AlertChannel.TELEGRAM:
                tasks.append(self._send_telegram(alert))
            elif channel == AlertChannel.CONSOLE:
                self._send_console(alert)
        
        # Execute all sends concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log failures
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to send alert via {channels[i].value}: {result}")
    
    async def _send_email(self, alert: Alert):
        """Send alert via email"""
        try:
            email_config = self.config.get('email', {})
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{alert.priority.upper()}] {alert.title}"
            msg['From'] = email_config.get('from', 'noreply@themoneybroker.com')
            msg['To'] = email_config.get('to', '')
            
            # Attach HTML version
            html_part = MIMEText(alert.format_email_html(), 'html')
            msg.attach(html_part)
            
            # Send via SMTP
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            username = email_config.get('username', '')
            password = email_config.get('password', '')
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                if username and password:
                    server.login(username, password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent: {alert.title}")
        
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            raise
    
    async def _send_discord(self, alert: Alert):
        """Send alert via Discord webhook"""
        try:
            webhook_url = self.config.get('discord', {}).get('webhook_url')
            if not webhook_url:
                raise ValueError("Discord webhook_url not configured")
            
            payload = alert.format_discord()
            
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Discord alert sent: {alert.title}")
        
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
            raise
    
    async def _send_telegram(self, alert: Alert):
        """Send alert via Telegram bot"""
        try:
            telegram_config = self.config.get('telegram', {})
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')
            
            if not bot_token or not chat_id:
                raise ValueError("Telegram bot_token and chat_id not configured")
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': alert.format_telegram(),
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Telegram alert sent: {alert.title}")
        
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            raise
    
    def _send_console(self, alert: Alert):
        """Print alert to console"""
        priority_prefix = {
            'low': '📘',
            'medium': '📙',
            'high': '📕',
            'critical': '🚨'
        }
        
        prefix = priority_prefix.get(alert.priority, '📢')
        logger.info(f"{prefix} ALERT [{alert.priority.upper()}] {alert.title}: {alert.message}")
    
    def get_history(self, limit: int = 100, alert_type: Optional[AlertType] = None) -> List[Alert]:
        """Get alert history"""
        history = self.alert_history[-limit:]
        
        if alert_type:
            history = [a for a in history if a.type == alert_type]
        
        return history
    
    def clear_history(self):
        """Clear alert history"""
        self.alert_history = []
        logger.info("Alert history cleared")
    
    # Convenience methods for common alerts
    
    async def alert_trade_executed(self, symbol: str, side: str, quantity: int, price: float):
        """Send trade executed alert"""
        alert = Alert(
            type=AlertType.TRADE_EXECUTED,
            title=f"Trade Executed: {side.upper()} {symbol}",
            message=f"{side.upper()} {quantity} shares of {symbol} at ${price:.2f}",
            priority='medium',
            timestamp=datetime.now(),
            data={
                'Symbol': symbol,
                'Side': side.upper(),
                'Quantity': quantity,
                'Price': f"${price:.2f}",
                'Total Value': f"${quantity * price:.2f}"
            }
        )
        await self.send_alert(alert)
        return alert
    
    async def alert_moonshot_found(self, symbol: str, score: float, reason: str = "Strong growth indicators"):
        """Send moonshot found alert"""
        alert = Alert(
            type=AlertType.MOONSHOT_FOUND,
            title=f"🚀 Moonshot Opportunity: {symbol}",
            message=f"Growth Scanner found high-potential stock {symbol} with score {score:.1f}/100. {reason}",
            priority='high',
            timestamp=datetime.now(),
            data={
                'Symbol': symbol,
                'Score': f"{score:.1f}/100",
                'Reason': reason
            }
        )
        await self.send_alert(alert)
        return alert
    
    async def alert_rebalance_needed(self, actions_count: int):
        """Send rebalance needed alert"""
        alert = Alert(
            type=AlertType.REBALANCE_NEEDED,
            title="Portfolio Rebalancing Needed",
            message=f"Portfolio allocation has deviated from target. {actions_count} rebalancing action(s) recommended.",
            priority='medium',
            timestamp=datetime.now(),
            data={
                'Actions Count': actions_count
            }
        )
        await self.send_alert(alert)
    
    async def alert_stop_loss(self, symbol: str, price: float, loss: float):
        """Send stop-loss triggered alert"""
        alert = Alert(
            type=AlertType.STOP_LOSS_TRIGGERED,
            title=f"⛔ Stop-Loss Triggered: {symbol}",
            message=f"Stop-loss triggered for {symbol} at ${price:.2f}. Loss: ${loss:.2f}",
            priority='high',
            timestamp=datetime.now(),
            data={
                'Symbol': symbol,
                'Exit Price': f"${price:.2f}",
                'Loss': f"-${abs(loss):.2f}"
            }
        )
        await self.send_alert(alert)
    
    async def alert_take_profit(self, symbol: str, price: float, profit: float):
        """Send take-profit hit alert"""
        alert = Alert(
            type=AlertType.TAKE_PROFIT_HIT,
            title=f"🎯 Take-Profit Hit: {symbol}",
            message=f"Take-profit target reached for {symbol} at ${price:.2f}. Profit: ${profit:.2f}",
            priority='medium',
            timestamp=datetime.now(),
            data={
                'Symbol': symbol,
                'Exit Price': f"${price:.2f}",
                'Profit': f"+${profit:.2f}"
            }
        )
        await self.send_alert(alert)
    
    async def alert_daily_pnl(self, pnl: float, pnl_percent: float):
        """Send daily P/L alert"""
        priority = 'high' if abs(pnl_percent) > 5 else 'medium' if abs(pnl_percent) > 2 else 'low'
        
        alert = Alert(
            type=AlertType.DAILY_PNL,
            title=f"Daily P/L Update",
            message=f"Today's P/L: {'+'if pnl >= 0 else ''}{pnl:.2f} ({pnl_percent:+.2f}%)",
            priority=priority,
            timestamp=datetime.now(),
            data={
                'P/L': f"${pnl:+.2f}",
                'Percentage': f"{pnl_percent:+.2f}%"
            }
        )
        await self.send_alert(alert)
