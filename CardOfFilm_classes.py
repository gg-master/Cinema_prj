from main import MyQWidget, MyQDialog, DataBase
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.Qt import *
import os
import load_url_img
import QRcode

db = DataBase('mydatabase.db')

path_for_gui = 'ui_files\\'
base_path_for_none_img = r'system_image\none_img.jpg'
path_for_system_img = 'system_image\\'
relative_path_for_media = 'films_image\\'
splitter_in_db = ' '
tickets_numb = int(open('tickets_numb.txt', 'r').read())


class Film:
    def __init__(self):
        self.title = ''
        self.path_poster = None
        self.path_image_1 = None
        self.path_image_2 = None
        self.path_trailer = None


class CardOfFilm(MyQWidget):
    """Окно карточки
    Представляет просмотр информации о фильме и возможности покупки билета
    """
    resized = QtCore.pyqtSignal()

    def __init__(self, parent, id_film, window_arr):
        self.id = id_film
        super().__init__(window_ar=window_arr)
        window_arr.append(self)
        self.window_arr = window_arr
        self.parent = parent
        self.setStyleSheet(open("styles/film_card.css", "r").read())
        uic.loadUi(path_for_gui + 'card_of_film.ui', self)

        self.setWindowTitle('Карточка фильма')
        self.playBtn.clicked.connect(self.play_trailer)
        self.buy_ticket_btn.clicked.connect(self.buy_ticket)
        self.poster.installEventFilter(self)
        self.poster_2.installEventFilter(self)
        self.resized.connect(self.resize_image)

        # Определение некотрых переменных
        self.Filmcl = Film()
        self.wind = None

        self.load_info()

    def eventFilter(self, obj, event):
        """Событие, которое реагирует на нажатия кнопкой мыши на
        дополнительные изображения в карточке фильма"""
        pixmap_p = None
        # Получаем путь к изображениям, установленных в label в gui
        if obj == self.poster:
            pixmap_p = self.Filmcl.path_image_1
        elif obj == self.poster_2:
            pixmap_p = self.Filmcl.path_image_2
        if pixmap_p is not None:
            if event.type() == QEvent.MouseButtonPress:
                mouse_event = QMouseEvent(event)
                if mouse_event.buttons() == Qt.LeftButton:
                    # Если левая кнопка удерживается,
                    # то открываем окно с увеличенной картинкой
                    self.wind = MyPopup(self, pixmap_p)
                    self.wind.show()
            if event.type() == QEvent.MouseButtonRelease:
                self.wind.close()

        return MyQWidget.eventFilter(self, obj, event)

    def resizeEvent(self, event):
        self.resized.emit()
        return super().resizeEvent(event)

    def resize_image(self):
        """Была идея сделать мастшабируемую
        картику в карточке фильма.
        Но из-за технических сложностей отложили эту фичу"""
        pass
        # pixmap_poster = QPixmap(self.Filmcl.path_poster)
        #
        # max_h, max_w = self.img.height(), self.img.width()
        # p_h, p_w = pixmap_poster.height(), pixmap_poster.width()
        # print('max', max_h, max_w)
        # print(p_h, p_w)
        # k_h = max_h / p_h
        # k_w = max_w / p_w
        # if p_h > p_w:
        #     h = max_h
        #     w = p_w * k_h
        # else:
        #     h = p_h * k_w
        #     w = max_w
        # # self.img.setPixmap(pixmap_poster.scaled(int(w), int(h),
        # #                                         Qt.KeepAspectRatio))
        # pixSize = QSize(self.img.pixmap().size())
        # pixSize.scale(w, h, Qt.KeepAspectRatio)
        # self.img.setFixedSize(pixSize)

    def buy_ticket(self):
        """Функция, которая открывает окно для покупки билетов"""
        bt = BuyTct(self, self.id, self.Filmcl.title)
        bt.show()
        bt.exec_()

    def load_info(self):
        """Загрузка основной информации в оставшиеся label в gui"""
        rez = db.request("SELECT * from films where id like ?",
                         self.id).fetchall()[0]
        self.Filmcl.title = rez[1]
        rating = rez[2]
        genre = rez[3]
        actors = rez[4]
        producer = rez[5]
        year = str(rez[6]) + ' год'
        duration = str(rez[7]) + " мин"
        description = rez[8]
        """Под постером подразумевается основная картинка
        Под images подразумеваются кадры из фильма и тд
        """
        poster = rez[9]
        images = rez[10]
        self.Filmcl.path_trailer = self.setTrailerPath(str(rez[11]))

        pixmap_poster = QPixmap(base_path_for_none_img)
        pixmap_image = QPixmap(base_path_for_none_img)
        pixmap_image_2 = QPixmap(base_path_for_none_img)

        """Загрузка изображений в соответствии с тем, явлется путь 
        ссылкой на картинку или это путь к локальному файлу"""
        if poster:
            poster = poster.split(splitter_in_db)
            for img in range(len(poster)):
                if poster[img] and not poster[img].startswith('http'):
                    poster[img] = \
                        f'{relative_path_for_media}{poster[img]}'
            for path_p in poster:
                if os.path.isfile(path_p):
                    pixmap_poster = QPixmap(path_p)
                    self.Filmcl.path_poster = path_p
                    break
                elif path_p.startswith('http'):
                    pixmap_poster = load_url_img.load_image_from_url(path_p)
                    self.Filmcl.path_poster = pixmap_poster
                    break
        if images:
            images = images.split(splitter_in_db)
            for img in range(len(images)):
                if images[img] and not images[img].startswith('http'):
                    images[img] = \
                        f'{relative_path_for_media}{images[img]}'
            for path_p in images:
                if self.Filmcl.path_image_1 is not None \
                        and self.Filmcl.path_image_2 is not None:
                    break
                if os.path.isfile(path_p):
                    if self.Filmcl.path_image_1 is None:
                        self.Filmcl.path_image_1 = path_p
                        pixmap_image = QPixmap(path_p)
                    elif self.Filmcl.path_image_2 is None:
                        self.Filmcl.path_image_2 = path_p
                        pixmap_image_2 = QPixmap(path_p)
                elif path_p.startswith('http'):
                    if self.Filmcl.path_image_1 is None:
                        pixmap_image = load_url_img.load_image_from_url(path_p)
                        self.Filmcl.path_image_1 = pixmap_image
                    elif self.Filmcl.path_image_2 is None:
                        pixmap_image_2 = load_url_img.load_image_from_url(
                            path_p)
                        self.Filmcl.path_image_2 = pixmap_image_2
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
        self.title_2.setText(self.Filmcl.title)
        self.rating_2.setText(str(rating))
        self.genre_2.setText(genre)
        self.producer_2.setText(producer)
        self.actors_2.setText(actors)

    def setTrailerPath(self, name):
        """Узнаем является ли файл локальным или путем является ссылка
        !!! Не реализована проверка валидности файла,
        при условии, что ссылка файла побита"""
        if name != 'None':
            import validators
            if name.startswith('http') and validators.url(name):
                return name
            elif os.path.isfile(relative_path_for_media + name):
                return relative_path_for_media + name
        return None

    def play_trailer(self):
        """Открывает окно по ссылке на файл"""
        if self.Filmcl.path_trailer is not None:
            self.vid = TrailerWidget(self, self.Filmcl.path_trailer,
                                     self.Filmcl.title)
            self.vid.show()
        else:
            self.statusBar.setText('Трейлер не найден')

    def __hash__(self):
        return hash(int(self.id))


class MyPopup(QWidget):
    """Выслывающее окно для увеличенного просмотра изображений."""
    def __init__(self, parent, pixmap_path):
        super().__init__()
        self.label = QLabel(self)
        # Установка отсутствия рамок
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        # Загрузка изображения
        pixmap = QPixmap(pixmap_path)
        # Установка размеров окна, и изображения
        max_h, max_w = parent.height() * (2 / 3), parent.width() * (2 / 3)
        p_h, p_w = pixmap.height(), pixmap.width()
        k_h = max_h / p_h
        k_w = max_w / p_w
        if p_h > p_w:
            h = max_h
            w = p_w * k_h
        elif p_h < p_w:
            h = p_h * k_w
            w = max_w
        self.resize(w, h)
        self.label.resize(w, h)
        self.move(parent.x() + parent.width() // 2 - self.label.width() // 2,
                  parent.y() + parent.height() // 2 - self.label.height() //
                  2 + 30)

        self.label.setPixmap(pixmap.scaled(self.width(), self.height(),
                                           Qt.KeepAspectRatio))


class BuyTct(MyQDialog):
    """Форма покупки билетов"""
    def __init__(self, parent, id, title):
        super().__init__(parent, window_ar=parent.window_arr)
        self.parent = parent
        parent.window_arr.append(self)
        # self.window_arr = window_arr

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        uic.loadUi(path_for_gui + 'buy_tck.ui', self)
        self.setStyleSheet(open("styles/buy_tct_style.css", "r").read())
        self.cancel.clicked.connect(self.close)
        self.accept.clicked.connect(self.accept_action)

        self.cinemas_2.activated.connect(self.load_time)
        self.times.activated.connect(self.load_other)

        self.choose_place_btn.clicked.connect(self.choose_seat)

        self.film_id = id
        self.film_title = title
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
        name_c = self.cinemas_2.currentText()
        self.time_s = self.times.currentText()

        rez_c = db.request("""SELECT * from cinemas 
                                    where name_cinema like ?""",
                           name_c).fetchall()[0]
        id_c = rez_c[0]
        rez_f = db.request("""Select time_end, places, price, id, 
        cinema_hall_id from timetable where id_film like ? and cinema_id like ? 
                and time_start  like ?""",
                           self.film_id, id_c, self.time_s).fetchall()[0]
        self.time_to.setText(rez_f[0])
        self.price.setText(str(rez_f[2]))
        self.places = rez_f[1].split(', ')
        self.id_films_in_c = rez_f[-2]
        self.cinema_hall_id = rez_f[-1]
        self.hall.setText(str(self.cinema_hall_id))

    def load_time(self):
        """Загрузка доступного времени в
        соответствии с выбранным кинотетром из базы"""
        name_c = self.cinemas_2.currentText()

        # Загрузка информации о кинотетре
        rez_c = db.request("""SELECT * from cinemas 
                            where name_cinema like ?""", name_c).fetchall()[0]

        self.adress.setText(rez_c[2])
        self.phone.setText(rez_c[3])
        self.time_to.setText('---------')

        # Загрузка времени
        id_c = rez_c[0]
        rez_time = db.request("""SELECT time_start from timetable 
        where id_film like ? and cinema_id like ?""",
                              self.film_id, id_c).fetchall()
        if not rez_time:
            self.statusBar.setText('Данного фильма не найденно')
            return
        rez_s = list(map(lambda x: str(x[0]), rez_time))
        self.times.clear()
        self.times.addItems(rez_s)

    def load_cinemas(self):
        # Загрузка времени и добавление в ComboBox
        self.title.setText(self.film_title)
        self.dct_cinema = {}
        rez = db.request("""SELECT id, name_cinema from cinemas""").fetchall()
        for i in rez:
            id, name = i[:2]
            self.dct_cinema[id] = name
        rez = list(self.dct_cinema.values())
        self.cinemas_2.addItems(rez)

    def closeEvent(self, a0: QCloseEvent):
        """Планировалось при мгновенном закрытии окна автоматически
            сохранять билеты по указанному ранее пути
        Но из-за особенности системы закрытия окон эта возможность
            пока не может быть реализована"""
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
        msg = QMessageBox()
        ret = msg.question(self, 'Подтверждение заказа',
                           "Действительно подтвердить покупку?",
                           msg.Yes | msg.No)
        if ret == msg.Yes:
            self.isAccepted = True
            for i in self.numb:
                self.places[i] = '1'
            s = f'{", ".join(self.places)}'
            req = f'{s}'
            db.request(f'''UPDATE timetable
                            set places = ?
                            WHERE id = ?''', req, self.id_films_in_c)
            db.commit()
            for i in range(len(self.numb)):
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


class TrailerWidget(MyQWidget):
    """Виджет, который показывает окно с трейлером
    В данный момент работает только если видео-файл находится на устройстве"""
    def __init__(self, parent, url, title):
        super().__init__(window_ar=parent.window_arr)
        self.parent = parent
        parent.window_arr.append(self)
        self.ui = uic.loadUi(path_for_gui + "trailer.ui", self)
        self.setStyleSheet(open("styles/trailer_style.css", "r").read())
        self.url = url  # url такой: films_image/name_file.MP4
        # print(self.url)
        self.setWindowTitle(title)

        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.url)))
        self.player.setVideoOutput(self.ui.widget)
        self.player.play()
        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)

    def closeEvent(self, a0: QCloseEvent):
        self.player.pause()
        super().closeEvent(a0)


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
        super().__init__(parent, window_ar=parent.window_arr)
        self.parent = parent
        parent.window_arr.append(self)
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
        self.numb_of_choose_btn = []
        for btn in buttons:
            if btn.isSelected:
                self.numb_of_choose_btn.append(int(btn.text()) - 1)
        super().closeEvent(QCloseEvent())

    def set_default_places(self):
        # при закрытии окна с помощью кнопки "отмена"
        # восстанавливаются ранее выбранные кнопки
        if self.isSelected:
            self.numb_of_choose_btn = self.last_num_of_choose_btn
        super().closeEvent(QCloseEvent())

    def get_btn_numb(self):
        if self.numb_of_choose_btn:
            return self.numb_of_choose_btn

    def closeEvent(self, a0: QCloseEvent):
        self.set_default_places()


class Ticket(MyQWidget):
    """Класс билета. Показывает билет, кнопку для
    выбора пути сохранения и созраняет билет по выбранному пути"""
    def __init__(self, parent, place, btn_for_auto_save=False):
        super().__init__(window_ar=parent.window_arr)
        self.parent = parent
        parent.window_arr.append(self)

        uic.loadUi(path_for_gui + 'successful_purchase.ui', self)
        self.setStyleSheet(open("styles/ticket_style.css", "r").read())
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

        self.BtnIsClicked = btn_for_auto_save
        self.label.setPixmap(self.pixmap)

    def make_qrcode(self):
        """Возврадащет сгенеррированный Qrcode как объект Qpixmap"""
        import qrcode
        from numpy import unicode
        text = unicode(f'Билет на фильм '
                       f'"{self.parent.film_title}" - Подтвержден')
        return qrcode.make(text, image_factory=QRcode.Image).pixmap()

    def save_tct(self):
        # Если кнопка была нажата и выбран корректный путь,
        # то выполняем сохранение
        global tickets_numb
        if self.BtnIsClicked:
            self.render(self.pixmap)
            self.pixmap.save(f'{self.way}/'
                             f'{self.parent.film_title}'
                             f'-Билет-№{tickets_numb}.jpg')
            tickets_numb += 1
            with open('tickets_numb.txt', 'w') as f:
                f.write(str(tickets_numb))

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