from PyQt5.QtGui import QPixmap
from urllib.request import urlopen


def load_image_from_url(url):
    data = urlopen(url).read()
    pixmap = QPixmap()
    pixmap.loadFromData(data)
    return pixmap
