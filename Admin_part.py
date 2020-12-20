from PyQt5 import uic
from PyQt5.Qt import *
from project_film.main import MyQDialog, MyQWidget
from project_film.WindowArr_class import WindowArr
import sqlite3
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
import datetime as dt

admin_login = 'admin'
admin_pass = 'admin'
path_for_gui = 'ui_files\\'
path_for_db = 'database\\'


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


class AdminSignIn(MyQDialog):
    def __init__(self, parent, window_arr):
        super().__init__(parent, window_ar=window_arr)
        self.parent = parent
        window_arr.append(self)
        self.window_arr = window_arr
        uic.loadUi(path_for_gui + 'admin_sign_in.ui', self)
        # self.setStyleSheet(open("styles/admin_style.css", "r").read())
        self.pushButton.clicked.connect(self.accept_data)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.Form = parent

    def accept_data(self):
        # Открываем Интрефейс для админа
        if admin_login == self.lineEdit.text() and \
                admin_pass == self.lineEdit_2.text():
            self.ex = MyWidget()
            self.ex.show()
        else:
            self.statusBar.setText('Неправильно введен пароль или логин')
            return
        self.close()

    def reject_data(self):
        self.close()


class AddFilmDialog(MyQDialog):
    """Диалоговое окно добавления или изменения фильма"""
    def __init__(self, parent, array, changed=False):
        super().__init__(parent, window_ar=parent.window_arr)
        self.parent = parent
        parent.window_arr.append(self)
        uic.loadUi(path_for_gui + 'add_film_table.ui', self)
        self.pushButton.clicked.connect(self.accept_data)
        if changed:
            self.setWindowTitle('Редактирование записи')
            self.pushButton.setText('Сохранить')
            self.lineEdit.setText(str(array[1]))
            self.lineEdit_2.setText(str(array[2]))
            self.lineEdit_3.setText(str(array[3]))
            self.lineEdit_4.setText(str(array[4]))
            self.lineEdit_5.setText(str(array[5]))
            self.lineEdit_6.setText(str(array[6]))
            self.lineEdit_7.setText(str(array[7]))
            self.lineEdit_8.setText(str(array[8]))
            self.lineEdit_9.setText(str(array[9]))
            self.lineEdit_10.setText(str(array[10]))
            self.lineEdit_11.setText(str(array[11]))
        else:
            self.setWindowTitle('Добавить фильм')
            self.pushButton.setText('Добавить')
        self.arr = []

    def accept_data(self):
        title = self.lineEdit.text()
        rating = self.lineEdit_2.text()
        genre = self.lineEdit_3.text()
        actors = self.lineEdit_4.text()
        producer = self.lineEdit_5.text()
        year = self.lineEdit_6.text()
        duration = self.lineEdit_7.text()
        description = self.lineEdit_8.text()
        poster = self.lineEdit_9.text()
        images = self.lineEdit_10.text()
        trailer = self.lineEdit_11.text()
        # Проверка данных на корректность
        try:
            if title and int(year) <= dt.datetime.now().year and int(duration) > 0:
                self.arr = [title, rating, genre, actors, producer, year, duration,
                            description, poster, images, trailer]
                self.close()
            else:
                self.label_12.setText('Неверно заполнена форма')
                return
        except ValueError:
            self.label_12.setText('Неверно заполнена форма')
            return
        self.close()

    def get_items(self):
        """Возвращение данных"""
        return self.arr


class AddSessionDialog(MyQDialog):
    """Диалоговое окно добавления или редактирования сеанса"""
    def __init__(self, parent, array, changed=False):
        super().__init__(parent, window_ar=parent.window_arr)
        self.parent = parent
        parent.window_arr.append(self)
        uic.loadUi(path_for_gui + 'add_session_table.ui', self)
        self.con = sqlite3.connect(path_for_db + "mydatabase.db")
        self.pushButton.clicked.connect(self.check_data)
        self.arr = []
        if changed:
            self.setWindowTitle('Изменить сеанс')
            self.pushButton.setText('Сохранить')
            self.lineEdit.setText(str(array[1]))
            self.lineEdit_2.setText(str(array[2]))
            self.lineEdit_3.setText(str(array[3]))
            self.lineEdit_year_start.setText(array[4][:4])
            self.lineEdit_month_start.setText(array[4][5:7])
            self.lineEdit_day_start.setText(array[4][8:10])
            self.lineEdit_hour_start.setText(array[4][11:13])
            self.lineEdit_year_end.setText(array[5][:4])
            self.lineEdit_month_end.setText(array[5][5:7])
            self.lineEdit_day_end.setText(array[5][8:10])
            self.lineEdit_hour_end.setText(array[5][11:13])
            self.lineEdit_4.setText(str(array[7]))
        else:
            self.setWindowTitle('Добавить сеанс')
            self.pushButton.setText('Добавить')

    def check_data(self):
        cinema_id = self.lineEdit.text()
        hall_id = self.lineEdit_2.text()
        film_id = self.lineEdit_3.text()
        price = self.lineEdit_4.text()
        # Проверка данных на корректность
        if not (cinema_id.isnumeric() and int(cinema_id) > 0 and
                (int(cinema_id), ) in self.con.execute("""SELECT cinema_id from timetable""").fetchall()):
            self.label_7.setText('Неправильный формат ввода')
            return
        if not (hall_id.isnumeric() and int(hall_id) > 0 and
                (int(hall_id), ) in self.con.execute("""SELECT cinema_hall_id from timetable""").fetchall()):
            self.label_7.setText('Неправильный формат ввода')
            return
        if not (film_id.isnumeric() and int(film_id) > 0 and
                (int(film_id), ) in self.con.execute("""SELECT id from films""").fetchall()):
            self.label_7.setText('Неправильный формат ввода')
            return
        try:
            start_time = list(map(int, [self.lineEdit_year_start.text(),
                                        self.lineEdit_month_start.text(),
                                        self.lineEdit_day_start.text(),
                                        self.lineEdit_hour_start.text()]))
            end_time = list(map(int, [self.lineEdit_year_end.text(),
                                      self.lineEdit_month_end.text(),
                                      self.lineEdit_day_end.text(),
                                      self.lineEdit_hour_end.text()]))
            time_s = dt.datetime(*start_time, minute=0, second=0)
            time_e = dt.datetime(*end_time, minute=0, second=0)
        except (ValueError, TypeError):
            self.label_7.setText('Неправильный формат ввода')
            return
        duration = dt.timedelta(minutes=self.con.execute(f"""SELECT duration from
                                                             films where id = {film_id}""").fetchone()[0])
        if duration > time_e - time_s:
            self.label_7.setText('Неправильный формат ввода')
            return
        timetable = list(map(lambda x: (dt.datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'),
                                        dt.datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S')),
                             self.con.execute(f"""SELECT time_start, time_end from timetable
                                                  where (cinema_id = {cinema_id}
                                                  and cinema_hall_id = {hall_id})""").fetchall()))
        i = 0
        while time_s > timetable[i][0]:
            i += 1
        if self.pushButton.text() == 'Добавить' and not(timetable[i - 1][1] < time_s and time_e < timetable[i][0]):
            self.label_7.setText('Неправильный формат ввода')
            return
        if not (price.isnumeric() and int(price) > 0):
            self.label_7.setText('Неправильный формат ввода')
            return
        places = ', '.join(['0'] * self.con.execute(f"""SELECT number_of_sits
                                                        from cinema_hall where (cinema_id = {cinema_id}
                                                        and cinema_hall_id = {hall_id})""").fetchone()[0])
        self.arr = [cinema_id, hall_id, film_id, time_e, time_s, places, price]
        self.close()

    def get_items(self):
        """Возвращение данных"""
        return self.arr


class AddCinemaDialog(MyQDialog):
    """Диалоговое окно добавления или редактирования киноеатра"""
    def __init__(self, parent, array, changed=False):
        super().__init__(parent, window_ar=parent.window_arr)
        self.parent = parent
        parent.window_arr.append(self)
        uic.loadUi(path_for_gui + 'add_cinema_table.ui', self)
        self.con = sqlite3.connect(path_for_db + "mydatabase.db")
        self.pushButton.clicked.connect(self.check_data)
        self.arr = []
        if changed:
            self.lineEdit.setText(array[1])
            self.lineEdit_2.setText(array[2])
            self.lineEdit_3.setText(array[3])
            self.setWindowTitle('Изменить кинотеатр')
            self.pushButton.setText('Сохранить')
        else:
            self.setWindowTitle('Добавить кинотеатр')
            self.pushButton.setText('Добавить')

    def check_data(self):
        title_cinema = self.lineEdit.text()
        address_cinema = self.lineEdit_2.text()
        phone_cinema = self.lineEdit_3.text()
        # Проверка данных на корректность
        if not(title_cinema and address_cinema and phone_cinema):
            self.label_4.setText('Неправильный формат ввода')
            return
        self.arr = [title_cinema, address_cinema, phone_cinema]
        self.close()

    def get_items(self):
        """Возвращение данных"""
        return self.arr


class AddCinemaHallDialog(MyQDialog):
    """Диалоговое окно добавления или редактирования кинозала"""
    def __init__(self, parent, array, changed=False):
        super().__init__(parent, window_ar=parent.window_arr)
        self.parent = parent
        parent.window_arr.append(self)
        uic.loadUi(path_for_gui + 'add_cinema_hall_table.ui', self)
        self.con = sqlite3.connect(path_for_db + "mydatabase.db")
        self.pushButton.clicked.connect(self.check_data)
        self.arr = []
        if changed:
            self.lineEdit.setText(str(array[1]))
            self.lineEdit_2.setText(str(array[2]))
            self.lineEdit_3.setText(str(array[3]))
            self.setWindowTitle('Изменить кинозал')
            self.pushButton.setText('Сохранить')
        else:
            self.setWindowTitle('Добавить кинозал')
            self.pushButton.setText('Добавить')

    def check_data(self):
        cinema_id = self.lineEdit.text()
        cinema_hall_id = self.lineEdit_2.text()
        number_of_sits = self.lineEdit_3.text()
        # Проверка данных на корректность
        if not(cinema_id and cinema_hall_id and number_of_sits and type(cinema_id) == int,
               type(cinema_hall_id) == int, type(number_of_sits) == int):
            self.label_4.setText('Неправильный формат ввода')
            return
        self.arr = [int(cinema_id), int(cinema_hall_id), int(number_of_sits)]
        self.close()

    def get_items(self):
        """Возвращение данных"""
        return self.arr


class MyWidget(QMainWindow):
    """Главное окно работы с базой данных"""
    def __init__(self):
        self.window_arr = WindowArr()
        super().__init__()
        self.window_arr.append(self)
        uic.loadUi(path_for_gui + "admin_panel.ui", self)
        self.con = sqlite3.connect(path_for_db + "mydatabase.db")
        self.setWindowTitle("Панель администратора")
        self.pushButton.clicked.connect(self.del_film)
        self.pushButton_2.clicked.connect(self.change_film)
        self.pushButton_3.clicked.connect(self.add_film)
        self.pushButton_4.clicked.connect(self.update_films)
        self.pushButton_5.clicked.connect(self.add_session)
        self.pushButton_6.clicked.connect(self.change_session)
        self.pushButton_7.clicked.connect(self.del_session)
        self.pushButton_8.clicked.connect(self.update_sessions)
        self.pushButton_9.clicked.connect(self.add_cinema)
        self.pushButton_10.clicked.connect(self.change_cinema)
        self.pushButton_11.clicked.connect(self.del_cinema)
        self.pushButton_12.clicked.connect(self.update_cinemas)
        self.pushButton_13.clicked.connect(self.add_cinema_hall)
        self.pushButton_14.clicked.connect(self.change_cinema_hall)
        self.pushButton_15.clicked.connect(self.del_cinema_hall)
        self.pushButton_16.clicked.connect(self.update_cinema_halls)
        self.dict_films = {'ID': 'id', 'Название (title)': 'title', 'Рейтинг (rating)': 'rating',
                           'Жанр (genre)': 'genre', 'Актёры (actors)': 'actors', 'Продюссер (producer)': 'producer',
                           'Год (year)': 'year', 'Продолжительность (duration)': 'duration',
                           'Описание (description)': 'description', 'Постер (poster)': 'poster',
                           'Картинки (images)': 'images', 'Трейлер (trailer)': 'trailer', '': ''}
        self.dict_sessions1 = {'ID': 'id', 'id кинотеатра (cinema_id)': 'cinema_id',
                               'id кинозала (cinema_hall_id)': 'cinema_hall_id', 'id фильма (id_film)': 'id_film',
                               'Время начала (time_start)': 'time_start', 'Время конца (time_end)': 'time_end',
                               'Цена (price)': 'price', '': ''}
        self.dict_sessions2 = {'ID': 'id', 'id кинотеатра (cinema_id)': 'cinema_id',
                               'id кинозала (cinema_hall_id)': 'cinema_hall_id', 'id фильма (id_film)': 'id_film',
                               'Дата': 'date', 'Цена (price)': 'price', '': ''}
        self.dict_cinemas = {'ID': 'id', 'Название кинотеатра (name_cinema)': 'name_cinema',
                             'Адрес (address)': 'address', 'Телефон (telephone)': 'telephone', '': ''}
        self.dict_cinema_halls = {'ID': 'id', 'id кинотеатра (cinema_id)': 'cinema_id',
                                  'id кинозала (cinema_hall_id)': 'cinema_hall_id',
                                  'Кол-во мест (number_of_sits)': 'number_of_sits', '': ''}
        self.comboBox.addItems([_ for _ in self.dict_films.keys()])
        self.comboBox_2.addItems([_ for _ in self.dict_films.keys()])
        self.comboBox_3.addItems([_ for _ in self.dict_sessions1.keys()])
        self.comboBox_4.addItems([_ for _ in self.dict_sessions2.keys()])
        self.comboBox_5.addItems([_ for _ in self.dict_cinemas.keys()])
        self.comboBox_6.addItems([_ for _ in self.dict_cinemas.keys()])
        self.comboBox_7.addItems([_ for _ in self.dict_cinema_halls.keys()])
        self.comboBox_8.addItems([_ for _ in self.dict_cinema_halls.keys()])
        self.update_films()
        self.update_sessions()
        self.update_cinemas()
        self.update_cinema_halls()

    def update_films(self):
        self.statusBar().showMessage('')
        cur = self.con.cursor()
        search = self.lineEdit.text()
        s = self.dict_films[self.comboBox_2.currentText()]
        request = 'SELECT * FROM films'
        if s:
            request = f'SELECT * FROM films where {s} like "%{search}%"'
        result = cur.execute(request).fetchall()
        s = self.dict_films[self.comboBox.currentText()]
        if s:
            result.sort(key=lambda x: x[['id', 'title', 'rating', 'genre', 'actors',
                                         'producer', 'year', 'duration', 'description',
                                         'poster', 'images', 'trailer'].index(s)])
        self.tableWidget.setColumnCount(12)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Название', 'Рейтинг', 'Жанр', 'Актёры',
                                                    'Режиссер', 'Год', 'Продолжительность', 'Описание',
                                                    'Постер', 'Картинки', 'Трейлер'])
        self.tableWidget.horizontalHeader().setMinimumSectionSize(50)
        self.tableWidget.verticalHeader().setVisible(False)
        for i, row in enumerate(result):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def add_film(self):
        self.statusBar().showMessage('')
        cur = self.con.cursor()
        mdf = AddFilmDialog(self, [], False)
        mdf.show()
        # mdf.exec_()
        data = mdf.get_items()
        if data:
            max_id = cur.execute("""select max(id) from films""").fetchone()[0]
            cur = self.con.cursor()
            cur.execute("""INSERT INTO films(id, title, rating, genre, actors, producer, year,
                           duration, description, poster, images, trailer, cinema_id) VALUES(
                           ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (max_id + 1, *[i for i in data]))
            self.con.commit()
            self.update_films()

    def change_film(self):
        self.statusBar().showMessage('')
        cur = self.con.cursor()
        rows = list(
            set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Запись не выделена')
            return
        elif len(ids) > 1:
            self.statusBar().showMessage('Выбрано более 1 записи')
            return
        item_inf = cur.execute(
            "SELECT * FROM Films WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids).fetchone()
        mdf = AddFilmDialog(self, item_inf, True)
        mdf.show()
        # mdf.exec_()
        data = mdf.get_items()
        if data:
            cur.execute("""UPDATE films 
            SET  title = ?, rating = ?, genre = ?, actors = ?, producer = ?,
            year = ?, duration = ?, description = ?, poster = ?, images = ?, trailer = ?
            where id LIKE ?""",
                        (data[0], float(data[1]), data[2], data[3], data[4], int(data[5]),
                         int(data[6]), data[7], data[8], data[9], data[10], item_inf[0]))
            self.con.commit()
            self.update_films()

    def del_film(self):
        self.statusBar().showMessage('')
        rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Запись не выделена')
            return
        elif len(ids) > 1:
            self.statusBar().showMessage('Выбрано более 1 записи')
            return
        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы с id " + ",".join(ids),
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute("DELETE FROM films WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            self.con.commit()
            self.update_sessions()

    def update_sessions(self):
        self.statusBar().showMessage('')
        cur = self.con.cursor()
        search = self.lineEdit_2.text()
        string = self.dict_sessions2[self.comboBox_4.currentText()]
        request = 'SELECT * FROM timetable'
        if string:
            if string != 'date':
                request = f'SELECT * FROM timetable where {string} like "%{search}%"'
            else:
                request = f'SELECT * FROM timetable where (time_end like "%{search}%" or time_start like "%{search}%")'
        result = cur.execute(request).fetchall()
        s = self.dict_sessions1[self.comboBox_3.currentText()]
        if s:
            for i in range(len(result)):
                result[i] = list(result[i])
                result[i][4] = dt.datetime.strptime(result[i][4], '%Y-%m-%d %H:%M:%S')
                result[i][5] = dt.datetime.strptime(result[i][5], '%Y-%m-%d %H:%M:%S')
            result.sort(key=lambda x: x[['id', 'cinema_id', 'cinema_hall_id', 'id_film', 'time_start', 'time_end',
                                         'price'].index(s)])
        self.tableWidget_2.setColumnCount(8)
        self.tableWidget_2.setRowCount(0)
        self.tableWidget_2.setHorizontalHeaderLabels(['ID', 'ID кинотеатра', 'ID кинозала', 'ID фильма',
                                                      'Время начала', 'Время конца',
                                                      'Места', 'Цена'])
        self.tableWidget_2.verticalHeader().setVisible(False)
        for i, row in enumerate(result):
            self.tableWidget_2.setRowCount(
                self.tableWidget_2.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget_2.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tableWidget_2.resizeColumnsToContents()

    def add_session(self):
        self.statusBar().showMessage('')
        mdf = AddSessionDialog(self, [], False)
        mdf.show()
        # mdf.exec_()
        data = mdf.get_items()
        if data:
            cur = self.con.cursor()
            cur.execute("""INSERT INTO timetable (cinema_id, cinema_hall_id, id_film, time_start, time_end,
                           places, price) VALUES(?, ?, ?, ?, ?, ?, ?)""", tuple(data))
            self.con.commit()
            self.update_sessions()

    def change_session(self):
        self.statusBar().showMessage('')
        cur = self.con.cursor()
        rows = list(
            set([i.row() for i in self.tableWidget_2.selectedItems()]))
        ids = [self.tableWidget_2.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Запись не выделена')
            return
        elif len(ids) > 1:
            self.statusBar().showMessage('Выбрано более 1 записи')
            return
        item_inf = cur.execute(
            "SELECT * FROM timetable WHERE id = (" + ", ".join(
                '?' * len(ids)) + ")", ids).fetchone()
        mdf = AddSessionDialog(self, item_inf, True)
        mdf.show()
        # mdf.exec_()
        data = mdf.get_items()
        if data:
            cur.execute("""UPDATE timetable SET  cinema_id = ?, cinema_hall_id = ?, id_film = ?,
                           time_start = ?, time_end = ?,
                           places = ?, price = ? where id LIKE ?""",
                        (int(data[0]), int(data[1]), int(data[2]), data[3], data[4], data[5],
                         int(data[6]), item_inf[0]))
            self.con.commit()
            self.update_sessions()

    def del_session(self):
        self.statusBar().showMessage('')
        rows = list(set([i.row() for i in self.tableWidget_2.selectedItems()]))
        ids = [self.tableWidget_2.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Запись не выделена')
            return
        elif len(ids) > 1:
            self.statusBar().showMessage('Выбрано более 1 записи')
            return
        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы с id " + ",".join(ids),
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute("DELETE FROM timetable WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            self.con.commit()
            self.update_sessions()

    def update_cinemas(self):
        self.statusBar().showMessage('')
        cur = self.con.cursor()
        search = self.lineEdit_3.text()
        s = self.dict_cinemas[self.comboBox_6.currentText()]
        request = 'SELECT * FROM cinemas'
        if s:
            request = f'SELECT * FROM cinemas where {s} like "%{search}%"'
        result = cur.execute(request).fetchall()
        s = self.dict_cinemas[self.comboBox_5.currentText()]
        if s:
            result.sort(key=lambda x: x[['id', 'name_cinema', 'address', 'telephone'].index(s)])
        self.tableWidget_3.setColumnCount(4)
        self.tableWidget_3.setRowCount(0)
        self.tableWidget_3.setHorizontalHeaderLabels(['ID', 'Название кинотеатра', 'Адрес', 'Телефон'])
        self.tableWidget_3.verticalHeader().setVisible(False)
        for i, row in enumerate(result):
            self.tableWidget_3.setRowCount(
                self.tableWidget_3.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget_3.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tableWidget_3.resizeColumnsToContents()

    def add_cinema(self):
        self.statusBar().showMessage('')
        mdf = AddCinemaDialog(self, [], False)
        mdf.show()
        # mdf.exec_()
        data = mdf.get_items()
        if data:
            cur = self.con.cursor()
            cur.execute("""INSERT INTO cinemas (name_cinema, address, telephone) VALUES(?, ?, ?)""", tuple(data))
            self.con.commit()
            self.update_cinemas()

    def change_cinema(self):
        self.statusBar().showMessage('')
        cur = self.con.cursor()
        rows = list(
            set([i.row() for i in self.tableWidget_3.selectedItems()]))
        ids = [self.tableWidget_3.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Запись не выделена')
            return
        elif len(ids) > 1:
            self.statusBar().showMessage('Выбрано более 1 записи')
            return
        item_inf = cur.execute(
            "SELECT * FROM cinemas WHERE id = (" + ", ".join(
                '?' * len(ids)) + ")", ids).fetchone()
        mdf = AddCinemaDialog(self, item_inf, True)
        mdf.show()
        # mdf.exec_()
        data = mdf.get_items()
        if data:
            cur.execute("""UPDATE cinemas SET  name_cinema = ?, address = ?, telephone = ? where id LIKE ?""",
                        (*data, item_inf[0]))
            self.con.commit()
            self.update_cinemas()

    def del_cinema(self):
        self.statusBar().showMessage('')
        rows = list(set([i.row() for i in self.tableWidget_3.selectedItems()]))
        ids = [self.tableWidget_3.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Запись не выделена')
            return
        elif len(ids) > 1:
            self.statusBar().showMessage('Выбрано более 1 записи')
            return
        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы с id " + ",".join(ids),
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute("DELETE FROM cinemas WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            self.con.commit()
            self.update_cinemas()

    def update_cinema_halls(self):
        self.statusBar().showMessage('')
        cur = self.con.cursor()
        search = self.lineEdit_4.text()
        s = self.dict_cinema_halls[self.comboBox_8.currentText()]
        request = 'SELECT * FROM cinema_hall'
        if s:
            request = f'SELECT * FROM cinema_hall where {s} like "%{search}%"'
        result = cur.execute(request).fetchall()
        s = self.dict_cinema_halls[self.comboBox_7.currentText()]
        if s:
            result.sort(key=lambda x: x[['id', 'cinema_id', 'cinema_hall_id', 'number_of_sits'].index(s)])
        self.tableWidget_4.setColumnCount(4)
        self.tableWidget_4.setRowCount(0)
        self.tableWidget_4.setHorizontalHeaderLabels(['ID', 'ID кинотеатра', 'ID кинозала', 'Количество мест'])
        self.tableWidget_4.verticalHeader().setVisible(False)
        for i, row in enumerate(result):
            self.tableWidget_4.setRowCount(
                self.tableWidget_4.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget_4.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def add_cinema_hall(self):
        self.statusBar().showMessage('')
        mdf = AddCinemaHallDialog(self, [], False)
        mdf.show()
        # mdf.exec_()
        data = mdf.get_items()
        if data:
            cur = self.con.cursor()
            cur.execute("""INSERT INTO cinema_hall (cinema_id, cinema_hall_id, number_of_sits)
                           VALUES(?, ?, ?)""",
                        tuple(data))
            self.con.commit()
            self.update_cinema_halls()

    def change_cinema_hall(self):
        self.statusBar().showMessage('')
        cur = self.con.cursor()
        rows = list(
            set([i.row() for i in self.tableWidget_4.selectedItems()]))
        ids = [self.tableWidget_4.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Запись не выделена')
            return
        elif len(ids) > 1:
            self.statusBar().showMessage('Выбрано более 1 записи')
            return
        item_inf = cur.execute(
            "SELECT * FROM cinema_hall WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids).fetchone()
        mdf = AddCinemaHallDialog(self, item_inf, True)
        mdf.show()
        # mdf.exec_()
        data = mdf.get_items()
        if data:
            cur.execute("""UPDATE cinema_hall SET cinema_id = ?, cinema_hall_id = ?, number_of_sits = ?
                        where id LIKE ?""",
                        (*data, item_inf[0]))
            self.con.commit()
            self.update_cinema_halls()

    def del_cinema_hall(self):
        self.statusBar().showMessage('')
        rows = list(set([i.row() for i in self.tableWidget_4.selectedItems()]))
        ids = [self.tableWidget_4.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Запись не выделена')
            return
        elif len(ids) > 1:
            self.statusBar().showMessage('Выбрано более 1 записи')
            return
        valid = QMessageBox.question(
            self, '', "Действительно удалить элементы с id " + ",".join(ids),
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute("DELETE FROM cinema_hall WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            self.con.commit()
            self.update_cinema_halls()

    def __hash__(self):
        return hash('admin_panel')

    def closeEvent(self, a0: QCloseEvent):
        if self.window_arr.check_for_main_w(self):
            a0.ignore()
        else:
            super().closeEvent(a0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
