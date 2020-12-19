from PyQt5 import uic
from PyQt5.Qt import *
from main import MyQDialog

admin_login = 'admin'
admin_pass = 'admin'
path_for_gui = 'ui_files\\'


class AdminSignIn(MyQDialog):
    def __init__(self, parent, window_arr):
        super().__init__(parent, window_ar=window_arr)
        self.parent = parent
        window_arr.append(self)
        uic.loadUi(path_for_gui + 'admin_sign_in.ui', self)
        # self.setStyleSheet(open("styles/admin_style.css", "r").read())
        self.pushButton.clicked.connect(self.accept_data)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.Form = parent

    def accept_data(self):
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
