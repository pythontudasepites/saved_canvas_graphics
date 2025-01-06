import tkinter as tk
from pathlib import Path
import json
from collections.abc import Callable, Iterable
from typing import Any
import sys

assert sys.version_info[:2] >= (3, 10)  # A működéshez Python 3.10+ verzió szükséges.


class TcgFileMaker:
    """Az osztály példánya egy .tcg kiterjesztésű, tkinter canvas grafikát leíró fájlt készít a generate_tcg_file_from_factory() vagy
    generate_tcg_file_from_canvas() metódusok meghívásával. Az előbbit akkor kell meghívni, ha a grafika egy grafikaelőállító
    függvényben van definiálva. Az utóbbi metódust pedig akkor, ha a grafika egy vászon elemen van létrehozva és megjelenítve.
    """
    def __init__(self, master):
        super().__init__()
        self.canvas = tk.Canvas(master, width=master.winfo_screenwidth() / 2, height=master.winfo_screenheight() / 2)

    def _write_itemconfigs(self, filename: str | Path, canvas: tk.Canvas = None):
        """Az aktuális vászon elemen létrehozott grafika rajzelemeinek adatait (típus, koordinták és konfigurációs paraméterek értékei)
        JSON formátumban fájlba menti a megadott fájlnévvel.
        """
        # Ha a canvas argumentum meg van gadva, akkor azt, egyébként a példány saját canvas objektumát vesszük.
        _canvas = canvas if canvas is not None else self.canvas
        # A fill_transparent és outline_transparent tag-ek kivételével mindent törlünk az elmentendő rajzelemekről, hogy
        # későbbi felhasználásnál ne lehessen azonosító-tag egyezés más grafikákkal.
        for oid in _canvas.find_all():
            tags_string = _canvas.itemcget(oid, 'tags')
            tags_set = set(tags_string.split())
            _canvas.itemconfig(oid, tags=tuple({'outline_transparent', 'fill_transparent'} & tags_set))

        # A grafikát alkotó rajzelemek elmentendő adatait egy szótárban gyűjtjük össze, amelynek kulcsai a rajzelemazonosítók.
        # A kulcshoz tartozó érték egy háromelemű tuple, amelyben az elemek tartalma sorrendben:
        # - a rajzelem típusa ('rectangle', 'oval', arc' stb),
        # - a rajzelem koordinátáit tartalmazó lista,
        # - a rajzelem konfigurációs paramétereinek aktuális értékét tartalmazó szótár.
        canvas_items_data_to_be_saved: dict = {oid: (_canvas.type(oid),
                                                     _canvas.coords(oid),
                                                     {option_name: _canvas.itemcget(oid, option_name)
                                                      for option_name in _canvas.itemconfig(oid)}
                                                     )
                                               for oid in _canvas.find_all()
                                               }
        # Az adatokat tartalmazó szótárt JSON formátummal fájlba mentjük.
        json.dump(canvas_items_data_to_be_saved, open(Path(filename), "w", encoding='UTF8'), indent=4)

    def generate_tcg_file_from_factory(self, filename: str | Path, canvas_graphics_factory_function: Callable[[tk.Canvas], Any]):
        """Az inicializáláskor létrejövő canvas elemen előállítja a grafikát, meghívva a megadott canvas_graphics_factory_function
        grafikaelőállító függvényt. E függvény egyetlen, kötelezően megadandó pozícionális argumentumot fogad, egy vászon elemet, amelyen
        a grafikát az összetevő rajzelemek (téglalap, sokszög, ellipszis, ellipszisív és vonal) létrehozásával valósítja meg.
        Ezt követően a grafikát alkotó rajzelemek adatai a megadott nevű fájlba .tcg kiterjesztéssel el lesznek mentve.
        """
        canvas_graphics_factory_function(self.canvas)
        filepath = Path(filename).with_suffix('.tcg')
        self._write_itemconfigs(filepath)
        self.canvas.delete('all')

    def generate_tcg_file_from_canvas(self, filename: str | Path, canvas: tk.Canvas):
        """A megadott canvas elemen meglévő grafika rajzelemeinek adatait a megadott nevű fájlba .tcg kiterjesztéssel elmenti."""
        filepath = Path(filename).with_suffix('.tcg')
        self._write_itemconfigs(filepath, canvas)


class Tcg:
    """Az osztály példánya az inicializáláskor megadott fájl által definiált tkinter canvas grafikát állítja elő és
    jeleníti meg a megadott vászon elemen, amikor a render() metódus meghívásra kerül. Ezt követően a grafika áthelyezhető és
    átméretezhető a példányon meghívott megfelelő metódusokkal.
    A példány metódusainak meghívása helyett a Canvas metódusaival is megvalósíthatók a műveletek, amelyekhez a példány
    id_tag azonosító tag-e használható a metódus által elvárt tag_or_id argumentumként.
    Ha grafika előállításakor egy rajzelemen a 'fill_transparent' tag található, akkor az adott rajzelem kitöltőszíne a vászon
    aktuális háttérszínével fog megegyezni, az átlátszóság érzetét keltve.
    Ha a grafika előállításakor a rajzelemen az 'outline_transparent' tag található, akkor az adott rajzelem körvonalának színe
    a vászon aktuális háttérszínével fog megegyezni.
    """
    def __init__(self, canvas: tk.Canvas, tcg_filepath: str | Path):
        self.canvas = canvas  # Az a Canvas példány, amelyen a grafikát megjelenítjük.
        self.id_tag = Path(tcg_filepath).stem + str(id(self))  # A grafika egyedi azonosító tag-e.
        self._filepath = str(tcg_filepath)  # A grafikát leíró adatokat tartalmazó fájl elérési útvonala.
        # A grafikát leíró JSON fájlból az adatok szótárba olvasása.
        self._graphics_definitions: dict = json.load(open(Path(tcg_filepath), "r", encoding='UTF8'))

    def __str__(self) -> str:
        return f'{type(self).__name__} object | obj id = {hex(id(self))} | id tag = "{self.id_tag}"'

    def _create_canvas_item(self, item_data: tuple[str, tuple | list, dict], id_tag: str) -> None:
        """A példány canvas elemén létrehoz egy, az item_data argumentumban foglalt adatokkal jellemzett rajzelemet, és
        ehhez az id_tag tag-et adja hozzá.
        Az item_data egy olyan tuple, amelynek elemei sorrendben:
        - a rajzelem típusa ('rectangle', 'oval', arc', 'line', 'polygon'),
        - a rajzelem koordinátáit tartalmazó tuple vagy lista,
        - a rajzelem konfigurációs paramétereinek aktuális értékét tartalmazó szótár.
        """
        # Ellenőrizzük, hogy az item_data megfelel a követelményeknek.
        match item_data:
            case ['arc' | 'oval' | 'rectangle' | 'line' | 'polygon' as item_type, [*coords], dict() as configs]:
                pass
            case _:
                raise ValueError('A rajzelemleíró szekvencia nem megfelelő')
        # A példány canvas elemén az adott koornitákkal létrehozzuk a megfelelő típusú rajzelemet, kihasználva, hogy a
        # Canvas rajzelem-létrehozó metódusainak neve egységesen 'create_' + típusnév felépítésűek.
        oid = getattr(self.canvas, 'create_' + item_type)(*coords)
        # A kapott egyedi rajzelem azonosítót felhasználva konfiguráljuk a rajzelemet az item_data harmadik eleme szerint.
        self.canvas.itemconfig(oid, **configs)
        # Ha a konfigurációs paraméterek között a tags opció tartalmazza a 'fill_transparent' tag-et, akkor a rajzelem háttérszínét
        # a canvas aktuális háttérszínére változtatjuk, amivel az átlátszóság hatását keltjük.
        if 'fill_transparent' in configs['tags']:
            self.canvas.itemconfig(oid, fill=self.canvas.cget('bg'))
        # Ha a konfigurációs paraméterek között a tags opció tartalmazza az 'outline_transparent' tag-et, akkor a rajzelem körvonalszínét
        # a canvas aktuális háttérszínére változtatjuk.
        if 'outline_transparent' in configs['tags']:
            self.canvas.itemconfig(oid, outline=self.canvas.cget('bg'))
        # Az így létrehozott rajzelemhez az id_tag argumentum szerinti tag-et mint azonosítócímkét rendeljük.
        self.canvas.addtag_withtag(id_tag, oid)

    def render(self, x, y) -> str:
        """Az inicializáláskor megadott fájlból származó rajzelemadatok alapján előállítja és megjeleníti a grafikát
        a vásznon úgy, hogy befoglaló téglalapjának bal felső sarokpontja az x, y koordinátákra kerül.
        Visszatérési értéke a grafika egyedi azonosító tag-e.
        """
        for item_data in self._graphics_definitions.values():
            self._create_canvas_item(item_data, self.id_tag)
        x1, y1, *_ = self.canvas.bbox(self.id_tag)
        self.canvas.move(self.id_tag, x - x1, y - y1)
        return self.id_tag

    @property
    def file(self) -> str:
        """Visszaadja a grafikát leíró adatokat tartalmazó fájl elérési útvonalát."""
        return self._filepath

    @property
    def center_point(self) -> tuple[float, float]:
        """A megjelenített grafika középpontjának koordinátáit adja vissza egy tuple objektumban."""
        x1, y1, x2, y2 = self.canvas.bbox(self.id_tag)
        return (x1 + x2) / 2, (y1 + y2) / 2

    @property
    def dimensions(self) -> tuple[int, int]:
        """A megjelenített grafika pixelben mért szélességét és magasságát adja vissza egy tuple objektumban."""
        x1, y1, x2, y2 = self.canvas.bbox(self.id_tag)
        return x2 - x1, y2 - y1

    @property
    def width(self) -> int:
        """Visszaadja a megjelenített grafika szélességét pixelben."""
        return self.dimensions[0]

    @property
    def height(self) -> int:
        """Visszaadja a megjelenített grafika magasságát pixelben."""
        return self.dimensions[1]

    def move(self, dx, dy):
        """A megjelenített grafikát jelenlegi pozícióhoz képest x irányban dx, y irányban dy értékekkel növelt
        koordinátákra helyezi át a vásznon.
        """
        self.canvas.move(self.id_tag, dx, dy)

    def move_to(self, x, y):
        """Áthelyezi a megjelenített grafikát úgy, hogy befoglaló téglalapjának bal felső sarokpontja az x, y koordinátákra kerül."""
        x1, y1, *_ = self.canvas.bbox(self.id_tag)
        self.move(x - x1, y - y1)

    def move_center_to(self, x, y):
        """Áthelyezi a megjelenített grafikát úgy, hogy annak középpontja az x, y koordinátákra kerül."""
        cpx, cpy = self.center_point
        self.move(x - cpx, y - cpy)

    def scale(self, x_scale, y_scale):
        """A megjelenített grafika méretét x irányban x_scale, y irányban y_scale szeresre változtatja."""
        self.canvas.scale(self.id_tag, *self.center_point, x_scale, y_scale)


def view_tcg(root, filename: str | Path, **canvas_configs):
    """A filename argumentummal megadott .tcg fájl által definiált grafikát egy ablakban elhelyezett vászon elemen megjeleníti.
    Ha a fájlból bármilyen okból nem lehet a grafikát előállítani, akkor az nem fog az ablakban megjelenni.
    A root argumentumként a főablakot (gyökérelemet) kell megadni.
    """
    # Az ablak létrehozása.
    window = tk.Toplevel(root)
    window.title(f'Tkinter Canvas Graphics (TCG) Viewer - File: {filename}')
    scr_w, scr_h = window.winfo_screenwidth(), window.winfo_screenheight()
    cnv_w, cnv_h = scr_w / 2, scr_h / 2
    # A vászon elem létrehozása, konfigurálása és lehelyezése az ablakban.
    canvas = tk.Canvas(window, width=cnv_w, height=cnv_h)
    canvas.config(**canvas_configs)
    canvas.pack()
    try:
        # A vászon és a megadott fájl ismeretében a Tcg objektum létrehozása.
        tcg = Tcg(canvas, filename)
        # A Tcg példányt használva a grafika előállítása és megjelenítése.
        tcg.render(0, 0)
        # A megjelenített grafikát a vászon középére helyezzük és átméretezzük úgy, hogy a vászon területén
        # teljes egészében látszódjon.
        tcg.move_center_to(cnv_w / 2, cnv_h / 2)
        tcg.scale(k := min(cnv_w, cnv_h) * 0.8 / max(tcg.dimensions), k)

    except Exception:
        pass


def view_tcg_files(root, filenames: Iterable[str | Path], **canvas_configs):
    """A filenames argumentummal megadott létező .tcg fájlok által definiált grafikákat egy közös ablakban
    táblázatos elrendezésben megjeleníti. Ha egy fájlból bármilyen okból nem lehet a grafikát előállítani, akkor
    az nem fog az ablakban megjelenni.
    A root argumentumként a főablakot (gyökérelemet) kell megadni.
    """
    # Az iterálható objektumként átadott fájlútvonalakból csak a létező, .tcg kiterjesztéssel rendelkezőket tartjuk meg.
    filenames = tuple(filename for filename in filenames if Path(filename).exists() and Path(filename).suffix == '.tcg')
    # Ha van legalább egy érvényes fájl, akkor az vagy azok által definiált grafikákat táblázatosan megjelenítjük.
    if filenames:
        # Az ablak létrehozása a képernyő közepén a képernyőmérethez igazított szélességgel és magassággal.
        window = tk.Toplevel(root)
        window.title('Tkinter Canvas Graphics (TCG) Viewer')
        scr_w, scr_h = window.winfo_screenwidth(), window.winfo_screenheight()
        window_width, window_height = int(scr_w * 0.8), int(scr_h * 0.8)
        window_x = scr_w // 2 - window_width // 2
        window_y = scr_h // 2 - window_height // 2
        window.geometry(f'{window_width}x{window_height}+{window_x}+{window_y}')
        # A táblázatos elrendezés sor- és oszlopszámának meghatározása a megjelenítendő grafikák
        # száma alapján úgy, hogy a sor- és oszlopszám minél közelebb legyen egymáshoz.
        n = len(filenames)
        rowcount = round(n ** 0.5)
        columncount = n // rowcount if n % rowcount == 0 else n // rowcount + 1
        # A létező fájlok által definiált grafikákat külön rácscellákban, saját vásznon jelenítjünk meg.
        for i, filename in enumerate(filenames):
            canvas = tk.Canvas(window, width=window_width / columncount, height=window_height / rowcount)
            canvas.config(**canvas_configs)
            ri, ci = divmod(i, columncount)
            canvas.grid(row=ri, column=ci)
            try:
                # A vászon és a megadott fájl ismeretében a Tcg objektum létrehozása.
                tcg = Tcg(canvas, filename)
                # A Tcg példányt használva a grafika előállítása és megjelenítése.
                tcg.render(0, 0)
                # A megjelenített grafikát az aktuális vászon középére helyezzük és átméretezzük úgy, hogy a vászon területén
                # teljes egészében látszódjon.
                canvas.update_idletasks()  # A canvas elem méretének lekérdezése előtt annak frissítése.
                cnv_width, cnv_height = canvas.winfo_width(), canvas.winfo_height()  # A canvas elem méretének lekérdezése.
                tcg.move_center_to(cnv_width / 2, cnv_height / 2)
                tcg.scale(k := min(cnv_width, cnv_height) * 0.8 / max(tcg.dimensions), k)

            except Exception:
                pass
