from PyQt5.Qt import *


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
        elif h in self.dct and obj.__class__.__name__ != 'Ticket' \
                and obj.__class__.__name__ in \
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
