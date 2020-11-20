# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'card.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.Qt import *
import os


class BtnWid(QPushButton):
    def __init__(self, *args, film_id):
        super().__init__(*args)
        self.id = film_id


class Ui_Form(object):
    def setupUi(self, Form, id, title, rating, genre,
                                            year, images, rect=None):

        self.layoutWidget = QtWidgets.QWidget(Form)

        # self.layoutWidget.setStyleSheet(
        #     "background-color: rgb(228, 225, 229);")

        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 191, 341))
        # self.layoutWidget.setMaximumWidth(193)
        # self.layoutWidget.setMaximumHeight(346)

        self.layoutWidget.setMinimumSize(QtCore.QSize(193, 346))

        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.image_label = QtWidgets.QLabel(self.layoutWidget)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setObjectName("image_label_2")
        self.verticalLayout.addWidget(self.image_label)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName("formLayout")
        self.title = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.title.setFont(font)
        self.title.setObjectName("title_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.title)
        self.genre = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.genre.setFont(font)
        self.genre.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.genre.setObjectName("genre")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.genre)
        self.rating = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rating.setFont(font)
        self.rating.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.rating.setObjectName("rating")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.rating)
        self.year = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.year.setFont(font)
        self.year.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.year.setObjectName("year")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.year)
        self.verticalLayout.addLayout(self.formLayout)
        self.btn = BtnWid(self.layoutWidget, film_id=id)
        self.btn.setMinimumWidth(189)
        self.btn.setMinimumHeight(35)
        self.btn.setObjectName("btn")
        self.verticalLayout.addWidget(self.btn)

        self.retranslateUi(Form, title, rating, genre,
                                            year, images)
        QtCore.QMetaObject.connectSlotsByName(Form)
        return self.layoutWidget

    def retranslateUi(self, Form, title, rating, genre, year, images):
        _translate = QtCore.QCoreApplication.translate
        # Form.setWindowTitle(_translate("Form", "Form"))

        pixmap = QPixmap(images[1])
        if images[0] and os.path.isfile(images[0][0]):
            pixmap = QPixmap(images[0][0])

        # win_w, win_h = Form.width(), Form.height()
        # win_w, win_h = self.layoutWidget.width(), self.layoutWidget.height()
        win_w, win_h = 250, 400
        # Загрузка фото
        w_l, h_l = self.image_label.width(), self.image_label.height()
        self.image_label.setPixmap(pixmap.scaled(w_l + (win_w // 2.5),
                                                 h_l + (win_h // 2.5),
                                                 Qt.KeepAspectRatio))

        self.title.setText(_translate("Form", title))
        self.title.setWordWrap(True)
        self.genre.setText(_translate("Form", genre))
        self.rating.setText(_translate("Form", str(rating)))
        self.year.setText(_translate("Form", str(year)))
        self.btn.setText(_translate("Form", "Открыть карточку"))
        self.btn.clicked.connect(Form.open_card)