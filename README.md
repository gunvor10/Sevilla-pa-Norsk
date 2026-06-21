# Gunvor i Sevilla – nettsted

## Status

`index.html` og `template.html` er nå på plass, i tillegg til de 8 blogginnleggene,
`robots.txt` og `llms.txt`. Det som gjenstår i hovedmenyen: `om-meg.html`,
`hverdagen.html`, `reisebyra.html`, `guide.html`, `rom.html`, `bryllup.html`,
`reiser.html`, `hemmeligheter.html`, `personvern.html`. Bruk `template.html` som
utgangspunkt for hver av dem.

## Siste runde med endringer (SEO + GEO/AI-søkbarhet)

1. **Alle 8 titler og meta-beskrivelser er strammet inn** – var 61–83 tegn på titler
   (mal sier maks 60), nå alle ≤59 tegn. Meta-beskrivelser var 157–186 tegn, nå alle
   ≤154 tegn. Samme stemme og fakta, bare kuttet ned.
2. **"Sevilla historie"-innlegget manglet ordet "historie" i tittelen** – lagt til,
   siden det er nøyaktig det folk søker etter.
3. **`robots.txt` lagt til** – eksplisitt tillatelse for AI-roboter (GPTBot/ChatGPT,
   ClaudeBot/Claude, PerplexityBot, Google-Extended/Gemini) i tillegg til vanlige
   søkemotorer.
4. **`llms.txt` lagt til** – en markdown-basert innholdsoversikt spesielt formatert
   for språkmodeller (en slags "robots.txt for AI-æraen").
5. **Hvert blogginnlegg åpner nå med én kort faktasetning** før den personlige
   historien – AI-systemer (ChatGPT, Perplexity, Google AI Overviews) henter oftest
   sitater fra de første 40–50 ordene på en side. Stemmen og historien din er
   uendret, bare med et faktaanker aller først.

## Det som IKKE er gjort ennå (trenger info/handling fra deg)

- **Bildet `bilder/sevilla-akvarell.png` mangler fysisk** – `index.html` peker til den,
  men selve filen (akvarellen fra ChatGPT) må lastes opp i `bilder/`-mappen.
- To lenker på forsiden peker til blogginnlegg som ikke er skrevet ennå:
  `bloggposter/hilsen-fra-gunvor.html` og `bloggposter/gruppe-program-sevilla.html`.
- Menysidene nevnt under "Status" over.
- **`DITTDOMENE.com`** står fortsatt som plassholder i alle filer.
- Bildene er fortsatt Unsplash-bilder/plassholdere.
- Google Analytics-koden ligger klar, men kommentert ut.
- Favicon/logo – kommentert ut i `template.html`.
- **Sitemap.xml** – lages helt til slutt, rett før lansering, når domenet er valgt
  (referansen til den ligger som kommentar i `robots.txt`, klar til å skrus på).

## Mappestruktur

```
gunvor-i-sevilla/
├── index.html              ← forsiden
├── template.html           ← mal å kopiere for nye sider
├── robots.txt               ← tillater søkemotorer + AI-roboter
├── llms.txt                 ← innholdsoversikt for AI-språkmodeller
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
denne mappen (README.md, index.html, robots.txt, llms.txt, css/, bloggposter/,
bilder/) direkte i repoets **rotmappe** – ikke inni en undermappe som heter
`gunvor-i-sevilla`. Loading.es henter sannsynligvis innholdet i repo-roten rett til
nettstedets webroot.

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


