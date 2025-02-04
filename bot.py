import requests
import telebot
import json
import os
from time import sleep

# Bot token
TELEGRAM_BOT_TOKEN = '7988299708:7734895902:AAF0fCUsnNjaJUI2YU1r7r3lW-NBZnTu-x8'

# Owner ID
owner_id = 7661505696

# Create bot with MarkdownV2 enabled
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode="MarkdownV2")

# Groups file path
GROUPS_FILE_PATH = 'allowed_groups.json'

def load_allowed_groups():
    """Load allowed groups from file"""
    if os.path.exists(GROUPS_FILE_PATH):
        with open(GROUPS_FILE_PATH, 'r') as file:
            return set(json.load(file))
    return set()

def save_allowed_groups():
    """Save allowed groups to file"""
    with open(GROUPS_FILE_PATH, 'w') as file:
        json.dump(list(allowed_group_ids), file)

# Load allowed groups on startup
allowed_group_ids = load_allowed_groups()

def escape_markdown(text):
    """Escape special markdown characters"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

def get_player_info(uid, region):
    """Get player info from API"""
    url = f"https://ariiflexlabs-playerinfo.onrender.com/ff_info?uid={uid}&region={region}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if not data:
            return "❌ No data found for this account."

        account_info = data.get('AccountInfo', {})
        guild_info = data.get('GuildInfo', {})
        pet_info = data.get('petInfo', {})
        credit_score_info = data.get('creditScoreInfo', {})
        social_info = data.get('socialinfo', {})

        result = f"""
📝 *Account Info:*
┌ 👤 Name: {escape_markdown(str(account_info.get('AccountName', 'Not Available')))}
├ 🌍 Region: {escape_markdown(str(account_info.get('AccountRegion', 'Not Available')))}
├ 🔢 Level: {escape_markdown(str(account_info.get('AccountLevel', 'Not Available')))}
├ ❤️ Likes: {escape_markdown(str(account_info.get('AccountLikes', 'Not Available')))}
├ ⚡ EXP: {escape_markdown(str(account_info.get('AccountEXP', 'Not Available')))}
├ 💼 Type: {escape_markdown(str(account_info.get('AccountType', 'Not Available')))}
├ 🏅 Max BR: {escape_markdown(str(account_info.get('BrMaxRank', 'Not Available')))}
├ 📈 BR Points: {escape_markdown(str(account_info.get('BrRankPoint', 'Not Available')))}
├ 🏅 Max CS: {escape_markdown(str(account_info.get('CsMaxRank', 'Not Available')))}
└ 📈 CS Points: {escape_markdown(str(account_info.get('CsRankPoint', 'Not Available')))}

⚔️ *Guild Info:*
┌ 🏆 Name: {escape_markdown(str(guild_info.get('GuildName', 'Not Available')))}
├ 👥 Members: {escape_markdown(str(guild_info.get('GuildMember', 'Not Available')))}
├ 💪 Level: {escape_markdown(str(guild_info.get('GuildLevel', 'Not Available')))}
└ 📊 Capacity: {escape_markdown(str(guild_info.get('GuildCapacity', 'Not Available')))}

🐾 *Pet Info:*
┌ 🐶 Name: {escape_markdown(str(pet_info.get('name', 'Not Available')))}
├ 🔋 Level: {escape_markdown(str(pet_info.get('level', 'Not Available')))}
└ 💥 EXP: {escape_markdown(str(pet_info.get('exp', 'Not Available')))}

💳 *Credit Info:*
┌ 📊 Score: {escape_markdown(str(credit_score_info.get('creditScore', 'Not Available')))}
└ 🎁 Reward: {escape_markdown(str(credit_score_info.get('rewardState', 'Not Available')))}

🌐 *Social Info:*
┌ 🗣️ Language: {escape_markdown(str(social_info.get('AccountLanguage', 'Not Available')))}
├ ✍️ Signature: {escape_markdown(str(social_info.get('AccountSignature', 'Not Available')))}
└ 🎮 Mode: {escape_markdown(str(social_info.get('AccountPreferMode', 'Not Available')))}"""
        return result.strip()
    else:
        return f"❌ Failed to connect to the server. Error code: {response.status_code}"

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle /start command"""
    if message.chat.id in allowed_group_ids:
        bot_info = bot.get_chat_member(message.chat.id, bot.get_me().id)
        if bot_info.status not in ["administrator", "creator"]:
            bot.send_message(message.chat.id, escape_markdown("❌ I am not an admin in this group. Please make me an admin to fetch player commands."))
            return
        
        bot.send_message(message.chat.id, escape_markdown("👋 Welcome! Use `/ff <region> <uid>` to get Free Fire account details.\n\n🔹 Example: `/ff sg 12345678`"))
    elif message.chat.type == 'private' and message.from_user.id == owner_id:
        bot.reply_to(message, escape_markdown("👋 Welcome! Use `/ff <region> <uid>` to get Free Fire account details.\n\n🔹 Example: `/ff sg 12345678`"))
    elif message.chat.type == 'private':
        bot.reply_to(message, escape_markdown("❌ *This bot is currently unavailable in private chat*\nPlease use the bot in an authorized group."))

@bot.message_handler(commands=['ff'])
def handle_ff_command(message):
    """Handle /ff command"""
    if message.chat.id in allowed_group_ids:
        try:
            bot_info = bot.get_chat_member(message.chat.id, bot.get_me().id)
            if bot_info.status not in ["administrator", "creator"]:
                bot.send_message(message.chat.id, escape_markdown("❌ I am not an admin in this group. Please make me an admin to fetch player commands."))
                return
            
            args = message.text.split()
            if len(args) != 3:
                bot.reply_to(message, escape_markdown("❌ Please use the correct format: `/ff <region> <uid>`"))
                return
            
            region = args[1].lower()
            uid = args[2]

            if not uid.isdigit():
                bot.reply_to(message, escape_markdown("❌ Please enter a valid UID (numbers only)."))
                return
            
            if region not in ["sg", "me", "eu", "ind"]:
                bot.reply_to(message, escape_markdown("❌ Invalid region. Choose from: `sg`, `me`, `eu`, `ind`"))
                return

            player_info = get_player_info(uid, region)
            bot.reply_to(message, player_info)

        except Exception as e:
            bot.reply_to(message, f"❌ An error occurred: {escape_markdown(str(e))}")
    elif message.chat.type == 'private' and message.from_user.id == owner_id:
        try:
            args = message.text.split()
            if len(args) != 3:
                bot.reply_to(message, escape_markdown("❌ Please use the correct format: `/ff <region> <uid>`"))
                return
            
            region = args[1].lower()
            uid = args[2]

            if not uid.isdigit():
                bot.reply_to(message, escape_markdown("❌ Please enter a valid UID (numbers only)."))
                return
            
            if region not in ["sg", "me", "eu", "ind"]:
                bot.reply_to(message, escape_markdown("❌ Invalid region. Choose from: `sg`, `me`, `eu`, `ind`"))
                return

            player_info = get_player_info(uid, region)
            bot.reply_to(message, player_info)

        except Exception as e:
            bot.reply_to(message, f"❌ An error occurred: {escape_markdown(str(e))}")
    elif message.chat.type == 'private':
        bot.reply_to(message, escape_markdown("❌ *This bot is currently unavailable in private chat*\nPlease use the bot in an authorized group."))

@bot.message_handler(commands=['add'])
def add_group(message):
    """Add group to allowed list"""
    if message.chat.type == 'private' and message.from_user.id == owner_id:
        try:
            group_id = message.text.split()[1]
            if group_id.startswith('-100') and group_id[1:].isdigit():
                group_id = int(group_id)
                if group_id not in allowed_group_ids:
                    allowed_group_ids.add(group_id)
                    save_allowed_groups()
                    bot.send_message(group_id, escape_markdown("✅ Group activated successfully.\nPlease make sure the bot is an admin in this group to fetch player commands."))
                else:
                    bot.reply_to(message, escape_markdown("❌ This group is already added."))
            else:
                bot.reply_to(message, escape_markdown("❌ Please enter a valid group ID (must start with -100)."))
        except IndexError:
            bot.reply_to(message, escape_markdown("❌ Please enter a group ID after the command."))
    else:
        bot.reply_to(message, escape_markdown("❌ This command is only available to the owner in private."))

@bot.message_handler(commands=['list_groups'])
def list_groups(message):
    """List allowed groups"""
    if message.chat.type == 'private' and message.from_user.id == owner_id:
        if allowed_group_ids:
            groups = "\n".join([str(group_id) for group_id in allowed_group_ids])
            bot.reply_to(message, escape_markdown(f"Allowed Groups:\n{groups}"))
        else:
            bot.reply_to(message, escape_markdown("❌ No groups added yet."))
    else:
        bot.reply_to(message, escape_markdown("❌ This command is only available to the owner in private."))

@bot.message_handler(commands=['remove_group'])
def remove_group(message):
    """Remove group from allowed list"""
    if message.chat.type == 'private' and message.from_user.id == owner_id:
        try:
            group_id = message.text.split()[1]
            if group_id.startswith('-100') and group_id[1:].isdigit():
                group_id = int(group_id)
                if group_id in allowed_group_ids:
                    allowed_group_ids.remove(group_id)
                    save_allowed_groups()
                    bot.reply_to(message, escape_markdown(f"✅ Group with ID {group_id} removed successfully."))
                else:
                    bot.reply_to(message, escape_markdown("❌ This group ID is not in the allowed list."))
            else:
                bot.reply_to(message, escape_markdown("❌ Please enter a valid group ID (must start with -100)."))
        except IndexError:
            bot.reply_to(message, escape_markdown("❌ Please enter a group ID after the command."))
    else:
        bot.reply_to(message, escape_markdown("❌ This command is only available to the owner in private."))

def main():
    """Main function to run the bot"""
    while True:
        try:
            print("Bot started...")
            bot.infinity_polling()
        except Exception as e:
            print(f"Error occurred: {e}")
            sleep(10)

if __name__ == "__main__":
    main()
