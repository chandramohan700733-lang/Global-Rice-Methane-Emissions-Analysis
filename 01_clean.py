"""
Step 1: Clean the FAOSTAT "Emissions Totals" extract and build a tidy table for rice methane.

Source : FAOSTAT, Emissions Totals (Emissions_Totals_E_All_Data_NOFLAG.csv), downloaded Nov 2026
Focus  : Item = Rice Cultivation, Element = Emissions (CH4), unit = kt
Output : data/clean/rice_emissions_clean.csv, data/clean/world_totals.csv, rice.db
"""
import os
import sqlite3
import numpy as np
import pandas as pd

RAW = "data/raw/Emissions_Totals_E_All_Data_NOFLAG.csv"
FIRST_YEAR, LAST_YEAR = 1990, 2024      # real estimates only; 2030 and 2050 are FAO projections
os.makedirs("data/clean", exist_ok=True)

df = pd.read_csv(RAW, encoding="utf-8")
print("Raw file:", df.shape)

# 1) Keep one source only. FAO TIER 1 has the data, UNFCCC rows are mostly empty.
df = df[df["Source"] == "FAO TIER 1"]

# 2) Keep only what we need
items = {"Rice Cultivation": "rice", "IPCC Agriculture": "agri"}
elements = {"Emissions (CH4)": "ch4_kt", "Emissions (CO2eq) (AR5)": "co2eq_kt"}
df = df[df["Item"].isin(items) & df["Element"].isin(elements)]
assert (df["Unit"] == "kt").all(), "unexpected unit"

# 3) Wide -> long (one row per area, item, element, year)
year_cols = [f"Y{y}" for y in range(FIRST_YEAR, LAST_YEAR + 1)]
long = df.melt(id_vars=["Area Code", "Area", "Item", "Element"], value_vars=year_cols,
               var_name="year", value_name="value_kt")
long["year"] = long["year"].str[1:].astype(int)
long["metric"] = long["Item"].map(items) + "_" + long["Element"].map(elements)

# 4) One row per area and year, one column per metric
tidy = (long.pivot_table(index=["Area Code", "Area", "year"], columns="metric",
                         values="value_kt", aggfunc="first").reset_index())
tidy.columns.name = None
tidy = tidy.rename(columns={"Area Code": "area_code", "Area": "area"})
print("Tidy table:", tidy.shape, "| areas:", tidy.area.nunique())

# 5) Classify areas. FAOSTAT codes 5000+ are groups (World, Asia, OECD ...).
#    "China" (351) is the total of mainland + Hong Kong + Macao + Taiwan, so keeping it
#    together with those four would count China twice.
def area_type(row):
    if row.area_code >= 5000:
        return "Group"
    if row.area_code == 351:
        return "China total (overlap)"
    return "Country"
tidy["area_type"] = tidy.apply(area_type, axis=1)
print(tidy.drop_duplicates("area").area_type.value_counts().to_string())

countries = tidy[tidy.area_type == "Country"].copy()
world = tidy[tidy.area == "World"].copy()

# 6) Validation: do the countries add up to the World total?
chk = (countries.groupby("year").rice_ch4_kt.sum().to_frame("sum_countries")
       .join(world.set_index("year").rice_ch4_kt.rename("world")))
chk["diff_pct"] = (chk.sum_countries - chk.world) / chk.world * 100
print("\nSum of countries vs World (rice CH4, kt):\n", chk.round(2).iloc[[0, 10, 20, 30, 34]])
print("Max abs difference (%):", round(chk.diff_pct.abs().max(), 3))
assert chk.diff_pct.abs().max() < 0.5, "countries do not add up to World"

# 7) Missing values and negative values
print("\nMissing values (country rows):\n", countries[["rice_ch4_kt", "rice_co2eq_kt", "agri_ch4_kt"]].isna().sum().to_string())
assert (countries.rice_ch4_kt.dropna() >= 0).all(), "negative emissions found"

# 8) Derived metrics
countries["share_of_world_pct"] = countries.rice_ch4_kt / countries.year.map(world.set_index("year").rice_ch4_kt) * 100
countries["rank_in_year"] = countries.groupby("year").rice_ch4_kt.rank(ascending=False, method="min")
countries["rice_share_of_agri_ch4_pct"] = np.where(countries.agri_ch4_kt > 0,
                                                   countries.rice_ch4_kt / countries.agri_ch4_kt * 100, np.nan)

# 9) Keep only areas that actually have rice emissions in at least one year
has_rice = countries.groupby("area").rice_ch4_kt.sum()
countries = countries[countries.area.isin(has_rice[has_rice > 0].index)]
print("\nCountries with rice methane:", countries.area.nunique())

# 10) Save
countries.sort_values(["year", "rice_ch4_kt"], ascending=[True, False]).to_csv("data/clean/rice_emissions_clean.csv", index=False)
world[["year", "rice_ch4_kt", "rice_co2eq_kt", "agri_ch4_kt"]].to_csv("data/clean/world_totals.csv", index=False)
with sqlite3.connect("rice.db") as con:
    countries.to_sql("rice_emissions", con, if_exists="replace", index=False)
    world.to_sql("world_totals", con, if_exists="replace", index=False)
print("Saved: data/clean/rice_emissions_clean.csv, data/clean/world_totals.csv, rice.db")
