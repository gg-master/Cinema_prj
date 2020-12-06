import sys
import sqlite3
import os

import card_widget
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
import load_url_img
import QRcode
import time

# Settings
with_wind_load = False
base_path_for_none_img = r'system_image\none_img.jpg'
path_for_system_img = 'system_image\\'
relative_path_for_media = 'films_image\\'
path_for_gui = 'ui_files\\'
path_for_db = 'database\\'

admin_login = 'admin'
admin_pass = 'admin'
col_in_mainWindow = 4

conn = sqlite3.connect(path_for_db + "mydatabase.db")

wdw = 207 * col_in_mainWindow
wdh = 346 + 50 + 150

tickets_numb = 0


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

'''
    Переопределение классов использовалось для реализации закрытия окон
    
    Использованы две реализации закрытия форм:
    1) Когда при закрытии родительского окна закрыватся все дочернии окна
    Реализовано через добавление всех форм в список window_arr
    2) Когда при открытом дочернем окне не возможно будет закрыть 
    родительское окно
    Реализовано также через window_arr

    См закомментированный и не закоментированный методы ниже
'''


class WindowArr(list):
    """Для корректной реализации системы закрытия окон реализован класс,
    наследующийся от списка и выполняющий проверки с окнами при их открытии  и
    закрытии"""
    def __init__(self):
        super().__init__()
        """Словарь используется для кранения 
        открытых окон и их детей в этих окнах"""
        self.dct = {}
        """Список необходим для хранения все отрытых окон"""
        self.list = list()
        """В этот список добавляется окно, 
        которое необходимо закрыти при открытии"""
        self.list_when_show_del = []

    def setActive(self, el, op_el_list=True):
        """метод, который активирует окна в списке отрытых окон
        или же октивирует все октрытые окна в каком то
        отдельном окне(для этого и используется словарь)"""
        if op_el_list:
            for i in self.list:
                for j in self.dct[hash(i)]:
                    j.setWindowState(Qt.WindowActive)
                    j.activateWindow()
        else:
            """хэшем используется для понимания к 
            какому главному окносится то или иное дочернее окно"""
            h = hash(el)
            for item in self.dct[h]:
                item.setWindowState(Qt.WindowActive)
                item.activateWindow()

    def check_for_main_w(self, item):
        """Метод, который проверяет отрыти ли окна в
        главном окне(фильтр и пр) или же открыты ли другие окна
        (в нашем случае карточки фильмов)"""
        if self.dct[hash(item)][-1] != item:
            self.setActive(item, False)
            return True
        elif self.list:
            """Если есть элементы в списке, то открываем их последовательно"""
            self.setActive(item)
            return True
        return False

    def check_window(self, wind):
        """Проверяем является ли окно последним в списке
        октрытых окон (НЕ У ГЛАВНОГО)"""
        h = hash(wind)
        if self.dct[h][-1] == wind:
            return False
        return True

    def check_wind_in_list(self, wind):
        """Если окно в списке для удаления -> удаляем"""
        if wind in self.list_when_show_del:
            del self.list_when_show_del[self.list_when_show_del.index(wind)]
            return True
        return False

    def append(self, obj):
        # Узнаем номер родителя у окна, чтобы понять в каком
        # именно окне октрылось новое окно
        h = hash(obj)
        if h not in self.dct:
            # Если окна нет, то понимаем,
            # что оно является родителем, и создаем новый элемент в словаре
            self.dct[h] = [obj]
        elif h in self.dct and obj.__class__.__name__ in \
                list(map(lambda x: x.__class__.__name__, self.dct[h])):
            # print(obj, h)
            """Если подобно окно уже было открыто, 
            то активируем его, а новое, которо совпадает 
            с открытым отправляем в список для закрытия, 
            где окно закроется как только запустится метод show у этого окна"""
            self.setActive(obj, False)
            self.list_when_show_del.append(obj)
        else:
            self.dct[h].append(obj)
        # Если класс окна является карточкой, то добавляем в список
        if obj.__class__.__name__ == 'CardOfFilm' and \
                obj not in self.list_when_show_del:
            self.list.append(obj)

    def __getitem__(self, item):
        return self.list[item]

    def del_item(self, item):
        """Узнаем номер, и в зависимости от того,
        является окно родителем или нет, удаляем
        его или из списка и словаря или только из словаря"""
        h = hash(item)
        if item.__class__.__name__ != 'CardOfFilm':
            del self.dct[h][-1]
        else:
            del self.list[self.list.index(item)]
            del self.dct[h]


class MyQWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def closeEvent(self, a0: QCloseEvent):
        if window_arr.check_window(self):
            window_arr.setActive(self, False)
            a0.ignore()
        else:
            window_arr.del_item(self)
            super().closeEvent(a0)

    def show(self):
        """Узнаем есть ли наше окно в списке тех окон,
        которые надо закрыть при открытии"""
        # В зависимоти от этого или показываем окно или закрываем его
        if window_arr.check_wind_in_list(self):
            super().close()
        else:
            super().show()

    def __hash__(self):
        return hash(self.parent)


class MyQDialog(QDialog):
    def __init__(self, *args):
        super().__init__(*args)

    def closeEvent(self, a0: QCloseEvent):
        if window_arr.check_window(self):
            window_arr.setActive(self, False)
            a0.ignore()
        else:
            window_arr.del_item(self)
            super().closeEvent(a0)

    def show(self):
        # Аналогично как в классе MyQWidget
        if window_arr.check_wind_in_list(self):
            self.close()
        else:
            super().show()

    def __hash__(self):
        return hash(self.parent)


class MyPopup(QWidget):
    """Выслывающее окно для увеличенного просомтра изображений."""
    def __init__(self, parent, pixmap_path):
        super().__init__()
        self.label = QLabel(self)
        # Установка отсутствия рамок
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        # Загрузка изображения
        pixmap = QPixmap(pixmap_path)
        # Установка размеров окна, и изображения
        # TODO можно поиграться с размером изображения
        #  установить может быть коэффициенты и пр
        self.resize(parent.width() // 2, parent.height())
        self.label.resize(self.width(), self.height())
        self.move(parent.x() + parent.width() // 2 - self.label.width() // 2,
                  parent.y() + parent.height() // 2 - self.label.height() // 2 + 30)

        self.label.setPixmap(pixmap.scaled(self.width(), self.height(),
                                           Qt.KeepAspectRatio))


class MainWindow(QMainWindow, card_widget.Ui_Form):
    """Главное окно"""
    def __init__(self, parent=None):
        self.id = 0
        super().__init__(parent)
        window_arr.append(self)
        self.setStyleSheet(open("styles/main_wind.css", "r").read())
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

        cur = conn.cursor()
        # Запрос в базу
        request = f'''SELECT id, title, rating, genre, 
                                        year, poster from films
                                        where title like "{search_text}" {s}'''
        rez = cur.execute(request).fetchall()

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
                id, title, rating, genre, year, images = rez[i + j]
                """Форматируем даные, добавляем коренную папку с картинкам"""
                if images:
                    images = images.split(', ')
                    for img in range(len(images)):
                        # Если путь является ссылкой, то не преобразуем
                        if images[img] and not images[img].startswith('http'):
                            images[img] = \
                                f'{relative_path_for_media}{images[img]}'
                """Создаем мини-карточку фильма"""
                w = self.make_card_film(id, title, rating, genre, year,
                                        [images, base_path_for_none_img])
                self.layout.addWidget(w, i, j)
        # Заполняем наш виджет карточками
        self.scrollAreaWidgetContents.setLayout(self.layout)

        self.setWindowTitle('Кинотеатр-0.0.1')

    def make_card_film(self, id, title, rating, genre, year, images):
        # Загрузка миник-карточки из ui кода сгенерированная с помощью pyuic
        w = QWidget(self)
        lo = QVBoxLayout(w)
        lo.addWidget(self.setupUi(self, id, title, rating, genre,
                                               year, images))
        w.setLayout(lo)
        return w

    def open_card(self):
        self.card = CardOfFilm(self, self.sender().id)
        self.card.show()

    def filter_wind_open(self):
        window_arr.append(self.filt)
        self.filt.show()
        # Добавление в список для реализации закрытия окон

        self.filt.exec_()
        self.load_films()

    def filter_load(self):
        """
        Открытие окна фильтровки поиска и обновление
        главного окна в соответствии с установленными фильтрами
        """
        cur = conn.cursor()
        # Запрос в базу
        rez = cur.execute("""SELECT DISTINCT year, genre, rating, producer 
        from films""").fetchall()
        # Форматирование результата запроса
        years = list(set(map(lambda x: str(x[0]), rez)))
        genre = list(set(map(lambda x: x[1], rez)))

        """Стоит включить, но придется настроить поиск
        Проблема состоит в том, что вместо определенных жанров, загружаются 
        сразу те, которые определенеы у фильмов"""
        # new_genre = set()
        # for i in genre:
        #     arr = i.split(', ')
        #     for j in arr:
        #         j = j.strip('\n')
        #         new_genre.add(j)
        # genre = list(sorted(list(new_genre)))
        rating = list(set(map(lambda x: str(x[2]), rez)))
        producer = []
        for i in rez:
            name = i[3]
            if name is not None:
                name = name.strip('\n')
                producer.append(name)

        self.filt = FilterDialog(self)
        self.filt.reload_ui(years, genre, rating, producer)

    def create_request_for_filter(self):
        # Возвращает сформированный запрос для базы
        # основываясь на данных диалога
        try:
            dct = self.filt.get_items()
            s = ''
            if dct['year'][0]:
                s += f' and year like "{dct["year"][1]}"'
            if dct['genre'][0]:
                s += f' and genre like "{dct["genre"][1]}"'
            if dct['rating'][0]:
                s += f' and rating like "{dct["rating"][1]}"'
            if dct['producer'][0]:
                if not dct['producer'][1]:
                    dct['producer'][1] = 'NONE'
                s += f' and producer like "{dct["producer"][1]}"'
            return s
        except Exception as ex:
            print(ex)

    def admin_sign_in(self):
        self.aW = AdminSignIn(self)
        self.aW.show()
        self.aW.exec_()

    def closeEvent(self, a0: QCloseEvent):
        if window_arr.check_for_main_w(self):
            a0.ignore()
        else:
            super().closeEvent(a0)

    def __hash__(self):
        return hash(self.id)


class CardOfFilm(MyQWidget):
    """Окно карточки
    Представляет просмотр информации о фильме и возможности покупки билета
    """
    def __init__(self, parent, id_film):
        self.id = id_film
        super().__init__()
        window_arr.append(self)
        self.parent = parent
        self.setStyleSheet(open("styles/film_card.css", "r").read())
        uic.loadUi(path_for_gui + 'card_of_film.ui', self)

        self.setWindowTitle('Карточка фильма')
        self.playBtn.clicked.connect(self.play_trailer)
        self.buy_ticket_btn.clicked.connect(self.buy_ticket)
        self.poster.installEventFilter(self)
        self.poster_2.installEventFilter(self)

        self.load_info()

    def eventFilter(self, obj, event):
        """Событие, которое реагирует на нажатия кнопкой мыши на
        дополнительные изображения в карточке фильма"""
        pixmap = None
        # Получаем путь к изображениям, установленных в label в gui
        if obj == self.poster:
            pixmap = self.path_img['poster_1']
        elif obj == self.poster_2:
            pixmap = self.path_img['poster_2']
        if pixmap is not None:
            if event.type() == QEvent.MouseButtonPress:
                mouseEvent = QMouseEvent(event)
                if mouseEvent.buttons() == Qt.LeftButton:
                    # Если левая кнопка удерживается,
                    # то открываем окно с увеличенной картинкой
                    self.wind = MyPopup(self, pixmap)
                    self.wind.show()
            if event.type() == QEvent.MouseButtonRelease:
                self.wind.close()

        return MyQWidget.eventFilter(self, obj, event)

    def buy_ticket(self):
        """Функция, которая открывает окно для покупки билетов"""
        bt = BuyTct(self, self.id, self.title)
        bt.show()
        bt.exec_()

    def load_info(self):
        """Загрузка основной информации в оставшиеся label в gui"""
        cur = conn.cursor()
        rez = cur.execute("""SELECT * from films
                                        where id like ?""",
                          (self.id,)).fetchall()[0]

        self.path_img = {"poster_1": None,
                         'poster_2': None}
        self.title = rez[1]
        rating = rez[2]
        genre = rez[3]
        actors = rez[4]
        producer = rez[5]
        year = str(rez[6]) + ' год'
        duration = str(rez[7]) + " мин"
        description = rez[8]
        """Под постером подразумевается основная картинка
        Под images подразумеваются кадры из фильма и тд
        Здесь """
        poster = rez[9]
        images = rez[10]
        self.trailer = relative_path_for_media + str(rez[11])

        pixmap_poster = QPixmap(base_path_for_none_img)
        pixmap_image = QPixmap(base_path_for_none_img)
        pixmap_image_2 = QPixmap(base_path_for_none_img)

        """Загрузка изображений в соответствии с тем, явлется путь 
        ссылкой на картинку или это путь к локальному файлу"""
        if poster:
            poster = poster.split(', ')
            for img in range(len(poster)):
                if poster[img] and not poster[img].startswith('http'):
                    poster[img] = \
                        f'{relative_path_for_media}{poster[img]}'
            if poster[0].startswith('http'):
                pixmap_poster = load_url_img.load_image_from_url(poster[0])
            elif os.path.isfile(poster[0]):
                pixmap_poster = QPixmap(poster[0])
            elif len(poster) > 1 and os.path.isfile(poster[1]):
                pixmap_poster = QPixmap(poster[1])
            elif len(poster) > 1 and poster[1].startswith('http'):
                pixmap_poster = load_url_img.load_image_from_url(poster[1])
        if images:
            images = images.split(', ')
            for img in range(len(images)):
                if images[img] and not images[img].startswith('http'):
                    images[img] = \
                        f'{relative_path_for_media}{images[img]}'
            if images[0].startswith('http'):
                pixmap_image = load_url_img.load_image_from_url(images[0])
                self.path_img["poster_1"] = images[0]
            elif len(images) > 1 and images[1].startswith('http'):
                pixmap_image_2 = load_url_img.load_image_from_url(images[1])
                self.path_img["poster_2"] = images[1]
            elif os.path.isfile(images[0]):
                pixmap_image = QPixmap(images[0])
                self.path_img["poster_1"] = images[0]
            elif len(images) > 1 and os.path.isfile(images[1]):
                pixmap_image_2 = QPixmap(images[1])
                self.path_img["poster_2"] = images[1]

        """Установка всех данных и корректировка размеров картинок"""
        win_w, win_h = self.width(), self.height()

        # Загрузка фото
        w_l, h_l = self.img.width(), self.img.height()
        self.img.setPixmap(pixmap_poster.scaled(w_l + win_w // 2,
                                         h_l + win_h // 2,
                                         Qt.KeepAspectRatio))
        self.poster.setPixmap(pixmap_image.scaled(w_l * 3, h_l * 3,
                                                   Qt.KeepAspectRatio))

        self.poster_2.setPixmap(pixmap_image_2.scaled(w_l * 3, h_l * 3,
                                                       Qt.KeepAspectRatio))

        # Загрузка текстовой информации
        self.year.setText(str(year))
        self.duration.setText(str(duration))
        self.description_2.setText(description)
        self.title_2.setText(self.title)
        self.rating_2.setText(str(rating))
        self.genre_2.setText(genre)
        self.producer_2.setText(producer)
        self.actors_2.setText(actors)

    def play_trailer(self):
        """Открывает окно по ссылке на локальный файл
        В будущем есть идея ввести открытие видео-файла по ссылке,
        чтобы не хранить видео-файл на устройстве"""
        # TODO попробовать реализовать открытие видео по ссылке
        try:
            if self.trailer is not None and os.path.isfile(self.trailer):
                self.vid = TrailerWidget(self, self.trailer, self.title)
                self.vid.show()
            else:
                self.statusBar.setText('Трейлер не найден')
        except:
            pass

    def __hash__(self):
        return hash(int(self.id))


class BuyTct(MyQDialog):
    """Форма покупки билетов"""
    def __init__(self, parent, id, title):
        super().__init__(parent)
        self.parent = parent
        window_arr.append(self)

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        uic.loadUi(path_for_gui + 'buy_tck.ui', self)
        self.cancel.clicked.connect(self.close)
        self.accept.clicked.connect(self.accept_action)

        self.cinemas_2.activated.connect(self.load_time)
        self.times.activated.connect(self.load_other)

        self.choose_place_btn.clicked.connect(self.choose_seat)

        self.film_id = id
        self.film_title = title
        self.counter_places = 0
        self.path_for_tct = None
        self.isAccepted = False

        self.load_cinemas()

    def set_path(self, path):
        self.path_for_tct = path

    def choose_seat(self):
        """Открывает окно для выбора мест
        В зависимости от некоторых факторов, таких как:
        1) Пользователь открыл но не выбрал место -
        появляетс надпись о необходимости выборам места
        2) Пользователь открыл выбрал но отменил выбор -
        восстанавливаются прежние значения
        3) Пользователь выбрал место -
        В scrollArea добавляются выбранные места

        !!!! Весь выше описанный функционал
        реализован частично как в этом классе,
        так и в классе формы в которой выбираются сами места"""

        # Проверка выбрано время или нет
        if self.times.currentText() == 'Выбрать':
            self.statusBar.setText('Выберите время')
            return
        try:
            cs = ChooseSeat(self, self.places)
            # Если кнопка подтверждения заказа активка и
            # места прежде уже выбраны, то в созданную форму
            # добавляются прежде выбранные места
            if self.accept.isEnabled() and self.numb is not None:
                cs.set_selected_btn(self.numb, isSelected=True)
            cs.show()
            cs.exec_()
            """Получаем номера кресел и если все в норме, 
            то разрешаем пользователю подтвердить заказ"""
            self.numb = cs.get_btn_numb()
            self.create_new_seat()
            if self.numb is not None:
                self.accept.setEnabled(True)
                self.statusBar.setText('')
                self.it_price.setText(
                    f'{int(self.price.text().split()[0]) * len(self.numb)}')
            else:
                # Если места оказались не выбранными,
                # то блокируем кнопку подтвержения и
                # выводим предупредительное сообщение
                self.statusBar.setText('Место не выбрано')
                self.accept.setEnabled(False)
        except Exception:
            """Исключение введено для предотвращения конфликта, 
            когда не выбран кинотеатр и время"""

            """
            !!!! Иногда этот except может хавать ошибки
            Необходимо отключать его, если собираетесь изменять и 
            тестировать форму для выбора билетов
            """
            self.statusBar.setText('Выберите кинотеатр и время')

    def create_new_seat(self):
        """Метод заполняет ScrollArea выбранными местами
        Части кода сгенерированы через pyuic
        """
        if self.scrollArea_2:
            self.scrollArea_2.deleteLater()
        self.scrollArea_2 = QtWidgets.QScrollArea(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scrollArea_2.sizePolicy().hasHeightForWidth())
        self.scrollArea_2.setSizePolicy(sizePolicy)
        self.scrollArea_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea_2.setLineWidth(1)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(
            QtCore.QRect(0, 0, 260, 60))
        self.scrollAreaWidgetContents_3.setObjectName(
            "scrollAreaWidgetContents_3")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(
            self.scrollAreaWidgetContents_3)

        font = QtGui.QFont()
        font.setPointSize(10)
        if self.numb is not None:
            for num in range(len(self.numb)):
                horizontalLayout = QtWidgets.QHBoxLayout()
                place_text = QtWidgets.QLabel(f'Место ({num + 1}):',
                                              self.scrollAreaWidgetContents_3)
                number = QtWidgets.QLabel(f'№ {self.numb[num] + 1}',
                                          self.scrollAreaWidgetContents_3)

                spacerItem = QtWidgets.QSpacerItem(40, 20,
                                                   QtWidgets.QSizePolicy.
                                                   Expanding,
                                                   QtWidgets.QSizePolicy.
                                                   Minimum)
                place_text.setFont(font)
                number.setFont(font)

                horizontalLayout.addWidget(place_text)
                horizontalLayout.addWidget(number)
                horizontalLayout.addItem(spacerItem)
                self.verticalLayout_7.addLayout(horizontalLayout)
        else:
            horizontalLayout = QtWidgets.QHBoxLayout()
            place_text = QtWidgets.QLabel('Место:',
                                          self.scrollAreaWidgetContents_3)
            number = QtWidgets.QLabel("Место не выбрано",
                                      self.scrollAreaWidgetContents_3)
            spacerItem = QtWidgets.QSpacerItem(40, 20,
                                               QtWidgets.QSizePolicy.Expanding,
                                               QtWidgets.QSizePolicy.Minimum)
            place_text.setFont(font)
            number.setFont(font)

            horizontalLayout.addWidget(place_text)
            horizontalLayout.addWidget(number)
            horizontalLayout.addItem(spacerItem)
            self.verticalLayout_7.addLayout(horizontalLayout)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_3)
        self.verticalLayout_6.addWidget(self.scrollArea_2)

    """Реализованная последовательная загрузка данных в 
    зависимости от выбранного кинотеатра и времени"""

    def load_other(self):
        """Загружаются оставшиеся данные в соответствии с
        выбранным кинотеатром и временем"""
        cur = conn.cursor()
        name_c = self.cinemas_2.currentText()
        self.time_s = self.times.currentText()

        rez_c = cur.execute("""SELECT * from cinemas 
                                    where name_cinema like ?""", (
            name_c,)).fetchall()[0]
        id_c = rez_c[0]
        rez_f = cur.execute("""Select 
                time_end, places, 
                price, id, cinema_hall_id 
                from timetable 
                where id_film like ? 
                and cinema_id like ? 
                and time_start  like ?""", (
            self.film_id, id_c, self.time_s)).fetchall()[0]
        self.time_to.setText(rez_f[0])
        self.price.setText(str(rez_f[2]))
        self.places = rez_f[1].split(', ')
        self.id_films_in_c = rez_f[-2]
        self.cinema_hall_id = rez_f[-1]
        self.hall.setText(str(self.cinema_hall_id))

    def load_time(self):
        """Загрузка доступного времени в
        соответствии с выбранным кинотетром из базы"""
        cur = conn.cursor()
        name_c = self.cinemas_2.currentText()

        # Загрузка информации о кинотетре
        rez_c = cur.execute("""SELECT * from cinemas 
                            where name_cinema like ?""", (
            name_c,)).fetchall()[0]

        self.adress.setText(rez_c[2])
        self.phone.setText(rez_c[3])
        self.time_to.setText('---------')

        # Загрузка времени
        id_c = rez_c[0]
        rez_time = cur.execute("""SELECT time_start from timetable 
        where id_film like ? and cinema_id like ?""", (
            self.film_id, id_c)).fetchall()
        if not rez_time:
            self.statusBar.setText('Данного фильма не найденно')
            return
        rez_s = list(map(lambda x: str(x[0]), rez_time))
        self.times.clear()
        self.times.addItems(rez_s)

    def load_cinemas(self):
        # Загрузка времени и добавление в ComboBox
        cur = conn.cursor()
        self.title.setText(self.film_title)
        self.dct_cinema = {}
        rez = cur.execute("""SELECT id, name_cinema from cinemas""").fetchall()
        for i in rez:
            id, name = i[:2]
            self.dct_cinema[id] = name
        rez = list(self.dct_cinema.values())
        self.cinemas_2.addItems(rez)

    def closeEvent(self, a0: QCloseEvent):
        # if self.isAccepted:
        #     if self.counter_places != len(self.numb):
        #         if self.path_for_tct is not None:
        #             for i in range(self.counter_places, len(self.numb)):
        #                 self.counter_places += 1
        #                 place = self.numb[i] + 1
        #                 Ticket(self, place, btn_for_auto_save=True)
        #             print('Билеты сохранены')
        super().closeEvent(a0)

    def accept_action(self):
        """Метод, который вызывается при нажатии кнопки "Подтвердить"
        Обновляется строчка с порядком сиденей а также для каждого билета
        появляется окно с информацией о месте, времени и тд
        Кроме этого окно нельзя будет закрыть пока пользователь не нажмет на
        кнопку "Сохранить" и не выберет путь для сохранения билета"""
        cur = conn.cursor()
        self.isAccepted = True
        for i in self.numb:
            self.places[i] = '1'
        s = f'{", ".join(self.places)}'
        req = f'{s}'
        cur.execute(f'''UPDATE timetable
                        set places = ?
                        WHERE id = ?''', (req, self.id_films_in_c))
        conn.commit()
        for i in range(len(self.numb)):
            self.counter_places += 1
            place = self.numb[i] + 1
            self.ticket = Ticket(self, place)
            self.ticket.show()
        # После сохранения всех билетов отключается
        # возможность повторного подтверждения заказа и выбора места
        self.statusBar.setText("Билеты сохранены. Ждем вас на сеансе")
        self.accept.setEnabled(False)
        self.choose_place_btn.setEnabled(False)
        self.cancel.setEnabled(False)
    #
    # def __hash__(self):
    #     return hash(self.parent)


class Ticket(MyQWidget):
    """Класс билета. Показывает билет, кнопку для
    выбора пути сохранения и созраняет билет по выбранному пути"""
    def __init__(self, parent, place, btn_for_auto_save=False):
        super().__init__()
        self.parent = parent
        window_arr.append(self)

        uic.loadUi(path_for_gui + 'successful_purchase.ui', self)
        self.pushButton.clicked.connect(self.choose_way)

        # Разметка
        self.pixmap = QPixmap(path_for_system_img + 'ticket.jpg')
        qp = QPainter()
        qp.begin(self.pixmap)
        qp.setFont(QFont('Peignot', 17))
        qp.drawText(QPoint(123, 112), parent.film_title)
        qp.drawText(QPoint(123, 148), str(parent.cinema_hall_id))
        qp.drawText(QPoint(123, 176), str(place))

        qp.setFont(QFont('Peignot', 15))
        qp.drawText(QPoint(57, 232), f'{parent.time_s}')
        qp.drawText(QPoint(57, 249), f'{parent.time_to.text()}')

        qp.setFont(QFont('Peignot', 13))
        qp.drawText(QPoint(102, 284), f'{parent.phone.text()}')

        qrcode = self.make_qrcode()
        qrcode = qrcode.scaled(179, 125, Qt.KeepAspectRatio)
        qp.drawPixmap(QPoint(360, 175), qrcode)
        qp.end()

        # 321 175
        self.BtnIsClicked = btn_for_auto_save
        self.label.setPixmap(self.pixmap)

    def make_qrcode(self):
        """Возврадащет сгенеррированный Qrcode как объект Qpixmap"""
        import qrcode
        from numpy import unicode
        text = unicode('Билет подтвержден')
        return qrcode.make(text, image_factory=QRcode.Image).pixmap()

    def save_tct(self):
        # Если кнопка была нажата и выбран корректный путь,
        # то выполняем сохранение
        global tickets_numb
        if self.BtnIsClicked:
            self.render(self.pixmap)
            self.pixmap.save(f'{self.way}/Билет-№{tickets_numb}.jpg')
            tickets_numb += 1

    def choose_way(self):
        # Диалог выбора пути
        from PyQt5.QtWidgets import QFileDialog
        self.way = QFileDialog.getExistingDirectory()
        if self.way:
            self.BtnIsClicked = True
            self.save_tct()
            self.close()

    def closeEvent(self, a0: QCloseEvent):
        if self.BtnIsClicked:
            self.parent.set_path(self.way)
            super().closeEvent(a0)
        else:
            a0.ignore()
            self.statusBar.setText('Выберите путь для сохранения')


class MyPushButton(QPushButton):
    """Модифицированная кнопка, которая меняет цвет в
    зависимости забранированно место или нет

    Также реагирует как на нажатие левой кнопкой мыши,
    так и на нажатие правой кнопкой мыши"""
    def __init__(self, *args):
        super().__init__(*args)
        self.isSelected = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setStyleSheet(
                "background-color: rgb(255, 227, 156);")
            self.isSelected = True
        elif event.button() == Qt.RightButton:
            self.setStyleSheet(
                "background-color: none;")
            self.isSelected = False
        return QPushButton.mousePressEvent(self, event)


class ChooseSeat(MyQDialog):
    """Диалог который предлагает пользователю выбрать места"""
    def __init__(self, parent, places):
        super().__init__(parent)
        self.parent = parent
        window_arr.append(self)
        self.places = places

        self.isSelected = False
        self.numb_of_choose_btn = []
        self.last_num_of_choose_btn = self.numb_of_choose_btn

        self.setupUi()
        self.buttonBox.accepted.connect(self.c_action)
        self.buttonBox.rejected.connect(self.set_default_places)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        # self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setToolTip("left-click  -  book"
                        "\nright-click  -  cancel your reservation")

    def setupUi(self):
        """Происходит загрузка интерфейса посредством циклического
        заполнения кнопок в зависимости от количества месте в базе

        UPD: окзалось, что можно выбрать любое количество мест,
        разве лишь будет немного изменен внешний вид при просомтре мест

        Реализовал через преобразование pyuic так как сначала прикинул нужный
        мне дизайн и потом отформатировал под свои задачи"""
        self.resize(599, 215)
        self.setWindowTitle('Выбор места')
        # self.setGeometry(300, 300, 300, 300)
        gridLayout = QtWidgets.QGridLayout(self)
        verticalLayout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        label.setFont(font)
        label.setStyleSheet("background-color: rgb(152, 152, 152);")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setText('Экран')
        verticalLayout.addWidget(label)
        spacerItem = QtWidgets.QSpacerItem(20, 40,
                                           QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        verticalLayout.addItem(spacerItem)
        verticalLayout_3 = QtWidgets.QVBoxLayout()

        self.bG = QButtonGroup()
        k = 3
        horizontalLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(40, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        horizontalLayout.addItem(spacerItem)

        for i in range(1, len(self.places) + 1):
            if i >= k:
                k += 2 + i
                spacerItem = QtWidgets.QSpacerItem(40, 20,
                                                   QtWidgets.QSizePolicy.
                                                   Expanding,
                                                   QtWidgets.QSizePolicy.
                                                   Minimum)
                horizontalLayout.addItem(spacerItem)
                verticalLayout_3.addLayout(horizontalLayout)

                spacerItem = QtWidgets.QSpacerItem(40, 20,
                                                   QtWidgets.QSizePolicy.
                                                   Expanding,
                                                   QtWidgets.QSizePolicy.
                                                   Minimum)
                horizontalLayout = QtWidgets.QHBoxLayout()
                horizontalLayout.addItem(spacerItem)

            pushButton = MyPushButton(str(i), self)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                               QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                pushButton.sizePolicy().hasHeightForWidth())
            pushButton.setSizePolicy(sizePolicy)
            if int(self.places[i - 1]):
                pushButton.setEnabled(False)
                pushButton.setStyleSheet(
                    "background-color: rgb(172, 163, 181);")
            horizontalLayout.addWidget(pushButton)
            self.bG.addButton(pushButton)

        spacerItem = QtWidgets.QSpacerItem(40, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        horizontalLayout.addItem(spacerItem)
        verticalLayout_3.addLayout(horizontalLayout)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)

        verticalLayout.addLayout(verticalLayout_3)
        gridLayout.addLayout(verticalLayout, 0, 0, 1, 1)
        gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(self)

    def set_selected_btn(self, num_of_choose_btn, isSelected):
        """При повторном октрытии диалога загружаются ранее выбранные места"""
        self.isSelected = isSelected
        btn_arr = self.bG.buttons()
        btns = []
        for num in num_of_choose_btn:
            btn = btn_arr[num]
            btn.isSelected = True
            btn.setStyleSheet(
                "background-color: rgb(255, 227, 156);")
            btns.append(num)
        self.last_num_of_choose_btn = btns

    def c_action(self):
        # при закрытии окна узнаем какие кнопки были выбраны и
        # сохраняем их в список
        buttons = self.bG.buttons()
        for btn in buttons:
            if btn.isSelected:
                self.numb_of_choose_btn.append(int(btn.text()) - 1)
        self.close()

    def set_default_places(self):
        # при закрытии окна с помощью кнопки "отмена"
        # восстанавливаются ранее выбранные кнопки
        if self.isSelected:
            self.numb_of_choose_btn = self.last_num_of_choose_btn
        self.close()

    def get_btn_numb(self):
        if self.numb_of_choose_btn:
            return self.numb_of_choose_btn


class TrailerWidget(MyQWidget):
    """Виджет, который показывает окно с трейлером
    В данный момент работает только если видео-файл находится на устройстве"""
    def __init__(self, parent, url, title):
        super().__init__()
        self.parent = parent
        window_arr.append(self)
        self.ui = uic.loadUi(path_for_gui + "trailer.ui", self)
        self.url = url
        self.setWindowTitle(title)

        # Попытки загружать через ссылки
        # playlist = QMediaPlaylist()
        # playlist.addMedia(QUrl("http://example.com/movie1.mp4"))
        #
        # player = QMediaPlayer()
        # player.setPlaylist(playlist)
        #
        # videoWidget = QVideoWidget()
        # player.setVideoOutput(videoWidget)
        # videoWidget.show()
        #
        # player.play()
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.url)))
        # self.player.setMedia(QMediaContent(QUrl('https://www.youtube.com/embed/xfIQ8h2_0TI')))
        self.player.setVideoOutput(self.ui.widget)
        self.play()
        self.play_btn.clicked.connect(self.play)
        self.pause_btn.clicked.connect(self.pause)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def closeEvent(self, a0: QCloseEvent):
        self.player.stop()
        super().closeEvent(a0)


class FilterDialog(MyQDialog):
    """Окно, которое отвечает за работу фильтра"""
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
        uic.loadUi(path_for_gui + 'filter.ui', self)
        self.setWindowTitle('Настройки сортировки')
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.buttonBox.accepted.connect(self.acept_data)
        self.buttonBox.rejected.connect(self.reject_data)
        self.a = {'year': [False, ''],
                  'genre': [False, ''],
                  'rating': [False, ''],
                  'producer': [False, '']}

    def reload_ui(self, y, g, r, p):
        self.comboBox.addItems(y)
        self.comboBox_2.addItems(g)
        self.comboBox_3.addItems(r)
        self.comboBox_4.addItems(p)

    def acept_data(self):
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

    def reject_data(self):
        self.close()

    def get_items(self):
        return self.a


class AdminSignIn(MyQDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        window_arr.append(self)
        uic.loadUi(path_for_gui + 'admin_sign_in.ui', self)
        self.pushButton.clicked.connect(self.acept_data)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.Form = parent

    def acept_data(self):
        # TODO вставить открытие интерфейса для админа
        # Открываем Интрефейс для админа
        if admin_login == self.lineEdit.text() and \
                admin_pass == self.lineEdit_2.text():
            pass
        else:
            self.statusBar.setText('Неправильно введен пароль или логин')
            return
        self.close()

    def reject_data(self):
        self.close()


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


# if __name__ == '__main__':
#

if __name__ == "__main__":
    window_arr = WindowArr()
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
