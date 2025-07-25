import os
import telebot
import paramiko
import zipfile

BOT_TOKEN = '7900178390:AAFQ7VlVcDkUtvzbXf45XdKkFBCQmqx367I'
AUTHORIZED_USER_ID = 6205215318

bot = telebot.TeleBot(BOT_TOKEN)

# Load setup script
with open("setup.sh", "r") as f:
    SETUP_SCRIPT = f.read()

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "🚫 Access denied.")
        return
    bot.send_message(message.chat.id, "👋 Welcome to VPS Setup Bot!

Commands:
/start – Show this message
/deploy – Run setup on default `vps_list.txt`
/status – Show current deployment status

Send a .txt or .zip file containing VPS credentials in `user@ip:password` format.")

@bot.message_handler(commands=['deploy'])
def deploy_command(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "🚫 Access denied.")
        return
    filename = "vps_list.txt"
    if not os.path.exists(filename):
        bot.send_message(message.chat.id, "❌ `vps_list.txt` not found.")
        return

    bot.send_message(message.chat.id, "🚀 Starting deployment from `vps_list.txt`")
    deploy_from_file(message.chat.id, filename)

@bot.message_handler(commands=['status'])
def status_command(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "🚫 Access denied.")
        return
    status = "✅ Bot is online.
Waiting for your file or /deploy command."
    bot.send_message(message.chat.id, status)

@bot.message_handler(content_types=['document'])
def handle_file(message):
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "🚫 Access denied.")
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = message.document.file_name

    with open(filename, 'wb') as f:
        f.write(downloaded_file)

    if filename.endswith('.zip'):
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall("vps_data")
            for f in zip_ref.namelist():
                if f.endswith(".txt"):
                    filename = os.path.join("vps_data", f)
                    break

    bot.reply_to(message, f"📄 `{filename}` received. Starting deployment...")
    deploy_from_file(message.chat.id, filename)

def deploy_from_file(chat_id, filename):
    with open(filename, 'r') as f:
        vps_list = f.read().splitlines()

    for vps in vps_list:
        try:
            user_host, password = vps.strip().split(":")
            username, ip = user_host.split("@")
            deploy_to_vps(ip, username, password)
            bot.send_message(chat_id, f"✅ Success: {ip}")
        except Exception as e:
            bot.send_message(chat_id, f"❌ Failed on {vps}: {str(e)}")

def deploy_to_vps(ip, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, username=username, password=password, timeout=10)

    sftp = ssh.open_sftp()
    sftp_file = sftp.file('/root/setup.sh', 'w')
    sftp_file.write(SETUP_SCRIPT)
    sftp_file.chmod(0o755)
    sftp_file.close()
    sftp.close()

    ssh.exec_command('bash /root/setup.sh')
    ssh.close()

bot.polling()
