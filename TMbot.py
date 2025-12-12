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
    datetime(2025, 12, 12).date(): {
        "Title": "Modules 3: Idea Validation",
        "Link": "https://drive.google.com/drive/u/0/folders/1ZgSzzZYRR4uFY3VazihUylpffLmBteWJ_4wAQH5EsdFTDSGEZ8rhMeioif_0hrCYQxhzElc9"
    },
    
    datetime(2025, 12, 29).date(): {
        "Title": "Module 4: Product Development Research",
        "Link": "https://drive.google.com/drive/u/0/folders/1bYxp31DdzEYlsEqxBW78ScyKlERK8ePsqv2l4M-LSKfbHT9RX14oYZLzYyPXpVKFSD2Fb31-"
    },
    
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
    await update.message.reply_text(help_msg, parse_mode='Markdown')


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the chat ID for configuration."""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title if chat_type != 'private' else 'Private Chat'
    
    msg = (
        f'📋 *Chat Information*\n\n'
        f'*Chat ID:* `{chat_id}`\n'
        f'*Chat Type:* {chat_type}\n'
        f'*Chat Name:* {chat_title}\n\n'
        f'ℹ️ Copy the Chat ID above and set it as `CHAT_ID` in your Railway environment variables.'
    )
    await update.message.reply_text(msg, parse_mode='Markdown')
    logger.info(f"Chat ID requested: {chat_id} ({chat_type})")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bot status."""
    current_time = datetime.now(TIMEZONE)
    configured_chat = CHAT_ID if CHAT_ID else "Not configured"
    
    status_msg = (
        f'✅ *LaunchPad Bot Status*\n\n'
        f'*Bot:* Running\n'
        f'*Current Time:* {current_time.strftime("%Y-%m-%d %H:%M:%S %Z")}\n'
        f'*Configured Chat ID:* `{configured_chat}`\n'
        f'*Timezone:* {TIMEZONE}\n\n'
        f'*Scheduler:* {"Active ✓" if scheduler.running else "Inactive ✗"}\n'
        f'*Jobs Scheduled:* {len(scheduler.get_jobs())}\n\n'
        f'Use /nextreminder to see upcoming reminders.'
    )
    await update.message.reply_text(status_msg, parse_mode='Markdown')


async def next_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show next scheduled reminder."""
    jobs = scheduler.get_jobs()
    
    if not jobs:
        await update.message.reply_text('❌ No reminders scheduled.')
        return
    
    now = datetime.now(TIMEZONE)
    next_runs = []
    
    for job in jobs:
        if job.next_run_time:
            next_runs.append((job.name, job.next_run_time))
    
    if not next_runs:
        await update.message.reply_text('❌ No upcoming reminders found.')
        return
    
    next_runs.sort(key=lambda x: x[1])
    
    msg = '📅 *Next Scheduled Reminders:*\n\n'
    for job_name, next_run in next_runs[:3]:  # Show next 3
        time_diff = next_run - now
        days = time_diff.days
        hours = time_diff.seconds // 3600
        
        msg += f'*{job_name}*\n'
        msg += f'└ {next_run.strftime("%Y-%m-%d %H:%M %Z")}\n'
        msg += f'└ In {days} days, {hours} hours\n\n'
    
    await update.message.reply_text(msg, parse_mode='Markdown')


# ============================================
# REMINDER FUNCTIONS
# ============================================

async def send_weekly_event_reminder():
    """Send weekly reminder for external events/workshops."""
    if not CHAT_ID:
        logger.warning("CHAT_ID not configured. Skipping weekly event reminder.")
        return
    
    try:
        message = (
            "📅 *Weekly Event Reminder*\n\n"
            "🎯 Don't forget to check this week's external events and workshops organized by BD!\n\n"
            "*Please review:*\n"
            "• Upcoming networking events\n"
            "• Industry workshops\n"
            "• Guest speaker sessions\n"
            "• Professional development opportunities\n\n"
            "Stay engaged and make the most of these learning opportunities! 🚀"
        )
        await app.bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"✅ Weekly event reminder sent to {CHAT_ID}")
    except Exception as e:
        logger.error(f"❌ Error sending weekly event reminder: {e}")


async def send_biweekly_module_reminder():
    """Send biweekly reminder for module releases."""
    if not CHAT_ID:
        logger.warning("CHAT_ID not configured. Skipping biweekly module reminder.")
        return
    
    today = datetime.now(TIMEZONE).date()
    #days_diff = (today - MODULE_START_DATE).days
    #current_week_num = days_diff // 7

    if today in RELEASE_CALENDAR:
        module_data = RELEASE_CALENDAR[today]
        #topic = module_data['Title']
        #link = module_data['Link']
        try:
            message = (
                f"📚 *Module Release Update*\n\n"
                f"🎓 *Topic:* {module_data['Title']}\n"
                f"🔗 *Link:* [Click to Open]({module_data['Link']})\n\n"
                f"🗓 _Released on: {today.strftime('%d %b %Y')}_"
            )
        
            await app.bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"✅ Biweekly module reminder sent to {CHAT_ID}")
        except Exception as e:
            logger.error(f"❌ Error sending biweekly module reminder: {e}")
    else:
        logger.info(f"No content for today ({today}).")


##def should_send_module_reminder():
##    """Check if today is a biweekly module release day."""
##    today = datetime.now(TIMEZONE).date()
##    days_diff = (today - MODULE_START_DATE).days
##    weeks_diff = days_diff // 7
##    return weeks_diff % 2 == 0


async def monday_reminder_job():
    """Combined Monday reminder job - checks and sends appropriate reminders."""
    logger.info("🔔 Monday reminder job triggered")
    
    # Always send weekly event reminder
    await send_weekly_event_reminder()
    
    # Check if it's a biweekly module release week
    if should_send_module_reminder():
        logger.info("📚 Biweekly module reminder week - sending module reminder")
        await send_biweekly_module_reminder()
    else:
        logger.info("📚 Not a module release week - skipping module reminder")


# ============================================
# MAIN APPLICATION
# ============================================

def setup_scheduler():
    """Set up scheduled jobs."""
    # Monday at 9:00 AM - Combined reminder check
    scheduler.add_job(
        monday_reminder_job,
        trigger=CronTrigger(day_of_week='mon', hour=9, minute=0, timezone=TIMEZONE),
        id='monday_reminders',
        name='Monday Reminders',
        replace_existing=True
    )
    
    logger.info("✅ Scheduler jobs configured:")
    logger.info(f"   - Monday reminders: Every Monday at 9:00 AM {TIMEZONE}")
    logger.info(f"   - Module start date: {MODULE_START_DATE}")

async def start_scheduler_hook(application: Application):
    """Start the scheduler after the bot loop is running."""
    scheduler.start()
    logger.info("✅ Scheduler started successfully!")

def main():
    """Start the bot."""
    global app
    
    # Validate environment variables
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment variables!")
        return
    
    if not CHAT_ID:
        logger.warning("⚠️  CHAT_ID not configured. Use /getchatid command to get your chat ID.")
        logger.warning("⚠️  Reminders will not be sent until CHAT_ID is set.")
    
    # Create the Application
    app = Application.builder().token(BOT_TOKEN).post_init(start_scheduler_hook).build()     
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("getchatid", get_chat_id))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("nextreminder", next_reminder))
    
    # Set up scheduler
    setup_scheduler()
    
    # Start scheduler
    # scheduler.start()
    
    logger.info("=" * 50)
    logger.info("🚀 LaunchPad Bot started successfully!")
    logger.info("=" * 50)
    logger.info(f"Timezone: {TIMEZONE}")
    logger.info(f"Configured Chat ID: {CHAT_ID if CHAT_ID else 'Not set'}")
    logger.info("Scheduled reminders:")
    logger.info("  📅 Weekly events: Every Monday at 9:00 AM")
    logger.info("  📚 Biweekly modules: Every other Monday at 9:00 AM")
    logger.info("=" * 50)
    
    # Run the bot until stopped
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        scheduler.shutdown()
        logger.info("Scheduler shut down")


if __name__ == '__main__':
    main()
