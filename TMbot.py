import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8553959845:AAGRpYDMQXG1nKHvIEDFee5_MqnFpd40ivc"
CHAT_ID = os.environ.get('CHAT_ID')  # The chat/group ID where reminders will be sent
TIMEZONE = pytz.timezone('Asia/Singapore')  # Adjust to your timezone

# Module release tracking - set your program start date here
MODULE_START_DATE = datetime(2025, 10, 5, tzinfo=TIMEZONE).date()

RELEASE_CALENDAR = {
    # UPCOMING: Monday Dec 15
    datetime(2025, 12, 15).date(): {
        "Title": "Modules 3: Idea Validation",
        "Link": "https://drive.google.com/drive/u/0/folders/1ZgSzzZYRR4uFY3VazihUylpffLmBteWJ_4wAQH5EsdFTDSGEZ8rhMeioif_0hrCYQxhzElc9"
    },
    
    datetime(2025, 12, 29).date(): {
        "Title": "Module 4: Product Development Research",
        "Link": "https://drive.google.com/drive/u/0/folders/1bYxp31DdzEYlsEqxBW78ScyKlERK8ePsqv2l4M-LSKfbHT9RX14oYZLzYyPXpVKFSD2Fb31-"
    },
    s
    datetime(2026, 1, 12).date(): {
        "Title": "Module 5",
        "Link": "https://drive.google.com/drive/u/0/folders/1gAUFM5LX2KPGYJ4ILf40WDbQmdxpD9FnYu3GPaUeewDZrlo_wxSRGOp_HibkX1IAMZS_ZNCE"
    }
 
}

MODULE_CONTENT = {
    # Week Number : { Title, Link }
    1:{
        "Title": "Module 1: Ideation",
        "Link": "https://drive.google.com/drive/u/0/folders/1CAzJcch-0-F3TCUCXUYs4lYOH8-Bhx5bjySyu4qxZBwyBuSguvjTGxWr3Pb0EYh1oyAnHuks"
    },
    2:{
        "Title": "Module 2: Crafting Your Business Model Canvas",
        "Link": "https://drive.google.com/drive/u/0/folders/1rf0WUdEZs4Ml3V3NGbUQYL-S1eSZaryKrs-jAjFuIVpO0KMSqOAytqLuKqL-8uD5dYsfZisM"
    },
    3:{
        "Title": "Module 3: Idea Validation",
        "Link": "https://drive.google.com/drive/u/0/folders/1ZgSzzZYRR4uFY3VazihUylpffLmBteWJ_4wAQH5EsdFTDSGEZ8rhMeioif_0hrCYQxhzElc9"
    },
    4:{
        "Title": "Module 4: Product Development Research",
        "Link": "https://drive.google.com/drive/u/0/folders/1bYxp31DdzEYlsEqxBW78ScyKlERK8ePsqv2l4M-LSKfbHT9RX14oYZLzYyPXpVKFSD2Fb31-"
    },
    5:{
        "Title": "Module 5",
        "Link": "https://drive.google.com/drive/u/0/folders/1gAUFM5LX2KPGYJ4ILf40WDbQmdxpD9FnYu3GPaUeewDZrlo_wxSRGOp_HibkX1IAMZS_ZNCE"
    }
}

# Initialize scheduler
scheduler = AsyncIOScheduler(timezone=TIMEZONE)

# Global application reference for scheduler
app = None


# ============================================
# COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    chat_type = update.effective_chat.type
    welcome_msg = (
        '🚀 *LaunchPad Bot is now active!*\n\n'
        'I will send you:\n'
        '📅 Weekly reminders for external events/workshops by BD\n'
        '📚 Biweekly reminders for module releases\n\n'
        '*Schedule:*\n'
        '• Weekly events: Every Monday at 9:00 AM\n'
        '• Biweekly modules: Every other Monday at 9:00 AM\n\n'
        '*Available Commands:*\n'
        '/start - Start the bot\n'
        '/help - Get help\n'
        '/getchatid - Get current chat ID\n'
        '/status - Check bot status\n'
        '/nextreminder - See next scheduled reminder\n'
    )
    
    if chat_type == 'private':
        welcome_msg += '\n💡 Tip: Add me to a group to send reminders there!'
    
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')
    logger.info(f"Bot started in chat: {update.effective_chat.id} ({chat_type})")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_msg = (
        '🤖 *LaunchPad Bot Help*\n\n'
        '*Automatic Reminders:*\n'
        '• Weekly events: Every Monday at 9:00 AM SGT\n'
        '• Biweekly modules: Every other Monday at 9:00 AM SGT\n\n'
        '*Commands:*\n'
        '/start - Initialize the bot\n'
        '/help - Show this help message\n'
        '/getchatid - Get your chat ID for configuration\n'
        '/status - Check if reminders are active\n'
        '/nextreminder - See when next reminder will be sent\n\n'
        '*Setup:*\n'
        '1. Use /getchatid to get your chat ID\n'
        '2. Set CHAT\\_ID in your Railway environment\n'
        '3. Reminders will be sent automatically!\n\n'
        '*For Groups:*\n'
        'Add me to your group and I will send reminders there.'
    )
