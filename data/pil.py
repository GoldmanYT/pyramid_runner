from PIL import Image

a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'a1', 'b1', 'c1', 'd1', 'e1', 'f1']
f = '085.jpg'
d = []
h = 0
w = 0

for i in range(len(a)):
    try:
        im0 = Image.open(a[i] + '/' + f)
        x, y = im0.size
        w = max(w, x)
        h += y
    except FileNotFoundError:
        d.append(i)
for i in d[::-1]:
    a.pop(i)

im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
s = 0

for j, i in enumerate(a):
    im0 = Image.open(i + '/' + f)
    im.paste(im0, (0, s))
    x, y = im0.size
    s += y

im.save(input('Введите имя файла: '), 'PNG')
