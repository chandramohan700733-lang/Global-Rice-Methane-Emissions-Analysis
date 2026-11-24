# Raw data (not included)

The raw FAOSTAT file is about 40 MB, so it is not stored in this repository.

To reproduce the project:
1. Go to FAOSTAT (https://www.fao.org/faostat), Emissions - Totals, and download the bulk file "Emissions Totals (All Data)".
2. Unzip it and put `Emissions_Totals_E_All_Data_NOFLAG.csv` in this folder (`data/raw/`).
3. Run `python 01_clean.py`.

The file used here was downloaded in November 2026. FAOSTAT revises its estimates from time to time, so newer downloads may give slightly different numbers.
