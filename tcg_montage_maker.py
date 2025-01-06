import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter.filedialog import askdirectory, asksaveasfilename, askopenfilename
from pathlib import Path
from itertools import count
from operator import itemgetter
from tcg import Tcg, TcgFileMaker, view_tcg


class TcgMontageMakerApp(tk.Tk):
    """
    GUI alkalmazás, amellyel .tcg fájlokban definiált grafikák felhasználásával egy új grafikát lehet készíteni az alkalmazás
    erre szolgáló felületén. Az egyéni terv szerint elrendezett (áthelyezett és/vagy átméretezett) komponens grafikákból álló
    montázst egy megadható mappába lehet elmenteni .tcg fájl formátumban. Ezt követően a montázst meg is lehet jeleníteni egy
    külön ablakban.
    Az alkalmazás indítása után a beviteli mezők és vezérlő gombok a bal oldalon, a vizuális grafikai tervező felület a jobb oldalon
    látható.

    A mappaútvonalakat a beviteli mezőkben két módon adhatjuk meg. Vagy manuálisan begépelve, vagy a beviteli mezők jobb szélén
    található, három ponttal jelzett nyomógomb megnyomására felugró párbeszédablak segítségével.

    A "Komponens Tcg fájlok beolvasása" gombra kattintva az első beviteli mezőben megadott mappában levő .tcg fájlok beolvasása
    megtörténik, és a fájlnevek a listadobozban jelennek meg egymás alatt.

    A felsorolt fájlnevek közül kiválaszthatjuk, hogy melyekhez tartozó grafikákat akarjuk megjeleníteni a jobb oldali felületen.
    Ha egy sorban a bal egérgombbal kattintunk, akkor csak az a fájlnév lesz kiválasztva. Ha egyszerre többet akarunk kiválasztani,
    akkor ezt több módon is megtehetjük. Ha egymást követő több sort akarunk egyszerre kijelölni, akkor a kezdősoron nyomjuk le a
    bal egérgombot, majd a blokk utolsó során a Shift billentyű lenyomva tartása mellett újra nyomjuk le a bal egérgombot.
    Ha több, de nem egymást követő sorokat akarunk kijelölni, akkor a Control billentyűt lenyomva tartva nyomjuk le a bal egérgombot
    a kívánt sorokon.
    Azt, hogy mely sorok vannak kijelölve onnan látható, hogy a háttérszínük megváltozik. A legutoló kijelölést az ESC billentyűvel
    lehet törölni.

    A kívánt sorok kijelölése után a "A kijelölt egy vagy több fájl grafikájának megjelenítése" gombra kattintva a grafikák a jobb
    oldali felület közepén egymás felett jelennek meg. Innen az adott grafikát elmozgathatjuk a szokásos módon, azaz a bal egérgombot
    a grafikán lenyomva tartva az egérmutatót a kívánt helyre húzzuk és ott az egérgombot elengedjük.

    A felületen megjelent komponens grafikák nagyíthatók vagy kicsinyíthetők. Ehhez az egeret az adott grafika fülé kell vinni és a
    görgővel felfelé vagy lefelé görgetni. Az előbbi esetben a rajz mérete finom léptékben nő, az utóbbi esetben csökken. Ha gyorsabban,
    azaz nagyobb léptékben akarjuk a méretváltoztatást, akkor a görgetés közben a Control billentyűt lenyomva kell tartani.

    A grafikák, ha területük fedik egymást, akkor az átfedő területen az egyik kitakarja a másikat. Az, hogy melyik grafika melyiket
    takarja el, egy megjelenítési sorrendet határoz meg. Ha azt szeretnénk, hogy egy adott grafika ebben a sorrendben egy szinttel feljebb
    kerüljön, akkor az egérmutatót vigyük a grafika fölé, és nyomjuk le a Shift billentyűt majd a bal egérgombot. Ha egy szinttel lejjebb
    akarjuk küldeni, akkor nyomjuk le a Control billentyűt majd a bal egérgombot.
    Ha a grafikát a megjelenítési lista legtetejére akarjuk hozni, akkor nyomjuk le az Alt és Shift billentyűt majd a bal egérgombot.
    Ha a grafikát a megjelenítési lista legaljára akarjuk küldeni, akkor nyomjuk le az Alt és Control billentyűt majd a bal egérgombot.

    A tervezőfelületről grafikát úgy lehet eltávolítani, ha az egermutatót a grafika felett van és lenyomjuk a jobb egérgombot.

    A vászon színének megváltoztatására is van lehetőség, ha a vászon egy pontján az Alt billentyűt lenyomva tartva lenyomjuk a jobb
    egérgombot. Az ezt követően felugró színválasztó párbeszédablakban ki kell választani az új háttérszínt.

    Ha a montázs elkészült, akkor azt a "A létrehozott montázs grafika mentése TCG fájlba" gomb megnyomásával menthetjük el megadva a
    fájlnevet a felugró párbeszédablakban. A mentés után a montázs törlődik, tiszta felületet adva a következő alkotáshoz.

    A mentési mappába került montázsok megtekinthetők, ha a "Mentett grafikák megjelenítése" gomb lenyomása után felugró párbeszédablakban
    kiválasztunk egy .tcg fájlt. Alapértelmezésben az ablak a legutoljára elmentett montázs fájlnevét kínálja fel.
    """
    _cntr = count()  # Sorszámgenerátor az ugyanolyan grafikák másolatainak megkülönböztetéséhez.

    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        self.title('tkinter canvas grafika montázs készítő'.title())
        self._tcgfilemaker = TcgFileMaker(self)  # A fájlkészítést ténylegesen végző objektum.

        # Kontrollváltozók
        self._input_tcg_folderpath_var = tk.StringVar(self)  # A montázs komponesek .tcg fájljainak a mappaútvonalát tároló változó.
        self._output_tcg_folderpath_var = tk.StringVar(self)  # Az elkészült montázs .tcg fájljának mentési mappaútvonalát tároló változó.
        self._tcgfilenames_var = tk.StringVar(self)  # A listadobozban felsorolt .tcg fájlok neveit tároló változó.
        self._tcg_objects: list[Tcg] = []  # A komponens .tcg fájlokból előállított Tcg objektumok.
        self._rendered_tcg_objects: list[Tcg] = []  # Az előállított és megjelenített grafikákhoz tartozó Tcg objektumok.
        self._filename = ''

        # A grafikus felhasználói felület elemeinek létrehozása.
        frm_left, frm_right = tk.Frame(self), tk.Frame(self)

        self._canvas = tk.Canvas(frm_right, width=800, bg='ivory2')

        common_configs = dict(font=('Consolas', 14, 'bold'))
        lblfrm1 = tk.LabelFrame(frm_left, text='Kompones TCG fájlok mappája', **common_configs)
        ent1 = tk.Entry(lblfrm1, width=70, textvariable=self._input_tcg_folderpath_var, **common_configs)
        btn_input_dir_dialog = tk.Button(lblfrm1, text=chr(0x22ee), **common_configs,
                                         command=lambda: self._input_tcg_folderpath_var.set(askdirectory(title='A komponens TCG fájlok mappája'.upper())))

        lblfrm2 = tk.LabelFrame(frm_left, text='A készített montázs TCG fájl mentési mappája', **common_configs)
        ent2 = tk.Entry(lblfrm2, width=70, textvariable=self._output_tcg_folderpath_var, **common_configs)
        btn_output_dir_dialog = tk.Button(lblfrm2, text=chr(0x22ee), **common_configs,
                                          command=lambda: self._output_tcg_folderpath_var.set(askdirectory(title='A TCG fájl mentési mappája'.upper())))

        btn_gen_filenames = tk.Button(frm_left, text='Komponens TCG fájlok beolvasása'.upper(), **common_configs, bg='gray87',
                                      command=self._creat_tcg_objects_from_files)

        lblfrm3 = tk.LabelFrame(frm_left, text='TCG fájlok', **common_configs)
        self._lbox = tk.Listbox(lblfrm3, height=8, width=70, listvariable=self._tcgfilenames_var, selectmode=tk.EXTENDED, **common_configs)
        yscb = tk.Scrollbar(lblfrm3, orient=tk.VERTICAL)
        self._lbox.config(yscrollcommand=yscb.set)
        yscb.config(command=self._lbox.yview)

        btn_render = tk.Button(frm_left, text='A kijelölt egy vagy több fájl grafikájának megjelenítése'.upper(), bg='gray87', **common_configs,
                               command=self._render_selected_items)

        btn_save = tk.Button(frm_left, text='A létrehozott montázs grafika mentése TCG fájlba'.upper(), bg='gray87', **common_configs,
                             command=self._save_graphics)

        btn_view = tk.Button(frm_left, text='Mentett grafikák megjelenítése'.upper(), bg='gray87', **common_configs,
                             command=self._show_saved_graphics)

        # Grafikus elemek lehelyezése.
        frm_left.grid(row=0, column=0, sticky='news')
        frm_right.grid(row=0, column=1, sticky='news')
        self.grid_columnconfigure((0, 1), weight=1, uniform='a')

        self._canvas.pack(fill=tk.BOTH, expand=True)

        common_grid_options = dict(sticky='news', padx=10, pady=10)
        lblfrm1.grid(row=0, column=0, **common_grid_options)
        ent1.grid(row=0, column=1, **common_grid_options)
        btn_input_dir_dialog.grid(row=0, column=2, **common_grid_options)
        btn_input_dir_dialog.grid_configure(padx=(0, 10))

        lblfrm2.grid(row=1, column=0, **common_grid_options)
        ent2.grid(row=1, column=1, **common_grid_options)
        btn_output_dir_dialog.grid(row=1, column=2, **common_grid_options)
        btn_output_dir_dialog.grid_configure(padx=(0, 10))

        btn_gen_filenames.grid(row=2, column=0, **common_grid_options)

        lblfrm3.grid(row=3, column=0, **common_grid_options)
        self._lbox.grid(row=3, column=0, **common_grid_options)
        yscb.grid(row=3, column=1, sticky='ns')

        btn_render.grid(row=4, column=0, **common_grid_options)
        btn_save.grid(row=5, column=0, **common_grid_options)
        btn_view.grid(row=6, column=0, **common_grid_options)

        # Események és eseménykezelők hozzárendelése a vászon grafikus elemhez.
        self._canvas.bind('<Alt Button 3>', self._change_canvas_bg)
        self._canvas.bind('<MouseWheel>', lambda e: self._resize(e, 0.01))
        self._canvas.bind('<Control MouseWheel>', lambda e: self._resize(e, 0.05))

    def _make_item_draggable(self, tag_or_id):
        """A tag_or_id azonosítóval rendelkező grafikus elemek mozgatását (vonszolását) valósítja meg.
        A mozgatandó elemen a bal egérgombot le kell nyomni, és lenyomva tartva az egeret a kívánt pozícióig
        kell mozgatni, majd ott felengedni a bal egérgombot.
        """

        def grab_item(e: tk.Event):
            """Az eseménnyel érintett grafika mozgatásra kijelölése."""
            tcg_to_grab = self._get_tcg(tk.CURRENT)
            e.widget.addtag_withtag('to_be_moved', tcg_to_grab.id_tag)
            e.widget.x0, e.widget.y0 = e.x, e.y

        def dragging(e: tk.Event):
            """A mozgatásra kijelölt grafika mozgatása (vonszolása)."""
            dx, dy = e.x - e.widget.x0, e.y - e.widget.y0
            e.widget.move('to_be_moved', dx, dy)
            e.widget.x0, e.widget.y0 = e.x, e.y

        def stop_dragging(e: tk.Event):
            """A mozgatásra kijelölt grafika vonszolásának befejezése a mozgatásra kijelöltség megszűntetésével."""
            e.widget.dtag('to_be_moved')

        # Események és eseménykezelők hozzárendelése az adott tag_or_id azonosítóval rendelkező grafikához.
        self._canvas.tag_bind(tag_or_id, '<ButtonPress 1>', grab_item)
        self._canvas.tag_bind(tag_or_id, '<B1-Motion>', dragging)
        self._canvas.tag_bind(tag_or_id, '<ButtonRelease 1>', stop_dragging)

    def _get_tcg(self, tag_or_id):
        """A tag_or_id rajzelem-azonosító alapján visszaadja azt a Tcg objektumot, amelyhez a rajzelem tartozik."""
        # Mivel tag_or_id azonosítóhoz tartozó rajzelem egy grafika része lehet, ezért meghatározzuk, hogy a rajzelemnek
        # milyen más tag-ei vannak.
        potential_idtags = self._canvas.gettags(tag_or_id)
        # Ha a rajzelem egy már előállított és megjelenített (renderelt) grafikához (Tcg objektumhoz) tartozik, akkor a
        # kapott tag-ek között a grafika id_tag azonosítója is szerepelni fog. Az ehhez tartozó Tcg objektummal tér vissza a metódus.
        for idtag in potential_idtags:
            for tcg in self._rendered_tcg_objects:
                if tcg.id_tag == idtag:
                    return tcg

    def _change_canvas_bg(self, e: tk.Event):
        """Eseménykezelő, amely a vászon háttérszínét változtatja meg a megjelenített színpaletta párbeszédablakból
        kíválasztott színnek megfelelően.
        """
        color = askcolor(title='Canvas háttérszín beállítás'.upper(), color='ivory2')[1]
        e.widget.config(bg=color)

    def _resize(self, e: tk.Event, resolution=0.05):
        """Eseménykezelő, amely az egérgörgő-forgatás eseménnyel érintett grafika méretét minden felfelé görgetéssel
        resolution mértékkel növeli, illetve minden lefelé görgetéssel resolution mértékkel csökkenti.
        """
        # Meghatározzuk, hogy melyik az eseménnyel érintett rajzelem.
        object_ids: tuple = self._canvas.find_withtag(tk.CURRENT)
        if object_ids:
            # Meghatározzuk, hogy melyik az eseménnyel érintett grafika (Tcg objektum).
            tcg_to_resize: Tcg = self._get_tcg(*object_ids)
            if tcg_to_resize:
                # Az egérgörgő-forgatás esemény "delta" attribútumának előjelétől függően növeljük vagy csökkentjük a
                # grafika méretét a Tcg objektum scale() metódusának meghívásával.
                scale_factor = 1 + resolution if e.delta > 0 else 1 - resolution
                tcg_to_resize.scale(scale_factor, scale_factor)

    def _remove_item(self, e: tk.Event):
        """Eseménykezelő, amely az eseménnyel érintett grafikát eltávolítja a vászonról."""
        canvas: tk.Canvas = e.widget
        # Meghatározzuk, hogy melyik az eseménnyel érintett grafika (Tcg objektum).
        tcg = self._get_tcg(tk.CURRENT)
        canvas.delete(tcg.id_tag)  # Töröljük a grafikát a vászonról.
        self._rendered_tcg_objects.remove(tcg)  # Töröljük a grafikát a megjelenített grafikák nyilvántartásából.

    def _bring_forward(self, e: tk.Event):
        """Eseménykezelő, amely az eseménnyel érintett grafikát a megjelenítési listában egy szinttel feljebb levő
        grafika fölé hozza. Ezt követően az eseménnyel érintett grafika az alatta levőket részben vagy egészben kitakarja.
        """
        # Meghatározzuk, hogy melyik az eseménnyel érintett grafika.
        tcg: Tcg = self._get_tcg(tk.CURRENT)
        # Meghatározzuk, hogy melyik az eseménnyel érintett grafika feletti rajzelem a megjelenítési listában.
        items_id_above: tuple = self._canvas.find_above(tcg.id_tag)
        if items_id_above:
            # Ha van feljebb levő rajzelem, akkor meghatározzuk, hogy az melyik grafikához tartozik.
            tcg_above = self._get_tcg(*items_id_above)
            # Az eseménnyel érintett grafikát a felette levő grafika fölé visszük a megjelenítési listában.
            self._canvas.tag_raise(tcg.id_tag, tcg_above.id_tag)

    def _send_backward(self, e: tk.Event):
        """Eseménykezelő, amely az eseménnyel érintett grafikát a megjelenítési listában egy szinttel lejjebb levő
        grafika alá teszi. Ezt követően az eseménnyel érintett grafikát a felette levők részben vagy egészben kitakarják.
        """
        # A metódus logikája hasonló a _bring_forward() metóduséhoz.
        tcg = self._get_tcg(tk.CURRENT)
        items_id_below: tuple = self._canvas.find_below(tcg.id_tag)
        if items_id_below:
            tcg_below = self._get_tcg(*items_id_below)
            self._canvas.tag_lower(tcg.id_tag, tcg_below.id_tag)

    def _bring_to_front(self, e: tk.Event):
        """Eseménykezelő, amely az eseménnyel érintett grafikát a megjelenítési lista tetejére teszi. Ezt követően az eseménnyel
        érintett grafika minden mást, amely részben vagy egészben átfedő, kitakar.
        """
        # Meghatározzuk, hogy melyik az eseménnyel érintett grafika.
        tcg: Tcg = self._get_tcg(tk.CURRENT)
        # Ha az eseménnyel érintett grafika azonosító tag-ével úgy hívjuk meg a Canvas tag_raise() metódust, hogy
        # nem határozzuk meg mi fölé kerüljön, akkor a megjelenítési lista tetejére kerül, vagyis minden más felett jelenik meg.
        self._canvas.tag_raise(tcg.id_tag)

    def _send_to_back(self, e: tk.Event):
        """Eseménykezelő, amely az eseménnyel érintett grafikát a megjelenítési lista aljára teszi. Ezt követően az eseménnyel
        érintett grafikát minden más, amely részben vagy egészben átfedő, kitakarja.
        """
        #  Meghatározzuk, hogy melyik az eseménnyel érintett grafika.
        tcg = self._get_tcg(tk.CURRENT)
        # Ha az eseménnyel érintett grafika azonosító tag-ével úgy hívjuk meg a Canvas tag_lower() metódust, hogy
        # nem határozzuk meg mi alá kerüljön, akkor a megjelenítési lista aljára kerül, vagyis minden más alatt jelenik meg.
        self._canvas.tag_lower(tcg.id_tag)

    def _creat_tcg_objects_from_files(self):
        """A komponens grafikák .tcg fájljaiból Tcg objektumokat állít elő, és a fájlneveket a listadobozban felsorolja."""
        self._tcg_objects.extend(Tcg(self._canvas, fpath) for fpath in Path(self._input_tcg_folderpath_var.get()).glob('*.tcg'))
        filenames = [fpath.name for fpath in Path(self._input_tcg_folderpath_var.get()).glob('*.tcg')]
        listbox_items = list(eval(self._tcgfilenames_var.get())) if self._tcgfilenames_var.get() != '' else []
        listbox_items.extend(filenames)
        self._tcgfilenames_var.set(' '.join(listbox_items))

    def _render_selected_items(self):
        """A listadobozból kiválasztott fájlnevekhez tartozó Tcg objektumok által képviselt grafikákat megjeleníti a vászon közepén."""
        items: tuple = self._lbox.curselection()  # A hívás eredménye a listadoboz kiválasztott sorának indexét tartalmazó tuple.
        selected_tcg_objects: tuple = ()  # A kiválasztott sorokhoz tartozó Tcg objektumok tárolója.
        if items:
            # Ha van legalább egy kiválasztott sor, akkor az annak/azoknak megfelőlő egy vagy több Tcg objektumot eltároljuk.
            selected_tcg_objects: tuple[Tcg] = (selected,) if isinstance(selected := itemgetter(*items)(self._tcg_objects), Tcg) else selected
        # A kiválasztott Tcg objektumok által képviselt grafikákat előállítjuk és megjelenítjük. A már megjelenített grafikákhoz tartozó
        # Tcg objektumokról egy külön nyilvántartást vezetünk, hogy egy újabb kiválasztás esetén vizsgálhassuk, hogy mi van már megjelenítve.
        for tcg_obj in selected_tcg_objects:
            if tcg_obj not in self._rendered_tcg_objects:
                tcg = tcg_obj
            else:
                tcg = Tcg(self._canvas, tcg_obj.file)
                tcg.id_tag += str(next(self._cntr))
            self._rendered_tcg_objects.append(tcg)
            # Az Tcg objektum alapján a grafikát előállítjuk és megjelenítjük a (0,0) koordinátákon.
            tcg.render(0, 0)
            # Lekérdezzük a vászon méreteit.
            tcg.canvas.update()
            cnv_w, cnv_h = tcg.canvas.winfo_width(), tcg.canvas.winfo_height()
            # A megjelenített grafikát áthelyezzük úgy, hogy a középpontja a vászon középpontjával essen egybe.
            tcg.move_center_to(cnv_w / 2, cnv_h / 2)
            # A grafikát átméretezzük.
            tcg.scale(k := min(cnv_w, cnv_h) * 0.25 / max(tcg.dimensions), k)

            # Események és eseménykezelők hozzárendelése a grafikákhoz.
            # Vonszolhatóvá tétel.
            self._make_item_draggable(tcg.id_tag)
            # Eltávolíthatóvá tétel.
            self._canvas.tag_bind(tcg.id_tag, '<Button 3>', self._remove_item)
            # A megjelenítési sorrendben egy szinttel előrébb és hátrébb küldhetővé tétel.
            self._canvas.tag_bind(tcg.id_tag, '<Shift Button 1>', self._bring_forward)
            self._canvas.tag_bind(tcg.id_tag, '<Control Button 1>', self._send_backward)
            # A megjelenítési sorrend legtetejére és legaljára küldhetővé tétel.
            self._canvas.tag_bind(tcg.id_tag, '<Alt Shift Button 1>', self._bring_to_front)
            self._canvas.tag_bind(tcg.id_tag, '<Alt Control Button 1>', self._send_to_back)

    def _save_graphics(self):
        """Az összetevő grafikákból a vászonon megalkotott montázs grafikát .tcg fájlba menti a felugró párbeszédablakban kiválasztott
        mappába és az ott megadott névvel. Alapértelmezésben a korábban meghatározott mentési mappa lesz felkínálva.
        A mentés után a montázs a vászonról törlődik."""
        self._filename = asksaveasfilename(title='canvas montázs grafika mentése TCG fájlba'.upper(),
                                           defaultextension='.tcg', confirmoverwrite=True,
                                           initialdir=self._output_tcg_folderpath_var.get(),
                                           filetypes=(('TCG fájl', '.tcg'),))
        if self._filename:
            self._tcgfilemaker.generate_tcg_file_from_canvas(Path(self._output_tcg_folderpath_var.get()) / self._filename, self._canvas)
            self._canvas.delete('all')

    def _show_saved_graphics(self):
        """Egy, a felugró párbeszédablakban kiválasztható mappában elmentett .tcg fájl által definiált grafikát jelenít meg
        egy új ablakban. Alapértelmezésben a legutoljára elmentett montázs fájlnevét kínálja fel.
        """
        filename = askopenfilename(title='mentett canvas grafika megjelenítése', defaultextension='.tcg',
                                   initialdir=self._output_tcg_folderpath_var.get(),
                                   initialfile=Path(self._output_tcg_folderpath_var.get()) / self._filename,
                                   filetypes=(('TCG files', '.tcg'), ('All files', '*')))
        if filename:
            view_tcg(self, filename)

    def run(self):
        self.mainloop()


TcgMontageMakerApp().run()
