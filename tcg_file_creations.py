import tkinter as tk
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showinfo, showerror
from pathlib import Path
from importlib import import_module
from tcg import TcgFileMaker, view_tcg_files
import sys


class TcgFileCreatorApp(tk.Tk):
    """
    GUI alkalmazás, amely egy megadható modulfájlban definiált egy vagy több tkinter canvas grafikát előállító függvény alapján
    a grafikákat leíró .tcg kiterjesztésű fájlokat készít és ment el egy előre megadható mappába. E mappába elmentett létező .tcg fájlok
    által definiált grafikákat egy közös ablakban táblázatos elrendezésben is meg lehet jeleníteni.
    A működéshez a grafikaelőállító függvényekre vonatkozóan vannak követelmények, amelyek az alábbiak:
    - nevük create_ kezdetű,
    - csak egyetlen kötelezően megadandó pozícionális argumentumot fogadhatnak, ami a Canvas példány,
    - az átlátszóvá tenni kívánt rajzelemhez a 'fill_transparent' tag van rendelve.
    - az aktuális canvas háttérszínnel egyező körvonal szín eléréséhez a rajzelemhez az 'outline_transparent' tag van rendelve.

    Az alkalmazás indítása után beviteli mezőkből és vezérlő gombokból álló felhasználó felület jelenik meg.
    A grafikaelőállító függvényeket tartalmazó modulfájl elérési útvonalát és az elkészült .tcg kiterjesztésű fájlok mentési mappájának
    útvonalát a megfelelő beviteli mezőkben két módon adhatjuk meg. Vagy manuálisan begépelve, vagy a beviteli mezők jobb szélén
    található, három ponttal jelzett nyomógomb megnyomására felugró párbeszédablak segítségével.

    Ha ezeket megadtuk, akkor a "TCG fájlnevek generálása" gombot megnyomva a modulfáljban található grafikaelőállító függvények nevei
    alapján a listadobozban egymás alatt fájlnevek jelennek meg, amely neveken a grafikák .tcg kiterjesztésű fájlokba menthetők.
    Ezek a nevek azonban csak ajánlott, alapértelmezett nevek. Ha mást szeretnénk, akkor módosítani lehet úgy, hogy kétszer a névre kell
    kattintani a bal egérgombbal, és a felugró beviteli párbeszédablakba az új nevet kell beírni, majd az OK gomb lenyomásával érvényesíteni.

    A "Grafika leíró fájlok készítése" gomb lenyomására a .tcg kiterjesztésű fájlok elkészülnek és a korábbban megadott mappába mentődnek.
    A sikeres műveletetről egy üzenetablak tájékoztat. Ha a fájlok készítése valamiért nem sikerül, akkor a hiba valószínű okáról szintén
    egy üzenetablakban kapunk információt.

    A megadott mentési mappában található .tcg fájlok által leírt grafikákat egyetlen ablakban táblázatos elrendezésben tekinthetjük meg, ha
    a "Mentett grafikák megjelenítése" gombot megnyomjuk.
    """
    def __init__(self):
        super().__init__()
        self.title('TCG fájlok készítése grafikaelőállító függvények alapján'.upper())
        self.resizable(False, False)
        self._tcgmaker = TcgFileMaker(self)  # A fájlkészítést ténylegesen végző objektum.
        # A fájlnevek és grafikaelőállító függvényobjektumok összerendelését tartalmazó szótár.
        self._filename_factory_functions = {}
        # Kontrollváltozók.
        # A grafikaelőállító függvények definícióit tartalmazó modulfájl elérési útvonalának változója.
        self._factories_module_path_var = tk.StringVar(self)
        # A .tcg fájlok mentési mappája útvonalának változója.
        self._tcg_files_folderpath_var = tk.StringVar(self)
        # A .tcg fájlneveket tároló változó.
        self._tcgfilenames_var = tk.StringVar(self)

        # A felhasználói felület felépítése a grafikus elemek létrehozásával.
        common_configs = dict(font=('Consolas', 14, 'bold'))
        lblfrm1 = tk.LabelFrame(self, text='Grafikaelőállító függvényeket tartalmazó modulfájl', **common_configs)
        ent1 = tk.Entry(lblfrm1, width=70, textvariable=self._factories_module_path_var, **common_configs)
        btn_module_selection_dialog = tk.Button(lblfrm1, text=chr(0x22ee), **common_configs, command=self._select_module_file)

        lblfrm2 = tk.LabelFrame(self, text='TCG fájlok mentési mappája', **common_configs)
        ent2 = tk.Entry(lblfrm2, width=70, textvariable=self._tcg_files_folderpath_var, **common_configs)
        btn_dir_selection_dialog = tk.Button(lblfrm2, text=chr(0x22ee), **common_configs,
                                             command=lambda: self._tcg_files_folderpath_var.set(askdirectory(title='TCG fájlok mentési mappája'.upper())))

        btn_gen_filenames = tk.Button(self, text='TCG fájlnevek generálása'.upper(), **common_configs, bg='gray87',
                                      command=self._get_factory_function_objects)

        lblfrm3 = tk.LabelFrame(self, text='TCG fájlok alapértelmezett nevei', **common_configs)
        lbox = tk.Listbox(lblfrm3, height=8, width=70, listvariable=self._tcgfilenames_var, **common_configs)
        yscb = tk.Scrollbar(lblfrm3, orient=tk.VERTICAL)
        lbox.config(yscrollcommand=yscb.set)
        yscb.config(command=lbox.yview)

        btn_makefiles = tk.Button(self, text='Grafika leíró fájlok készítése'.upper(), bg='gray87', **common_configs,
                                  command=self._create_tcg_files)

        btn_view = tk.Button(self, text='Mentett grafikák megjelenítése'.upper(), bg='gray87', **common_configs,
                             command=self._display_saved_graphics)

        # Grafikus elemek lehelyezése.
        common_grid_options = dict(sticky='news', padx=10, pady=10)
        lblfrm1.grid(row=0, column=0, **common_grid_options)
        ent1.grid(row=0, column=1, **common_grid_options)
        btn_module_selection_dialog.grid(row=0, column=2, **common_grid_options)
        btn_module_selection_dialog.grid_configure(padx=(0, 10))

        lblfrm2.grid(row=1, column=0, **common_grid_options)
        ent2.grid(row=1, column=1, **common_grid_options)
        btn_dir_selection_dialog.grid(row=1, column=2, **common_grid_options)
        btn_dir_selection_dialog.grid_configure(padx=(0, 10))

        btn_gen_filenames.grid(row=2, column=0, **common_grid_options)

        lblfrm3.grid(row=3, column=0, **common_grid_options)
        lbox.grid(row=3, column=0, **common_grid_options)
        yscb.grid(row=3, column=1, sticky='ns')

        btn_makefiles.grid(row=4, column=0, **common_grid_options)
        btn_view.grid(row=5, column=0, **common_grid_options)

        # Események és eseménykezelők listadobozhoz rendelése.
        lbox.bind('<Double Button 1>', self._modify_filename)
        lbox.bind('<Key Delete>', self._delete_filename)

    def _select_module_file(self):
        """Párbeszédablak megjelenítésével lehetővé teszi a grafikaelőállító függvények definícióit tartalmazó modulfájl
        útvonalának megadását.
        """
        module_path = askopenfilename(title='válaszd ki a grafikaelőállító függvények definícióit tartalmazó modult'.upper(),
                                      defaultextension='.py', initialdir=Path())
        # Ha a párbeszédablak nem üres karakterlánccal tér vissza, akkor a fájlútvonalat eltároljuk a megfelelő kontrollváltozóban.
        if module_path:
            self._factories_module_path_var.set(module_path)

    def _get_factory_function_objects(self):
        """A grafikaelőállító függvényeket tartalmazó modul beimportálása után a modulobjektumból kinyeri a függvényobjektumokat.
        A függvényobjektumok fájlnevekhez lesznek rendelve és e párok egy szótárban tárolódnak. A fájlnevek a grafikaelőállító függvények
        nevéból képződnek olyan módon, hogy a függvénynév 'create_' kezdete levágásra kerül.
        Az így kapott fájlnevekkel lesznek a listadoboz sorai feltöltve.
        """
        module_dir: str = str(Path(self._factories_module_path_var.get()).parent)  # A modulfájlt tartalmazó mappa.
        modulename: str = str(Path(self._factories_module_path_var.get()).stem)  # A modulnév a modulfájlnév alapján.
        # A grafikaelőállító függvényeket tartalmazó modul mappájának útvonalát felvesszük a rendszer keresési útvonalai közé.
        sys.path.append(module_dir)
        try:
            module_obj = import_module(modulename)  # A modulobjektum beimportálása.
        except (ValueError, ModuleNotFoundError):
            showerror('modulmegadási hiba'.upper(), 'Nem létező vagy hibásan megadott modul.')
            return

        except Exception:
            showerror('modulmegadási hiba'.upper(), 'Nem megfelelő modul lett importálva.')
            return

        # A függvényobjektumokat fájlnevekhez rendeljük és ezeket együtt egy szótárban tároljuk.
        # A fájlnevek a grafikaelőállító függvények nevéből képződnek a függvénynév 'create_' után maradt részéből.
        self._filename_factory_functions.update({attn.removeprefix('create_'): getattr(module_obj, attn)
                                                 for attn in dir(module_obj) if attn.startswith('create_')})
        # A fájlnevekkel a listadoboz sorait feltöltjük.
        self._tcgfilenames_var.set(' '.join(self._filename_factory_functions.keys()))
        # A grafikaelőállító függvényeket tartalmazó modul mappájának útvonalát eltávolítjuk a rendszer keresési útvonalai közül.
        sys.path.remove(module_dir)

    def _delete_filename(self, event):
        """Eseménykezelő, amely a listadoboz kiválasztott sorában szereplő fájlnevet törli.
        Törölt fájlnévhez tartozó .tcg fájl nem fog készülni.
        """
        lbox: tk.Listbox = event.widget
        i, *_ = event.widget.curselection()  # A hívás eredménye a listadoboz kiválasztott sorának indexét tartalmazó tuple.
        # A kiválasztott fájlnevet mind a listadobozból, mind a fájlnév-előállítőfüggvény nyilvántartásból töröljük.
        del self._filename_factory_functions[lbox.get(i)]
        lbox.delete(i)

    def _modify_filename(self, event):
        """Eseménykezelő, amely a listadoboz kiválasztott sorában szereplő fájlnév módosítását teszi lehetővé.
        Ehhez egy beviteli párbeszédablakot jelenít meg, amelyben az új fájlnév adható meg.
        """
        try:
            i, *_ = event.widget.curselection()  # A hívás eredménye a listadoboz kiválasztott sorának indexét tartalmazó tuple.
            names = list(eval(self._tcgfilenames_var.get()))  # A listadobozban felsorolt összes név listája.
            new_name = askstring('fájlnév megváltoztatás'.upper(),
                                 '{:80}'.format('Add meg az új fájlnevet!'), initialvalue=names[i])
            # Ha a párbeszédablak nem üres karakterlánccal tér vissza, akkor a régi nevet az újra cseréljük.
            if new_name:
                old_name = names[i]
                names[i] = new_name
                self._tcgfilenames_var.set(' '.join(names))
                self._filename_factory_functions.update({new_name: self._filename_factory_functions[old_name]})
                del self._filename_factory_functions[old_name]
        except ValueError:
            showerror('fájlnévmódosítási hiba'.upper(), 'Fájlnevek nem állnak rendelkezésre, ezért \nnincs mit módosítani.')

    def _create_tcg_files(self):
        """Az aktuális fájlnevekkel létrehozza a grafikaelőlállító függvényekkel definiált .tcg fájlokat. Sikeres fájlkészítés
        esetén tájékoztató üzenetablak ugrik fel.
        Ha a listadobozban nem szerepelnek fájlnevek, vagy a fájlkészítés bármilyen más okból nem lehetséges, akkor
        hibaüzenetetablak jelenik meg a hiba lehetséges okát leírva.
        """
        if self._filename_factory_functions:
            try:
                for filename, graphics_factory_function in self._filename_factory_functions.items():
                    self._tcgmaker.generate_tcg_file_from_factory(Path(self._tcg_files_folderpath_var.get()) / filename, graphics_factory_function)

                showinfo('fájlkészítés végrehajtva'.upper(), 'A listában szereplő nevekkel a .tcg kiterjesztésű fájlok elkészültek és '
                                                             'megtalálhatók a megadott mappában.')
            except TypeError:
                showerror('fájlkészítési hiba'.upper(), f'A {filename} névhez tartozó grafikaelőállító függvény nem megfelelő. '
                                                        f'A hiba oka lehet például:\n'
                                                        f'- nem fogad argumentumot\n'
                                                        f'- egynél több pozicionális argumentumot kell megadni.')
        else:
            showerror('fájlkészítési hiba'.upper(), 'Fájlnevek nem állnak rendelkezésre.')

    def _display_saved_graphics(self):
        """A korábban megadott mappába elmentett létező .tcg fájlok által definiált grafikákat egy közös ablakban
        táblázatos elrendezésben megjeleníti. Ha fáljból bármilyen okból nem lehet a grafikát előállítani, akkor az
        nem fog az ablakban megjelenni.
        """
        view_tcg_files(self, Path(self._tcg_files_folderpath_var.get()).glob('*.tcg'), bg='gray85')

    def run(self):
        self.mainloop()


TcgFileCreatorApp().run()
