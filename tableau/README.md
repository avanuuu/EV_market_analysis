# Tableau Workbook Assets & Deployment Guide

This directory contains the Tableau BI assets for the **Electric Vehicle (EV) Market Analysis** project.

## File Assets
- `ev_market_analysis.twb`: Standalone Tableau workbook XML pre-configured with data connections, calculated fields, 12 worksheets, 3 executive dashboards, and a 5-scene analytical story.
- `workbook_assets/`: Static mockups, color palette definitions, and data export references.

---

## Data Source Connections

### Option A: Direct MySQL Live / Extract Connection (Recommended for Enterprise BI)
1. Open Tableau Desktop (version 2022.1 or newer).
2. Click **Connect** -> **To a Server** -> **MySQL**.
3. Configure the connection parameters:
   - **Server**: `localhost` (or `$MYSQL_HOST`)
   - **Port**: `3306`
   - **Database**: `ev_market_db`
   - **Username**: `root` (or `$MYSQL_USER`)
   - **Password**: `$MYSQL_PASSWORD`
4. Drag the pre-built view `v_executive_market_kpis` or join `vehicles`, `manufacturers`, `battery_technologies`, and `sales` onto the canvas using standard inner joins.

### Option B: Pre-Packaged Denormalized CSV Extract (Tableau Public Compatible)
The workbook `ev_market_analysis.twb` is directly pre-wired to:
`data/processed/ev_market_master_tableau.csv`
- 1,149 vehicle model variants.
- 26 cleaned, harmonized dimensions and numerical measures.
- Zero configuration required: Simply open `ev_market_analysis.twb` in Tableau Desktop or Tableau Public.

---

## Calculated Fields Reference

| Calculated Field | Formula | Purpose | Persona |
| :--- | :--- | :--- | :--- |
| **Vehicle Count** | `COUNT([Vehicle ID])` | Unique count of vehicle configurations | BI Manager |
| **Average Range (km)** | `AVG([Driving Range (km)])` | Mean driving range per cohort | Market Strategy |
| **Average Battery (kWh)** | `AVG([Battery Capacity Gross (kWh)])` | Mean pack size across categories | Research Analyst |
| **Range Efficiency** | `AVG([Driving Range (km)]) / NULLIF(AVG([Battery Capacity Net (kWh)]), 0)` | Effective range delivered per usable kWh | Research Analyst |
| **Price per km Range** | `AVG([Base Price (USD)]) / NULLIF(AVG([Driving Range (km)]), 0)` | Capital cost efficiency ratio | Market Strategy |
| **Customer Rating Avg** | `AVG([Customer Rating (1-5)])` | Consumer satisfaction benchmark | Market Strategy |

---

## Dashboard Architecture

### Dashboard A: EV Market Overview (`Dashboard_A_EV_Market_Overview`)
- **KPI Summary Card**: Total vehicles cataloged (1,149), average driving range (443.9 km), average battery size (76.2 kWh), and average MSRP ($42,054).
- **Worksheet 1 (`Sales_Trend_By_Year`)**: Longitudinal area chart of BEV vs PHEV adoption from 2015 to 2023.
- **Worksheet 2 (`Sales_By_Manufacturer`)**: Horizontal bar chart of top global OEMs (Tesla, BYD, VW, SAIC, Geely, BMW, Hyundai).
- **Worksheet 3 (`Sales_By_Category`)**: Stacked bar breakdown showing SUVs dominating over 55% of global consumer demand.

### Dashboard B: Battery and Performance (`Dashboard_B_Battery_and_Performance`)
- **Worksheet 1 (`Battery_Tech_Distribution`)**: Pie/donut chart comparing NMC (80.1%) vs LFP (19.9%) model adoption.
- **Worksheet 2 (`Driving_Range_By_Category`)**: Box-and-whisker plot of driving ranges across SUVs, Sedans, Pickups, and Vans.
- **Worksheet 3 (`Battery_Capacity_vs_Range_Scatter`)**: Dual-axis scatter plot of usable battery capacity (kWh) vs driving range (km) color-coded by chemistry.
- **Worksheet 4 (`Charging_Time_and_Efficiency`)**: Scatter plot correlating 10-80% DC fast-charging duration (min) with peak charging power (kW).

### Dashboard C: Manufacturer and Geography (`Dashboard_C_Manufacturer_and_Geography`)
- **Worksheet 1 (`Manufacturer_Sales_Ranking`)**: Global OEM volume and market share leaderboard.
- **Worksheet 2 (`Manufacturing_Country_Distribution`)**: Geographic bubble chart depicting Gigafactory capacity (China 52.8%, USA 23.5%, Germany 15.7%).
- **Worksheet 3 (`Customer_Satisfaction_Matrix`)**: Multi-attribute spider/heat grid of reliability, charging, software, and build quality.
- **Worksheet 4 (`Vehicle_Comparison_Detailed_Table`)**: Filterable data table of vehicles with sorting by price, range, and efficiency.

---

## Tableau Story: 5-Scene Narrative Walkthrough

1. **Scene 1: Global EV Market Expansion**: Demonstrates the exponential inflection point in sales from 1.6M in 2018 to 13.8M in 2023.
2. **Scene 2: OEM Competitive Duopoly**: Highlights Tesla and BYD capturing over 35% of global BEV production.
3. **Scene 3: The Battery Chemistry Bifurcation**: Contrasts LFP affordability ($30.9k avg) with NMC long-range dominance ($44.8k avg).
4. **Scene 4: Category Range Capabilities & Fast Charging**: Details consumer preference for SUVs and 800V high-power charging platforms.
5. **Scene 5: Strategic Takeaways & Sustainable Mobility Roadmaps**: Summarizes recommendations on supply-chain regionalization and LFP cell scaling.

---

## Publishing to Tableau Public / Tableau Server
1. In Tableau Desktop, select **Server** -> **Tableau Public** -> **Save to Tableau Public As...**.
2. Sign in with your Tableau Public credentials.
3. Name the workbook: `ElectricVehicleMarketAnalysis`.
4. Copy the public URL (e.g. `https://public.tableau.com/views/ElectricVehicleMarketAnalysis/EVMarketOverview`).
5. Update your `.env` file:
   ```bash
   TABLEAU_DASHBOARD_URL="https://public.tableau.com/views/ElectricVehicleMarketAnalysis/EVMarketOverview"
   TABLEAU_STORY_URL="https://public.tableau.com/views/ElectricVehicleMarketAnalysis/EVMarketStory"
   ```
6. The Flask application automatically embeds your live dashboard via the Tableau Javascript Embedding API v3!
