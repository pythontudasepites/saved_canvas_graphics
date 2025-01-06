import tkinter as tk
from typing import NamedTuple
import math, cmath


# A grafikaelőállító függvények a következő jellemzőkkel bírnak:
# - csak egyetlen kötelezően megadandó pozícionális argumentumot fogadnak, ami a Canvas példány,
# - az átlátszóvá tenni kívánt rajzelemhez a 'fill_transparent' tag társul.
# - az aktuális canvas háttérszínnel egyező körvonal szín eléréséhez a rajzelemhez az 'outline_transparent' tag van hozzáadva.
# - nevük create_ kezdetű,
# - visszatérési értékük egy karakterlánc, amely a grafika összes rajzeleméhez tag-ként hozzá van rendelve.


class Point(NamedTuple):
    x: int | float
    y: int | float


def create_yin_yang(canvas: tk.Canvas) -> str:
    cnv_width, cnv_height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    cnv_center = Point(cnv_width / 2, cnv_height / 2)

    r = min(cnv_width, cnv_height) / 3
    # Nagy félkörök.
    canvas.create_arc(- r, - r, + r, + r, start=270, extent=180, fill='black', outline='black', tags='yin_yang')
    canvas.create_arc(- r, - r, + r, + r, start=90, extent=180, fill='white', outline='white', tags='yin_yang')
    # Kis félkörök.
    canvas.create_arc(- r / 2, 0, + r / 2, + r, start=270, extent=+180, fill='white', width=1, outline='white', tags='yin_yang')
    canvas.create_arc(- r / 2, 0, + r / 2, - r, start=90, extent=+180, fill='black', width=1, outline='black', tags='yin_yang')
    # Kis körök.
    dx = dy = r / 8
    canvas.create_oval(- dx, + r / 2 - dy, + dx, + r / 2 + dy, fill='black', outline='black', tags='yin_yang')
    canvas.create_oval(- dx, - r / 2 - dy, + dx, - r / 2 + dy, fill='white', outline='white', tags='yin_yang')

    canvas.move('yin_yang', *cnv_center)

    return 'yin_yang'


def create_ankh(canvas: tk.Canvas) -> str:
    cnv_width, cnv_height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    cnv_center = Point(cnv_width / 2, cnv_height / 2)

    canvas.create_polygon((0, -40), (25, 180), (-25, +180), tags='ankh')
    canvas.create_polygon((+20, 0), (-80, 25), (-80, -25), tags='ankh')
    canvas.create_polygon((-20, 0), (+80, 25), (+80, -25), tags='ankh')

    canvas.create_oval(-40, -40 - 65, +40, +40 - 65, fill='black', tags='ankh')
    canvas.create_arc(-50, -50, +50, +50, start=52, extent=76, fill='black', tags='ankh')

    canvas.create_oval(-40, -40 - 65, +40, +40 - 65, fill=canvas.cget('bg'), width=0,
                       tags=('inner', 'fill_transparent', 'outline_transparent', 'ankh'))
    canvas.create_arc(-50, -50, +50, +50, start=52, extent=76, fill=canvas.cget('bg'), width=0, outline=canvas.cget('bg'),
                      tags=('inner', 'fill_transparent', 'outline_transparent', 'ankh'))
    canvas.scale('inner', 0, 0, 0.7, 0.7)
    canvas.move('inner', 0, -20)

    canvas.move('ankh', *cnv_center)
    canvas.scale('ankh', *cnv_center, 2, 2)

    canvas.dtag('ankh', 'inner')

    return 'ankh'


def _create_right_angle_with_circular_arc(canvas: tk.Canvas, a, b, k=1.0, **options):
    cnv_width, cnv_height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    a, b = min(cnv_width, cnv_height) / 4, min(cnv_width, cnv_height) / 4 * b / a

    def get_line_y(x):
        y = (a / b) * x + 0.5 * (b ** 2 - a ** 2) / b
        return y

    def get_line_x(y):
        x = (y - 0.5 * (b ** 2 - a ** 2) / b) / (a / b)
        return x

    if max(a, b) == a:
        ccpx, ccpy = a, get_line_y(a)
    else:
        ccpx, ccpy = get_line_x(b), b

    ccpx, ccpy = k * ccpx, get_line_y(k * ccpx)

    r, fi1 = cmath.polar(complex(-ccpx, b - ccpy))
    _, fi2 = cmath.polar(complex(a - ccpx, -ccpy))
    fi1 = fi1 if fi1 >= 0 else math.tau + fi1
    fi2 = fi2 if fi2 >= 0 else math.tau + fi2
    dfi = abs(fi2 - fi1)

    n = 64

    circle_segment_points = tuple(map(lambda c: (c.real + ccpx, c.imag + ccpy),
                                      (cmath.rect(r, min(fi1, fi2) + dfi * i / n) for i in range(1, n))))
    shape_points = [(0, 0), (0, b), *circle_segment_points, (a, 0)]

    canvas.create_polygon(*shape_points, **options)


def create_right_angle_with_circular_arc(canvas: tk.Canvas) -> str:
    cnv_width, cnv_height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    cnv_center = Point(cnv_width / 2, cnv_height / 2)

    _create_right_angle_with_circular_arc(canvas, 3, 4, 1, tags='right_angle_with_circular_arc', fill='black')
    canvas.move('right_angle_with_circular_arc', *cnv_center)
    canvas.scale('right_angle_with_circular_arc', *cnv_center, 2, 2)
    return 'right_angle_with_circular_arc'


def create_diamonds_suit(canvas: tk.Canvas) -> str:
    cnv_width, cnv_height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    cnv_center = Point(cnv_width / 2, cnv_height / 2)

    type(canvas).reflect_across_x = lambda self, tag_or_id: self.coords(tag_or_id, *[coord if i % 2 == 0 else -coord
                                                                                     for i, coord in enumerate(canvas.coords(tag_or_id))])
    type(canvas).reflect_across_y = lambda self, tag_or_id: self.coords(tag_or_id, *[coord if i % 2 != 0 else -coord
                                                                                     for i, coord in enumerate(canvas.coords(tag_or_id))])

    for tag in ['right_arc' + str(i) for i in range(1, 5)]:
        _create_right_angle_with_circular_arc(canvas, 3, 4, 3, tags=(tag, 'diamonds_suit'), fill='red')

    canvas.reflect_across_x('right_arc1')
    canvas.reflect_across_x('right_arc2')
    canvas.reflect_across_y('right_arc2')
    canvas.reflect_across_y('right_arc4')

    canvas.move('diamonds_suit', *cnv_center)
    canvas.scale('diamonds_suit', *cnv_center, 2, 2)

    for tag in ['right_arc' + str(i) for i in range(1, 5)]:
        canvas.dtag('diamonds_suit', tag)

    return 'diamonds_suit'


def create_pinetree(canvas: tk.Canvas) -> str:
    cnv_width, cnv_height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    cnv_center = Point(cnv_width / 2, cnv_height / 2)
    type(canvas).reflect_across_y = lambda self, tag_or_id: self.coords(tag_or_id, *[coord if i % 2 != 0 else -coord
                                                                                     for i, coord in enumerate(canvas.coords(tag_or_id))])
    type(canvas).reflect_across_x = lambda self, tag_or_id: self.coords(tag_or_id, *[coord if i % 2 == 0 else -coord
                                                                                     for i, coord in enumerate(canvas.coords(tag_or_id))])
    color = 'green4'

    for i, args in enumerate(((4, 1.2, 0, 1), (7, 1.4, 70, 1.5), (6, 1.4, 160, 1.8)), 1):
        a, k, y, scale_fact = args
        _create_right_angle_with_circular_arc(canvas, a, 3, k, tags=(f'rarc{i}r', f'rarc{i}', 'pinetree'), fill=color)
        _create_right_angle_with_circular_arc(canvas, a, 3, k, tags=(f'rarc{i}l', f'rarc{i}', 'pinetree'), fill=color)
        canvas.reflect_across_x(f'rarc{i}r')
        canvas.reflect_across_x(f'rarc{i}l')
        canvas.reflect_across_y(f'rarc{i}l')
        canvas.move(f'rarc{i}', 0, y)
        canvas.scale(f'rarc{i}', 0, y, scale_fact, scale_fact)

    canvas.create_rectangle(-10, 160, +10, 200, fill=color, width=0, tags='pinetree')

    canvas.move('pinetree', *cnv_center)
    canvas.scale('pinetree', *cnv_center, 1.5, 2.25)

    for tag in ['rarc' + str(i) for i in range(1, 4)]:
        canvas.dtag('pinetree', tag)
        canvas.dtag('pinetree', tag + 'l')
        canvas.dtag('pinetree', tag + 'r')

    return 'pinetree'


def create_wheel(canvas: tk.Canvas) -> str:
    cnv_width, cnv_height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    cnv_center = Point(cnv_width / 2, cnv_height / 2)
    min_dim = min(cnv_width, cnv_height)

    radiuses = [r * min_dim for r in (1, 0.85, 0.8, 0.18, 0.07)]
    for i, radius in enumerate(radiuses, 1):
        canvas.create_oval(-radius, -radius, radius, radius, tags=('r' + str(i), 'wheel'))
    canvas.itemconfig('r1', fill='black')
    canvas.itemconfig('r2', fill='silver')
    canvas.itemconfig('r3', fill=canvas.cget('bg'), width=2)
    canvas.addtag_withtag('fill_transparent', 'r3')
    canvas.itemconfig('r4', fill='silver', width=2)
    canvas.itemconfig('r5', fill=canvas.cget('bg'), width=2)
    canvas.addtag_withtag('fill_transparent', 'r5')

    spoke_points = [(x * min_dim, y * min_dim) for x, y in ((-0.05, 0), (+0.05, 0), (+0.05, 0.79), (-0.05, 0.79))]

    for angle_deg in range(0, 360, 45):
        angle = math.radians(angle_deg)
        rotated_spoke_points = [(x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle)) for x, y in spoke_points]
        canvas.create_polygon(*rotated_spoke_points, fill='silver', width=0, tags=('spoke', 'wheel'))

    canvas.lower('spoke', 'r4')
    canvas.move('wheel', *cnv_center)
    canvas.scale('wheel', *cnv_center, 0.6, 0.6)

    for i in range(1, 6):
        canvas.dtag('wheel', 'r' + str(i))

    canvas.dtag('wheel', 'spoke')

    return 'wheel'

