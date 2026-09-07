#!/bin/bash
# Publiser Sevilla på norsk
# Bruk: dobbeltklikk, eller skriv  bash ~/Desktop/publiser.sh  i terminalen
#
# Skriptet finner den nyeste zip-filen fra Claude i Nedlastinger,
# pakker den ut, kopierer filene inn i repoet og laster opp til GitHub.
# Det stopper av seg selv hvis noe ser feil ut.

set -e

REPO="$HOME/Desktop/Sevilla-pa-Norsk"
TMP="$HOME/Downloads/.publiser-tmp"

echo "──────────────────────────────────────────"
echo "  Publiserer Sevilla på norsk"
echo "──────────────────────────────────────────"

# 1. Finn repoet
if [ ! -d "$REPO/.git" ]; then
  echo "STOPP: fant ikke $REPO"
  exit 1
fi

# 2. Finn nyeste zip fra Claude
ZIP=$(ls -t "$HOME/Downloads/"*.zip 2>/dev/null | head -1)
if [ -z "$ZIP" ]; then
  echo "STOPP: fant ingen zip-fil i Nedlastinger."
  echo "Last ned mappa fra Claude først."
  exit 1
fi
echo "Bruker: $(basename "$ZIP")"

# 3. Pakk ut
rm -rf "$TMP"
mkdir -p "$TMP"
unzip -q -o "$ZIP" -d "$TMP"

# 4. Finn mappa med index.html
SRC=$(find "$TMP" -maxdepth 2 -name index.html | head -1 | xargs dirname 2>/dev/null || true)
if [ -z "$SRC" ] || [ ! -f "$SRC/index.html" ]; then
  echo "STOPP: fant ikke nettsidefilene i zip-filen."
  exit 1
fi

# 5. Sjekk at det ser ut som nettsiden, ikke noe annet
if [ ! -f "$SRC/turer.html" ]; then
  echo "STOPP: dette ser ikke ut som Sevilla på norsk (mangler turer.html)."
  exit 1
fi
echo "Fant $(ls "$SRC"/*.html | wc -l | tr -d ' ') sider"

# 6. Rydd bort Finder-dubletter fra tidligere
cd "$REPO"
find . -name "* [0-9].*" -not -path "./.git/*" -delete 2>/dev/null || true
rm -rf Library System usr bin sbin etc var home private 2>/dev/null || true

# 7. Kopier inn
cp -R "$SRC"/. "$REPO"/
echo "Filene er kopiert inn."

# 8. Last opp
git add -A
if git diff --cached --quiet; then
  echo "Ingenting nytt å laste opp — nettsiden er allerede oppdatert."
  exit 0
fi
git commit -m "Oppdatering fra Claude $(date '+%d.%m.%Y %H:%M')"
git push origin main

echo "──────────────────────────────────────────"
echo "  Ferdig. Nettsiden er oppdatert om"
echo "  et par minutter."
echo "──────────────────────────────────────────"
