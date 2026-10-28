"""
app/routes.py
=============
Modular Flask blueprint definitions for the EV Market Analysis web application.
Includes views, data explorer with pagination, Tableau embeds, and REST API endpoints.
"""

from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from app.services import (
    get_executive_kpis,
    get_annual_sales_trends,
    get_top_manufacturers_sales,
    get_category_performance,
    get_battery_tech_summary,
    get_manufacturing_geography,
    get_customer_satisfaction_benchmarks,
    get_vehicles_paginated
)
from app.db import check_mysql_status, load_table_dataframe

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Home page with hero, executive KPI cards, and strategic highlights."""
    kpis = get_executive_kpis()
    trends = get_annual_sales_trends()
    top_oems = get_top_manufacturers_sales()
    db_status = check_mysql_status(current_app.config)
    return render_template(
        "index.html",
        kpis=kpis,
        trends=trends,
        top_oems=top_oems,
        db_status=db_status
    )


@main_bp.route("/overview")
def overview():
    """Market Overview page with detailed metrics across personas."""
    kpis = get_executive_kpis()
    trends = get_annual_sales_trends()
    top_oems = get_top_manufacturers_sales()
    cat_perf = get_category_performance()
    battery_summary = get_battery_tech_summary()
    return render_template(
        "overview.html",
        kpis=kpis,
        trends=trends,
        top_oems=top_oems,
        cat_perf=cat_perf,
        battery_summary=battery_summary
    )


@main_bp.route("/dashboard")
def dashboard():
    """Tableau Embedded Dashboard page with dashboard selector and interactive controls."""
    dashboard_url = current_app.config.get("TABLEAU_DASHBOARD_URL")
    kpis = get_executive_kpis()
    db_status = check_mysql_status(current_app.config)
    return render_template(
        "dashboard.html",
        dashboard_url=dashboard_url,
        kpis=kpis,
        db_status=db_status
    )


@main_bp.route("/story")
def story():
    """Tableau Story walkthrough page with 5 narrative scenes."""
    story_url = current_app.config.get("TABLEAU_STORY_URL")
    kpis = get_executive_kpis()
    return render_template(
        "story.html",
        story_url=story_url,
        kpis=kpis
    )


@main_bp.route("/vehicles")
def vehicles():
    """Searchable, filterable, and paginated vehicle specification explorer."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str)
    category = request.args.get("category", "All", type=str)
    manufacturer = request.args.get("manufacturer", "All", type=str)
    chemistry = request.args.get("chemistry", "All", type=str)

    # Get distinct filter options
    df_master = load_table_dataframe("master_tableau")
    categories = sorted(df_master["Vehicle Category"].dropna().unique().tolist()) if not df_master.empty else []
    manufacturers = sorted(df_master["Manufacturer"].dropna().unique().tolist()) if not df_master.empty else []
    chemistries = sorted(df_master["Battery Technology Code"].dropna().unique().tolist()) if not df_master.empty else []

    page_data, total_records, total_pages = get_vehicles_paginated(
        page=page,
        per_page=20,
        search_query=search,
        category_filter=category,
        manufacturer_filter=manufacturer,
        chemistry_filter=chemistry
    )

    return render_template(
        "vehicles.html",
        vehicles=page_data,
        page=page,
        total_pages=total_pages,
        total_records=total_records,
        search=search,
        selected_category=category,
        selected_mfg=manufacturer,
        selected_chem=chemistry,
        categories=categories,
        manufacturers=manufacturers,
        chemistries=chemistries
    )


@main_bp.route("/methodology")
def methodology():
    """Methodology, Data Dictionary, Schema, and Data Quality Report page."""
    import os, json
    report_path = os.path.join(current_app.root_path, "..", "data", "processed", "data_quality_report.json")
    dq_report = {}
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            dq_report = json.load(f)

    return render_template("methodology.html", dq_report=dq_report)


@main_bp.route("/findings")
def findings():
    """Evidence-based findings and actionable recommendations for the 3 business personas."""
    kpis = get_executive_kpis()
    oems = get_top_manufacturers_sales()
    cats = get_category_performance()
    bats = get_battery_tech_summary()
    geos = get_manufacturing_geography()
    rats = get_customer_satisfaction_benchmarks()

    return render_template(
        "findings.html",
        kpis=kpis,
        oems=oems,
        cats=cats,
        bats=bats,
        geos=geos,
        rats=rats
    )


@main_bp.route("/about")
def about():
    """About page covering tech stack, architecture, academic criteria, and evaluation."""
    db_status = check_mysql_status(current_app.config)
    return render_template("about.html", db_status=db_status)


# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@main_bp.route("/health")
def health():
    """Health-check endpoint validating system status and database connectivity."""
    db_status = check_mysql_status(current_app.config)
    return jsonify({
        "status": "healthy",
        "service": "EV Market Analysis Intelligence Platform",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "database": db_status
    }), 200


@main_bp.route("/api/kpis")
def api_kpis():
    """REST API returning verified executive KPIs."""
    return jsonify(get_executive_kpis()), 200


@main_bp.route("/api/trends")
def api_trends():
    """REST API returning annual sales trends."""
    return jsonify(get_annual_sales_trends()), 200


@main_bp.route("/api/manufacturers")
def api_manufacturers():
    """REST API returning top global OEM rankings."""
    return jsonify(get_top_manufacturers_sales()), 200
