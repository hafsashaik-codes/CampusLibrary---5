import json
import csv
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "books": DATA_DIR / "books.json",
    "members": DATA_DIR / "members.json",
    "transactions": DATA_DIR / "transactions.json"
}

ERROR_LOG = DATA_DIR / "error.log"


def log_error(message):
    with open(ERROR_LOG, "a", encoding="utf-8") as file:
        file.write(
            f"{datetime.now():%Y-%m-%d %H:%M:%S} - {message}\n"
        )


def load_records(name):
    path = FILES[name]

    if not path.exists():
        save_records(name, [])
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            records = json.load(file)

        if not isinstance(records, list):
            raise ValueError("Data must be a list.")

        return records

    except (json.JSONDecodeError, OSError, ValueError) as error:
        log_error(f"Could not read {path}: {error}")
        print(f"\nWarning: {path} could not be read.")
        return []


def save_records(name, records):
    path = FILES[name]
    temporary = path.with_suffix(".tmp")

    with open(temporary, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    temporary.replace(path)


def next_id(records):
    return max(
        (record.get("id", 0) for record in records),
        default=0
    ) + 1


# ---------------- BOOK MANAGEMENT ----------------

def add_book(title, author, category, quantity):
    books = load_records("books")

    book = {
        "id": next_id(books),
        "title": title,
        "author": author,
        "category": category,
        "quantity": quantity,
        "available": quantity
    }

    books.append(book)
    save_records("books", books)
    return book


def update_book(book_id, title, author, category):
    books = load_records("books")

    for book in books:
        if book["id"] == book_id:
            book["title"] = title
            book["author"] = author
            book["category"] = category
            save_records("books", books)
            return True

    return False


def delete_book(book_id):
    books = load_records("books")

    for book in books:
        if book["id"] == book_id:
            if book["available"] != book["quantity"]:
                return False

            books.remove(book)
            save_records("books", books)
            return True

    return False


def search_books(keyword):
    keyword = keyword.lower().strip()

    return [
        book for book in load_records("books")
        if keyword in book["title"].lower()
        or keyword in book["author"].lower()
        or keyword in book["category"].lower()
    ]


# ---------------- MEMBER MANAGEMENT ----------------

def add_member(name, email, phone):
    members = load_records("members")

    if any(m["email"].lower() == email.lower() for m in members):
        return None

    member = {
        "id": next_id(members),
        "name": name,
        "email": email,
        "phone": phone
    }

    members.append(member)
    save_records("members", members)
    return member


# ---------------- ISSUE AND RETURN ----------------

def issue_book(book_id, member_id):
    books = load_records("books")
    members = load_records("members")
    transactions = load_records("transactions")

    book = next(
        (b for b in books if b["id"] == book_id), None
    )
    member = next(
        (m for m in members if m["id"] == member_id), None
    )

    if book is None or member is None:
        return False, "Book or member ID not found."

    if book["available"] <= 0:
        return False, "No copies are currently available."

    book["available"] -= 1

    transaction = {
        "id": next_id(transactions),
        "book_id": book_id,
        "member_id": member_id,
        "issue_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "return_date": None,
        "status": "Issued"
    }

    transactions.append(transaction)

    save_records("books", books)
    save_records("transactions", transactions)

    return True, f"Book issued successfully to {member['name']}."


def return_book(transaction_id):
    books = load_records("books")
    transactions = load_records("transactions")

    transaction = next(
        (
            t for t in transactions
            if t["id"] == transaction_id
            and t["status"] == "Issued"
        ),
        None
    )

    if transaction is None:
        return False, "Active transaction not found."

    book = next(
        (b for b in books if b["id"] == transaction["book_id"]),
        None
    )

    if book is None:
        return False, "Book record not found."

    book["available"] += 1
    transaction["status"] = "Returned"
    transaction["return_date"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    save_records("books", books)
    save_records("transactions", transactions)

    return True, "Book returned successfully."


# ---------------- CSV IMPORT AND EXPORT ----------------

def import_books_csv(file_path):
    books = load_records("books")
    added = 0
    errors = []

    try:
        with open(
            file_path, "r", newline="", encoding="utf-8-sig"
        ) as file:
            reader = csv.DictReader(file)

            required = {"title", "author", "category", "quantity"}

            if not reader.fieldnames or not required.issubset(
                set(reader.fieldnames)
            ):
                return 0, [
                    "CSV needs title, author, category and quantity columns."
                ]

            for row_number, row in enumerate(reader, start=2):
                try:
                    title = row["title"].strip()
                    author = row["author"].strip()
                    category = row["category"].strip()
                    quantity = int(row["quantity"])

                    if not title or not author or not category:
                        raise ValueError("Text fields cannot be empty.")

                    if quantity < 1:
                        raise ValueError("Quantity must be at least 1.")

                    books.append({
                        "id": next_id(books),
                        "title": title,
                        "author": author,
                        "category": category,
                        "quantity": quantity,
                        "available": quantity
                    })

                    added += 1

                except (ValueError, KeyError, TypeError) as error:
                    errors.append(f"Row {row_number}: {error}")

        save_records("books", books)

    except (OSError, csv.Error) as error:
        log_error(f"CSV import failed: {error}")
        errors.append(str(error))

    return added, errors


def export_csv(name, file_path):
    records = load_records(name)

    if not records:
        return False

    fields = list(records[0].keys())

    with open(
        file_path, "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

    return True


# ---------------- SAMPLE DATA ----------------

def add_sample_data():
    books = load_records("books")

    if books:
        return False

    samples = [
        ("Python Programming", "Reema Thareja", "Programming", 5),
        ("Clean Code", "Robert C. Martin", "Software", 3),
        ("Database System Concepts", "Abraham Silberschatz", "Database", 4),
        ("Computer Networks", "Andrew Tanenbaum", "Networking", 2),
        ("Artificial Intelligence", "Stuart Russell", "AI", 3)
    ]

    for title, author, category, quantity in samples:
        add_book(title, author, category, quantity)

    return True