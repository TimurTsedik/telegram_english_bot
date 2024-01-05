import random

from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

from dict_jobs import random_word_from_base
from dict_jobs import random_engl_words
from dict_jobs import random_rus_words
from dict_jobs import if_user_not_exist
from dict_jobs import add_user
from dict_jobs import add_word_to_dict
from dict_jobs import delete_word_from_dict
from dict_jobs import custom_words_user_count
from credentials import token_bot

print('Start telegram bot...')

state_storage = StateMemoryStorage()
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []
e_word_to_add = {}
r_word_to_add = {}


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if if_user_not_exist(uid):
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0
    else:
        return userStep[uid]


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    if if_user_not_exist(cid):
        known_users.append(cid)
        add_user(cid, message.from_user.first_name)
        userStep[cid] = 0
        user_name = message.from_user.first_name
        bot.send_message(cid, f"Ну что, {user_name}, поучим Английский?")
    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    eng_rus = True
    if eng_rus:
        words = random_word_from_base(cid)
        target_word = words[0]
        translate = words[1]
        target_word_btn = types.KeyboardButton(target_word)
        buttons.append(target_word_btn)
        others = list(random_rus_words(target_word, cid))
    else:
        words = random_word_from_base(cid)
        target_word = words[1]
        translate = words[0]
        target_word_btn = types.KeyboardButton(target_word)
        buttons.append(target_word_btn)
        others = list(random_engl_words(target_word, cid))
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    cid = message.chat.id
    userStep[cid] = 3
    markup = types.ReplyKeyboardMarkup(row_width=2)
    hint = "Напишите слово, которое надо удалить"
    bot.send_message(message.chat.id, hint, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    markup = types.ReplyKeyboardMarkup(row_width=2)
    hint = "Напишите новое английское слово"
    bot.send_message(message.chat.id, hint, reply_markup=markup)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    sucsess = False
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    if len(userStep) == 0 or userStep.get(message.from_user.id) == 0:
        if len(userStep) == 0:
            userStep[message.from_user.id] = 0
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            target_word = data['target_word']
            if text == target_word:
                hint = show_target(data)
                hint_text = ["Отлично!❤", hint]
                hint = show_hint(*hint_text)
                sucsess = True
            else:
                for btn in buttons:
                    if btn.text == text:
                        btn.text = text + '❌'
                        break
                hint = show_hint("Допущена ошибка!",
                                 f"Попробуй ещё раз вспомнить слово {data['translate_word']}")
    elif userStep[message.from_user.id] == 1:
        e_word_to_add[message.from_user.id] = text
        hint = "Отлично, теперь введите значение слова " + text
        userStep[message.from_user.id] = 2
    elif userStep[message.from_user.id] == 2:
        r_word_to_add[message.from_user.id] = text
        userStep[message.from_user.id] = 0
        if add_word_to_dict(message.from_user.id, e_word_to_add[message.from_user.id],
                            r_word_to_add[message.from_user.id]) == 'Duplicate':
            hint = "Такое слово уже есть в словаре"
        else:
            hint = "Отлично, запишем слово " + text + ". в словаре уже "
            hint += custom_words_user_count(message.from_user.id) + " ваших слов"
        e_word_to_add.pop(message.from_user.id)
        r_word_to_add.pop(message.from_user.id)
    elif userStep[message.from_user.id] == 3:
        if not delete_word_from_dict(message.from_user.id, text):
            hint = "Такого слова нет в словаре"
        else:
            hint = "Отлично, вы удалили слово " + text + ". в словаре уже "
            hint += custom_words_user_count(message.from_user.id) + " ваших слов"
        userStep[message.from_user.id] = 0
    # markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)
    if sucsess:
        next_cards(message)


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)
