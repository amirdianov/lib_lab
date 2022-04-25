import logging
import sqlite3
import time
from typing import Any

from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, CommandHandler, Filters, \
    CallbackContext, PrefixHandler
from db_func import add_item


def check_registration(user_id: int) -> bool:
    """u can make this method not static, how u can - make"""
    conn = sqlite3.connect('library.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT * from Users WHERE id = ?", (user_id, ))
    res = cursor.fetchone()
    if res[3]:
        return True
    return False


def begin_registration_user(update: Update, context: Any):
    """make people to registred and insert to db"""
    """use ConversationHandler to insert user for db"""
    if check_registration(update.message.from_user.id):
        update.message.reply_text('Вы уже зарегистрированы в системе👍')
        return ConversationHandler.END
    else:
        update.message.reply_text('Давайте регистрироваться 📝.\n Введите свои фамилию и имя через пробел.\n'
                                  'Допустимые символы: заглавные и строчные буквы кириллицы и пробел.\n'
                                  'Например, Иванов Иван.😉')
        return 1


def handle_user_data(update: Update, context: Any):
    """handle user data and insert it into db"""
    context.user_data['name_surname']: str = update.message.text.strip().title()
    re_expression: str = re.search(r'[А-Яа-я]+ [А-Яа-я]+', context.user_data['name_surname'])
    if re_expression is None or re_expression.group() != \
        context.user_data['name_surname']:
        update.message.reply_text('Фамилия и имя введены неправильно ⛔️😪\n'
        '🔄 Давай попробуем ввести их заново, но сначала я напомню основные правила ввода:\n'
        'Допустимые символы: заглавные и строчные буквы кириллицы и пробел.\n'
        'Например, Иванов Иван.😉')
        return False
    update_items('users', 'name_surname', 'telegram_id', context.user_data['name_surname'],
                 update.message.from_user.id)
    update_items('users', 'registration', 'telegram_id', True,
                 update.message.from_user.id)
    update.message.reply_text('✅ Регистрация прошла успешно.\n'
                              f'{context.user_data["name_surname"]}, добро пожаловать '
                              f'в сообщество нашей библиотеки! 🎆')
    return True




