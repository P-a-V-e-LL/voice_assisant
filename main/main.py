import os
import time
import speech_recognition as sr
from fuzzywuzzy import fuzz
import pyttsx3
import datetime
import webbrowser
import random
import platform
import requests
from mutagen.mp3 import MP3
from googletrans import Translator
import threading
from currency_converter import CurrencyConverter

sites = {}

# настройки
options = {
    "alias": ('оксана', 'окс', 'окси'),
    "tbr": (
    'скажи', 'расскажи', 'покажи', 'сколько', 'произнеси', 'запусти', 'открой', 'как', 'поставь', 'переведи', 'засеки',
    'сколько будет'),
    "cmds": {
        "ctime": ('текущее время', 'сейчас времени', 'который час', 'сколько времени'),
        "explorer": ('мой компьютер', 'проводник'),
        "calc": ('прибавить', 'умножить', 'разделить', 'степень', 'вычесть', 'поделить', 'х', '+', '-', '/'),
        "game_start": ('игрушку', 'игру'),
        "conv": ("валюта", "конвертер", "доллар", 'руб', 'евро'),
        "joke": ('расскажи анекдот', 'рассмеши меня', 'ты знаешь анекдоты', 'шутка'),
        "user_help": ('что ты можешь', 'что ты умеешь'),
        "internet": ("вк", "vk", "контакт", "гугл", "google", "google chrome", "хром", "youtube"
                     "сайт", 'вконтакте', "ютуб",
                     "алиэкспресс", "aliexpress", "wikipedia", "wiki",
                     "википедия", "вики", "орел универ", "универ", "огу", "агу", "gmail"),
        "user_settings": ('пользовательские настройки', 'настройки'),  # не прописаны
        "translator": ("переводчик","translate"),
        "music": ("музыку", "музыка", "воспроизведи музыку"),
        "startStopwatch": ('запусти секундомер', "включи секундомер", "засеки время"),
        "stopStopwatch": ('останови секундомер', "выключи секундомер", "останови"),
        "goodbye": ('прощай', 'до свидания', 'до скорого', 'аривидерчи', 'пока')
    }
}


###########################funcs#############################

def HelperSay(whatSpeek):
    print(whatSpeek)
    speak_engine.say(whatSpeek)
    speak_engine.runAndWait()
    speak_engine.stop()


def ListenUserVoice(recognizer, audio):
    try:
        global voice
        voice = recognizer.recognize_google(audio, language="ru-RU").lower()
        print("Распознано: " + voice)
        if voice.startswith(options["alias"]):  # обращение к помошнику
            cmd = voice
            for i in options['alias']:
                cmd = cmd.replace(i, "").strip()
            for i in options['tbr']:
                cmd = cmd.replace(i, "").strip()

            cmd = RecognizeCommand(cmd)
            ExecuteCommand(cmd['cmd'])

    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print("[log] Неизвестная ошибка, проверьте интернет!")


def RecognizeCommand(cmd):
    RC = {'cmd': '', 'percent': 0}
    for c, v in options['cmds'].items():
        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > RC['percent']:
                RC['cmd'] = c
                RC['percent'] = vrt
    return RC


def convertation():
    class CurrencyError(Exception):
        pass
    c = CurrencyConverter()
    money = None
    from_currency = None
    to_currency = None
    list_of_conv = voice.split()
    if len(list_of_conv) > 4:
        list_of_conv = list_of_conv[1:]
    else:
        print()
    while money is None:
        try:
            money = list_of_conv[0]
        except ValueError:
            HelperSay("Скажите, к примеру: 50 долларов в рубли")
            break
    while from_currency is None:
        try:
            list_of_conv[0] = int(list_of_conv[0])
        except ValueError:
            HelperSay("Скажите, к примеру: 50 долларов в рубли")
            break
        try:
            if "руб" in list_of_conv[1]:
                from_currency = "RUB"
            elif "дол" in list_of_conv[1]:
                from_currency = "USD"
            elif "евр" in list_of_conv[1]:
                from_currency = "EUR"
            if from_currency not in c.currencies:
                raise CurrencyError

        except (CurrencyError, IndexError):
            from_currency = None
            HelperSay("Скажите, например: 50 долларов в рубли")
            break

    while to_currency is None:
        try:
            list_of_conv[0] = int(list_of_conv[0])
        except ValueError:
            return None
        try:
            if "руб" in list_of_conv[3]:
                to_currency = "RUB"
            elif "дол" in list_of_conv[3]:
                to_currency = "USD"
            elif "евр" in list_of_conv[3]:
                to_currency = "EUR"
            if to_currency not in c.currencies:
                raise CurrencyError

        except (CurrencyError, IndexError):
            to_currency = None
            HelperSay("Скажите, например: 50 долларов в рубли")
            break
    while True:
        try:
            HelperSay(f"{money} {from_currency} в {to_currency} - "
                f"{round(c.convert(money, from_currency, to_currency), 2)}")
            break
        except ValueError:
            HelperSay("Скажите, например: 50 долларов в рубли")
            break


def ctime():
    now1 = datetime.datetime.now()
    HelperSay("Сейчас " + str(now1.hour) + ":" + str(now1.minute))


def explorer():
    HelperSay("Открываю проводник")
    os.system(f'start {os.path.realpath("C:/")}')


def game_start():
    HelperSay("Запускаю игру")
    os.system(f'start RacerGame.py')


def user_help():
    HelperSay("ВЫ обращаетесь ко мне по имени а потом "
              "говорите команду и я её выполняю. Вот список того, что я могу: ")
    print("Сказать время\n Рассказать анекдот\n"
          " Запустить сайт из перечисленных (Google, Firefox, Aliexpress, vk, oreluniver)\n "
          "Открыть проводник\n Посчитать на калькуляторе\n"
          " Выполнить перевод валюты (доступно RUB, USD, EUR)\n Запустить музыку из папки\n"
          " Запустить встроенную игру\n Поставить секундомер\n")


def user_settings():
    HelperSay("Открываю настройки")
    UserSettings()


def music():
    thread2 = threading.Thread(target=music_play())
    thread2.start()
    thread2.join()


def startStopwatch():
    HelperSay("Секундомер запущен")
    global startTime
    startTime = time.time()


def stopStopwatch():
    global startTime
    if startTime != 0:
        Time = time.time() - startTime
        HelperSay(f"Прошло {round(Time // 3600)} часов {round(Time // 60)} минут {round(Time % 60, 2)} секунд")
        startTime = 0
    else:
        HelperSay("Секундомер не включен")


def gb():
    HelperSay("До свиданья!")
    os.abort()


def UserSettings():
    if platform.system() == 'Windows':
        os.system('cls')  # For Windows
    else:
        os.system('clear')  # For Linux/OS X
    loop = True
    while loop:  ## While loop which will keep going until loop = False
        print(30 * "-", "MENU", 30 * "-")
        print("1. Добавить сайт (нет)")
        print("2. Изменить голос ассистента (нет)")
        print("3. Изменить устройство ввода (нет)")
        print("4. Указать путь к пользовательской игре (нет)")
        print("5. Exit")
        print(67 * "-")  ## Displays menu
        choice = input("Enter your choice [1-5]: ")

        if choice == 1:
            print("Menu 1 has been selected")
        ## Код
        elif choice == 2:
            print("Menu 2 has been selected")
        ## Код
        elif choice == 3:
            print("Menu 3 has been selected")
        ## Код
        elif choice == 4:
            print("Menu 4 has been selected")
        ## Код
        elif choice == 5:
            print("Menu 5 has been selected")
            ## Код
            loop = False  # This will make the while loop to end as not value of loop is set to False
        else:
            # Any integer inputs other than values 1-5 we print an error message
            print("Wrong option selection. Enter any key to try again..")


def GetJocke():
    file = open('Jockes.txt', 'r', encoding='utf-8')
    for line in file:
        jockesToUser.append(line)
    HelperSay(random.choice(jockesToUser))


def music_play():
    import pyglet
    DIR = 'Music/'
    filename = random.choice(os.listdir(DIR))
    f = MP3('Music/' + filename)
    song = pyglet.media.load(os.path.join(DIR, filename))
    song.play()
    pyglet.app.run()


def translate():
    url = 'https://translate.yandex.net/api/v1.5/tr.json/translate?'
    key = 'trnsl.1.1.20190227T075339Z.1b02a9ab6d4a47cc.f37d50831b51374ee600fd6aa0259419fd7ecd97'
    text = voice.split()[1:]
    lang = 'en-ru'
    r = requests.post(url, data={'key': key, 'text': text, 'lang': lang}).json()
    try:
        HelperSay(r["text"])
    except:
        HelperSay("Обратитесь к переводчику, начиная со слова 'Переводчик'")


def calculator():
    try:
        list_of_nums = voice.split()
        num_1, num_2 = int((list_of_nums[-3]).strip()), int((list_of_nums[-1]).strip())
        opers = [list_of_nums[0].strip(), list_of_nums[-2].strip()]
        for i in opers:
            if 'дел' in i or 'множ' in i or 'лож' in i or 'приба' in i or 'выч' in i or i == 'x' or i == '/' or i == '+' or i == '-' or i == '*' or "степен" in i or "в степен" in i:
                oper = i
                break
            else:
                oper = opers[1]
        if oper == "+" or 'слож' in oper:
            ans = num_1 + num_2
        elif oper == "-" or 'выче' in oper:
            ans = num_1 - num_2
        elif oper == "х" or 'множ' in oper:
            ans = num_1 * num_2
        elif oper == "/" or 'дел' in oper:
            if num_2 != 0:
                ans = num_1 / num_2
            else:
                HelperSay("Делить на ноль невозможно")
        elif "степен" in oper or oper == "**":
            ans = num_1 ** num_2
        HelperSay("Будет {0}".format(ans))
    except:
        HelperSay("Скажите, например: Сколько будет 2+2?")


def browser():
    global sites
    sites = {"https://vk.com": ["vk", "вк"], 'https://www.youtube.com/': ['youtube', 'ютуб'],
             'https://ru.wikipedia.org': ["вики", "wiki"],
             'https://ru.aliexpress.com': ['али', 'ali', 'aliexpress', 'алиэспресс'],
             'http://google.com': ['гугл', 'google'],
             'https://www.amazon.com': ['амазон', 'amazon'],
             'https://www.apple.com/ru': ['apple', 'эпл'],
             'http://www.oreluniver.ru/': ['огу', 'агу', 'орел универ'],
             'https://mail.google.com/mail/u/0/': ['gmail']}
    site = voice.split()[-1]
    for k, v in sites.items():
        for i in v:
            if i not in site.lower():
                open_tab = None
            else:
                open_tab = webbrowser.open_new_tab(k)
                break
        if open_tab is not None:
            break

exec = {
        "ctime": ctime,
        "explorer": explorer,
        "calc": calculator,
        "game_start": game_start,
        "conv": convertation,
        "joke": GetJocke,
        "user_help": user_help,
        "internet": browser,
        "user_settings": user_settings,
        "translator": translate,
        "music": music,
        "startStopwatch": startStopwatch,
        "stopStopwatch": stopStopwatch,
        "goodbye": gb,
    }

def ExecuteCommand(cmd):
    global exec
    if cmd not in exec.keys():
        HelperSay("Я еще так не умею.")
    else:
        exec[cmd]()


#########################################################################

jockesToUser = []
voice = "str"
startTime = 0

speak_engine = pyttsx3.init()

voices = speak_engine.getProperty('voices')
speak_engine.setProperty('voice', voices[0].id)

now = datetime.datetime.now()
if now.hour >= 6 and now.hour < 12:
    HelperSay("Доброе утро!")
elif now.hour >= 12 and now.hour < 18:
    HelperSay("Добрый день!")
elif now.hour >= 18 and now.hour < 23:
    HelperSay("Добрый вечер!")
else:
    HelperSay("Доброй ночи!")
HelperSay("Я слушаю")

# Запуск программы

if platform.system() == 'Linux':
    chrome_path = '/usr/bin/google-chrome %s'
elif platform.system() == 'Windows':
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

r = sr.Recognizer()
m = sr.Microphone(device_index=0)

while True:
    with m as source:
        print("Слушаю...")
        r.adjust_for_ambient_noise(source, duration=0.1)
        audio = r.listen(source)
    ListenUserVoice(r, audio)

