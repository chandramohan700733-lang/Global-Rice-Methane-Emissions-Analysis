-- Q1. World rice methane emissions by year (kt CH4) and year-on-year change
SELECT year,
       ROUND(rice_ch4_kt, 0) AS world_ch4_kt,
       ROUND((rice_ch4_kt - LAG(rice_ch4_kt) OVER (ORDER BY year)) * 100.0
             / LAG(rice_ch4_kt) OVER (ORDER BY year), 1) AS yoy_pct
FROM world_totals
ORDER BY year;

-- Q2. Top 10 emitting countries in 2024 with share of the world total
SELECT CAST(rank_in_year AS INTEGER) AS rank, area AS country,
       ROUND(rice_ch4_kt, 0) AS ch4_kt,
       ROUND(share_of_world_pct, 1) AS share_pct
FROM rice_emissions
WHERE year = 2024
ORDER BY rice_ch4_kt DESC
LIMIT 10;

-- Q3. India over time: emissions, world share and rank
SELECT year, ROUND(rice_ch4_kt, 0) AS ch4_kt,
       ROUND(share_of_world_pct, 1) AS share_pct,
       CAST(rank_in_year AS INTEGER) AS rank
FROM rice_emissions
WHERE area = 'India' AND year IN (1990, 2000, 2010, 2015, 2020, 2024)
ORDER BY year;

-- Q4. Biggest increases from 1990 to 2024 (countries above 100 kt in 2024)
WITH a AS (
  SELECT area,
         MAX(CASE WHEN year = 1990 THEN rice_ch4_kt END) AS y1990,
         MAX(CASE WHEN year = 2024 THEN rice_ch4_kt END) AS y2024
  FROM rice_emissions GROUP BY area
)
SELECT area AS country, ROUND(y1990, 0) AS ch4_1990, ROUND(y2024, 0) AS ch4_2024,
       ROUND(y2024 - y1990, 0) AS change_kt,
       ROUND((y2024 - y1990) * 100.0 / y1990, 0) AS change_pct
FROM a WHERE y1990 > 0 AND y2024 > 100
ORDER BY change_kt DESC
LIMIT 10;

-- Q5. Biggest decreases from 1990 to 2024 (countries above 100 kt in 1990)
WITH a AS (
  SELECT area,
         MAX(CASE WHEN year = 1990 THEN rice_ch4_kt END) AS y1990,
         MAX(CASE WHEN year = 2024 THEN rice_ch4_kt END) AS y2024
  FROM rice_emissions GROUP BY area
)
SELECT area AS country, ROUND(y1990, 0) AS ch4_1990, ROUND(y2024, 0) AS ch4_2024,
       ROUND(y2024 - y1990, 0) AS change_kt,
       ROUND((y2024 - y1990) * 100.0 / y1990, 0) AS change_pct
FROM a WHERE y1990 > 100 AND y2024 < y1990
ORDER BY change_kt ASC
LIMIT 10;

-- Q6. How concentrated is it? Share of the top 5 and top 10 emitters by year
SELECT year,
       ROUND(SUM(CASE WHEN rank_in_year <= 5  THEN share_of_world_pct END), 1) AS top5_share_pct,
       ROUND(SUM(CASE WHEN rank_in_year <= 10 THEN share_of_world_pct END), 1) AS top10_share_pct
FROM rice_emissions
WHERE year IN (1990, 2000, 2010, 2020, 2024)
GROUP BY year ORDER BY year;

-- Q7. Where is rice the biggest part of agricultural methane? (2024, agriculture above 500 kt)
SELECT area AS country,
       ROUND(agri_ch4_kt, 0) AS agri_ch4_kt,
       ROUND(rice_ch4_kt, 0) AS rice_ch4_kt,
       ROUND(rice_share_of_agri_ch4_pct, 1) AS rice_share_pct
FROM rice_emissions
WHERE year = 2024 AND agri_ch4_kt > 500
ORDER BY rice_share_of_agri_ch4_pct DESC
LIMIT 10;
