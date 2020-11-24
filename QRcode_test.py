import qrcode
# пример данных
data = "Это я"
# имя конечного файла
filename = "text.png"
# генерируем qr-код
img = qrcode.make(data)
# сохраняем img в файл
img.save(filename)
