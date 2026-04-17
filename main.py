import telebot
from mysql.connector import connect
import random

connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

try:
    create_table_query = """
    CREATE TABLE solves(
        pupil_id INT NOT NULL,
        pupil_name VARCHAR(35) NOT NULL,
        prob_id INT NOT NULL,
        solve TEXT
    )
    """

    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()
except:
    pass

try:
    create_table_query = """
    CREATE TABLE tasks(
        prob_id INT NOT NULL AUTO_INCREMENT,
        PRIMARY KEY (prob_id),
        topic_name VARCHAR(35) NOT NULL,
        type_name VARCHAR(35) NOT NULL,
        prob_text TEXT,
        prob_img BLOB,
        prob_ans VARCHAR(30) NOT NULL,
        prob_solve TEXT
    )
    """

    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()
except:
    pass

try:
    create_table_query = """
    CREATE TABLE pupils(
        pupil_id INT NOT NULL,
        topic_name VARCHAR(35) NOT NULL,
        type_name VARCHAR(35) NOT NULL,
        type_interval FLOAT,
        correct_count INT,
        incorrect_count INT
    )
    """

    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()
except:
    pass


def convert_data(file_name):

    with open(file_name, 'rb') as file:

        binary_data = file.read()

    return binary_data


def add_problem_to_tasks(topic_name, type_name, prob_text, prob_ans, prob_img=None, prob_solve=None):
    connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

    if prob_img and prob_solve:
        insert_tasks_query = """
            INSERT INTO tasks
            (topic_name, type_name, prob_text, prob_img, prob_ans, prob_solve)
            VALUES ( %s, %s, %s, %s, %s, %s)
            """
        tasks_records = [(topic_name, type_name, prob_text, prob_img, prob_ans, prob_solve)]
    elif prob_img:
        insert_tasks_query = """
            INSERT INTO tasks
            (topic_name, type_name, prob_text, prob_img, prob_ans)
            VALUES ( %s, %s, %s, %s, %s)
            """
        tasks_records = [(topic_name, type_name, prob_text, prob_img, prob_ans)]
    elif prob_solve:
        insert_tasks_query = """
                    INSERT INTO tasks
                    (topic_name, type_name, prob_text, prob_ans, prob_solve)
                    VALUES ( %s, %s, %s, %s, %s)
                    """
        tasks_records = [(topic_name, type_name, prob_text, prob_ans, prob_solve)]
    else:
        insert_tasks_query = """
        INSERT INTO tasks
        (topic_name, type_name, prob_text, prob_ans)
        VALUES ( %s, %s, %s, %s)
        """
        tasks_records = [(topic_name, type_name, prob_text, prob_ans)]

    with connection.cursor() as cursor:
        cursor.executemany(insert_tasks_query,
                           tasks_records)
        connection.commit()

    add_problem_to_pupils(topic_name, type_name)


def add_problem_to_pupils(now_topic, now_type):
    connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

    show_table_query = "SELECT pupil_id FROM pupils WHERE type_name = %s AND topic_name = %s"
    with connection.cursor() as cursor:
        cursor.execute(show_table_query, [now_type, now_topic])
        result = cursor.fetchall()
        if result:
            return

    show_table_query = "SELECT pupil_id FROM pupils"
    with connection.cursor() as cursor:
        cursor.execute(show_table_query)
        result = cursor.fetchall()
        for pupil in result:
            pupil = pupil[0]
            insert_pupils_query = """
            INSERT INTO pupils
            (pupil_id, topic_name, type_name, type_interval, correct_count, incorrect_count)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            pupils_records = [(pupil, now_topic, now_type, 1, 0, 0)]

            with connection.cursor() as cursor:
                cursor.executemany(insert_pupils_query, pupils_records)
                connection.commit()


def read_exact_type(now_topic, now_type):
    connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

    select_tasks_query = "SELECT * FROM tasks WHERE type_name = %s AND topic_name = %s"
    with connection.cursor() as cursor:
        cursor.execute(select_tasks_query, (now_type, now_topic))
        result = cursor.fetchall()
        lst = list()
        for row in result:
            lst.append(row)
        n = len(lst)
        return lst[random.randint(0, n - 1)]


def list_of_topics():
    connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

    select_tasks_query = "SELECT topic_name FROM tasks"
    with connection.cursor() as cursor:
        cursor.execute(select_tasks_query)
        result = cursor.fetchall()
        a = set()
        for row in result:
            a.add(row[0])
        return list(a)


def list_of_types(now_topic):
    connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

    select_tasks_query = "SELECT type_name FROM tasks WHERE topic_name = %s"
    with connection.cursor() as cursor:
        cursor.execute(select_tasks_query, [now_topic])
        result = cursor.fetchall()
        a = set()
        for row in result:
            a.add(row[0])
        return list(a)


def add_solve_to_solves(pupil_id, prob_id, message):
    connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    bot.send_message(pupil_id, "Пожалуйста, пришлите своё решение.", reply_markup=keyboard)
    answer = []  # обработка сообщения от пользователя
    bot.register_next_step_handler(message, answer_message, answer)
    while not answer:
        pass
    solve = answer[0]
    insert_tasks_query = """
            INSERT INTO solves
            (pupil_id, pupil_name, prob_id, solve)
            VALUES ( %s, %s, %s, %s)
            """
    tasks_records = [(pupil_id, message.from_user.username, prob_id, solve)]

    with connection.cursor() as cursor:
        cursor.executemany(insert_tasks_query,
                           tasks_records)
        connection.commit()


def require_teacher(teacher):
    connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

    select_solves_query = "SELECT * FROM solves"
    with connection.cursor() as cursor:
        cursor.execute(select_solves_query)
        result = cursor.fetchall()
        for row in result:
            select_tasks_query = "SELECT prob_text FROM tasks WHERE prob_id = %s"
            cursor.execute(select_tasks_query, [row[2]])
            prob_t = cursor.fetchall()
            mes = f"Ученик: {row[1]}\nЗадача: {prob_t[0][0]}\nРешение: {row[3]}"
            bot.send_message(teacher, mes)

    drop_table_query = "DROP TABLE solves"
    with connection.cursor() as cursor:
        cursor.execute(drop_table_query)

    try:
        create_table_query = """
        CREATE TABLE solves(
            pupil_id INT NOT NULL,
            pupil_name VARCHAR NOT NULL,
            prob_id INT NOT NULL,
            solve TEXT
        )
        """

        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
    except:
        pass


class Flashcard:
    def __init__(self, question, answer, interval=1, correct_count=0, incorrect_count=0):
        self.question = question
        self.answer = answer
        self.interval = interval  # Начальный интервал повторения в днях
        self.correct_count = correct_count  # Количество правильных ответов
        self.incorrect_count = incorrect_count  # Количество неправильных ответов

    def update_interval(self):
        # Количество ответов на карточку
        total_attempts = self.correct_count + self.incorrect_count
        # Процент правильных ответов на карточку
        correct_percentage = self.correct_count / total_attempts if total_attempts > 0 else 0
        # Изменяем интервал повторения в зависимости от процента правильных ответов
        self.interval = 1 + (correct_percentage - 0.5) * 2  # Интервал будет варьироваться от 0.5 до 1.5


def run_exact_topic(now_topic, now_pupil, bot, message):
    flashcards = list()
    now_types = list_of_types(now_topic)
    for typ in now_types:
        weights = weight_of_type_for_pupil(now_topic, typ, now_pupil)
        flashcard = Flashcard(typ, "Paris", weights[0], weights[1], weights[2])
        flashcards.append(flashcard)

    while True:
        flashcards.sort(key=lambda card: card.interval)
        for card in flashcards:
            prob = read_exact_type(now_topic, card.question)
            # (3, 'topic2', 'type2', 'solve the problem x + x = 1', None, '0.5', '2*x = 1 => x = 0.5')
            # print("Problem:", prob[3])  # tg def that prints problem
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            bot.send_message(now_pupil, "Вот какая-то задачка:" + prob[3] +
                             "\nЧтобы остановиться, напишите stop", reply_markup=keyboard)
            answer = []  # обработка сообщения от пользователя
            bot.register_next_step_handler(message, answer_message, answer)
            while not answer:
                pass
            user_answer = answer[0]
            if user_answer.lower() == 'stop':
                all_topics = list_of_topics()
                keyboard = telebot.types.InlineKeyboardMarkup()
                for topic in all_topics:
                    keyboard.add(telebot.types.InlineKeyboardButton(text=topic, callback_data="p" + topic))
                bot.send_message(now_pupil,
                                 "Вы можете заново выбрать одну из тем:",
                                 reply_markup=keyboard)
                return
            is_correct = user_answer.strip().lower() == prob[5].lower()
            if is_correct:
                card.correct_count += 1
            else:
                card.incorrect_count += 1
            card.update_interval()
            # print("Your answer is", "correct!" if is_correct else "incorrect. Please send your solution.")
            if is_correct:
                bot.send_message(now_pupil, "Ваш ответ правильный!")
            else:
                bot.send_message(now_pupil, "Ваш ответ неправильный.")
                add_solve_to_solves(now_pupil, prob[0], message)

    connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

    for card in flashcards:
        update_query = """
        UPDATE
            pupils
        SET
            type_interval = %s,
            correct_count = %s,
            incorrect_count = %s
        WHERE
            pupil_id = %s AND topic_name = %s AND type_name = %s
        """
        with connection.cursor() as cursor:
            params = [card.interval, card.correct_count, card.incorrect_count, now_pupil, now_topic, card.question]
            cursor.execute(update_query, params)
            connection.commit()


def answer_message(message, answer):
    answer.append(message.text)


def add_new_pupil(new_id):
    connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

    select_pupils_query = "SELECT * FROM pupils WHERE pupil_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(select_pupils_query, [new_id])
        result = cursor.fetchall()
        if result:
            return
        now_topics = list_of_topics()
        for topic in now_topics:
            now_types = list_of_types(topic)
            for cur_type in now_types:
                insert_pupils_query = """
                        INSERT INTO pupils
                        (pupil_id, topic_name, type_name, type_interval, correct_count, incorrect_count)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                pupils_records = [(new_id, topic, cur_type, 1, 0, 0)]

                with connection.cursor() as cursor:
                    cursor.executemany(insert_pupils_query, pupils_records)
                    connection.commit()


def weight_of_type_for_pupil(now_topic, now_type, now_pupil):
    connection = connect(
        host="localhost",
        user="root",
        password="aes16fk09",
        database="train_brain",
    )

    select_pupils_query = "SELECT * FROM pupils WHERE pupil_id = %s AND topic_name = %s AND type_name = %s"
    with connection.cursor() as cursor:
        cursor.execute(select_pupils_query, [now_pupil, now_topic, now_type])
        result = cursor.fetchall()
        if not result:
            return [1, 0, 0]
        return [result[0][3], result[0][4], result[0][5]]


TOKEN = "6693567428:AAGfGM8EHz473RFwjXbIURRllEtwlU7rzFY"
bot = telebot.TeleBot(TOKEN)

TEACHERS = [851895817, 1886737119]  # aesfk and swoodge


@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    # приветствие пользователя, выбор учитель/ученик
    name = message.chat.first_name
    chat_id = message.chat.id
    add_new_pupil(chat_id)
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).row("Учитель", "Ученик")
    bot.send_message(chat_id, f"Здравствуйте, {name}! Пожалуйста, выберите роль:", reply_markup=keyboard)

    # Направляем в функцию выбора темы
    bot.register_next_step_handler(message, handle_branch_choice_start)


def handle_branch_choice_start(message):
    chat_id = message.chat.id
    branch_choice = message.text

    if branch_choice == "Учитель":
        # Проверка ID пользователя
        if chat_id in TEACHERS:
            bot.send_message(chat_id, f"Добавлять новые задачи можно с помощью команды /document. "
                                      f"Запросить непроверенные решения можно с помощью /solutions")
        else:
            bot.send_message(chat_id, f"К сожалению, Вас нет в списки учителей. "
                                      f"Если Вы считаете это ошибкой, то свяжитесь с разработчиками: @swoodge и @aesfk. "
                                      f"Попробовать снова Вы можете с помощью команды /start или /help.")
    elif branch_choice == "Ученик":
        # Работаем с учеником
        all_topics = list_of_topics()
        keyboard = telebot.types.InlineKeyboardMarkup()
        for topic in all_topics:
            keyboard.add(telebot.types.InlineKeyboardButton(text=topic, callback_data="p" + topic))
        bot.send_message(chat_id,
                         "Добро пожаловать! Это бот, который подбирает задачки на интересующую Вас тему. Вот они:",
                         reply_markup=keyboard)
    else:
        # Если ошибка
        keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True).row("Учитель", "Ученик")
        bot.send_message(chat_id, "Выберите, пожалуйста, из двух вариантов: Ученик, Учитель", reply_markup=keyboard)
        bot.register_next_step_handler(message, handle_branch_choice_start)


@bot.callback_query_handler(func=lambda call: call.data[:1] == "p")
def callback_function2(callback_obj):
    user_give_task(callback_obj, callback_obj.data[1:])
    bot.answer_callback_query(callback_query_id=callback_obj.id)


def user_give_task(message, text):
    try:
        bot.send_message(message.from_user.id, "Вы выбрали тему: " + text +
                         f"\nВоспользуйтесь командой /run {text}, чтобы начать решать задачи!")
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так.")


@bot.message_handler(commands=['run'])
def run_topic(message):
    topic = message.text[5:]
    run_exact_topic(topic, message.from_user.id, bot, message)


@bot.message_handler(commands=['document'])
def document_command(message):
    chat_id = message.chat.id
    if chat_id in TEACHERS:
        try:
            keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            bot.send_message(chat_id, "Напишите название темы, в которую бы Вы хотели добавить задачу",
                             reply_markup=keyboard)
            answer = []  # обработка сообщения от пользователя
            bot.register_next_step_handler(message, answer_message, answer)
            while not answer:
                pass
            new_topic = answer[0]
            bot.send_message(chat_id, "Напишите название карточки, в которую бы Вы хотели добавить задачу",
                             reply_markup=keyboard)
            answer = []  # обработка сообщения от пользователя
            bot.register_next_step_handler(message, answer_message, answer)
            while not answer:
                pass
            new_type = answer[0]
            bot.send_message(chat_id, "Напишите условие задачи",
                             reply_markup=keyboard)
            answer = []  # обработка сообщения от пользователя
            bot.register_next_step_handler(message, answer_message, answer)
            while not answer:
                pass
            prob_text = answer[0]
            bot.send_message(chat_id, "Напишите ответ на задачу",
                             reply_markup=keyboard)
            answer = []  # обработка сообщения от пользователя
            bot.register_next_step_handler(message, answer_message, answer)
            while not answer:
                pass
            prob_ans = answer[0]
            bot.send_message(chat_id, "Если Вы хотите добавить картинку к задаче, пришлите ее в формате файла. "
                                      "Иначе напишите 'нет'.",
                             reply_markup=keyboard)
            answer = []  # обработка сообщения от пользователя
            bot.register_next_step_handler(message, answer_file, answer)
            while not answer:
                pass
            img = answer[0]
            if type(img) == str and img.lower().strip() == "нет":
                add_problem_to_tasks(new_topic, new_type, prob_text, prob_ans)
            elif img == 0:
                bot.send_message(chat_id, f"Что-то пошло не так. Попробовать снова можно с помощью "
                                          f"команды /start.")
                return
            else:
                add_problem_to_tasks(new_topic, new_type, prob_text, prob_ans, prob_img=img)
            bot.send_message(chat_id, f"Задача успешно добавлена!")
        except:
            bot.send_message(chat_id, f"Что-то пошло не так. Попробовать снова можно с помощью "
                                      f"команды /start.")
    else:
        bot.send_message(chat_id, f"К сожалению, Вас нет в списки учителей. "
                                  f"Если Вы считаете это ошибкой, то свяжитесь с разработчиками: @swoodge и @aesfk."
                                  f" Попробовать снова Вы можете с помощью команды /start.")


def answer_file(message, answer):
    if message.content_type == 'text' and message.text.lower().strip() == "нет":
        answer.append(message.text)
        return
    if message.content_type == 'document':
        file_name = message.document.file_name
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_name, 'r+b') as new_file:
            new_file.write(downloaded_file)
        with open(new_file.name, 'rb') as file:
            a = file.read()
        answer.append(a)
    else:
        answer.append(0)


@bot.message_handler(commands=['solutions'])
def solutions_command(message):
    teacher = message.from_user.id
    if teacher not in TEACHERS:
        bot.send_message(teacher, f"К сожалению, Вас нет в списки учителей. "
                                  f"Если Вы считаете это ошибкой, то свяжитесь с разработчиками: @swoodge и @aesfk."
                                  f" Попробовать снова Вы можете с помощью команды /start.")
        return
    require_teacher(teacher)


bot.infinity_polling()
