# CBS StatLine Table Registry: Housing × Energy Transition

## How to use this registry

This is a curated list of CBS StatLine tables relevant to research and analysis
at the intersection of housing and energy transition. Tables are grouped by theme
and annotated with:

- **ID**: The CBS table identifier (use this in API calls)
- **Title**: Human-readable name
- **Geo level**: Finest geographic granularity available
- **Perioden**: Available time range and frequency
- **Key dimensions**: The columns you'll filter/group by
- **Key measures**: The numbers you'll analyse
- **Join keys**: Which region/period codes this table uses (for cross-table joins)
- **Status**: `active`, `deprecated` (being replaced), or `archived`
- **Notes**: Caveats, methodology changes, gotchas

## Join key compatibility

Tables can be joined when they share the same geographic and temporal keys.
Here's the compatibility matrix for the most important join levels:

| Join level | RegioS prefix | Example code | Tables that support it |
|---|---|---|---|
| Nederland | `NL` | `NL01` | Nearly all |
| Provincie | `PV` | `PV28` | Most regional tables |
| Gemeente | `GM` | `GM0344` | Most tables listed below |
| Wijk | `WK` | `WK034401` | Kerncijfers, verwarmingsinstallaties, aardgasvrij, zonnestroom |
| Buurt | `BU` | `BU03440100` | Kerncijfers, some energy tables |

**Critical rule**: Always `.strip()` RegioS codes before joining — CBS pads
them with trailing spaces. Also normalise to the same length: gemeente codes
are sometimes `GM0344` and sometimes `GM0344  ` (with spaces to pad to the
same width as buurt codes within the same table).

---

## THEME 1: HOUSING STOCK & CHARACTERISTICS

### 1.1 Voorraad woningen; eigendom, type verhuurder, bewoning, regio
- **ID**: `82900NED`
- **Geo level**: Gemeente, COROP, Provincie, Landsdeel
- **Perioden**: 2012–2025 (annual, per 1 januari)
- **Key dimensions**: RegioS, Perioden
- **Key measures**: Koopwoningen, Huurwoningen (corporatie/overig), Bewoond/Niet-bewoond
- **Join keys**: RegioS (GM level), Perioden (year)
- **Status**: ⚠️ DEPRECATED — methodology change in 2026, will be replaced by new tables
- **Notes**: Definitive through 2025. Still valid for historical analysis. Corrections applied 2019–2022 for housing corporation classification errors.

### 1.2 Voorraad woningen en niet-woningen; mutaties, gebruiksfunctie, regio
- **ID**: `81955NED`
- **Geo level**: Gemeente
- **Perioden**: 2012–present (annual)
- **Key dimensions**: RegioS, Perioden, Gebruiksfunctie
- **Key measures**: Nieuwbouw, Sloop, Overige toevoegingen, Overige onttrekkingen, Saldo
- **Join keys**: RegioS (GM level), Perioden (year)
- **Status**: Active
- **Notes**: Tracks how housing stock changes: new construction, demolition, conversions. Good for "where is new housing being built?" stories.

### 1.3 Bestaande koopwoningen; verkoopprijzen prijsindex
- **ID**: `83625NED`
- **Geo level**: Gemeente, COROP, Provincie
- **Perioden**: 1995–present (annual, quarterly, monthly)
- **Key dimensions**: RegioS, Perioden, Woningtype
- **Key measures**: Prijsindex, Gemiddelde verkoopprijs, Aantal verkopen
- **Join keys**: RegioS (GM level), Perioden (mixed: JJ/KW/MM)
- **Status**: Active
- **Notes**: The go-to table for housing price stories. Can correlate with energy label distribution to test "does energy efficiency affect house prices?"

### 1.4 Woningen naar bewoning en woningtype, buurt (Kerncijfers)
- **ID**: `83765NED`
- **Geo level**: Wijk, Buurt
- **Perioden**: 2017–present (annual)
- **Key dimensions**: WijkenEnBuurten (RegioS equivalent)
- **Key measures**: Hundreds of neighbourhood indicators: population, income, housing, land use
- **Join keys**: WijkenEnBuurten (BU/WK/GM level), Perioden
- **Status**: Active
- **Notes**: The Swiss Army knife. Contains housing density, average home value (WOZ), % rental vs ownership, average income, demographics. **OData v4 structure**: uses `WijkenEnBuurten` instead of `RegioS` and `Measure` codes instead of named columns. Read the metadata carefully.

### 1.5 Bouwvergunningen; nieuwbouw, woongebouwen naar opdrachtgever, regio
- **ID**: `83671NED`
- **Geo level**: Gemeente, Provincie
- **Perioden**: 2012–present (annual, quarterly)
- **Key dimensions**: RegioS, Perioden, Opdrachtgever
- **Key measures**: Verleende bouwvergunningen (aantallen en m²)
- **Join keys**: RegioS (GM level), Perioden
- **Status**: Active
- **Notes**: Leading indicator for housing supply. Compare building permits to actual completions (81955NED) for "housing pipeline" stories.

### 1.6 WOZ-waarden van woningen
- **ID**: `85011NED`
- **Geo level**: Gemeente
- **Perioden**: 2019–present (annual)
- **Key dimensions**: RegioS, Perioden
- **Key measures**: Gemiddelde WOZ-waarde, mediaan, verdeling naar waardeklasse
- **Join keys**: RegioS (GM level), Perioden (year)
- **Status**: Active
- **Notes**: Property tax valuations. Proxy for wealth/housing quality. Joins cleanly with energy tables for "do expensive homes go green faster?" analysis.

---

## THEME 2: ENERGY TRANSITION

### 2.1 Woningen; hoofdverwarmingsinstallaties, regio
- **ID**: `84948NED`
- **Geo level**: Gemeente, Wijk, Buurt
- **Perioden**: 2017–2022 (annual)
- **Key dimensions**: RegioS, Perioden
- **Key measures**: % Individuele CV, % Blokverwarming, % Stadsverwarming, % All-electric
- **Join keys**: RegioS (GM/WK/BU level), Perioden (year)
- **Status**: ⚠️ DEPRECATED — replaced by ASD-tables with new methodology from 2022
- **Notes**: Historical reference. Shows heating type per region. The new 2022–2023 data uses revised methodology and is published as custom tables (maatwerk), not yet on StatLine.

### 2.2 Woningen; hoofdverwarmingsinstallaties, wijken en buurten, 2022
- **ID**: `85677NED`
- **Geo level**: Wijk, Buurt
- **Perioden**: 2022 only
- **Key dimensions**: RegioS
- **Key measures**: Same as 84948NED but single year, wijk/buurt level
- **Join keys**: RegioS (WK/BU level)
- **Status**: ⚠️ DEPRECATED — see notes on 84948NED
- **Notes**: Snapshot for 2022. Use for wijk/buurt level heating maps.

### 2.3 Aardgasvrije woningen; regio, wijken en buurten
- **ID**: `84838NED`
- **Geo level**: Wijk, Buurt
- **Perioden**: 2017–2022 (annual)
- **Key dimensions**: RegioS, Perioden
- **Key measures**: % Aardgasvrij, % Stadsverwarming zonder gas, % All-electric, Gasverbruik categorieën
- **Join keys**: RegioS (GM/WK/BU level), Perioden (year)
- **Status**: Active (check for updates)
- **Notes**: Directly tracks Klimaatakkoord goal. Best table for "which neighbourhoods are off gas?" stories. Combines info from energy labels, gas delivery data, and RVO heat pump registrations.

### 2.4 Zonnestroom; vermogen, bedrijven en woningen, regio
- **ID**: `85005NED`
- **Geo level**: Gemeente
- **Perioden**: 2018–present (annual)
- **Key dimensions**: RegioS, Perioden, Sector (woningen/bedrijven)
- **Key measures**: Opgesteld vermogen (MW), Aantal installaties
- **Join keys**: RegioS (GM level), Perioden (year)
- **Status**: Active
- **Notes**: Solar PV capacity per gemeente. CBS took over data collection from Netbeheer Nederland. Based on PIR (Productie Installatie Register) + additional sources.

### 2.5 Zonnestroom; woningen, wijk en buurt
- **ID**: `84518NED`
- **Geo level**: Wijk, Buurt
- **Perioden**: 2016–present (annual)
- **Key dimensions**: WijkenEnBuurten, Perioden
- **Key measures**: Opgesteld vermogen per woning, Aantal installaties, % woningen met zonnepanelen
- **Join keys**: WijkenEnBuurten (WK/BU level), Perioden (year)
- **Status**: Active
- **Notes**: The finest-grained solar data. Joins with Kerncijfers (83765NED) on WijkenEnBuurten for income × solar analysis.

### 2.6 Warmtepompen; aantallen, thermisch vermogen en energiestromen
- **ID**: `82380NED`
- **Geo level**: National only
- **Perioden**: 1994–2021
- **Key dimensions**: Perioden, Warmtebron (bodem/buitenlucht), Sector (woningen/utiliteit)
- **Key measures**: Aantal, Thermisch vermogen, Energieproductie, Vermeden fossiel
- **Join keys**: Perioden only (national level)
- **Status**: ⚠️ STOPPED (2023) — replaced by newer table
- **Notes**: Historical time series for heat pump adoption nationally. No regional breakdown.

### 2.7 Hernieuwbare energie; zonnestroom, windenergie, RES-regio
- **ID**: `85004NED`
- **Geo level**: RES-regio (30 regions)
- **Perioden**: 2018–present (annual)
- **Key dimensions**: RESRegio, Perioden
- **Key measures**: Opgesteld vermogen zon, Productie zon, Opgesteld vermogen wind, Productie wind
- **Join keys**: RESRegio (special codes, not standard GM/PV)
- **Status**: Active
- **Notes**: Tracks Regionale Energiestrategie progress. RES-regio codes don't map 1:1 to gemeenten but CBS provides a mapping table. Good for "which RES region is meeting its renewable targets?" stories.

### 2.8 Hernieuwbare elektriciteit; productie en vermogen
- **ID**: `82610NED`
- **Geo level**: National, some provincial
- **Perioden**: 1990–present (annual)
- **Key dimensions**: Perioden, Energiebron
- **Key measures**: Productie (GWh), Opgesteld vermogen (MW)
- **Join keys**: Perioden
- **Status**: Active
- **Notes**: Long time series for overall renewable electricity. Context table for trend pieces.

### 2.9 Energieverbruik woningen; type, oppervlakte, bouwjaar
- **ID**: `83878NED`
- **Geo level**: National (cross-tabulated by housing characteristics)
- **Perioden**: 2018–present (annual)
- **Key dimensions**: Perioden, Woningtype, Oppervlakteklasse, Bouwjaarklasse
- **Key measures**: Gemiddeld aardgasverbruik (m³), Gemiddeld elektriciteitsverbruik (kWh)
- **Join keys**: Perioden (national breakdowns only)
- **Status**: Active
- **Notes**: Not regional, but shows how housing age and type drive energy consumption. Essential context for "old homes use X times more gas" stories.

---

## THEME 3: INTERSECTION — HOUSING × ENERGY

These tables explicitly combine housing characteristics with energy metrics.

### 3.1 Energieleveringen particuliere woningen naar energielabel
- **ID**: Custom/maatwerk (not a standard StatLine table — published as Excel on CBS website)
- **Geo level**: National (cross-tabulated)
- **Perioden**: 2019–2023
- **Key dimensions**: Energielabel, Woningtype, Eigenaar, Hoofdverwarmingsinstallatie, Zonnestroominstallatie
- **Key measures**: Aardgaslevering, Elektriciteitslevering, Teruglevering
- **Status**: Active (maatwerk publication, check CBS website)
- **Notes**: The most explicit housing × energy cross-tabulation. Shows how gas/electricity use varies by energy label, housing type, and whether the home has solar or a heat pump. ⚠️ Methodology correction in 2025: solar panel classification error affected 2022–2023 data.

### 3.2 Woningen met een energielabel; woningkenmerken
- **ID**: `82550NED`
- **Geo level**: Gemeente, Provincie
- **Perioden**: 2011–present (irregular updates)
- **Key dimensions**: RegioS, Perioden, Energielabelklasse, Eigendomssituatie
- **Key measures**: Aantal woningen per labelklasse (A through G)
- **Join keys**: RegioS (GM level), Perioden
- **Status**: Active
- **Notes**: Distribution of energy labels per region and ownership type. Key for "what % of rental housing still has label F or G?" stories. Labels can change over time as buildings are renovated.

### 3.3 Kerncijfers wijken en buurten (energy-relevant measures)
- **ID**: `83765NED` (same as 1.4 — subset of measures)
- **Key measures relevant to energy**: Percentage meergezinswoningen, Gemiddelde WOZ-waarde, Percentage koopwoningen, Percentage huurwoningen, Bouwjaar mediaan
- **Notes**: When joined with 84518NED (zonnestroom wijk/buurt) or 84838NED (aardgasvrij wijk/buurt), this gives you the housing context for energy transition metrics at neighbourhood level.

---

## RECOMMENDED JOINS (Quick-win combinations)

These are the highest-value cross-table analyses:

### Join A: Solar adoption × Neighbourhood wealth
- **Tables**: `84518NED` (zonnestroom wijk/buurt) + `83765NED` (kerncijfers)
- **Join on**: WijkenEnBuurten + Perioden
- **Story**: "Do wealthy neighbourhoods adopt solar faster?"
- **Difficulty**: ⭐⭐ (medium — Kerncijfers uses Measure-based OData v4 layout)

### Join B: Gas-free progress × Housing ownership
- **Tables**: `84838NED` (aardgasvrij) + `82900NED` (woningvoorraad eigendom)
- **Join on**: RegioS (GM level) + Perioden
- **Story**: "Is the gas transition happening in social housing or owner-occupied homes?"
- **Difficulty**: ⭐ (easy — both use standard RegioS)

### Join C: Housing prices × Energy labels
- **Tables**: `83625NED` (verkoopprijzen) + `82550NED` (energielabels)
- **Join on**: RegioS (GM level) + Perioden (align annual periods)
- **Story**: "Does energy efficiency affect property values?"
- **Difficulty**: ⭐⭐ (medium — price table has mixed period frequencies)

### Join D: New construction × Heating type over time
- **Tables**: `81955NED` (woningmutaties) + `84948NED` (verwarmingsinstallaties)
- **Join on**: RegioS (GM level) + Perioden
- **Story**: "Are new homes being built without gas connections?"
- **Difficulty**: ⭐⭐ (medium — need to filter mutaties to nieuwbouw only)

### Join E: Wijk-level triple join (advanced)
- **Tables**: `83765NED` (kerncijfers) + `84518NED` (zonnestroom) + `84838NED` (aardgasvrij)
- **Join on**: WijkenEnBuurten + Perioden
- **Story**: "Map of energy transition readiness by neighbourhood, combining income, solar, and gas-free status"
- **Difficulty**: ⭐⭐⭐ (hard — three tables, large datasets, need careful filtering)
