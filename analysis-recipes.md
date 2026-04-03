# Analysis Recipes: Housing × Energy Transition Story Angles

## How to use these recipes

Each recipe is a complete story template: a journalistic question, the CBS
tables needed, the analysis approach, and what to look for. They're ranked
by difficulty (⭐ = achievable in 1–2 hours, ⭐⭐⭐ = full-day project).

Pick one, adapt it to a specific region or angle, and run the code.

---

## Recipe 1: The Solar Divide ⭐⭐

**Question**: Do wealthy neighbourhoods adopt solar panels faster than
low-income areas? Is the energy transition creating a two-speed Netherlands?

**Tables**:
- `84518NED` — Zonnestroom per wijk/buurt (solar PV by neighbourhood)
- `83765NED` — Kerncijfers wijken en buurten (income, housing, demographics)

**Approach**:
1. Download solar data for most recent year, filter to wijk level
2. Download Kerncijfers for same year, extract average income and WOZ value per wijk
3. Join on WijkenEnBuurten code
4. Scatter plot: income (x) vs. % homes with solar (y)
5. Calculate correlation coefficient
6. Identify outliers: low-income wijken with high solar (why?) and high-income wijken with low solar (why?)

**What to look for**:
- Strong positive correlation = solar is a wealth indicator
- Exceptions often have stories: social housing corporations with solar programmes, or old city centres where roofs are unsuitable
- Compare urban vs rural: different patterns expected
- Year-over-year trend: is the gap widening or closing?

**Lede template**: "In [rich neighbourhood], [X]% of homes have solar panels. Five kilometres away in [poor neighbourhood], it's just [Y]%. The energy transition is [widening/narrowing] the gap between Dutch neighbourhoods."

**Caveats**: Solar capacity ≠ electricity production. Flat roofs on apartments may have shared solar not counted per home. Some social housing solar is registered under the corporation, not the address.

---

## Recipe 2: Gas-Free Scoreboard ⭐

**Question**: Which municipalities are leading and lagging in the transition
off natural gas? How does progress compare to Klimaatakkoord ambitions?

**Tables**:
- `84838NED` — Aardgasvrije woningen per gemeente/wijk/buurt
- `82900NED` — Woningvoorraad eigendom (for ownership context)

**Approach**:
1. Download gas-free data for latest year, filter to gemeente level
2. Rank municipalities by % aardgasvrij
3. Compare top 10 and bottom 10
4. Join with housing ownership data: do gas-free leaders have more or less social housing?
5. Calculate the year-over-year change to show momentum

**What to look for**:
- Municipalities with district heating (stadsverwarming) will score high — is that "real" transition or legacy infrastructure?
- New-build areas (post-2018 gas connection ban) should show up as clusters
- Compare the rate of change, not just the level — who's accelerating?

**Lede template**: "Municipality [X] has taken [Y]% of its homes off natural gas — [Z] times the national average. But in [A], just [B]% of homes are gas-free, and the pace is [slowing/stalling]."

**Caveats**: "Gas-free" in CBS data means no gas delivery at all. Homes with hybrid heat pumps (gas backup) are NOT counted as gas-free. Post-2018 newbuild is gas-free by law, so high-growth municipalities get a boost automatically.

---

## Recipe 3: The Energy Label Gap ⭐⭐

**Question**: How does energy label distribution differ between rental and
owner-occupied housing? Are tenants stuck in poorly insulated homes?

**Tables**:
- `82550NED` — Woningen met energielabel (labels by region and ownership)
- `83625NED` — Verkoopprijzen (house prices, for wealth context)

**Approach**:
1. Download energy label data for most recent year, filter to gemeente level
2. Calculate % of homes with label A/B vs. F/G per gemeente, split by ownership type
3. Create a diverging bar chart: koop vs huur label distribution
4. Optional: correlate with house prices to see if expensive areas have better labels
5. Show change over time if multiple years available

**What to look for**:
- Rental housing typically lags in label quality — quantify the gap
- Some municipalities have aggressive renovation programmes — they'll show improving rental labels
- Energy labels changed methodology (there were "provisional" labels based on building year vs. "certified" labels from inspections) — be careful about mixing these

**Lede template**: "In gemeente [X], [Y]% of rental homes still carry energy label F or G — the worst categories. Owner-occupied homes are [Z] times more likely to have an A or B label."

---

## Recipe 4: Old Homes, Cold Homes ⭐

**Question**: How much more energy do older homes consume compared to new
construction? What does building age mean for gas dependency?

**Tables**:
- `83878NED` — Energieverbruik woningen naar type, oppervlakte, bouwjaar

**Approach**:
1. Download national data, all years available
2. Group by bouwjaarklasse (building age class)
3. Create bar chart: average gas consumption by building age, overlay with electricity
4. Show trend over time: are older homes improving?
5. Calculate: if all pre-1970 homes were insulated to post-2000 standards, how much gas would the Netherlands save?

**What to look for**:
- Pre-1970 homes typically use 2–3× more gas than post-2000 homes
- After the 2018 gas connection ban, newest homes show near-zero gas and higher electricity (heat pumps)
- Housing type matters: detached homes (vrijstaand) use far more than apartments

**Lede template**: "A Dutch home built before 1970 consumes an average of [X] m³ of natural gas per year — [Y] times more than a home built after 2000. Together, these [Z] million older homes account for [W]% of residential gas demand."

---

## Recipe 5: The Heat Pump Map ⭐⭐

**Question**: Where in the Netherlands are heat pumps concentrated? Is
all-electric heating still a niche phenomenon?

**Tables**:
- `84948NED` or `85677NED` — Hoofdverwarmingsinstallaties (heating type by region)
- `83765NED` — Kerncijfers (housing age, income context)

**Approach**:
1. Download heating installation data, filter to gemeente level
2. Map % all-electric per gemeente (this includes heat pumps)
3. Join with Kerncijfers to correlate with building age and income
4. Identify clusters: are heat pumps in new-build suburbs? Wealthy areas? Rural?

**What to look for**:
- Post-2018 new-build areas will have 100% all-electric by law
- Existing stock heat pump adoption is still very low (<5% nationally)
- Hybrid heat pumps (gas + electric) are classified under "individuele CV" so they're invisible in this data — mention this caveat

---

## Recipe 6: Building Permits vs. Reality ⭐⭐

**Question**: How does the housing construction pipeline look? Are building
permits translating into actual homes?

**Tables**:
- `83671NED` — Bouwvergunningen (building permits)
- `81955NED` — Woningmutaties (actual new construction, demolition)

**Approach**:
1. Download both tables for overlapping years, gemeente level
2. Compare permits issued vs homes completed (with ~2 year lag)
3. Calculate the "completion ratio": what % of permits become homes?
4. Identify municipalities where permits far exceed completions (stuck pipeline)
5. Overlay with housing price data for context

---

## Recipe 7: Energy Transition Inequality Index ⭐⭐⭐

**Question**: Can we create a single score per neighbourhood that captures
how ready it is for the energy transition — and does that correlate with
socioeconomic status?

**Tables** (triple join):
- `83765NED` — Kerncijfers (income, housing type, WOZ, demographics)
- `84518NED` — Zonnestroom wijk/buurt (solar adoption)
- `84838NED` — Aardgasvrij wijk/buurt (gas-free status)

**Approach**:
1. Download all three tables for the same year, filter to wijk level
2. Join on WijkenEnBuurten
3. Create a composite "energy transition readiness" index:
   - Weight 1: % homes with solar panels
   - Weight 2: % homes gas-free
   - Weight 3: Inverse of average building age (newer = more ready)
4. Correlate this index with average income and WOZ value
5. Map the index geographically (see geo-pdok.md)
6. Rank the 10 "most ready" and "least ready" wijken nationwide

**What to look for**:
- Is the transition index just a proxy for wealth? Or are there surprises?
- Social housing areas with active corporations might punch above their weight
- Very old city centres (grachtengordel) might score low despite wealth (heritage restrictions)

**Lede template**: "We created an energy transition readiness score for every neighbourhood in the Netherlands. The result: [core finding about inequality/surprises]."

---

## General analysis tips

### Finding stories in data

The best data stories come from one of these patterns:
- **Contrast**: A vs B (rich vs poor, urban vs rural, new vs old)
- **Ranking**: Best/worst municipalities, top/bottom neighbourhoods
- **Trend break**: When did something change direction? Why?
- **Gap**: The distance between policy ambition and reality
- **Outlier**: The case that doesn't fit the pattern (often the best story)

### Statistical hygiene

- Always report the **number of observations** — a wijk with 50 homes is not the same as one with 5,000
- Small areas (buurten) have high variance — consider aggregating to wijk or gemeente for reliable comparisons
- CBS marks provisional data with `*` or `**` — mention this
- Correlation is not causation, but data journalists can identify patterns worth investigating further

### Making it visual

For hackathon presentations:
- One strong chart beats three mediocre ones
- Chloropleth maps of the Netherlands are visually striking and immediately understood
- Annotations matter: label the outliers, mark the national average
- Always include the source: "Bron: CBS StatLine, tabel [ID], [year]"
