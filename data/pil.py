from PIL import Image

im = Image.open('spawner.png')
pix = im.load()
x, y = im.size

for i in range(x):
    for j in range(y):
        color = list(pix[i, j])
        if not all(i == 255 for i in color[:3]):
            color[3] = 255
        pix[i, j] = tuple(color)

im.save('spawner2.png')
