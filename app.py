from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecret"  # зміни на свій ключ

# --- Підключення до Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def getCategory(user):
    response = (
    supabase.table("expenses")
    .select("category")
    .eq("user_id", user)
    .execute())

    myCategories = set()
    for category in response.data:
        myCategories.add(category['category'])
    # print(myCategories)
    return myCategories

# --- Головна (лише для авторизованих) ---
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    data = supabase.table("expenses").select("*").eq("user_id", user_id).order("date", desc=True).execute()
    expenses = data.data
    return render_template("index.html", expenses=expenses, username=session["username"])

# --- API для графіка ---
@app.route("/chart-data")
def chart_data():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    result = supabase.table("expenses").select("amount, category").eq("user_id", user_id).execute()
    print(result.data)
    totals = {}
    for row in result.data:
        cat = row["category"]
        totals[cat] = totals.get(cat, 0) + row["amount"]

    labels = list(totals.keys())
    values = list(totals.values())

    return jsonify({"labels": labels, "values": values})

# --- Реєстрація ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]  # ⚠ у продакшені треба хешувати!

        existing = supabase.table("users").select("*").eq("username", username).execute()
        if existing.data:
            return "❌ Користувач вже існує!"

        supabase.table("users").insert({"username": username, "password": password}).execute()
        return redirect(url_for("login"))
    return render_template("register.html")

# --- Логін ---
@app.route("/login", methods=["GET", "POST"])
def login():    
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()

        if user.data:
            session["user_id"] = user.data[0]["id"]
            session["username"] = user.data[0]["username"]
            return redirect(url_for("index"))
        else:
            return "❌ Неправильний логін або пароль!"
    return render_template("login.html")

# --- Логаут ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- Додавання витрати ---
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        amount = float(request.form["amount"])
        category = request.form["category"]
        date = datetime.now().strftime("%Y-%m-%d")

        supabase.table("expenses").insert({
            "user_id": session["user_id"],
            "amount": amount,
            "category": category,
            "date": date
        }).execute()

        return redirect(url_for("index"))
    return render_template("add.html")

# --- Підрахунок по категорії ---
@app.route("/category", methods=["GET", "POST"])
def category():
    if "user_id" not in session:
        return redirect(url_for("login"))
    total = None
    catPASS = None
    cat = getCategory(session["user_id"]) # список категорій
    if request.method == "POST":
        catPASS = request.form["category"]
        result = supabase.table("expenses").select("amount").eq("user_id", session["user_id"]).eq("category", catPASS).execute()
        amounts = [row["amount"] for row in result.data]
        total = sum(amounts) if amounts else 0
    return render_template("category.html", total=total, categories=cat, category = catPASS)

if __name__ == "__main__":
    app.run(debug=True)
