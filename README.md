# Tkinter Canvas grafikák elmentése és fájlból történő megjelenítése
A tkinter modul vászon (Canvas) grafikus elemén a különféle típusú rajzelemekkel (ellipszis, ellipszisív, sokszög, téglalap, vonal) akár meglehetősen összetett grafikákat is tudunk alkotni. A rajzelemek létrehozása általában a vászon elemre meghívott konstruktormetódusokkal történik. De lehetséges az is, hogy egy rajzszerkesztő programot készítünk és/vagy használunk, ahol a rajzelemeket a program által biztosított módon helyezzük a vászonra és vizuálisan rendezzük el egér- vagy billentyűműveletekkel.

Akárhogy is készítjük el a grafikákat a kérdés az, hogy hogyan őrizhetnénk meg az alkotásunk eredményét egy fájlban úgy, hogy később a fájlból a grafika megjeleníthető legyen? És mindezt lehetőleg úgy, hogy nem támaszkodunk a szabványos könyvtáron túlmutató külső csomagokra vagy alkalmazásokra.

Nyilván egy lehetséges út a képernyőképmentés (printscreen). Ez azonban rasztergrafikát eredményez, aminek meg vannak a maga hátrányos jellemzői, pl. rögzített felbontás, nagyításnál minőségromlás, és formátumtól és képmérettől függő képfájlméret. Ráadásul a tkinter PhotoImage objektumot csak meglehetősen korlátozott számú képformátum esetén tudjuk használni.

E helyett, mivel a megjelenített grafikához a vásznon rendelkezésre állnak a rajzelemek, vektorgrafikusan fogjuk leírni a képet. Ennek elvét írja le az alábbi ábra. 

<img src="https://github.com/pythontudasepites/saved_canvas_graphics/blob/main/tcg_saving_principles.png" width="385" height="400">

Az elvet programban a következőképpen valósítjuk meg.

Az egyes rajzelemek adatait egy szótárban gyűjtjük össze, amelyben a kulcsok a rajzelemek egyedi azonosítói, a kulcsokhoz tartozó értékek pedig sorozat típusú konténerek, amelyek elemei a rajzelem típusa, a koordináták sorozata, valamint egy, a konfigurációs paraméternév-érték párokat tartalmazó szótár.
Ezen adatok mindegyike egyszerűen kinyerhető a vászon elemre meghívott megfelelő metódussal. A típust a **type()**, a koordinátákat a **coords()**, a konfigurációt tartalmazó szótárt a **itemconfig()** metódus hívásával kaphatjuk meg.

A rajzelemek adatait tartalmazó szótárt fájlba mentjük, mégpedig JSON formátumban, mert így a mentést és majd a visszaolvasást egyszerűen el tudjuk végezni.

Ahhoz, hogy tudjuk, hogy a fájl mit tartalmaz, legyen a fájl kiterjesztése .tcg, ami a tkinter canvas grafika kezdőbetűiből ered.

A canvas grafikák ilyen fájlokba történő mentését teszi lehetővé a *tcg* modulban található **TcgFileMaker** osztály. Ennek példánya egy .tcg kiterjesztésű, tkinter canvas grafikát leíró fájlt készít a **generate_tcg_file_from_factory()** vagy a **generate_tcg_file_from_canvas()** metódusok meghívásával. Az előbbit akkor kell használni, ha a grafika egy grafikaelőállító függvényben van definiálva. Az utóbbi metódust pedig akkor, ha a grafika egy vászon elemen van létrehozva és megjelenítve.

A  grafikaelőállító függvény egy olyan függvény, amely egyetlen, kötelezően megadandó pozícionális argumentumot fogad, mégpedig egy vászon elemet, amelyen a grafika az összetevő rajzelemek (téglalap, sokszög, ellipszis, ellipszisív és vonal) létrehozásával és megfelelő konfigurációjával valósul meg a függvény törzsében szereplő utasításokkal. Ilyen grafikaelőállító függvények találhatók a *tcg_factories* mappa *tcg_factories1* és  *tcg_factories2* modulokban. E függények készítéséhez első lépés, hogy a kívánt grafika rajzelemekből való felépítését fejben vagy papíron meg kell tervezni, amihez középszintű koordinátageometriai ismeretekre van csupán szükség. Ezt követően a rajzelemek előállítását és elhelyezését kell kódban megvalósítani a **Canvas** megfelelő metódusainak hívásával.

Egyes függvényekben megfigyelhetjük, hogy ha átlátszóság érzetét akarjuk kelteni, vagyis a grafika adott rajzelemének kitöltő színe a háttérszínnel egyezzen meg, akkor egyrészt a *fill* konfigurációs paraméterhez a vászon aktuális kitöltőszínét kell rendelni, másrészt, ahhoz hogy később a fájlba mentésnél a transzparenciára vonatkozó információ is rögzüljön, az adott rajzelemhez a „fill_transparent” tag-et kell társítani. Hasonlóan kell eljárni, ha a rajzelem körvonalát az aktuális háttérszínnel egyezőnek akarjuk, csak ilyenkor a rajzelemhez az „outline_transparent” tag-et kell adni.

A **TcgFileMaker** példányosításakor létrejön egy **Canvas** példány, amelynek szülőelemét a konstruktorban kell megadni. Ez legtöbbször a gyökérelem (főablak), de lehet más is, például egy keret (Frame) elem.

Ha a **TcgFileMaker** példánnyal létrehoztunk egy vagy több .tcg fájlt, akkor a következő kérdés, hogy hogyan tudjuk ezeket használni a GUI programunkban. Erre szolgál a *tcg* modul **Tcg** nevű osztálya. 

A **Tcg** osztály példánya az inicializáláskor megadott fájl által definiált tkinter canvas grafikát állítja elő és jeleníti meg az inicializáláskor megadott vászon elemen, amikor a **render()** metódus meghívásra kerül. Ezt követően a grafika áthelyezhető és átméretezhető a példányon meghívott megfelelő metódusokkal. E metódusok használata helyett a **Canvas** saját metódusaival is megvalósíthatók a műveletek, amelyekhez a **Tcg** példány **id_tag** azonosító tag-e használható az adott **Canvas** metódus által elvárt rajzelem-azonosítóként.

Ha a **render()** metódus hívásakor, vagyis ha a grafika előállításakor egy rajzelemen a „fill_transparent” tag található, akkor az adott rajzelem kitöltőszíne a vászon aktuális háttérszínével fog megegyezni, az átlátszóság érzetét keltve. Ha a grafika előállításakor a rajzelemen az „outline_transparent” tag található, akkor az adott rajzelem körvonalának színe a vászon aktuális háttérszínével fog megegyezni. Ebből következik, hogy a megjelenített grafika traszparens részei csak akkor hatnak átlátszónak, ha alattuk csak a vászon elem van. Ha a megjelenítési sorrendben más grafika van alattuk, akkor nem érvényesül az átlátszóság. Ez kompromisszum a grafika előállításának (a grafikaelőállító függvények kódolásának) egyszerűsége és a teljes, valódi átlátszóság között. Ez utóbbi ugyanis megvalósítható, de ekkor a grafikát sokkal bonyolultabb geometriával, sok csúcsponttal rendelkező sokszögekből kell felépíteni. 

Arra is lehet igény, hogy mielőtt egy .tcg fájlt használnánk, megtekintsük, hogy milyen grafikát képvisel. Erre szolgál a *tcg* modul **view_tcg()** és **view_tcg_files()** függvénye. Az előbbi egyetlen .tcg fájl által definiált grafikát jelenít meg egy ablakban. Az utóbbi több .tcg fájl által definiált grafikákat egy közös ablakban táblázatos elrendezésben jeleníti meg. Ezek a függvények már a **Tcg** osztályt használják, így akár a **Tcg** osztály alkalmazási példájaként is tekinthetünk rájuk.

A **TcgFileMaker** és **Tcg** osztályok, valamint a **view_tcg()** és **view_tcg_files()** függvények alkotják a tkinter canvas grafikák fájlba mentésének és onnan történő megjelenítésének és használatának eszköztárát. Ezért szerepelnek ezek egy közös, *tcg* nevű modulban. Ha egy GUI programban a grafikákat menteni akarjuk, és/vagy már .tcg fájlokba elmentett grafikákat akarunk behívni és azokkal dolgozni, akkor a *tcg* modult kell beimportálni, és használni a benne foglalt osztály- és függvényobjektumokat.

A *tcg* modul említett objektumai használatának demonstrálására két GUI alkalmazást mutatunk. 

## Tcg fájlokat létrehozó alkalmazás

A *tcg_file_creations* nevű modult szripként futtatva egy oly GUI alkalmazás indul el, amely egy megadható modulfájlban definiált egy vagy több tkinter canvas grafikát előállító függvény alapján a grafikákat leíró .tcg kiterjesztésű fájlokat készít és ment el egy előre megadható mappába. E mappába elmentett létező .tcg fájlok által definiált grafikákat egy közös ablakban táblázatos elrendezésben is meg lehet jeleníteni.

A működéshez a grafikaelőállító függvényekre vonatkozóan vannak követelmények, amelyek az alábbiak:
- nevük create_ kezdetű,
- csak egyetlen kötelezően megadandó pozícionális argumentumot fogadhatnak, ami a **Canvas** példány,
- az átlátszóvá tenni kívánt rajzelemhez a „fill_transparent” tag van rendelve,
- az aktuális canvas háttérszínnel egyező körvonal szín eléréséhez a rajzelemhez az „outline_transparent” tag van rendelve.

Az alkalmazás indítása után beviteli mezőkből és vezérlő gombokból álló felhasználó felület jelenik meg.

A grafikaelőállító függvényeket tartalmazó modulfájl elérési útvonalát és az elkészült .tcg kiterjesztésű fájlok mentési mappájának útvonalát a megfelelő beviteli mezőkben két módon adhatjuk meg. Vagy manuálisan begépelve, vagy a beviteli mezők jobb szélén található, három ponttal jelzett nyomógomb megnyomására felugró párbeszédablak segítségével.

Ha ezeket megadtuk, akkor a „TCG fájlnevek generálása” gombot megnyomva a modulfáljban található grafikaelőállító függvények nevei alapján a listadobozban egymás alatt fájlnevek jelennek meg, amely neveken a grafikák .tcg kiterjesztésű fájlokba menthetők. Ezek a nevek azonban csak ajánlott, alapértelmezett nevek. Ha mást szeretnénk, akkor módosítani lehet úgy, hogy kétszer a névre kell kattintani a bal egérgombbal, és a felugró beviteli párbeszédablakba az új nevet kell beírni, majd az OK gomb lenyomásával érvényesíteni.

A „Grafika leíró fájlok készítése” gomb lenyomására a .tcg kiterjesztésű fájlok elkészülnek és a korábbban megadott mappába mentődnek. A sikeres műveletetről egy üzenetablak tájékoztat. Ha a fájlok készítése valamiért nem sikerül, akkor a hiba valószínű okáról szintén egy üzenetablakban kapunk információt.
A megadott mentési mappában található .tcg fájlok által leírt grafikákat egyetlen ablakban táblázatos elrendezésben tekinthetjük meg, ha a „Mentett grafikák megjelenítése” gombot megnyomjuk.

Az alkalmazás grafikus felhasználói felületét és egy eredményképet mutat az alábbi ábra, ahol a használat lépéseit sorszámokkal jeleztük a megfelelő nyomógombokon. Itt az is látható, hogy akár több modulban szereplő  grafikaelőállító függvényekkel is dolgozhatunk.

A *tcg_files* mappában néhány elkészített és használható .tcg fájl található.

## Montázskészítő alkalmazás

A *tcg_montage_maker* modult szriptként futtatva egy olyan GUI alkalmazás indul el, amellyel .tcg fájlokban definiált grafikák felhasználásával egy új grafikát lehet készíteni az alkalmazás erre szolgáló felületén. Az egyéni terv szerint elrendezett (áthelyezett és/vagy átméretezett) komponens grafikákból álló montázst egy megadható mappába lehet elmenteni .tcg fájlformátumban. Ezt követően a montázst meg is lehet jeleníteni egy külön ablakban. Az alkalmazás indítása után a beviteli mezők és vezérlő gombok a bal oldalon, a vizuális grafikai tervező felület a jobb oldalon látható.

A mappaútvonalakat a beviteli mezőkben két módon adhatjuk meg. Vagy manuálisan begépelve, vagy a beviteli mezők jobb szélén található, három ponttal jelzett nyomógomb megnyomására felugró párbeszédablak segítségével.

A „Komponens Tcg fájlok beolvasása” gombra kattintva az első beviteli mezőben megadott mappában levő .tcg fájlok beolvasása megtörténik, és a fájlnevek a listadobozban jelennek meg egymás alatt.  A felsorolt fájlnevek közül kiválaszthatjuk, hogy melyekhez tartozó grafikákat akarjuk megjeleníteni a jobb oldali felületen.
Ha egy sorban a bal egérgombbal kattintunk, akkor csak az a fájlnév lesz kiválasztva. Ha egyszerre többet akarunk kiválasztani, akkor ezt több módon is megtehetjük. Ha egymást követő több sort akarunk egyszerre kijelölni, akkor a kezdősoron nyomjuk le a  bal egérgombot, majd a blokk utolsó során a Shift billentyű lenyomva tartása mellett újra nyomjuk le a bal egérgombot. Ha több, de nem egymást követő sorokat akarunk kijelölni, akkor a Control billentyűt lenyomva tartva nyomjuk le a bal egérgombot a kívánt sorokon. Azt, hogy mely sorok vannak kijelölve onnan látható, hogy a háttérszínük megváltozik. A legutoló kijelölést az ESC billentyűvel  lehet törölni.

A kívánt sorok kijelölése után a „A kijelölt egy vagy több fájl grafikájának megjelenítése” gombra kattintva a grafikák a jobb  oldali felület közepén egymás felett jelennek meg. Innen az adott grafikát elmozgathatjuk a szokásos módon, azaz a bal egérgombot a grafikán lenyomva tartva az egérmutatót a kívánt helyre húzzuk és ott az egérgombot elengedjük.

A felületen megjelent komponens grafikák nagyíthatók vagy kicsinyíthetők. Ehhez az egeret az adott grafika fülé kell vinni és a  görgővel felfelé vagy lefelé görgetni. Az előbbi esetben a rajz mérete finom léptékben nő, az utóbbi esetben csökken. Ha gyorsabban, azaz nagyobb léptékben akarjuk a méretváltoztatást, akkor a görgetés közben a Control billentyűt lenyomva kell tartani.

A grafikák, ha területük fedik egymást, akkor az átfedő területen az egyik kitakarja a másikat. Az, hogy melyik grafika melyiket takarja el, egy megjelenítési sorrendet határoz meg. Ha azt szeretnénk, hogy egy adott grafika ebben a sorrendben egy szinttel feljebb  kerüljön, akkor az egérmutatót vigyük a grafika fölé, és nyomjuk le a Shift billentyűt majd a bal egérgombot. Ha egy szinttel lejjebb akarjuk küldeni, akkor nyomjuk le a Control billentyűt majd a bal egérgombot. Ha a grafikát a megjelenítési lista legtetejére akarjuk hozni, akkor nyomjuk le az Alt és Shift billentyűt majd a bal egérgombot. Ha a grafikát a megjelenítési lista legaljára akarjuk küldeni, akkor nyomjuk le az Alt és Control billentyűt majd a bal egérgombot.

A tervezőfelületről grafikát úgy lehet eltávolítani, ha az egermutatót a grafika felett van és lenyomjuk a jobb egérgombot.
A vászon színének megváltoztatására is van lehetőség, ha a vászon egy pontján az Alt billentyűt lenyomva tartva lenyomjuk a jobb egérgombot. Az ezt követően felugró színválasztó párbeszédablakban ki kell választani az új háttérszínt.

Ha a montázs elkészült, akkor azt a „A létrehozott montázs grafika mentése TCG fájlba” gomb megnyomásával menthetjük el megadva a fájlnevet a felugró párbeszédablakban. A mentés után a montázs törlődik, tiszta felületet adva a következő alkotáshoz. A mentési mappába került montázsok megtekinthetők, ha a „Mentett grafikák megjelenítése” gomb lenyomása után felugró párbeszédablakban kiválasztunk egy .tcg fájlt. Alapértelmezésben az ablak a legutoljára elmentett montázs fájlnevét kínálja fel.

Ez az alkalmazás – minthogy alapvetően demonstrációs célú – nem rendelkezik egy képszerkesztő teljes funkcionalitásával. De az egyeni igényeknek megfelelően továbbfejleszthető: pl. beviteli mezők és nyomógombok helyett menürendszer, és funkcionalitásban kiegészíthető a tükrözés és forgatás geometriai transzformációkkal. Ez utóbbi alkalmazásához azonban alaktartóan forgatható rajzelemekből felépített grafikák szükségesek. Ehhez lásd a „Forgatható ellipszis, ellipszisív és téglalap” című korábbi bejegyzést. Ha pedig az alkotásunk rajzelemekből való felépítését mások elől el akarjuk rejteni, akkor .tcg fájlokat akár titkosítani is lehet.

A tcg_montage_files mappában található .tcg fájlok montázsokat képviselnek, amelyek komponens grafikákból lettek előállítva.

## A tcg fájlok készítésének és használatának előnyei
A tkinter canvas grafikák megtervezése és .tcg fájlok készítése igényel némi időt, de ha olyan képekre, grafikákra van szükség, amelyek a Canvas rajzelemeiből viszonylag egyszerűen létrehozhatók, akkor érdemes megtenni, mert akkor egyrészt a vektorgrafika előnyeit élvezhetjük, másrészt a mások által készített képek felhasználási liszensz kérdése nem merül fel.
