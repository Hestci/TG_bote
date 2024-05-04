from dotenv import load_dotenv
import os, logging, requests, re
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

logger = logging.getLogger(__name__)


load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
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
    logger.info("functioin start")
    user_input = update.message.text # Получаем текст, содержащий(или нет) Email

    logger.info("User input {user_inpu}")

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


def echo(update: Update, context):
    update.message.reply_text(update.message.text)


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
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
