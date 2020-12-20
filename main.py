import sys
import sqlite3

from project_film import card_widget
from PyQt5 import uic
from PyQt5.Qt import *
import time
from project_film.WindowArr_class import WindowArr


# Settings
with_wind_load = False
base_path_for_none_img = r'system_image\none_img.jpg'
path_for_system_img = 'system_image\\'
relative_path_for_media = 'films_image\\'
path_for_gui = 'ui_files\\'
path_for_db = 'database\\'
splitter_in_db = ' '

col_in_mainWindow = 4
wdw = 207 * col_in_mainWindow
wdh = 346 + 50 + 150


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


class DataBase:
    def __init__(self, name_db):
        self.conn = sqlite3.connect(path_for_db + name_db)

    def request(self, request, *param):
        cur = self.conn.cursor()
        if param:
            return cur.execute(request, (*param,))
        else:
            return cur.execute(request)

    def commit(self):
        self.conn.commit()


class MyQWidget(QWidget):
    def __init__(self, *args, window_ar):
        super().__init__(*args)
        self.window_arr = window_ar

    def closeEvent(self, a0: QCloseEvent):
        if self.window_arr.check_window(self):
            self.window_arr.setActive(self, False)
            a0.ignore()
        else:
            self.window_arr.del_item(self)
            super().closeEvent(a0)

    def show(self):
        """Узнаем есть ли наше окно в списке тех окон,
        которые надо закрыть при открытии"""
        # В зависимоти от этого или показываем окно или закрываем его
        if self.window_arr.check_wind_in_list(self):
            super().close()
        else:
            super().show()

    def __hash__(self):
        return hash(self.parent)


class MyQDialog(QDialog):
    def __init__(self, *args, window_ar, modal=True):
        super().__init__(*args)
        self.window_arr = window_ar
        if modal:
            self.setModal(True)
        else:
            self.setModal(False)

    """Для виджета этот кусок кода вполне 
    удовлетворительно выполняет функция setModal в QDialog"""
    def closeEvent(self, a0: QCloseEvent):
        if self.window_arr.check_window(self):
            self.window_arr.setActive(self, False)
            a0.ignore()
        else:
            self.window_arr.del_item(self)
            super().closeEvent(a0)

    def show(self):
        # Аналогично как в классе MyQWidget
        if self.window_arr.check_wind_in_list(self):
            super().close()
        else:
            super().show()

    def __hash__(self):
        return hash(self.parent)


class MainWindow(QMainWindow, card_widget.Ui_Form):
    """Главное окно"""
    def __init__(self, parent=None):
        self.id = 0
        super().__init__(parent)
        window_arr.append(self)
        # self.setStyleSheet(open("styles/main_wind.css", "r").read())
        uic.loadUi(path_for_gui + "main_window.ui", self)

        # Установка минимальных размеров окна
        self.setMinimumWidth(wdw + 30 * (col_in_mainWindow + 1))
        self.setMinimumHeight(wdh)

        self.layout = QGridLayout(self)

        self.sort_btn.clicked.connect(self.filter_wind_open)
        self.search_btn.clicked.connect(self.load_films)
        self.admin_btn.clicked.connect(self.admin_sign_in)
        """Подключение фильтра, для сохранения выбранных чекбоксов 
        при открытии окна в предыдущие разы"""
        self.filter_load()
        self.load_films()

    def load_films(self):
        """
        открываем базу, узнаем название, постер(картинка), жанр, год,
        и рейтинг
        также добавляем кнопку для перехода к более подробному описанию
        """
        search_text = self.search.text() + '%'
        s = self.create_request_for_filter()

        # Очищение экрана от старых результатов поиска
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Запрос в базу
        request = f'''SELECT id, title, rating, genre, 
                                        year, poster from films
                                        where title like "{search_text}" {s}'''
        rez = db.request(request).fetchall()
        if len(rez) == 0:
            self.statusbar.showMessage('Фильмы не найдены')
        else:
            self.statusbar.showMessage('')

        # Заполнение layout виджетами
        # Необходимо для корректной работы QScrollArea
        """Заполнение таблицы карточками"""
        for i in range(0, len(rez) + col_in_mainWindow, col_in_mainWindow):
            for j in range(col_in_mainWindow):
                if i + j >= len(rez):
                    break
                # images подразумевается как постер. т.е основная картинка
                id_f, title, rating, genre, year, images = rez[i + j]
                """Форматируем даные, добавляем коренную папку с картинкам"""
                if images:
                    images = images.split(splitter_in_db)
                    for img in range(len(images)):
                        # Если путь является ссылкой, то не преобразуем
                        if images[img] and not images[img].startswith('http'):
                            images[img] = \
                                f'{relative_path_for_media}{images[img]}'
                """Создаем мини-карточку фильма"""
                w = self.make_card_film(id_f, title, rating, genre, year,
                                        [images, base_path_for_none_img])
                self.layout.addWidget(w, i, j)
        # Заполняем наш виджет карточками
        self.scrollAreaWidgetContents.setLayout(self.layout)

        self.setWindowTitle('Кинотеатр-1.1.0')

    def make_card_film(self, id_f, title, rating, genre, year, images):
        # Загрузка миник-карточки из ui кода сгенерированная с помощью pyuic
        w = QWidget(self)
        lo = QVBoxLayout(w)
        lo.addWidget(self.setupUi(self, id_f, title, rating, genre,
                                  year, images))
        w.setLayout(lo)
        return w

    def open_card(self):
        from project_film.CardOfFilm_classes import CardOfFilm
        self.card = CardOfFilm(self, self.sender().id, window_arr)
        self.card.show()

    def filter_wind_open(self):
        window_arr.append(self.filt)
        self.filt.show()
        self.filt.exec_()
        self.load_films()

    def filter_load(self):
        """
        Открытие окна фильтровки поиска и обновление
        главного окна в соответствии с установленными фильтрами
        """
        # Запрос в базу
        rez = db.request("""SELECT DISTINCT year, genre, rating, producer 
        from films""").fetchall()
        # Форматирование результата запроса
        years = sorted(list(set(map(lambda x: str(x[0]), rez))),
                       key=lambda x: int(x))
        genre = sorted(list(set(map(lambda x: x[1], rez))))
        """Стоит включить, но придется настроить поиск
        Проблема состоит в том, что вместо определенных жанров, загружаются 
        сразу те, которые определенеы у фильмов"""
        new_genre = set()
        for i in genre:
            arr = i.split(', ')
            for j in arr:
                j = j.strip('\n')
                new_genre.add(j)
        genre = list(sorted(list(new_genre)))
        rating = sorted(list(set(map(lambda x: str(x[2]), rez))),
                        key=lambda x: float(x))
        producer = []
        for i in rez:
            name = i[3]
            if name is not None:
                name = name.strip('\n')
                producer.append(name)
        producer = sorted(set(producer))
        self.filt = FilterDialog(self)
        self.filt.reload_ui(years, genre, rating, producer)

    def create_request_for_filter(self):
        # Возвращает сформированный запрос для базы
        # основываясь на данных из окна диалога
        try:
            dct = self.filt.get_items()
            s = ''
            if dct['year'][0]:
                s += f' and year like "{dct["year"][1]}"'
            if dct['genre'][0]:
                s += f' and genre like "%{dct["genre"][1]}%"'
            if dct['rating'][0]:
                s += f' and rating like "{dct["rating"][1]}"'
            if dct['producer'][0]:
                if not dct['producer'][1]:
                    dct['producer'][1] = 'NONE'
                s += f' and producer like "{dct["producer"][1]}"'
            return s
        except Exception as exc:
            print(exc)

    def admin_sign_in(self):
        from project_film.Admin_part import AdminSignIn
        aw = AdminSignIn(self, window_arr)
        aw.show()
        aw.exec_()

    def closeEvent(self, a0: QCloseEvent):
        if window_arr.check_for_main_w(self):
            a0.ignore()
        else:
            super().closeEvent(a0)

    def __hash__(self):
        return hash(self.id)


class FilterDialog(MyQDialog):
    """Окно, которое отвечает за работу фильтра"""
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent, window_ar=window_arr)
        uic.loadUi(path_for_gui + 'filter.ui', self)
        self.setStyleSheet(open("styles/filter_style.css", "r").read())
        self.setWindowTitle('Настройки сортировки')
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.buttonBox.accepted.connect(self.accept_data)
        self.buttonBox.rejected.connect(self.close)
        self.a = {'year': [False, ''],
                  'genre': [False, ''],
                  'rating': [False, ''],
                  'producer': [False, '']}

    def reload_ui(self, y, g, r, p):
        self.comboBox.addItems(y)
        self.comboBox_2.addItems(g)
        self.comboBox_3.addItems(r)
        self.comboBox_4.addItems(p)

    def accept_data(self):
        if self.checkBox.isChecked():
            self.a['year'] = [True, self.comboBox.currentText()]
        else:
            self.a['year'] = [False, '']

        if self.checkBox_2.isChecked():
            self.a['genre'] = [True, self.comboBox_2.currentText()]
        else:
            self.a['genre'] = [False, '']

        if self.checkBox_3.isChecked():
            self.a['rating'] = [True, self.comboBox_3.currentText()]
        else:
            self.a['rating'] = [False, '']

        if self.checkBox_4.isChecked():
            self.a['producer'] = [True, self.comboBox_4.currentText()]
        else:
            self.a['producer'] = [False, '']
        # print(self.a)
        self.close()

    def get_items(self):
        return self.a


class MovieSplashScreen(QSplashScreen):
    """Реализовано для работы экрана загрузки"""
    def __init__(self, movie, parent=None):
        movie.jumpToFrame(0)
        pixmap = QPixmap(movie.frameRect().size())

        QSplashScreen.__init__(self, pixmap)
        self.movie = movie
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):
        self.movie.start()

    def hideEvent(self, event):
        self.movie.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        pixmap = self.movie.currentPixmap()
        self.setMask(pixmap.mask())
        painter.drawPixmap(0, 0, pixmap)

    def sizeHint(self):
        return self.movie.scaledSize()


if __name__ == "__main__":
    # import time
    # time.sleep(3)
    window_arr = WindowArr()
    db = DataBase('mydatabase.db')
    if not with_wind_load:
            app = QApplication(sys.argv)
            ex = MainWindow()
            ex.show()
            sys.exit(app.exec())
    else:
        app = QApplication(sys.argv)
        movie = QMovie(path_for_system_img + "load_v1.gif")
        splash = MovieSplashScreen(movie)
        splash.show()
        start = time.time()

        while movie.state() == QMovie.Running and time.time() < start + 4:
            app.processEvents()

        window = MainWindow()
        window.show()
        splash.finish(window)
        sys.exit(app.exec_())


"""Экран загрузки с использование статичной картинки"""
# if __name__ == '__main__':
#     import time
#     app = QApplication(sys.argv)
#     pixmap = QPixmap(path_for_system_img + 'log.jpg')
#     splash = QSplashScreen(pixmap)
#     splash.show()
#     for n in ("HW presence", "net connectivity", "API connectivity"):
#         splash.showMessage("Check for {0}".format(n))
#         time.sleep(1)
#         app.processEvents()
#     mainWin = MainWindow()
#     splash.finish(mainWin)
#     mainWin.show()
#     sys.exit(app.exec_())
