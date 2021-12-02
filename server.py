# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, redirect, url_for, request
from flask.templating import render_template
import mysql.connector as sql_db
import datetime
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd


def db_connect():
    mydb = sql_db.connect(
        host="Localhost",
        user="root",
        password="qwerty123!",
        port=3306,
        database="iot_project"
    )
    mycursor = mydb.cursor()

    return mydb, mycursor


def db_disconnect(mydb, mycursor):
    mycursor.close()
    mydb.close()
    return True


def push_iot_data_to_db(temp, hum, alcohol, timestamp):
    mydb, mycursor = db_connect()
    sql = "INSERT INTO iot_data (temperature, humidity, alcohol_value, time_stamp) VALUES(%s,%s,%s,%s)"
    val = (float(temp), float(hum), float(alcohol), str(timestamp))
    mycursor.execute(sql, val)
    mydb.commit()
    resp = mycursor.rowcount
    db_disconnect(mydb, mycursor)
    return resp


# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route("/receive_from_esp", methods=["GET"])
def receive_from_esp():
    if request.method == 'GET':
        temp = request.args.get('temp')
        hum = request.args.get('hum')
        alcohol = request.args.get('alcohol')
        # ct stores current time
        current_date_time = datetime.datetime.now()
        resp = push_iot_data_to_db(temp, hum, alcohol, current_date_time)
        if resp:
            return "Success"
        else:
            return "Failed"
    else:
        return "Failed"


@app.route('/')
def hello_world():
    mydb, mycursor = db_connect()
    sql = "SELECT time_stamp, temperature, humidity, alcohol_value FROM iot_data"
    mycursor.execute(sql)
    response = mycursor.fetchall()
    db_disconnect(mydb, mycursor)
    return render_template("index.html", data=response)


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run("0.0.0.0", port=5000, debug=True)
