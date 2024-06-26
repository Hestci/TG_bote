from dotenv import load_dotenv
import os, logging, requests, re, paramiko, psycopg2
from psycopg2 import Error
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Подключаем логирование
logging.basicConfig(
    filename='logfile.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

logger = logging.getLogger(__name__)


load_dotenv()
#Для ТГ-бота
TOKEN = os.getenv('BOT_TOKEN')

# Для SSH соеденения
host = os.getenv('SSH_HOST')
port = os.getenv('SSH_PORT')
username = os.getenv('SSH_USER')
password = os.getenv('SSH_PASSWORD')

# Для SQL соеденения
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')



def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Данный бот умеет:\n \
/find_email - Находить почту в тексте \n\
/find_phone_number  Находить номера телефонов в тексте \n\
/verify_password Проверять пароль на сложность \n\
/get_emails Выводит записанные в базу данных Email \n\
/get_phone_numbers Выводит записанные в базу данных номера телефонов')
    update.message.reply_text('Осуществляет функции мониторинга на linux сервере \n\
/get_release Выводит информацию о релизе \n\
/get_uname Выводит информацию об архитектуры процессора, имени хоста системы и версии ядра. \n\
/get_uptime Выводит информацию о времени работы \n\
/get_df Выводит информацию о состоянии файловой системы \n\
/get_free Выводит информацию о состоянии оперативной памяти \n\
/get_mpstat Выводит информацию о производительности системы \n\
/get_w Выводит информацию о работающих в данной системе пользователях. \n\
/get_auths Выводит последние 10 логов \n\
/get_critical Выводит последние 5 критических ошибок \n\
/get_ps Выводит информацию о запущенных процессах \n\
/get_ss Выводит информацию об используемых портах. \n\
/get_apt_list Выводит все установленные пакеты или ищет в системе пакет, название которого будет запрошено пользователем \n\
/get_services Выводит информацию об запущенных сервисах \n\
/get_repl_logs Вывод логов о репликации SQL сервера')


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findPhoneNumbers (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов
    global Bufer1
    Bufer1 = ''
    phoneNumRegex = re.compile(r'((\+7|7|8)(\-| |)(|\()(\d{3})(|\))(\-| |)(\d{3}(\-| |)\d{2}(\-| |)\d{2}))') # Возможно не лучший по скорости но рабочей Regex

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены.\n Попробуйте снова')
        return # Завершаем выполнение функции
    
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        # Записываем очередной номер
        phoneNumbers += f'{i+1}. {phoneNumberList[i][0]}\n'
        Bufer1 += phoneNumberList[i][0]+','
        
        
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    update.message.reply_text("Хотите записать данные номера телефонов в базу данных?\n1 - Записать \n2 - Не запиовать")
    return 'SendPhoneNumber'

def SendPhoneNumber (update: Update, context):
    user_input = update.message.text
    phoneNumberList = Bufer1.split(',')[:-1]

    if (user_input == "1"):
        connection = None

        try:
            connection = psycopg2.connect(user=DB_USER,
                                        password=DB_PASS,
                                        host=DB_HOST,
                                        port=DB_PORT, 
                                        database=DB_NAME)
            
            cursor = connection.cursor()
            for i in phoneNumberList:
                cursor.execute("INSERT INTO Phonenumbers(Phone ) VALUES('"+i+"');")
            connection.commit()
            update.message.reply_text("Команда успешно выполнена")
        except (Exception, Error) as error:
            update.message.reply_text("Ошибка при работе с БД")
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            return ConversationHandler.END # Завершаем работу обработчика диалога
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
            return
    elif (user_input == "2"):
        return ConversationHandler.END # Завершаем работу обработчика диалога
    else: 
        update.message.reply_text("Неверный ввод! Взаимодействие прекращается")
        return ConversationHandler.END # Завершаем работу обработчика диалога
    
def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска Email-адресов:')

    return 'findEmail'


def findEmail (update: Update, context):
    global Bufer
    Bufer = ''
    logger.info("functioin findEmail")
    user_input = update.message.text # Получаем текст, содержащий(или нет) Email

    EmailRegex = re.compile(r'(([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+)')

    EmailList = EmailRegex.findall(user_input) # Ищем номера Email

    if not EmailList: # Обрабатываем случай, когда Email нет
        update.message.reply_text('Email адресса не найдены. \n Попробуйте снова')
        logger.info("Email is not found {user_inpu}")
        return # Завершаем выполнение функции
    
    EmailAddress = '' # Создаем строку, в которую будем записывать Email
    for i in range(len(EmailList)):
        # Записываем очередной номер
        EmailAddress += f'{i+1}. {EmailList[i][0]}\n'
        Bufer += EmailList[i][0]+','

    update.message.reply_text(EmailAddress) # Отправляем сообщение пользователю
    update.message.reply_text("Хотите записать данные номера телефонов в базу данных?\n1 - Записать \n2 - Не запиовать")
    return 'SendEmail'


def SendEmail (update: Update, context):
    user_input = update.message.text
    EmailList = Bufer.split(',')[:-1]


    if (user_input == "1"):
        connection = None

        try:
            connection = psycopg2.connect(user=DB_USER,
                                        password=DB_PASS,
                                        host=DB_HOST,
                                        port=DB_PORT, 
                                        database=DB_NAME)
            
            cursor = connection.cursor()
            for i in EmailList:
                cursor.execute("INSERT INTO Email(Mail) VALUES('"+i+"');")
            connection.commit()
            update.message.reply_text("Команда успешно выполнена")
        except (Exception, Error) as error:
            update.message.reply_text("Ошибка при работе с БД")
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            return ConversationHandler.END # Завершаем работу обработчика диалога
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
            return
    elif (user_input == "2"):
        return ConversationHandler.END # Завершаем работу обработчика диалога
    else: 
        update.message.reply_text("Неверный ввод! Взаимодействие прекращается")
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
    stdin, stdout, stderr = client.exec_command('grep -i "priority=critical" /var/log/syslog  | tail -n 5')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def get_ps (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def get_ss (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ss | tail -n 30')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def get_services (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('systemctl  --type=service --state=running')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def aptCommand(update: Update, context):
    update.message.reply_text("Введите:\nAll для вывода всех пакетов\nИмя паекта для поиска пакета")
    return 'choice'

def choice(update: Update, context):
    user_input = update.message.text

    if user_input == 'All':

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command('apt list | tail -n 20')
        data = stdout.read() + stderr.read() # считываем вывод
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1].replace('WARNING: apt does not have a stable CLI interface. Use with caution in scripts.', '')
        client.close()

        update.message.reply_text(data)

        return ConversationHandler.END
    else: 

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command('apt-cache show '+ user_input)
        data = stdout.read() + stderr.read() # считываем вывод
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        client.close()
        
        if (re.findall('E: No packages found', data)):
            update.message.reply_text("Несуществующие имя пакета. повторите попытку")
            return 'choice'
        else:
            update.message.reply_text(data)
            return ConversationHandler.END
        
def get_repl_logs (update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('grep "replication" /var/log/postgresql/postgresql-14-main.log | tail -n 10')
    data = stdout.read() + stderr.read() # считываем вывод
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    client.close()
    update.message.reply_text(data)

def get_emails (update: Update, context):

    connection = None

    try:
        connection = psycopg2.connect(user=DB_USER,
                                    password=DB_PASS,
                                    host=DB_HOST,
                                    port=DB_PORT, 
                                    database=DB_NAME)
        
        output = ""
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM email;")
        data = cursor.fetchall()
        for row in data:
             output += str(row[0]) + "." + row[1] + "\n"
        logging.info("Команда успешно выполнена")
        update.message.reply_text(output)
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def get_phone_numbers (update: Update, context):

    connection = None

    try:
        connection = psycopg2.connect(user=DB_USER,
                                    password=DB_PASS,
                                    host=DB_HOST,
                                    port=DB_PORT, 
                                    database=DB_NAME)
        
        output = ""
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Phonenumbers;")
        data = cursor.fetchall()
        for row in data:
             output += str(row[0]) + ". " + row[1] + "\n"
        logging.info("Команда успешно выполнена")
        update.message.reply_text(output)
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'SendPhoneNumber': [MessageHandler(Filters.text & ~Filters.command, SendPhoneNumber)],
        },
        fallbacks=[]
    )

    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'SendEmail': [MessageHandler(Filters.text & ~Filters.command, SendEmail)],
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

    convHandlerApt = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', aptCommand)],
        states={
            'choice': [MessageHandler(Filters.text & ~Filters.command, choice)],
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
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(convHandlerApt)
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerFindPass)

		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
