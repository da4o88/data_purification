import requests
import json
from datetime import datetime
from flask_paginate import get_page_parameter, Pagination
from .handlers import *
from app import app
from flask import request, render_template, redirect

# Get current time
now = datetime.now()
current_year = now.year

# Create routes for app


@app.route('/api/insert-data', methods=["POST"])
def insert_data_db():
    """
    Insert data into mongo database
    :return:
    """
    received_data = request.data
    # print(received_data) # 'city': null
    # Convert Python type null into None
    data = json.loads(received_data)
    # print(data) # 'city': None
    result = insert_data_to_db(data)
    if result:
        response = '200'
    else:
        response = '500'
    return response


@app.route('/api/get-data', methods=["GET"])
def get_data():
    """
    Get data from sqlite database
    :return: json data with list of dictionaries
    """
    data = get_db_data()
    # return jsonify(data)
    return data


@app.route('/raw-data', methods=["POST", "GET"])
def show_raw_data():
    """
    Shows data from sqlite database
    :return: redirect response to html file
    """
    # Get data from DB
    url_get_data = "http://127.0.0.1:5000/api/get-data"
    data = requests.get(url_get_data)
    # print(data.json())

    # Data from Database
    companies = get_raw_data()
    total = len(companies)  # length of list
    btn_migrate_flag = False

    # Clicked on button Migrate Data
    if request.method == "POST" and request.form.get("btn-migrate"):
        url = "http://127.0.0.1:5000/api/insert-data"

        # Convert Python type None into null for json format
        # data_json = json.dumps(data)
        # r = requests.post(url, data=data_json)
        r = requests.post(url, data=data)

        if r.status_code == 200:
            return redirect('show-data')
        elif r.status_code == 500:
            return render_template('500.html')

    # Set Pagination

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page

    # Setting up the pagination variable, where using len(total) to set the total items available
    pagination_companies = get_total_companies(companies=companies, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap5')

    return render_template("raw_data.html",
                           current_year=current_year,
                           pagination_companies=pagination_companies,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           btn_migrate_flag=btn_migrate_flag,
                           )


@app.route('/show-data', methods=["GET", "POST"])
def show_data():
    """
    Shows data from mongo database
    :return: html template file
    """
    companies = get_all_mongo_data()
    records = count_all_records()

    # Check if DB is empty
    if request.method == "GET" and records == 0:
        records_flag = True
        return render_template('show_data.html', records_flag=records_flag, current_year=current_year,)

    if request.method == "POST" and request.form.get("btn-delete-all-records"):
        delete_all_data()
        records_flag = True
        return render_template('show_data.html', records_flag=records_flag, current_year=current_year,)

    # Set Pagination
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page

    # Setting up the pagination variable, where using len(total) to set the total items available
    pagination_companies = get_total_companies(companies=companies, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=records, css_framework='bootstrap5')

    return render_template("show_data.html",
                           current_year=current_year,
                           records=records,
                           companies=pagination_companies,
                           pagination=pagination,
                           page=page,
                           per_page=per_page,
                           )


@app.route('/', methods=["GET", "POST"])
def home():

    if request.method == "POST" and request.form.get("btn-home-migrate"):
        return redirect('raw-data')
    return render_template("home.html", current_year=current_year)

