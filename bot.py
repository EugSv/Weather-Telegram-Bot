from telebot import *
import requests

bot = telebot.TeleBot('###')

appid = "###"

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/weather':
        bot.send_message(message.from_user.id, "В каком городе вас интересует погода?")
        bot.register_next_step_handler(message, get_city_name)
    else:
        bot.send_message(message.from_user.id, 'Напиши /weather')

def get_city_name(message):
    city = message.text
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                           params={'q': city, 'type': 'like', 'units': 'metric', 'APPID': appid})
        data = res.json()
        cities = ["{} ({})".format(d['name'], d['sys']['country'])
                  for d in data['list']]
        city_id = data['list'][0]['id']

        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                     params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        weather_description = data['weather'][0]['description']
        temp = data['main']['temp']
        temp_min = data['main']['temp_min']
        temp_max = data['main']['temp_max']

        bot.send_message(message.from_user.id, f'В городе {city} {weather_description}, температура: {temp}°C, минимальная температура: {temp_min}°C, максимальная температура: {temp_max}°C')

        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        keyboard.add(key_yes)
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = 'Хотите еще?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

    except Exception as e:
        print("Exception:", e)
        bot.send_message(message.from_user.id, 'Произошла ошибка. Попробуйте еще раз.')

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, "В каком городе вас интересует погода?")
        bot.register_next_step_handler(call.message, get_city_name)
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Был рад помочь')

bot.polling(none_stop=True, interval=0)