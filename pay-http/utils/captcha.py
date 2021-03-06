from os import path, walk
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter


_letter_cases = "abcdefghjkmnpqrstuvwxy"

_upper_cases = _letter_cases.upper()

_numbers = ''.join(map(str, range(3, 10)))

init_chars = ''.join((_letter_cases, _upper_cases, _numbers))



FONT_PATH =  path.join(path.dirname(path.dirname(__file__)),
                      'static/font/')

font_list = []

for a, b, c in walk(FONT_PATH):
    font_list.append(c)
font_list = [FONT_PATH + file_name for file_name in font_list[0]]


def create_captcha(size=(120, 30),
                   chars=init_chars,
                   img_type="GIF",
                   mode="RGB",
                   bg_color=(122, 116, 95),
                   fg_color=(0, 0, 255),
                   font_size=18,
                   font_type=random.choice(font_list),
                   length=4,
                   draw_lines=True,
                   n_line=(0, 1),
                   draw_points=True,
                   point_chance=1):
    width, height = size
    img = Image.new(mode, size, bg_color)
    draw = ImageDraw.Draw(img)

    def get_chars():
        return random.sample(chars, length)

    def create_lines():
        line_num = random.randint(*n_line)
        for i in range(line_num):
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(0, 0, 0))

    def create_points():
        chance = min(100, max(0, int(point_chance)))

        for w in xrange(width):
            for h in xrange(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs():
        c_chars = get_chars()
        strs = ' %s ' % ' '.join(c_chars)

        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(strs)
        draw.text(((width - font_width) / 4, (height - font_height) / 4),
                  strs, font=font, fill=fg_color)

        return ''.join(c_chars)
    if draw_lines:
        create_lines()
    if draw_points:
        create_points()
    strs = create_strs()
    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    img = img.transform(size, Image.PERSPECTIVE, params)
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    img.rotate(random.randint(30, 100), expand=0)
    return img, strs


if __name__ == "__main__":
    code_img = create_captcha()
    code_img[0].save("xiaorui.cc.gif", "GIF")
    print code_img[1]
