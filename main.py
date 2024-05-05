from dotenv import load_dotenv
import os, logging, requests, re, paramiko
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

logger = logging.getLogger(__name__)


load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
host = os.getenv('HOST')
port = os.getenv('PORT')
username = os.getenv('USER')
password = os.getenv('PASSWORD')

#chat_id = os.getenv('CHAT_ID')

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findPhoneNumbers (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'((\+7|7|8)(\-| |)(|\()(\d{3})(|\))(\-| |)(\d{3}(\-| |)\d{2}(\-| |)\d{2}))') # Возможно не лучший по скорости но рабочей Regex

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return # Завершаем выполнение функции
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        # Записываем очередной номер
        phoneNumbers += f'{i+1}. {phoneNumberList[i][0]}\n' 
        
        
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска Email-адресов: ')

    return 'findEmail'


def findEmail (update: Update, context):
    logger.info("functioin findEmail")
    user_input = update.message.text # Получаем текст, содержащий(или нет) Email

    EmailRegex = re.compile(r'(([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+)')

    EmailList = EmailRegex.findall(user_input) # Ищем номера Email

    if not EmailList: # Обрабатываем случай, когда Email нет
        update.message.reply_text('Email адресса не найдены')
        logger.info("Email is not found {user_inpu}")
        return # Завершаем выполнение функции
    
    EmailAddress = '' # Создаем строку, в которую будем записывать Email
    for i in range(len(EmailList)):
        # Записываем очередной номер
        EmailAddress += f'{i+1}. {EmailList[i][0]}\n' 

    update.message.reply_text(EmailAddress) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def findPassCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')

    return 'verify_password'


def verify_password (update: Update, context):
    logger.info("functioin findPass")
    user_input = update.message.text # Получаем текст, содержащий(или нет) Пароль

    PassRegex = re.compile(r'^.*(?=.{8,})(?=.*[a-zA-Z])(?=.*\d)(?=.*[!#$%&?/)/(/* "]).*$')
    
    # проверяем пароль на сложность
    if PassRegex.match(user_input):
        update.message.reply_text("Пароль сложный") # Отправляем сообщение пользователю
    else:
        update.message.reply_text("Пароль простой") # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def get_unmae (update: Update, context):
    #Подключаемся по ssh
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uname -mnr') #Вводим Об архитектуры процессора, имени хоста системы и версии ядра
    data = stdout.read() + stderr.read() # считываем вывод
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1].replace(' ', '\n') # Заменяем Заменяем символы для поывышения читабельности
    update.message.reply_text(data)

def get_release (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('lsb_release -d')
    data = stdout.readline()
    client.close()
    update.message.reply_text(data)

def get_uptime (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uptime -p')
    data = stdout.readline()
    client.close()
    update.message.reply_text(data)

def get_df (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def get_free (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def get_mpstat (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def get_w (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def get_auths (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('grep "session opened for user" /var/log/auth.log | tail -n 10')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def get_critical (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('grep -i "priority=critical" /var/log/syslog  | tail -n 10')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
        },
        fallbacks=[]
    )

    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('findEmail', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
        },
        fallbacks=[]
    )

    convHandlerFindPass = ConversationHandler(
        entry_points=[CommandHandler('verify_password', findPassCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_unmae", get_unmae))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerFindPass)

		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
