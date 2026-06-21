# Gunvor i Sevilla – nettsted

## Status

`index.html` og `template.html` er nå på plass, i tillegg til de 8 blogginnleggene.
Det som gjenstår i hovedmenyen: `om-meg.html`, `hverdagen.html`, `reisebyra.html`,
`guide.html`, `rom.html`, `bryllup.html`, `reiser.html`, `hemmeligheter.html`,
`personvern.html`. Bruk `template.html` som utgangspunkt for hver av dem.

## Hva er gjort i denne runden

**Ingen av tekstene dine er endret.** All historiefortelling, fakta og stemmen din er
100% som du skrev den. Det som er gjort er rent teknisk/strukturelt:

1. **Fjernet duplisert CSS** – hver side hadde tidligere ~1350 linjer CSS limt inn i
   `<style>`-taggen i tillegg til den separate `style.css`-filen. Det gjorde hver side
   3x tyngre enn nødvendig (44 KB → 15–24 KB per side), som er dårlig for fartstesten
   Google bruker (Core Web Vitals). Nå linker alle sider kun til `css/style.css`.
2. **Lagt til "Ofte stilte spørsmål"** i hvert blogginnlegg og på forsiden (synlig +
   `FAQPage`-strukturert data) – dette er det Google AI Overviews nå henter sitater fra.
3. **Fikset 55 døde lenker** – emneknaggene ("tags") nederst i hvert innlegg pekte til
   `#` (ingenting). De peker nå til `hemmeligheter.html`.
4. **Fikset en strukturfeil** i `triana-sevilla.html` – en `<div>`-tag for faktaboksen
   manglet, så "Triana – praktisk info"-boksen ble sannsynligvis ikke vist riktig før.
5. **Fjernet et ødelagt script i `index.html`** – et tidligere Claude-økt-script prøvde
   å hente akvarellbildet fra en sti i Claudes eget arbeidsområde
   (`/mnt/user-data/uploads/...`), som aldri ville fungert på en ekte nettside.
   Bildet vises nå korrekt direkte via `<img src="bilder/sevilla-akvarell.png">`.
6. **Styrket schema.org-data på forsiden** – lagt til `worksFor` (Spaniaopplevelser),
   `knowsLanguage` og `knowsAbout` på Person-dataen, for sterkere E-E-A-T-signaler.
7. **Validert** at all strukturert data (JSON-LD) er gyldig i alle filer, og at HTML-en
   er strukturelt balansert.

## Det som IKKE er gjort ennå (trenger info/handling fra deg)

- **Bildet `bilder/sevilla-akvarell.png` mangler fysisk** – `index.html` peker til den,
  men selve filen (akvarellen fra ChatGPT) må lastes opp i `bilder/`-mappen.
- To lenker på forsiden peker til blogginnlegg som ikke er skrevet ennå:
  `bloggposter/hilsen-fra-gunvor.html` og `bloggposter/gruppe-program-sevilla.html`.
  Disse vil 404 inntil de innleggene finnes – si fra om du har dem fra før, eller om
  jeg skal hjelpe deg skrive dem.
- Menysidene nevnt under "Status" over.
- **`DITTDOMENE.com`** står fortsatt som plassholder i alle filer. Si fra når du har
  valgt domene, så bytter jeg det ut overalt med riktig adresse i én operasjon.
- Bildene er fortsatt Unsplash-bilder/plassholdere – bytt ut med dine egne når du har
  dem klare.
- Google Analytics-koden ligger klar, men kommentert ut – aktiveres når domenet er klart.
- Favicon/logo – kommentert ut i `template.html`, venter på at du velger logo.

## Mappestruktur

```
gunvor-i-sevilla/
├── index.html              ← forsiden
├── template.html           ← mal å kopiere for nye sider
├── css/
│   └── style.css           ← ALL design samlet ett sted
├── bloggposter/
│   ├── alcazar-sevilla.html
│   ├── camino-santiago.html
│   ├── katedralen-sevilla.html
│   ├── plaza-espana-sevilla.html
│   ├── santa-cruz-sevilla.html
│   ├── sevilla-fra-fortid-til-natid.html
│   ├── spaniaopplevelser-reisebyraa.html
│   └── triana-sevilla.html
└── bilder/                 ← (tom – legg inn egne bilder her)
```

## Slik publiserer du

**Du har bekreftet med Loading.es** at de støtter Git-deploy gratis via Plesk-panelet
(Plesk → "Primeros pasos" → "Desplegar mediante Git"). Husk: domenekapasiteten din er
full, så du må slette et ubrukt domene før du kan legge til det nye.

**Viktig om mappestruktur:** Når du oppretter GitHub-repoet, last opp *innholdet* i
denne mappen (README.md, index.html, css/, bloggposter/, bilder/) direkte i repoets
**rotmappe** – ikke inni en undermappe som heter `gunvor-i-sevilla`. Loading.es henter
sannsynligvis innholdet i repo-roten rett til nettstedets webroot.

1. **Opprett GitHub-repoet** på github.com → "New" → naviger inn → "Add file → Upload
   files" → dra inn alt innholdet i denne mappen → "Commit changes".
2. **I Plesk hos Loading.es:** gå til domenet → "Primeros pasos" → "Desplegar mediante
   Git" → lim inn GitHub-repoets URL → velg branch `main` → fullfør oppsettet.
3. Sjekk om det finnes en innstilling for automatisk deploy ved push (webhook) i samme
   seksjon – hvis ikke, må du trolig trykke "Pull/Deploy" manuelt i Plesk hver gang du
   har lastet opp nye filer til GitHub.

## Backup

Behold Google Drive-mappen som backup slik du gjør i dag – GitHub blir stedet siden
faktisk *lever og publiseres fra*, Drive er sikkerhetskopien.

