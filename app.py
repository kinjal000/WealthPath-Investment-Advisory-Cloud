from flask import Flask, render_template, request, redirect, session
import pymysql
from config import *

app = Flask(__name__)
app.secret_key = "wealthpath123"


def get_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route("/")
def home():
    return redirect("/login")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()
        cur = con.cursor()

        sql = "SELECT * FROM users WHERE email=%s AND password=%s"

        cur.execute(sql, (email, password))

        user = cur.fetchone()

        con.close()

        if user:
            session["user"] = user["name"]
            return redirect("/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) as total FROM clients")
    total_clients = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) as total FROM investments")
    total_investments = cur.fetchone()["total"]

    con.close()

    return render_template(
        "dashboard.html",
        clients=total_clients,
        investments=total_investments
    )


# ---------------- CLIENTS ---------------- #

@app.route("/clients")
def clients():

    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT * FROM clients")

    data = cur.fetchall()

    con.close()

    return render_template("clients.html", clients=data)


@app.route("/add_client", methods=["POST"])
def add_client():

    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]
    city = request.form["city"]

    con = get_connection()
    cur = con.cursor()

    sql = """
    INSERT INTO clients(name,phone,email,city)
    VALUES(%s,%s,%s,%s)
    """

    cur.execute(sql, (name, phone, email, city))

    con.commit()
    con.close()

    return redirect("/clients")


@app.route("/delete_client/<int:id>")
def delete_client(id):

    con = get_connection()
    cur = con.cursor()

    cur.execute("DELETE FROM clients WHERE id=%s", (id))

    con.commit()
    con.close()

    return redirect("/clients")


# ---------------- INVESTMENTS ---------------- #

@app.route("/investments")
def investments():

    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT * FROM investments")

    data = cur.fetchall()

    con.close()

    return render_template(
        "investments.html",
        investments=data
    )


@app.route("/add_investment", methods=["POST"])
def add_investment():

    client = request.form["client"]

    investment = request.form["investment"]

    amount = request.form["amount"]

    risk = request.form["risk"]

    con = get_connection()

    cur = con.cursor()

    sql = """
    INSERT INTO investments
    (client_name,investment_type,amount,risk_level)

    VALUES(%s,%s,%s,%s)
    """

    cur.execute(sql, (client, investment, amount, risk))

    con.commit()

    con.close()

    return redirect("/investments")


@app.route("/delete_investment/<int:id>")
def delete_investment(id):

    con = get_connection()

    cur = con.cursor()

    cur.execute(
        "DELETE FROM investments WHERE id=%s",
        (id)
    )

    con.commit()

    con.close()

    return redirect("/investments")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5002,
        debug=True
    )