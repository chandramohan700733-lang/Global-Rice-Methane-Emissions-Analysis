# Global Rice Methane Emissions, 1990-2024 (with a focus on India)

An analysis of methane emissions from rice cultivation across countries, using public FAOSTAT data,
Python, SQL and a two-page Power BI dashboard.

**Tools:** Python (pandas), SQL (SQLite), Power BI

## Dashboard

### Global Overview
![Global Rice Methane - Global Overview](<dashboard/Global overview.png>)

### India's Story
![Global Rice Methane - India's Story](<dashboard/India's story.png>)

## Why this project
Flooded rice fields are a major source of agricultural methane. I wanted to see which countries emit the
most, how this has changed since 1990 and where India stands, using open data.

## Data
- Source: FAOSTAT, Emissions Totals (https://www.fao.org/faostat), downloaded in November 2026
- Used: Item = Rice Cultivation and IPCC Agriculture, Element = Emissions (CH4) and Emissions (CO2eq) (AR5), unit = kt
- Raw file: 67,197 rows and 76 columns (wide format, one column per year). It is not stored in this
  repository because of its size, see `data/raw/README.md`.
- Clean table: 4,264 rows (127 countries, 1990-2024), one row per country per year
- These are **modelled estimates** (FAO TIER 1, IPCC Tier 1 method), not measured emissions.

## What I did
1. **Cleaning (Python):**
   - Kept only the `FAO TIER 1` source (the `UNFCCC` rows are mostly empty).
   - Used 1990-2024 only. The 2030 and 2050 columns are FAO projections, so I left them out.
   - Reshaped the data from wide to long (one row per area, item, element and year).
   - Separated 37 group rows (World, Asia, OECD and so on) from the 239 country-level areas.
   - Removed "China" (the total of mainland China, Hong Kong, Macao and Taiwan). Keeping it together
     with its parts counted China twice and made the country sum about 20% higher than the World total.
     I use "China, mainland" and the other parts as separate countries.
2. **Validation:** the sum of all countries matches the World total within 0.01% in every year.
3. **SQL analysis (7 queries in `sql/analysis.sql`):** world trend, top emitters, India over time,
   biggest increases and decreases since 1990, concentration of the top emitters, and the rice share of
   agricultural methane.
4. **Power BI dashboard:** 2 pages, Global Overview and India's Story.

## Key findings
- World rice methane grew from about 22,173 kt (1990) to about 25,295 kt (2024), an increase of about 14%.
- In 2024 India is the largest emitter in this data: about 5,332 kt, or 21.1% of the world total.
  China, mainland is second with about 5,094 kt (20.1%). The two were almost equal in 2023 and India was
  second in every year from 1990 to 2020.
- India's emissions rose about 18% between 1990 and 2024, while China, mainland's fell about 12%
  (about 5,807 kt to 5,094 kt).
- The top 5 countries produce about 63% of the world total and the top 10 about 81%.
- Largest increases since 1990: India (+826 kt), the Philippines (+444), Thailand (+393), Nigeria (+368)
  and Myanmar (+353). Largest decreases: China, mainland (-713 kt), Brazil (-153), Japan (-128) and
  South Korea (-115).
- Rice makes up most of the agricultural methane in Thailand (83%), the Philippines (80%), Cambodia (73%)
  and Viet Nam (66%), compared with about 24% in India.

## Limitations
- These are model-based estimates, not measurements. Recent years (2023-2024) can be revised later,
  so India being first in 2024 is an estimate and not a fixed fact.
- The data has totals per country and year only. It has no information on farming practices, water
  management or yields, so it cannot show why emissions changed or how they could be reduced.
- Country boundaries and reporting can change over time, so I do not read too much into small year-to-year moves.

## How to run
```
pip install -r requirements.txt
```
1. Download the raw file as described in `data/raw/README.md`.
2. Run:
```
python 01_clean.py
python 02_run_sql.py
```
3. The Power BI dashboard (`dashboard/rice_methane.pbix`) uses `data/clean/rice_emissions_clean.csv`.
