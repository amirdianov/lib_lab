import logging
import sqlite3
import time
from typing import Any

from telegram import Update, ForceReply, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, CommandHandler, Filters, \
    CallbackContext, PrefixHandler

from registration import check_registration
from db_func import *
from subscription import activated_subscription
from bot import methods_func

#CONSTANTS
def create_back_to_main_menu_button():
    return InlineKeyboardButton(text='♻Вернуться в главное меню♻',
                                        callback_data='back_to_main_menu')
def create_back_to_prev_state_button():
    return InlineKeyboardButton(text='🔺Вернуться назад🔺',
                                        callback_data='back_to_prev_state')

def find_book(book):
    """use db"""
    return True

def delete_telegram_message(callback):
    try:
        print('message_id:', callback.inline_message_id)
        callback.delete_message()
    except Exception as ex:
        print(ex, '\nMessage has already deleted')


def inner_take_book_user(self, id):
    if check_registration(id):
        return True
    else:
        self.message.reply_text('Пройдите регистрацию💻')
        return False

def take_book_user(self: Update, context: Any):
    "checking user in db"
    user_id = self.message.from_user.id
    try:
        return inner_take_book_user(self, user_id)
    except IndexError:
        user_id = self.message.chat.id
        return inner_take_book_user(self, user_id)

def take_book_type(self: Update, context: Any):
    reply_keyboard = [['title', 'genre'], ['author', 'rating']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    self.message.reply_text('По какому критерию книги показать?', reply_markup=markup)

def inner_find_book_function_template(user, context):
    user.message.reply_text(text=f'📚Введите {context.user_data["criterion"] } книги:',
    reply_markup=InlineKeyboardMarkup([[create_back_to_prev_state_button()],
                                       [create_back_to_main_menu_button()]],
    one_time_keyboard=True,
    resize_keyboard=True))


def inner_find_book_function(user: Update, context: Any, canon: str):
    context.user_data['criterion'] = canon
    print('context.user_data', context.user_data['criterion'])
    inner_find_book_function_template(user, context)

def inner_find_book_function_for_inline(user: Update, context: Any):
    print('context.user_data', context.user_data['criterion'])
    return inner_find_book_function_template(user, context)

def inner_take_book(self: Update, context: Any, user_message: str, criterion: str):
    user_id = self.message.from_user.id
    is_subscriber = activated_subscription(user_id)
    needed_books = main_get_item(db_name='Books', some_column=criterion, value=user_message,
    column1='title', column2='name', column3='subscription_need')
    def smile(status):
        return '🔒' if status else '✅'
    buttons_list: list[list[str]] = []
    urls_list = main_get_item(column1='url', db_name='Books', some_column=criterion, value=user_message)
    for index, book_name in enumerate(needed_books):
        kw_args = {}
        if is_subscriber or not book_name[2]:
            kw_args['url'] = urls_list[index][0][:-1]
        else:
            kw_args['callback_data'] = 'need_to_get_subscription'
        button = InlineKeyboardButton(text=smile(book_name[2]) + book_name[0] + ' ' + book_name[1], **kw_args)
        buttons_list.append([button])
    #back_to_main_menu = InlineKeyboardButton(text='♻Вернуться в главное меню♻',
    #                                         callback_data='back_to_main_menu')
    buttons_list.extend([[create_back_to_prev_state_button()], [create_back_to_main_menu_button()]])
    print(buttons_list)
    reply_markup_books = InlineKeyboardMarkup(buttons_list, one_time_keyboard=True,
                                                            resize_keyboard=True)
    self.message.reply_text('📋Список книг, удовлетворяющих выбранным критериям:',
                            reply_markup=reply_markup_books)

"""def inner_check_book(self, context: Any):
        print("callback_query:", self.callback_query.data)
        response = self.callback_query
        response.answer()
        if response.data == 'need_to_get_subscription':
            reply_buttons = [['😍Да', 'Нет...']]
            reply_button_markup = ReplyKeyboardMarkup(reply_buttons, one_time_keyboard=True,resize_keyboard=True)
            response.message.reply_text('К сожалению, эта книга доступна только по подписке😔\n'
                            'Желаете ли вы её оформить?', reply_markup=reply_button_markup)
            return 'subscribe_stage'
        elif response.data == 'back_to_prev_state':
            return User.find_book_function_for_inline(self, context)
        elif response.data == 'back_to_main_menu':
            methods_func(response, context)
            return ConversationHandler.END
"""

def inner_handle_subscription_case(self, context):
        if self.message.text == 'Нет...':
            self.message.reply_text('🔁🔁 Переходим в основное меню 🔁🔁')
            methods_func(self, context)
        else:
            self.message.text = 'Да, давайте оформим 👌'
            subscription_need_ans(self, context)


def take_book_1_user(self: Update, context: Any):
    value = self.message.text
    self.message.reply_text('\n'.join(get_items('url', 'Books', 'title', value)))
