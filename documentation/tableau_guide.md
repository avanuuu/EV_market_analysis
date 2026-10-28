# Tableau Business Intelligence & Dashboard Development Guide

**Workbook Name:** `ev_market_analysis.twb`  
**Location:** `tableau/ev_market_analysis.twb`  
**Compatibility:** Tableau Desktop 2022.1+, Tableau Public 2022.1+  

---

## 1. Connecting Data Sources in Tableau

### Approach A: Enterprise MySQL Live Connection
1. Launch Tableau Desktop.
2. Under **Connect > To a Server**, select **MySQL**.
3. Enter connection parameters:
   - **Server:** `localhost` (or `$MYSQL_HOST`)
   - **Port:** `3306`
   - **Database:** `ev_market_db`
   - **Authentication:** Username `root`, Password `$MYSQL_PASSWORD`.
4. Open the database canvas and drag the pre-configured view `v_executive_market_kpis` or perform an inner join between:
   - `vehicles.manufacturer_id = manufacturers.manufacturer_id`
   - `vehicles.battery_tech_id = battery_technologies.battery_tech_id`
   - `sales.manufacturer_id = manufacturers.manufacturer_id` (Left Join)
   - `customer_ratings.manufacturer_id = manufacturers.manufacturer_id` (Left Join)

### Approach B: Pre-Engineered Master Data Extract (Tableau Public Ready)
The workbook `tableau/ev_market_analysis.twb` is pre-configured to read directly from:
`data/processed/ev_market_master_tableau.csv`
- 1,149 vehicle configurations.
- 26 harmonized dimensions and numerical measures.
- Zero database driver setup required: Double-click `tableau/ev_market_analysis.twb` in Tableau Desktop or Tableau Public to instantly load all worksheets and dashboards.

---

## 2. Calculated Fields & Technical Formulas

| Calculated Field Name | Tableau Formula | Data Type | Aggregation | Unit | Analytical Context |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Sales Volume** | `SUM([Units Sold])` | Integer | SUM | Units | Measures cumulative vehicle registrations |
| **Average Driving Range** | `AVG([Driving Range (km)])` | Float | AVG | km | Certified WLTP range capability |
| **Average Battery Capacity** | `AVG([Battery Capacity Gross (kWh)])` | Float | AVG | kWh | Mean gross pack capacity |
| **Calculated Range Efficiency** | `AVG([Driving Range (km)]) / NULLIF(AVG([Battery Capacity Net (kWh)]), 0)` | Float | Calculation | km/kWh | Usable range delivered per kWh of electrochemical storage |
| **Price per Range Ratio** | `AVG([Base Price (USD)]) / NULLIF(AVG([Driving Range (km)]), 0)` | Currency | Calculation | $/km | Capital cost efficiency across segments |
| **Manufacturer Market Share** | `SUM([Units Sold]) / TOTAL(SUM([Units Sold]))` | Percentage | Table (Across) | % | Share of volume within defined cohort |
| **YoY Sales Growth** | `(ZN(SUM([Units Sold])) - LOOKUP(ZN(SUM([Units Sold])), -1)) / ABS(LOOKUP(ZN(SUM([Units Sold])), -1))` | Percentage | Table (Down) | % | Annual compound growth rate |
| **Customer Satisfaction Index** | `AVG([Customer Rating (1-5)])` | Float | AVG | Score (1-5) | Consumer sentiment and reliability |

---

## 3. Executive Dashboard Architecture

### Dashboard A: EV Market Overview (`Dashboard_A_EV_Market_Overview`)
- **Target Persona:** Market Strategy Director & Automotive BI Manager
- **Layout:** Executive Grid (1400 x 900 px)
- **Components:**
  1. **Top KPI Banners:** Total Model Configurations (1,149), Average Range (443.9 km), Average Battery (76.2 kWh), and 2023 BEV Volume (10.06M).
  2. **Worksheet `Sales_Trend_By_Year`:** Dual area chart showing BEV vs PHEV adoption curve from 2015 to 2023.
  3. **Worksheet `Sales_By_Manufacturer`:** Horizontal bar chart illustrating the volume lead of Tesla, BYD, and VW Group.
  4. **Worksheet `Sales_By_Category`:** Stacked bar chart highlighting SUV and Sedan demand breakdown.

### Dashboard B: Battery and Performance (`Dashboard_B_Battery_and_Performance`)
- **Target Persona:** Sustainable Mobility Research Analyst
- **Layout:** Executive Grid (1400 x 900 px)
- **Components:**
  1. **Worksheet `Battery_Tech_Distribution`:** Donut chart showing NMC (80.1%) vs LFP (19.9%) adoption.
  2. **Worksheet `Driving_Range_By_Category`:** Box-plot distribution of real driving range across categories.
  3. **Worksheet `Battery_Capacity_vs_Range_Scatter`:** Scatter plot correlating net battery capacity (kWh) against driving range (km) color-coded by chemistry.
  4. **Worksheet `Charging_Time_and_Efficiency`:** Scatter chart mapping 10–80% fast-charging minutes vs peak DC charge power (kW).

### Dashboard C: Manufacturer and Geography (`Dashboard_C_Manufacturer_and_Geography`)
- **Target Persona:** Automotive BI Manager
- **Layout:** Executive Grid (1400 x 900 px)
- **Components:**
  1. **Worksheet `Manufacturer_Sales_Ranking`:** Global OEM leaderboard with ranking, volume, and pure EV flag.
  2. **Worksheet `Manufacturing_Country_Distribution`:** Global Gigafactory capacity map (China 52.8%, USA 23.5%, Germany 15.7%).
  3. **Worksheet `Customer_Satisfaction_Matrix`:** Heat grid of reliability, charging experience, and software scores.
  4. **Worksheet `Vehicle_Comparison_Detailed_Table`:** Interactive sortable data table of vehicles with price, range, and efficiency.

---

## 4. Tableau Story Architecture (5 Analytical Scenes)

The workbook includes a Tableau Story named `EV_Market_Story` structured into five analytical points:

1. **Scene 1: Global EV Market Expansion & Rapid Sales Growth**  
   *Focus:* Exponential growth from 1.6M in 2018 to 13.8M in 2023; BEVs capturing 70% share.
2. **Scene 2: OEM Competitive Duopoly & Market Share Dynamics**  
   *Focus:* Tesla (19.1%) and BYD (16.6%) capturing over 35% of global BEV production.
3. **Scene 3: The Battery Chemistry Bifurcation (LFP vs. NMC)**  
   *Focus:* LFP cost parity ($30.9k avg MSRP) vs NMC long-range luxury ($44.8k avg MSRP).
4. **Scene 4: Driving Range Capability & Fast-Charging Velocity**  
   *Focus:* SUV segment preference (450 km avg range) and 800V fast-charging architectures (<22 min top-up).
5. **Scene 5: Evidence-Based Findings & Business Recommendations**  
   *Focus:* Gigafactory supply chain regionalization, CTP battery scaling, and NACS charging standardization.

---

## 5. Publishing to Tableau Public & Web Embedding

1. In Tableau Desktop, select **Server > Tableau Public > Save to Tableau Public As...**.
2. Sign in with your Tableau Public account.
3. Save as `ElectricVehicleMarketAnalysis`.
4. Copy your embed URL:
   ```
   https://public.tableau.com/views/ElectricVehicleMarketAnalysis/EVMarketOverview
   ```
5. Set `TABLEAU_DASHBOARD_URL` and `TABLEAU_STORY_URL` in your `.env` file.
6. The Flask application embeds the dashboard seamlessly on `/dashboard` and the story on `/story`!
