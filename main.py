import sqlite3
import datetime as dt
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.datatables import MDDataTable
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.metrics import dp

sql_connection = sqlite3.connect('database.db')
cursor = sql_connection.cursor()
Window.clearcolor = (220 / 255, 220 / 255, 220 / 255, 1)
Window.maximize()


def time_now():
    utc_time = dt.datetime.utcnow()
    period = dt.timedelta(hours=3)
    moscow_time = utc_time + period
    return moscow_time


# 'MainScreen' contains two screens: Simulator and TableResults
class MainScreen(ScreenManager):
    pass


class Simulator(Screen):
    # 'choose_enabled' is required for the position of the buttons
    choose_enabled = BooleanProperty(True)
    # Username is saved after "start", the flag returns into "True" after "restart"
    save_user_name = False

    def give_name(self, text_input):
        if text_input.text != '':
            self.user_name = text_input.text
        else:
            # Application gives name - "Guest", if username is empty
            self.user_name = 'Guest'

    def choose_layout(self, ru_layout, en_layout):
        if ru_layout.state == 'down':
            self.layout = ru_layout.text
            en_layout.disabled = True
        if ru_layout.state == 'normal':
            en_layout.disabled = False
        if en_layout.state == 'down':
            self.layout = ru_layout.text
            ru_layout.disabled = True
        if en_layout.state == 'normal':
            ru_layout.disabled = False

    def choose_mode(self, words, sentences):
        if words.state == 'down':
            self.mode = words.text
            sentences.disabled = True
        if words.state == 'normal':
            sentences.disabled = False
        if sentences.state == 'down':
            self.mode = words.text
            words.disabled = True
        if sentences.state == 'normal':
            words.disabled = False

    def choose_level(self, simple, hard):
        if simple.state == 'down':
            self.level = simple.text
            hard.disabled = True
        if simple.state == 'normal':
            hard.disabled = False
        if hard.state == 'down':
            self.level = simple.text
            simple.disabled = True
        if hard.state == 'normal':
            simple.disabled = False

    def start_typing(self, start, check, restart, text_output, text_input, ru_layout, en_layout,
                     words, sentences, simple, hard):
        # If User hasn't chosen layout, mode and level, User can't start typing
        text_output.text = "Select practice mode"
        if ru_layout.state == 'down' or en_layout.state == 'down':
            if words.state == 'down' or sentences.state == 'down':
                if simple.state == 'down' or hard.state == 'down':
                    if self.save_user_name is False:
                        self.give_name(text_input)
                    text_input.text = ""
                    text_input.hint_text = ""
                    self.time_start = time_now()
                    cursor.execute(
                        f"SELECT * FROM Storage WHERE Layout = '{self.layout}' and Mode = '{self.mode}' and Level = '{self.level}'")
                    self.result_to_type = cursor.fetchall()[0][4]
                    restart.disabled = False
                    ru_layout.disabled = True
                    en_layout.disabled = True
                    words.disabled = True
                    sentences.disabled = True
                    simple.disabled = True
                    hard.disabled = True
                    check.disabled = False
                    start.disabled = True
                    text_output.text = self.result_to_type
                    text_input.text = ''

    def check_text(self, text_output, text_input, check, result):
        self.time_finish = time_now()
        check.disabled = True
        result.disabled = False
        list_to_type = []
        list_to_check = []
        list_mistakes = []
        # 'count' - counts amount of mistakes in typing
        count = 0
        for i in self.result_to_type:
            list_to_type.append(i)
        for j in text_input.text:
            list_to_check.append(j)
        diff_len = abs(len(list_to_type) - len(list_to_check))
        if diff_len > 0:
            if len(list_to_type) > len(list_to_check):
                for i in range(diff_len):
                    list_to_check.append(" ")
            if len(list_to_check) > len(list_to_type):
                for i in range(diff_len):
                    list_to_type.append(" ")
        for i in range(len(list_to_type)):
            if list_to_type[i] == list_to_check[i]:
                list_mistakes.append(list_to_check[i])
            elif list_to_type[i] != list_to_check[i] and list_to_check[i] == ' ':
                count += 1
                # mistakes are highlighted in red color
                list_mistakes.append('[color=ff3333]_[/color]')
            else:
                count += 1
                list_mistakes.append('[color=ff3333]' + list_to_check[i] + '[/color]')
        self.mistakes_count = count
        self.typed_text_black = ''.join(list_to_check)
        self.typed_text_red = ''.join(list_mistakes)
        if self.mistakes_count == 0:
            text_output.text = self.user_name + " , good job! You have no mistakes."
        else:
            text_output.text = self.user_name + " , please check your mistakes:\n\n" + self.result_to_type + "\n\n" + self.typed_text_red

    def count_speed(self):
        seconds = self.time_finish.timestamp() - self.time_start.timestamp()
        minutes = seconds / 60
        amount_characters = len(self.typed_text_black)
        speed = round(amount_characters / minutes)
        return speed

    def save_result(self):
        cursor.execute(
            f"INSERT INTO Progress VALUES ('{self.user_name}','{self.time_finish.strftime('%d-%b-%Y')}', '{self.time_finish.strftime('%H:%M:%S')}',"
            f" '{self.layout}', '{self.mode}', '{self.level}', '{self.mistakes_count}', '{self.count_speed()}')")
        sql_connection.commit()

    def show_result(self, text_output, result, restart):
        result.disabled = True
        restart.disabled = False
        text_output.text = "Your result:\n [size= 70][color=3C9315]" + str(
            self.count_speed()) + "[/color][/size]\n [characters per minute]"

    def restart_typing(self, restart, text_output, text_input, start, check, result,
                       ru_layout, en_layout, words, sentences, simple, hard):
        text_output.text = ""
        text_input.text = ""
        self.save_user_name = True
        ru_layout.state = 'normal'
        en_layout.state = 'normal'
        words.state = 'normal'
        sentences.state = 'normal'
        simple.state = 'normal'
        hard.state = 'normal'
        start.disabled = False
        check.disabled = True
        restart.disabled = True
        result.disabled = True


class TableResults(Screen):
    choose_enabled = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.give_table()

    def give_table(self):
        cursor.execute(f"SELECT * FROM Progress")
        user_result = cursor.fetchall()
        data_tables = MDDataTable(
            pos_hint={"center_x": 0.6, "center_y": 0.56},
            size_hint=(0.8, 0.9),
            use_pagination=True,
            rows_num=15,
            column_data=[("Name", dp(25)),
                         ("Date", dp(25)),
                         ("Time", dp(25)),
                         ("Layout", dp(30)),
                         ("Mode", dp(30)),
                         ("Level", dp(30)),
                         ("Mistakes", dp(20)),
                         ("Speed", dp(30))],
            row_data=[(user_result[i][0],
                       user_result[i][1],
                       user_result[i][2],
                       user_result[i][3],
                       user_result[i][4],
                       user_result[i][5],
                       user_result[i][6],
                       user_result[i][7])
                      for i in range(len(user_result))])
        self.add_widget(data_tables)


class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.title = "Fast Typing Simulator"
        super().__init__(**kwargs)

    def build(self):
        self.root = Builder.load_file('main_kivy.kv')


if __name__ == '__main__':
    MainApp().run()
