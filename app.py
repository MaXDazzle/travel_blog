from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

# --- Создание базы данных ---
def init_db():
    if not os.path.exists("travel_diary.db"):
        conn = sqlite3.connect("travel_diary.db")
        c = conn.cursor()

        # Таблица пользователей
        c.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)

        # Таблица путешествий
        c.execute("""
            CREATE TABLE trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                location TEXT,
                latitude REAL,
                longitude REAL,
                image_url TEXT,
                cost REAL,
                heritage TEXT,
                attractions TEXT,
                mobility_rating INTEGER,
                safety_rating INTEGER,
                population_rating INTEGER,
                greenery_rating INTEGER
            )
        """)

        conn.commit()
        conn.close()

# --- Главная страница ---
@app.route("/")
def index():
    conn = sqlite3.connect("travel_diary.db")
    c = conn.cursor()
    c.execute("""
        SELECT trips.id, users.username, trips.title, trips.location, trips.image_url, trips.cost
        FROM trips
        JOIN users ON trips.user_id = users.id
    """)
    trips = c.fetchall()
    conn.close()
    return render_template("index.html", trips=trips)

# --- Регистрация ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("travel_diary.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            conn.close()
            return "Пользователь уже существует!"
    return render_template("register.html")

# --- Авторизация ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("travel_diary.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("index"))
        else:
            return "Неверный логин или пароль!"
    return render_template("login.html")

# --- Выход ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# --- Добавление путешествия ---
@app.route("/add_trip", methods=["GET", "POST"])
def add_trip():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        location = request.form["location"]
        latitude = request.form["latitude"]
        longitude = request.form["longitude"]
        image_url = request.form["image_url"]
        cost = request.form["cost"]
        heritage = request.form["heritage"]
        attractions = request.form["attractions"]
        mobility_rating = request.form["mobility_rating"]
        safety_rating = request.form["safety_rating"]
        population_rating = request.form["population_rating"]
        greenery_rating = request.form["greenery_rating"]

        conn = sqlite3.connect("travel_diary.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO trips (user_id, title, location, latitude, longitude, image_url, cost, heritage, attractions, mobility_rating, safety_rating, population_rating, greenery_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session["user_id"], title, location, latitude, longitude, image_url, cost, heritage, attractions, mobility_rating, safety_rating, population_rating, greenery_rating))
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("add_trip.html")

# --- Просмотр отдельного путешествия ---
@app.route("/trip/<int:trip_id>")
def trip_detail(trip_id):
    conn = sqlite3.connect("travel_diary.db")
    c = conn.cursor()
    c.execute("""
        SELECT trips.*, users.username FROM trips
        JOIN users ON trips.user_id = users.id
        WHERE trips.id=?
    """, (trip_id,))
    trip = c.fetchone()
    conn.close()
    return render_template("trip_detail.html", trip=trip)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
