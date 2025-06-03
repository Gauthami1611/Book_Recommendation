import pymysql
import os
from flask import Flask, session, render_template, redirect, request,url_for
import pandas as pd

from datetime import datetime
import calendar

# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors




conn=pymysql.connect(host="localhost", user="root", password="Gauthu@12", db="e_book")
cursor=conn.cursor()
app=Flask(__name__)

App_root=os.path.dirname(os.path.abspath(__file__))
books_path = App_root + "/static/books"

app.secret_key="e_book"
admin_username="admin"
admin_password="admin"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username=request.form.get("username")
    password = request.form.get("password")
    if admin_username==username and admin_password==password:
        session['role']="admin"
        return render_template("admin_home.html")
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/genres")
def genres():
    cursor.execute("select * from genres")
    genres = cursor.fetchall()
    return render_template("genres.html", genres = genres)


@app.route("/add_genre_action", methods=['post'])
def add_genre_action():
    genre_name = request.form.get("genre_name")
    cursor.execute("insert into genres(genre_name) values('"+str(genre_name)+"')")
    conn.commit()
    return redirect("/genres")


@app.route("/reader_login")
def reader_login():
    return render_template("reader_login.html")


@app.route("/reader_login_action", methods=['post'])
def reader_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from readers where email = '"+str(email)+"' and password = '"+str(password)+"' ")
    if count > 0:
        readers = cursor.fetchall()
        session['role'] = "Reader"
        session['reader_id'] = str(readers[0][0])
        session['name'] = readers[0][1]
        reader_id = session['reader_id']
        count = cursor.execute("select * from reader_books where reader_id = '" + str(reader_id) + "' and status = 'Read' ")
        count1 = cursor.execute("select * from reader_books where reader_id = '" + str(reader_id) + "' and status = 'Currently Reading' ")
        count2 = cursor.execute("select * from reader_books where reader_id = '" + str(reader_id) + "' and status = 'Want to Read' ")
        return render_template("reader_home.html", count = count, count1 = count1, count2 = count2)
    else:
        return render_template("message.html", message="Invalid Login Details")


@app.route("/reader_home")
def reader_home():
    reader_id = session['reader_id']
    count = cursor.execute("select * from reader_books where reader_id = '"+str(reader_id)+"' and status = 'Read' ")
    count1 = cursor.execute("select * from reader_books where reader_id = '" + str(reader_id) + "' and status = 'Currently Reading' ")
    count2 = cursor.execute("select * from reader_books where reader_id = '" + str(reader_id) + "' and status = 'Want to Read' ")
    return render_template("reader_home.html", count = count, count1 = count1, count2 = count2)


@app.route("/reader_registration")
def reader_registration():
    return render_template("reader_registration.html")


@app.route("/reader_registration_action", methods=['post'])
def reader_registration_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    address = request.form.get("address")
    if confirm_password != password:
        return render_template("message.html", message="Password Doesn't Match")
    count = cursor.execute("select * from readers where email = '"+str(email)+"' ")
    if count > 0:
        return render_template("message.html", message="Email Id Already Registered")
    count = cursor.execute("select * from readers where phone='" + str(phone) + "' ")
    if count > 0:
        return render_template("message.html", message="Duplicate Phone Number")
    cursor.execute("insert into readers(first_name, last_name, email, phone, password, address) values('"+str(first_name)+"', '"+str(last_name)+"', '"+str(email)+"', '"+str(phone)+"', '"+str(password)+"', '"+str(address)+"') ")
    conn.commit()
    reader_id = cursor.lastrowid
    cursor.execute("select * from genres")
    genres = cursor.fetchall()
    return render_template("message.html", message1="Reader Successfully Registered")

    # return render_template("select_genres.html", reader_id = reader_id, genres = genres)


# @app.route("/submit_genres", methods=['post'])
# def submit_genres():
#     reader_id = request.form.get("reader_id")
#     selected_genres = request.form.getlist("selected_genres")
#     for selected_genre in selected_genres:
#         cursor.execute("insert into reader_genres(reader_id, genre_id) values('"+str(reader_id)+"', '"+str(selected_genre)+"') ")
#         conn.commit()
#     return render_template("message.html", message1 = "Reader Successfully Registered")


@app.route("/upload_book")
def upload_book():
    return render_template("upload_book.html")


@app.route("/upload_book_action", methods=['post'])
def upload_book_action():
    file = request.files.get("file")
    path = books_path + "/" + file.filename
    file.save(path)
    books = pd.read_csv(path)
    print(books)
    for book in books.values:
        cursor.execute("insert into books(title,author,book_link,genre,date_published,publisher, num_of_page, lang, rate, image_url, primary_genre, sub_genre) values('"+str(book[1]).replace("'", "")+"', '"+str(book[2]).replace("'", "")+"', '"+str(book[3]).replace("'", "")+"', '"+str(book[4]).replace("'", "")+"', '"+str(book[5]).replace("'", "")+"', '"+str(book[6]).replace("'", "").replace(",", "")+"', '"+str(book[7]).replace("'", "")+"', '"+str(book[8]).replace("'", "")+"', '"+str(book[9]).replace("'", "")+"', '"+str(book[10]).replace("'", "")+"', '"+str(book[11]).replace("'", "")+"', '"+str(book[12]).replace("'", "")+"') ")
        conn.commit()
    return render_template("message.html", message="File Uploaded Successfully")


@app.route("/view_books")
def view_books():
    genre = request.args.get("genre", "")
    author_name = request.args.get("author_name", "")
    status = request.args.get("status", "")
    lang = request.args.get("lang", "")
    page = int(request.args.get("page", 1))
    per_page = 8
    offset = (page - 1) * per_page

    conditions = []
    if genre:
        conditions.append("primary_genre = %s")
    if lang:
        conditions.append("lang = %s")
    if author_name:
        conditions.append("(title LIKE %s OR author LIKE %s)")

    query_params = []
    if genre:
        query_params.append(genre)
    if lang:
        query_params.append(lang)
    if author_name:
        query_params.append(f"%{author_name}%")
        query_params.append(f"%{author_name}%")

    base_query = "SELECT * FROM books"
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    # Handle Reader role + status filtering
    reader_books = {}
    if session['role'] == "Reader":
        reader_id = session['reader_id']
        if status:
            cursor.execute("SELECT * FROM reader_books WHERE reader_id = %s AND status = %s", (reader_id, status))
        else:
            cursor.execute("SELECT * FROM reader_books WHERE reader_id = %s", (reader_id,))
        reader_books_raw = cursor.fetchall()
        reader_books = {row[1]: row[3] for row in reader_books_raw}

        if status:
            book_ids = list(reader_books.keys())
            if book_ids:
                placeholders = ','.join(['%s'] * len(book_ids))
                base_query += (" AND" if conditions else " WHERE") + f" book_id IN ({placeholders})"
                query_params += book_ids
            else:
                # No books with selected status
                return render_template("view_books.html", books=[], reader_books=reader_books,
                                       author_name=author_name, lang=lang, genre=genre, status=status,
                                       page=page, total_pages=1)

    count_query = base_query.replace("SELECT *", "SELECT COUNT(*)")
    cursor.execute(count_query, tuple(query_params))
    total_books = cursor.fetchone()[0]

    base_query += " LIMIT %s OFFSET %s"
    query_params.extend([per_page, offset])
    cursor.execute(base_query, tuple(query_params))
    books = cursor.fetchall()

    total_pages = (total_books + per_page - 1) // per_page

    return render_template("view_books.html", books=books, reader_books=reader_books,
                           author_name=author_name, lang=lang, genre=genre, status=status,
                           page=page, total_pages=total_pages)

@app.route("/reader_book_action", methods=['post'])
def reader_book_action():
    book_id = request.form.get("book_id")
    status = request.form.get("status")
    reader_id = session['reader_id']
    cursor.execute("insert into reader_books(book_id, reader_id, status) values('"+str(book_id)+"', '"+str(reader_id)+"', '"+str(status)+"')")
    conn.commit()
    return redirect("/view_books")


@app.route("/view_book", methods=["GET"])
def view_book():
    book_id = request.args.get("book_id")
    cursor.execute("select * from books where book_id = '"+str(book_id)+"' ")
    books = cursor.fetchall()
    cursor.execute("select * from reader_books where book_id = '"+str(book_id)+"' ")
    reader_books = cursor.fetchall()
    other_books = []
    for reader_book in reader_books:
        status = reader_book[3]
        if status == "Read":
            reader_id = reader_book[2]
            cursor.execute("select * from reader_books where reader_id = '"+str(reader_id)+"' and status='Read' and book_id != '"+str(book_id)+"' ")
            other_books = cursor.fetchall()
            break
        else:
            other_books = None
    authors_str = books[0][2]
    print(books)
    print(type(books))
    authors = [author.strip() for author in authors_str.split(',')]
    where_clause = " OR ".join(["author LIKE %s" for _ in authors])
    query = f"SELECT * FROM books WHERE ({where_clause}) AND book_id != %s"
    params = [f"%{author}%" for author in authors] + [book_id]
    cursor.execute(query, params)
    authors = cursor.fetchall()
    selected_title = None
    recommendations = None
    if request.method == 'GET':
        selected_title = request.args.get('selected_title')
        recommendations = get_recommendations(selected_title)
        print("recommendations")
        print(recommendations)

    return render_template("view_book.html", books=books, authors=authors, other_books=other_books, get_book_by_book_id=get_book_by_book_id, recommendations = recommendations)


@app.route('/genre_books')
def genre_books():
    reader_id = session['reader_id']
    cursor.execute("SELECT genres.genre_name FROM reader_genres JOIN genres ON reader_genres.genre_id = genres.genre_id WHERE reader_genres.reader_id = '"+str(reader_id)+"' ")
    reader_genres = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM books")
    all_books = cursor.fetchall()
    genre_dict = {}
    for book in all_books:
        genre = book[11]
        if genre not in genre_dict:
            genre_dict[genre] = []
        if len(genre_dict[genre]) < 10:
            genre_dict[genre].append(book)
    preferred_genre_dict = {g: genre_dict[g] for g in reader_genres if g in genre_dict}
    other_genre_dict = {g: books for g, books in genre_dict.items() if g not in reader_genres}
    sorted_genre_dict = {**preferred_genre_dict, **other_genre_dict}
    return render_template("genre_books.html", books_by_genre=sorted_genre_dict)


@app.route("/new_arrivals")
def new_arrivals():
    cursor.execute("""
        SELECT *
        FROM new_arrivals r
        WHERE r.negative_score = (
            SELECT MAX(r2.negative_score)
            FROM new_arrivals r2
            WHERE r2.title = r.title
        )
    """)
    new_arrivals = cursor.fetchall()
    return render_template("new_arrivals.html", new_arrivals = new_arrivals)


@app.route("/view_new_arrival")
def view_new_arrival():
    book_title = request.args.get("book_title")
    cursor.execute("SELECT * FROM new_arrivals WHERE title LIKE %s", ("%" + book_title + "%",))
    new_arrivals = cursor.fetchall()
    pos_score = 0
    neg_score = 0
    for new_arrival in new_arrivals:
        pos_score = pos_score + float(new_arrival[6])
        neg_score = neg_score + float(new_arrival[7])
    pos_score = round(pos_score, 4)
    neg_score = round(neg_score, 4)
    title = new_arrivals[0][1]
    author = new_arrivals[0][2]
    rating = new_arrivals[0][3]
    book_url = new_arrivals[0][10]
    img_url = new_arrivals[0][11]
    return render_template("view_new_arrivals.html", new_arrivals = new_arrivals, title = title, author = author, rating = rating, book_url = book_url, img_url = img_url, pos_score = pos_score, neg_score = neg_score)


def get_book_by_book_id(book_id):
    cursor.execute("select * from books where book_id = '"+str(book_id)+"' ")
    books = cursor.fetchall()
    return books


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")





df = pd.read_csv("static/books/books_final_cleaned.csv")


df['combined_features'] = (
    df['primary_genre'].fillna('') + ' ' +
    df['sub_genre'].fillna('') + ' ' +
    df['author'].fillna('')
)


# vectorizer = TfidfVectorizer(stop_words='english')
#
# tfidf_matrix = vectorizer.fit_transform(df['combined_features'])
# cosine_sim = cosine_similarity(tfidf_matrix)
#
#
# def get_recommendations(title, top_n=8):
#     try:
#         idx = df[df['title'] == title].index[0]
#     except IndexError:
#         return []
#     sim_scores = list(enumerate(cosine_sim[idx]))
#     sim_scores = [score for score in sim_scores if score[0] != idx]
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[:top_n]
#     book_indices = [i[0] for i in sim_scores]
#     return df.iloc[book_indices].reset_index(drop=True)




# Vectorize only the necessary features
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)  # limit for memory
tfidf_matrix = vectorizer.fit_transform(df['combined_features'])

# Fit the NearestNeighbors model
model = NearestNeighbors(metric='cosine', algorithm='brute')
model.fit(tfidf_matrix)


# Get recommendations
def get_recommendations(title, top_n=8):
    try:
        idx = df[df['title'] == title].index[0]
    except IndexError:
        return []

    distances, indices = model.kneighbors(tfidf_matrix[idx], n_neighbors=top_n + 1)
    recommended_indices = indices.flatten()[1:]  # skip the first one (it’s the same book)
    return df.iloc[recommended_indices].reset_index(drop=True)


@app.route("/not_rated")
def not_rated():
    cursor.execute("select * from not_rated")
    not_rated_books=cursor.fetchall()
    print(not_rated_books)
    return render_template("not_rated.html",not_rated_books=not_rated_books)


@app.route("/view_not_rated_books")
def view_not_rated_books():
    book_title = request.args.get("book_title")
    reader_id = session.get("reader_id")

    cursor.execute("SELECT * FROM not_rated WHERE title LIKE %s", ("%" + book_title + "%",))
    not_rated_books = cursor.fetchall()

    # Default in case no match
    already_rated = False
    not_rated_id = None

    if not_rated_books:
        not_rated_book = not_rated_books[0]
        not_rated_id = not_rated_book[0]

        # Check if the user has already rated this book
        cursor.execute("SELECT * FROM rating WHERE reader_id = %s AND not_rated_id = %s", (reader_id, not_rated_id))
        already_rated = cursor.fetchone() is not None

        title = not_rated_book[1]
        author = not_rated_book[2]
        publisher = not_rated_book[3]
        published_date = not_rated_book[4]
        description = not_rated_book[5]
        cover_url = not_rated_book[6]
        categories = not_rated_book[7]
        rating = not_rated_book[8]

        return render_template(
            "view_not_rated_books.html",
            title=title,
            author=author,
            publisher=publisher,
            published_date=published_date,
            description=description,
            cover_url=cover_url,
            categories=categories,
            rating=rating,
            not_rated_id=not_rated_id,
            already_rated=already_rated
        )

    return "Book not found"


@app.route("/rate_book", methods=['POST'])
def rate_book():
    book_title = request.form.get("book_title")
    given_rating = float(request.form.get("given_rating"))
    reader_id = session['reader_id']

    # Get the book's not_rated_id
    cursor.execute("SELECT * FROM not_rated WHERE title = %s", (book_title,))
    not_rated_book = cursor.fetchone()
    not_rated_id = not_rated_book[0]

    # Insert the new rating
    cursor.execute(
        "INSERT INTO rating (rating, not_rated_id, reader_id) VALUES (%s, %s, %s)",
        (given_rating, not_rated_id, reader_id)
    )
    conn.commit()

    cursor.execute("SELECT AVG(rating) FROM rating WHERE not_rated_id = %s", (not_rated_id,))
    avg_result = cursor.fetchone()
    new_avg_rating = avg_result[0] if avg_result[0] is not None else 0.0

    cursor.execute("UPDATE not_rated SET rating = %s WHERE not_rated_id = %s", (new_avg_rating, not_rated_id))
    conn.commit()

    return redirect("/view_not_rated_books?book_title=" + book_title)


@app.route("/reading_challenge")
def reading_challenge():
    if 'reader_id' not in session:
        return redirect('/reader_login')

    reader_id = session['reader_id']
    now = datetime.now()
    current_month = now.strftime("%B")  # e.g., "May"
    current_month_num = now.month
    current_year = now.year

    # Get current month's goal (if any)
    cursor.execute("""
        SELECT * FROM reader_goal 
        WHERE reader_id = %s AND goal_month = %s AND goal_year = %s
    """, (reader_id, current_month_num, current_year))
    reader_goal = cursor.fetchone()

    goal_set = reader_goal is not None
    total_goal = reader_goal[1] if goal_set else 0

    # Count read books
    cursor.execute("""
        SELECT COUNT(*) FROM reader_books 
        WHERE reader_id = %s AND status = 'Read'
    """, (reader_id,))
    books_read = cursor.fetchone()[0]

    # Date logic
    total_days = calendar.monthrange(now.year, now.month)[1]
    days_left = total_days - now.day

    # Calculate if user can set a new goal
    can_set_goal = (not goal_set) or (days_left == 0)

    percentage = (books_read / total_goal) * 100 if total_goal else 0

    return render_template("reading_challenge.html",current_month=current_month,days_left=days_left,books_read=books_read,total_goal=total_goal,percentage=round(percentage, 2),goal_set=goal_set,can_set_goal =can_set_goal)


@app.route("/set_goal", methods=["GET", "POST"])
def set_goal():
    reader_id = session.get("reader_id")
    now = datetime.now()
    current_month = now.month
    current_year = now.year

    if request.method == "POST":
        goal = int(request.form.get("goal"))
        cursor.execute("""
            INSERT INTO reader_goal (no_of_books_goal, reader_id, goal_month, goal_year) 
            VALUES (%s, %s, %s, %s)
        """, (goal, reader_id, current_month, current_year))
        conn.commit()
        return redirect("/reading_challenge")

    return render_template("set_goal.html")


@app.route("/update_goal", methods=["GET", "POST"])
def update_goal():
    cursor.execute("select * from reader_goal where reader_id='"+str(session['reader_id'])+"' ")
    reader_goals=cursor.fetchall()
    reader_goals=(reader_goals[0][1])
    print("reader_goals")
    now = datetime.now()
    month = now.month
    year = now.year

    reader_id=session['reader_id']
    if request.method == 'POST':
        goal = request.form.get("goal")
        cursor.execute("""
            UPDATE reader_goal SET no_of_books_goal = %s
            WHERE reader_id = %s AND goal_month = %s AND goal_year = %s
        """, (goal, reader_id, month, year))
        conn.commit()
        return redirect("/reading_challenge")

    return render_template("update_goal_setting.html",reader_goals=reader_goals,current_month=now.strftime("%B"))



app.run(debug=True)