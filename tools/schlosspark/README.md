# Schlosspark: Generator für Theme, Karte und Karnevals-Hüte

Alles hier ist per Code gezeichnet (pycairo), im Cartoon-Stil mit dicken Konturen.
Vorlagen waren zwei Fotos: ein Sandstein-Schloss mit großem Turm und eine
Hochhaussiedlung vor bewaldeten Hügeln. Es wurden keine fremden Spielgrafiken verwendet.

Erzeugt:

| Datei | Inhalt |
|---|---|
| `Data/Maps/Schlosspark/map.png` | 4096x2048, spielbares Terrain: Schloss mit Turm, Terrasse, Treppe, Park (links), Hochhaus-Siedlung im Wald (rechts), Wasserspalt dazwischen |
| `Data/Themes/Schlosspark/` | Himmel, Horizont (Waldhügel, Stadt, ferne Hochhäuser in der Mitte; `horizontL/R` als Kacheln), Wolken, Sandstein-Texturen, Gras-Border, fallende Blätter, Icon |
| `Data/Graphics/Hats/Narrenkappe.png` | Narrenkappe rot/weiß/blau/gelb |
| `Data/Graphics/Hats/GardeDreispitz.png` | Garde-Dreispitz mit Feder und Kokarde |
| `Data/Graphics/Hats/Gardeuniform.png` | Dreispitz plus Uniform-Brustteil (rot, weiße Kreuzbandeliere, goldene Epauletten) |

Neu erzeugen (Python 3, `pip install pycairo numpy pillow`):

```
cd tools/schlosspark
python3 make_map.py   out/map
python3 make_theme.py out/theme
python3 make_hats.py  out/hats out/hats_preview.png
python3 compose.py    out/mock_full.png out/mock_zoom.png   # grobe Vorschau
```

Danach `out/map/*`, `out/theme/*` und `out/hats/*` in die Data-Ordner kopieren.

Hinweis zur Gardeuniform: Hedgewars kennt nur Hüte (32x32 über dem Kopf), keine Körper-Kostüme.
Die Uniform ist deshalb Teil des Hut-Sprites. Beim Zielen mit Waffen dreht das Spiel den Hut
mit, dann sitzt das Brustteil nicht mehr ganz richtig. Der reine Dreispitz hat das Problem nicht.
