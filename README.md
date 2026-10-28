# Electric Vehicle (EV) Market Analysis — Business Intelligence Platform

An end-to-end, full-stack Data Analytics, Business Intelligence, and Web Integration platform for the global electric vehicle (EV) industry.

Built with **Python Flask**, **MySQL (InnoDB)**, **Tableau Desktop / Tableau Public**, and **pandas**, this platform empowers three strategic automotive business personas:
1. **Market Strategy Director:** Analyze adoption trends, high-performing vehicle categories, pricing inflection points, and portfolio opportunities.
2. **Automotive BI Manager:** Benchmark OEM market shares, competitive sales rankings, and global Gigafactory manufacturing footprints.
3. **Sustainable Mobility Research Analyst:** Investigate electrochemical battery transitions (LFP vs. NMC), driving range capabilities, and charging velocity.

---

## System Architecture

```
+-----------------------------------------------------------------------------------+
|                            PRESENTATION TIER (Web & BI)                           |
|  Responsive HTML5/CSS3/JS Web App  <--->  Embedded Tableau Dashboards (A, B, C)   |
|  Vehicle Catalog & REST APIs       <--->  Tableau Story (5 Analytical Scenes)     |
+-----------------------------------------+-----------------------------------------+
                                          | HTTP / JSON / Embed API
+-----------------------------------------v-----------------------------------------+
|                              APPLICATION TIER (Flask 3.1)                         |
|  app.py / Application Factory      <--->  Modular Blueprints (routes.py)          |
|  Business Intelligence Services   <--->  Security Headers & Error Interceptors   |
+-----------------------------------------+-----------------------------------------+
                                          | SQLAlchemy 2.0 / PyMySQL Pooling
+-----------------------------------------v-----------------------------------------+
|                               DATABASE TIER (MySQL 8.0/9.0)                       |
|  Normalized 3NF Schema             <--->  InnoDB Tables, Indexes & Views          |
|  Parameterized Query Pipelines     <--->  Resilient Pre-Processed CSV Fallback   |
+-----------------------------------------+-----------------------------------------+
                                          | ETL / Ingestion Scripts
+-----------------------------------------v-----------------------------------------+
|                           DATA ENGINEERING TIER (Python)                          |
|  scripts/download_data.py          <--->  scripts/clean_data.py                   |
|  scripts/load_database.py          <--->  scripts/validate_data.py                |
+-----------------------------------------------------------------------------------+
```

---

## Key Features & Highlights

- **Authentic Dataset Harmonization:** Harmonizes over 13,000 raw records from OpenEV Data (CC-BY-4.0), IEA Global EV Outlook (CC BY 4.0), and EV-Database (CC0).
- **Normalized MySQL 3NF Database (`ev_market_db`):** 6 relational tables enforcing foreign keys, unique keys, and domain boundary constraints.
- **Advanced SQL Analytics (`analysis_queries.sql`):** 14 production queries utilizing window functions (`LAG()`, `DENSE_RANK()`), CTEs, safe division (`NULLIF()`), and multi-table joins.
- **Tableau Business Intelligence (`ev_market_analysis.twb`):**
  - **Dashboard A:** EV Market Overview (Sales trends, OEM leaderboards, category contributions).
  - **Dashboard B:** Battery & Performance (LFP vs. NMC chemistry, range distributions, 800V fast-charging curves).
  - **Dashboard C:** Manufacturer & Geography (Global Gigafactory capacity map, customer satisfaction matrix).
  - **Tableau Story:** 5 analytical scenes synthesizing macro trends and executive recommendations.
- **Interactive Flask Web Application:**
  - Executive branding, responsive layouts, and KPI summary cards.
  - Interactive vehicle database explorer with multi-parameter filtering and pagination across 1,149 models.
  - Live `/health` diagnostic endpoint reporting database connectivity and status in sub-millisecond latency.
- **Automated Test Suite:** 21 automated tests covering routing, SQL query execution, and data quality (100% pass rate).

---

## Project Folder Structure

```
project-root/
├── app.py                         # Flask web application entrypoint
├── config.py                      # Flask configuration classes (Dev, Test, Prod)
├── requirements.txt               # Python package dependencies
├── run_tests.py                   # Master test suite runner (21 test cases)
├── .env.example                   # Environment configuration template
├── .env                           # Local environment configuration
├── .gitignore                     # Git version-control exclusions
├── README.md                      # Complete system documentation
├── database/
│   ├── schema.sql                 # MySQL DDL with tables, indexes, and views
│   ├── analysis_queries.sql       # 14 advanced analytical SQL queries
│   └── validation_queries.sql     # Database referential integrity & constraint checks
├── data/
│   ├── raw/                       # Original downloaded datasets (Specs, Pricing, IEA)
│   └── processed/                 # Cleaned relational CSVs & Tableau master extract
├── scripts/
│   ├── download_data.py           # Automated dataset downloader
│   ├── clean_data.py              # Data cleaning and harmonization pipeline
│   ├── load_database.py           # MySQL database ingestion script
│   ├── validate_data.py           # Relational integrity and boundary checker
│   ├── run_analysis_queries.py    # Analytical queries executor
│   └── generate_tableau_workbook.py # Tableau XML (.twb) workbook generator
├── app/
│   ├── __init__.py                # Flask application factory & security headers
│   ├── routes.py                  # Web views, data explorer, and REST APIs
│   ├── db.py                      # MySQL connection pool & resilient fallback
│   └── services.py                # Analytical metrics & pagination services
├── templates/
│   ├── base.html                  # Executive base template & navigation
│   ├── index.html                 # Homepage with hero & executive KPIs
│   ├── overview.html              # Comprehensive market tables & charts
│   ├── dashboard.html             # Embedded Tableau dashboards (A, B, C)
│   ├── story.html                 # 5-scene Tableau story walkthrough
│   ├── vehicles.html              # 1,149 vehicle model specification explorer
│   ├── methodology.html           # Data dictionary, pipeline & ER diagram
│   ├── findings.html              # Tailored stakeholder recommendations
│   ├── about.html                 # System architecture & academic criteria
│   └── errors/
│       ├── 404.html               # Custom 404 Not Found error page
│       └── 500.html               # Custom 500 Server Error page
├── static/
│   ├── css/style.css              # Executive automotive BI design system
│   └── js/main.js                 # Dashboard view switching & interactions
├── tableau/
│   ├── README.md                  # Tableau guide & calculated fields catalog
│   └── ev_market_analysis.twb     # Enterprise Tableau workbook XML file
└── documentation/
    ├── project_report.md          # 19-section formal project report
    ├── sql_analysis.md            # Detailed walkthrough of all 14 SQL queries
    ├── tableau_guide.md           # Dashboard development & calculated fields
    ├── testing_report.md          # Test results, performance & latency metrics
    └── demo_script.md             # Demonstration video walkthrough script
```

---

## Quick Start & Installation Guide

### 1. Prerequisites
- **Python:** 3.11 or newer installed (`python3 --version`).
- **MySQL:** MySQL Server 8.0 or 9.0 installed (`mysql --version`).
- **Tableau:** Tableau Desktop or Tableau Public (2022.1 or newer).

### 2. Environment Setup
Clone or navigate to the project directory:
```bash
cd "ev-market-analysis"
```

Create and activate a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS / Linux
# venv\Scripts\activate   # On Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Data Processing Pipeline
Download the authentic raw datasets:
```bash
python3 scripts/download_data.py
```

Execute the data cleaning and harmonization pipeline:
```bash
python3 scripts/clean_data.py
```
*Outputs: 6 normalized CSVs in `data/processed/`, `ev_market_master_tableau.csv`, and `data_quality_report.json`.*

Validate data quality and relational integrity:
```bash
python3 scripts/validate_data.py
```

---

## MySQL Database Setup

### 1. Start MySQL Server
On macOS via Homebrew:
```bash
brew install mysql
brew services start mysql
```

Verify the service is running:
```bash
mysql -u root
```

### 2. Ingest Data into MySQL
Configure your database password in `.env`:
```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=ev_market_db
```

Run the automated ingestion pipeline:
```bash
python3 scripts/load_database.py
```
*This executes `database/schema.sql`, builds tables, constraints, indexes, and views, and loads all 1,149 vehicles, 74 manufacturers, 20 Gigafactories, and 872 sales records with transaction safety.*

### 3. Execute Analytical SQL Queries
Run the SQL analytical queries:
```bash
python3 scripts/run_analysis_queries.py
```
Or execute directly inside the MySQL CLI:
```bash
mysql -u root -p ev_market_db < database/analysis_queries.sql
```

---

## Tableau Workbook & Visualization Guide

### Option A: Direct Local Evaluation (Zero Setup)
Double-click `tableau/ev_market_analysis.twb` in **Tableau Desktop** or **Tableau Public**.
The workbook is pre-linked to `data/processed/ev_market_master_tableau.csv` and contains:
- **Dashboard A:** EV Market Overview
- **Dashboard B:** Battery & Performance
- **Dashboard C:** Manufacturer & Geography
- **Story:** EV_Market_Story (5 scenes)

### Option B: Live Enterprise MySQL Connection
1. In Tableau Desktop, select **Data > New Data Source > MySQL**.
2. Connect to `localhost:3306`, database `ev_market_db`.
3. Drag the view `v_executive_market_kpis` onto the canvas.

### Option C: Publish to Tableau Public for Web Embedding
1. In Tableau Desktop, choose **Server > Tableau Public > Save to Tableau Public As...**.
2. Save as `ElectricVehicleMarketAnalysis`.
3. Copy your live URL and update `.env`:
   ```bash
   TABLEAU_DASHBOARD_URL="https://public.tableau.com/views/ElectricVehicleMarketAnalysis/EVMarketOverview"
   TABLEAU_STORY_URL="https://public.tableau.com/views/ElectricVehicleMarketAnalysis/EVMarketStory"
   ```

---

## Running the Web Application

Start the Flask application:
```bash
python3 app.py
```

Open your browser at:
```
http://127.0.0.1:5001/
```

### Key Routes Available:
- `/`: Home page with executive branding, KPI cards, and strategic highlights.
- `/overview`: Market overview tables, category economics, and annual trends.
- `/dashboard`: Interactive Tableau dashboards with view switcher.
- `/story`: 5-scene Tableau story walkthrough.
- `/vehicles`: Filterable and paginated vehicle specification explorer (1,149 models).
- `/methodology`: Data dictionary, pipeline rules, ER diagram, and audit logs.
- `/findings`: Tailored recommendations for the three business personas.
- `/about`: System architecture, tech stack, and evaluation rubric compliance.
- `/health`: System health diagnostic JSON endpoint.

---

## Running Automated Tests

Run the complete test suite:
```bash
python3 run_tests.py
```
Or with pytest:
```bash
pytest -v
```

### Test Results Summary:
```
======================================================================
Total Tests Executed:   21
Total Passed:          21 (100.0%)
Total Failures:        0
Total Errors:          0
Execution Duration:    0.406 seconds
======================================================================
```

---

## Project Documentation Directory

- **[Project Report](documentation/project_report.md):** 19-section formal project report covering abstract, problem statement, architecture, ER diagrams, findings, and recommendations.
- **[SQL Analysis Catalog](documentation/sql_analysis.md):** Detailed breakdown of all 14 SQL queries with business questions, formulas, and verified output tables.
- **[Tableau Guide](documentation/tableau_guide.md):** Tableau connection guide, calculated fields catalog, and dashboard specifications.
- **[Testing Report](documentation/testing_report.md):** Detailed unit test breakdowns, performance benchmarks, and record count reconciliation.
- **[Demonstration Script](documentation/demo_script.md):** 8–10 minute demonstration video walkthrough script.

---

## License & Attribution
- OpenEV Data canonical specifications are provided under CC-BY-4.0.
- IEA Global EV Data Explorer statistics are provided under CC BY 4.0.
- EV-Database pricing benchmarks are provided under CC0 (Public Domain).
- Project implementation code is provided under the MIT License.
