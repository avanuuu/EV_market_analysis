# Electric Vehicle Market Analysis — Demonstration Video Script

**Walkthrough Duration:** Approximately 8–10 Minutes  
**Presenter Role:** Senior Data Analyst & Automotive BI Solutions Architect  
**Target Audience:** Academic Evaluators, Executive Leadership, BI Reviewers  

---

### [00:00 - 01:15] Scene 1: Introduction & Executive Problem Statement
- **Visual:** Screen opens on the Flask application homepage (`http://127.0.0.1:5001/`). Camera zooms slightly into the hero section and executive KPI cards.
- **Presenter (Voiceover):**  
  *"Hello and welcome to the end-to-end demonstration of the Electric Vehicle Market Analysis and Business Intelligence Platform. The global automotive sector is undergoing its most radical transformation in a century. However, automotive decision-makers face fragmented data, conflicting battery claims, and supply chain bottlenecks. 
  Our platform addresses three critical business personas:
  First, the **Market Strategy Director**, who needs to identify high-growth segments and pricing thresholds;
  Second, the **Automotive BI Manager**, who must benchmark OEM market shares and Gigafactory capacities;
  And third, the **Sustainable Mobility Research Analyst**, evaluating electrochemical battery transitions and lifecycle efficiency.
  Every metric in this project is grounded in authentic, verified data from OpenEV Data, the International Energy Agency Global EV Outlook, and EV-Database."*

---

### [01:15 - 02:45] Scene 2: Data Provenance & Cleaning Pipeline
- **Visual:** Presenter switches terminal, runs `python3 scripts/validate_data.py`, and opens the `/methodology` page on the web app.
- **Presenter (Voiceover):**  
  *"Let's examine our data engineering pipeline. In `scripts/clean_data.py`, we harmonized over 13,000 raw records across three public sources. 
  We resolved 40 duplicate vehicle configurations, normalized 65 global brand aliases into canonical entities, converted European pricing to USD at 1.08, and standardized miscellaneous battery chemistries into rigorous electrochemical categories: LFP, NMC, and NCA.
  Our automated validation test confirms zero null values in primary keys, zero orphaned foreign key relationships, and 100% boundary compliance across all numerical metrics."*

---

### [02:45 - 04:15] Scene 3: MySQL Relational Schema & Advanced SQL Analysis
- **Visual:** Presenter displays `database/schema.sql` and executes `scripts/run_analysis_queries.py` in the terminal.
- **Presenter (Voiceover):**  
  *"Turning to the database tier: We designed a normalized Third Normal Form schema in MySQL named `ev_market_db`. It features six core tables: `manufacturers`, `battery_technologies`, `manufacturing_locations`, `vehicles`, `sales`, and `customer_ratings`.
  In `database/analysis_queries.sql`, we implemented 14 complex analytical queries. 
  For example, in Query 2, we utilize the `LAG()` window function to track Year-over-Year global BEV sales growth—demonstrating a 30.5% growth rate in 2023 with sales exceeding 10 million units.
  In Query 3, `DENSE_RANK()` ranks global OEMs, showing Tesla at 19.1% market share with 1.81 million BEVs, closely followed by BYD at 16.6% with 1.57 million BEVs.
  Notice our safe division using `NULLIF()` to prevent runtime divide-by-zero errors."*

---

### [04:15 - 06:30] Scene 4: Interactive Tableau Dashboards
- **Visual:** Presenter clicks on the **Tableau Dashboards** navigation link (`/dashboard`) and interacts with the dashboard view switcher.
- **Presenter (Voiceover):**  
  *"Now let's explore our visual analytics tier. We built three executive dashboards in Tableau Desktop, encapsulated in `tableau/ev_market_analysis.twb`.
  On **Dashboard A: EV Market Overview**, we observe the longitudinal adoption curve: pure BEVs now comprise 70% of total electric sales, with SUVs commanding over 55% of global model demand.
  Switching to **Dashboard B: Battery & Performance**, we uncover a vital market dynamic: the bifurcation of battery chemistry. While NMC dominates premium vehicles with an average driving range of 470.7 km and pack sizes of 81.3 kWh, Lithium Iron Phosphate (LFP) delivers an average range of 336.3 km with 55.9 kWh packs at an average price of $30,930—a 31% cost reduction that unlocks the mass-market consumer.
  On **Dashboard C: Manufacturer & Geography**, our global map illustrates that 52.8% of operational Gigafactory capacity is located in China, highlighting substantial regional supply chain concentration."*

---

### [06:30 - 07:45] Scene 5: Tableau 5-Scene Analytical Story
- **Visual:** Presenter navigates to `/story` and walks through the 5 scene points.
- **Presenter (Voiceover):**  
  *"To synthesize these insights for senior leadership, we developed a 5-Scene Tableau Story:
  Scene 1 charts the global market explosion from 1.6 million in 2018 to 13.8 million in 2023.
  Scene 2 analyzes the duopolistic scale advantage of Tesla and BYD.
  Scene 3 investigates the LFP versus NMC electrochemical bifurcation.
  Scene 4 evaluates fast-charging velocity, showing 800V architectures cutting charge times below 22 minutes.
  And Scene 5 outlines our strategic roadmaps for sustainable mobility."*

---

### [07:45 - 09:15] Scene 6: Flask Web Application & Vehicle Database Explorer
- **Visual:** Presenter navigates to `/vehicles`, types 'Ioniq' in the search bar, filters by 'SUV', and clicks next page. Then navigates to `/health`.
- **Presenter (Voiceover):**  
  *"Our web tier is built with Python Flask using a modular application factory architecture. 
  Here in the Vehicle Catalog explorer, users can search, filter by manufacturer, body style, or battery chemistry, and browse 1,149 configurations with seamless pagination.
  Visiting `/health` reveals our live JSON diagnostics, reporting database connectivity, active vehicle counts, and system status in sub-millisecond latency.
  Our automated test suite runs 21 unit and integration tests across data quality, SQL query latency, and web routes, passing with a 100% success rate in under half a second."*

---

### [09:15 - 10:00] Scene 7: Conclusion & Strategic Recommendations
- **Visual:** Presenter returns to `/findings` and summarizes the final recommendations.
- **Presenter (Voiceover):**  
  *"In conclusion, the data demonstrates that the winning automotive formula requires:
  1. Adopting LFP battery chemistry for sub-$35,000 mass-market models;
  2. Prioritizing 800V fast-charging architectures over oversized battery packs;
  3. And regionalizing cell manufacturing to mitigate geographic supply chain exposure.
  Thank you for viewing our Electric Vehicle Market Analysis demonstration. All code, datasets, SQL scripts, and Tableau workbooks are fully reproducible and available in the project repository."*
