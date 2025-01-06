import tkinter as tk
from typing import NamedTuple
from math import cos, sin, radians

# A grafikaelőállító függvények a következő jellemzőkkel bírnak:
# - csak egyetlen kötelezően megadandó pozícionális argumentumot fogadnak, ami a Canvas példány,
# - az átlátszóvá tenni kívánt rajzelemhez a 'fill_transparent' tag társul.
# - az aktuális canvas háttérszínnel egyező körvonal szín eléréséhez a rajzelemhez az 'outline_transparent' tag van hozzáadva.
# - nevük create_ kezdetű,
# - visszatérési értékük egy karakterlánc, amely a grafika összes rajzeleméhez tag-ként hozzá van rendelve.


class Point(NamedTuple):
    x: int | float
    y: int | float


def create_drop(canvas: tk.Canvas) -> str:
    cnv_width, cnv_height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    cnv_center = Point(cnv_width / 2, cnv_height / 2)

    r = min(cnv_width, cnv_height) / 4
    alpha = 20  # degrees.
    alpha_rad = radians(alpha)
    color = 'sky blue'
    canvas.create_arc(-r, -r, +r, +r, start=alpha, extent=-180 - 2 * alpha, fill=color, width=0, outline='', tags='drop')
    p1 = 0, 0
    p2 = r * cos(alpha_rad), -r * sin(alpha_rad)
    p3 = 0, -r / sin(alpha_rad)
    p4 = -r * cos(alpha_rad), -r * sin(alpha_rad)

    canvas.create_polygon(p1, p2, p3, p4, fill=color, width=0, outline='', tags='drop')

    canvas.move('drop', *cnv_center)

    return 'drop'


def create_candle(canvas: tk.Canvas) -> str:
    cnv_width, cnv_height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    cnv_center = Point(cnv_width / 2, cnv_height / 2)
    h = min(cnv_width, cnv_height) / 2
    w = h / 4

    flame = create_drop(canvas)
    canvas.itemconfig(flame, fill='yellow')
    canvas.move(flame, -2 * cnv_center.x, -2 * cnv_center.y)
    canvas.scale(flame, -cnv_center.x, -cnv_center.y, 0.2, 0.2)

    canvas.create_oval(-w / 2, -h / 20 + h, +w / 2, +h / 20 + h, fill='#F3E6DC', width=0, outline='', tags='candle')

    canvas.create_arc(-w / 2, -h / 20 + h, +w / 2, +h / 20 + h, start=0, extent=-180,
                      fill='#F3E6DC', style='arc', width=1, outline='black', tags='candle')

    canvas.create_rectangle(-w / 2, 0, +w / 2, +h, fill='#F3E6DC', width=0, outline='', tags='candle')

    canvas.create_oval(-w / 2, -h / 20, +w / 2, +h / 20, fill='white', tags='candle')

    canvas.create_line(0, 0, 0, -h / 6, width=2, tags='candle')  # kanóc

    canvas.create_line(-w / 2, 0, -w / 2, h, tags='candle')
    canvas.create_line(+w / 2, 0, +w / 2, h, tags='candle')

    canvas.move('candle', -cnv_center.x, -cnv_center.y + h / 6)

    canvas.addtag_withtag('candle', flame)
    canvas.dtag('candle', 'drop')

    x1, y1, x2, y2 = canvas.bbox('candle')
    candle_cp = Point((x1 + x2) / 2, (y1 + y2) / 2)
    canvas.move('candle', cnv_center.x - candle_cp.x, cnv_center.y - candle_cp.y)

    return 'candle'


def create_star(canvas: tk.Canvas) -> str:
    cnv_width, cnv_height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    cnv_center = Point(cnv_width / 2, cnv_height / 2)

    def rotate_around_origin(_canvas, tag_or_id, angle_deg):
        coords_iter = iter(_canvas.coords(tag_or_id))
        rotated_coordinates = []
        for x, y in zip(coords_iter, coords_iter):
            x_rot = x * cos(radians(angle_deg)) - y * sin(radians(angle_deg))
            y_rot = x * sin(radians(angle_deg)) + y * cos(radians(angle_deg))
            rotated_coordinates.extend((x_rot, y_rot))
        return rotated_coordinates

    a = min(cnv_width, cnv_height) / 8
    b = a * 6
    canvas.create_polygon(-a, 0, 0, b, +a, 0, fill='yellow', tags=('star', 'beam0'))
    for i in range(1, 8):
        canvas.create_polygon(*rotate_around_origin(canvas, 'beam' + str(i - 1), 45 * i),
                              fill='yellow', tags=('star', 'beam' + str(i)))

    x1, y1, x2, y2 = canvas.bbox('star')
    star_cp = Point((x1 + x2) / 2, (y1 + y2) / 2)
    canvas.move('star', cnv_center.x - star_cp.x, cnv_center.y - star_cp.y)

    for tag in ['beam' + str(i) for i in range(0, 8)]:
        canvas.dtag('star', tag)

    return 'star'
