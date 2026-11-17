# Schlosspark: zwei Foto-Karten, Theme und Karnevals-Hüte

## Karten

- **Schloss** (`Data/Maps/Schloss`, 2848x2048): das Schloss aus Christians Foto, freigestellt (Himmel und Bäume entfernt), auf einem Erdsockel.
- **Hochhaus** (`Data/Maps/Hochhaus`, 3450x2048): die Hochhaussiedlung mit dem Wald davor aus dem zweiten Foto, ca. 2,6-fach vergrößert.

Beide nutzen das Theme **Schlosspark**: Himmelsverlauf und Waldhügel stammen aus dem Hochhaus-Foto,
die Land-Textur ist ein Stück Sandsteinmauer vom Schlossturm. Wolken und fallende Blätter sind generiert.

## Neu erzeugen

Python 3 mit `pip install pycairo numpy pillow scipy`. Die beiden Originalfotos liegen nicht im Repo.
Lege sie in einen Ordner als `schloss.png` und `hochhaus.png`.

```
cd tools/schlosspark
export PHOTO_DIR=/pfad/zu/den/fotos
mkdir -p out
python3 seg_castle.py            # -> out/castle_cut.png (Freisteller Schloss)
python3 seg_towers.py            # -> out/towers_cut.png (Freisteller Hochhäuser + Wald)
python3 make_photo.py out/photo  # -> Karten Schloss/Hochhaus + Theme-Bilder
python3 compose_photo.py         # grobe Vorschau mit Himmel/Horizont
python3 make_theme.py out/theme  # nur noch für Flake.png (Blätter) gebraucht
python3 make_hats.py out/hats out/hats_preview.png
```

Die Freistellung kombiniert Farbschwellen mit von Hand gesetzten Polygonen (Dächer, Turmspitzen,
Bäume neben dem Schloss). Wenn eine Kante nicht passt, dort die Polygon-Koordinaten anpassen.
Die Koordinaten beziehen sich beim Schloss auf eine Breite von 2000 px, beim Hochhaus-Foto auf 1500x1000.

## Hüte

`Narrenkappe`, `GardeDreispitz`, `Gardeuniform` in `Data/Graphics/Hats` (32x32).
Hedgewars kennt nur Hüte, keine Körper-Kostüme. Das Uniform-Oberteil ist deshalb Teil des Hut-Sprites
und sitzt beim Zielen etwas schief.
