from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -----------------------------
# Database Model
# -----------------------------
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "price": self.price,
            "stock": self.stock
        }

# Create database tables
with app.app_context():
    db.create_all()

# -----------------------------
# Routes
# -----------------------------

# 1️⃣ GET all books (with search & filter)
@app.route("/books", methods=["GET"])
def get_books():
    author = request.args.get("author")
    title = request.args.get("title")

    query = Book.query

    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))

    books = query.all()
    return jsonify([book.to_dict() for book in books]), 200


#  GET single book by ID
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.to_dict()), 200


# 3POST – Add new book
@app.route("/books", methods=["POST"])
def add_book():
    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400

    data = request.get_json()
    required_fields = ["title", "author", "price", "stock"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    book = Book(
        title=data["title"],
        author=data["author"],
        price=float(data["price"]),
        stock=int(data["stock"])
    )

    db.session.add(book)
    db.session.commit()

    return jsonify(book.to_dict()), 201


# 4️⃣ PUT – Update book
@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    if not request.is_json:
        return jsonify({"error": "JSON body required"}), 400

    data = request.get_json()

    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.price = data.get("price", book.price)
    book.stock = data.get("stock", book.stock)

    db.session.commit()
    return jsonify(book.to_dict()), 200


# 5️⃣ DELETE – Remove book
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted successfully"}), 200


# Home route
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Bookstore REST API",
        "endpoints": {
            "GET": "/books",
            "POST": "/books",
            "GET by ID": "/books/<id>",
            "PUT": "/books/<id>",
            "DELETE": "/books/<id>"
        }
    }), 200


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
