from database import load_records


def show_dashboard():
    books = load_records("books")
    members = load_records("members")
    transactions = load_records("transactions")

    total = sum(book["quantity"] for book in books)
    available = sum(book["available"] for book in books)
    issued = total - available

    active = sum(
        1 for t in transactions if t["status"] == "Issued"
    )

    returned = sum(
        1 for t in transactions if t["status"] == "Returned"
    )

    print("\n" + "=" * 58)
    print("                 LIBRARY DASHBOARD")
    print("=" * 58)
    print(f"  Total book copies       : {total}")
    print(f"  Available copies        : {available}")
    print(f"  Issued copies           : {issued}")
    print(f"  Registered members      : {len(members)}")
    print(f"  Active transactions     : {active}")
    print(f"  Completed returns       : {returned}")
    print("=" * 58)


def show_category_report():
    books = load_records("books")
    categories = {}

    for book in books:
        category = book["category"]
        categories[category] = (
            categories.get(category, 0) + book["quantity"]
        )

    print("\nCATEGORY-WISE BOOK REPORT")
    print("-" * 40)

    if not categories:
        print("No book records available.")
        return

    for category, count in sorted(categories.items()):
        print(f"{category:<25} {count:>8} copies")

    print("-" * 40)


def show_transaction_history():
    transactions = load_records("transactions")
    books = load_records("books")
    members = load_records("members")

    print("\nTRANSACTION HISTORY")
    print("-" * 75)
    print(
        f"{'ID':<5}{'BOOK':<23}{'MEMBER':<18}"
        f"{'STATUS':<12}{'ISSUE DATE'}"
    )
    print("-" * 75)

    if not transactions:
        print("No transactions available.")
        return

    for transaction in transactions:
        book = next(
            (b for b in books if b["id"] == transaction["book_id"]),
            {}
        )
        member = next(
            (m for m in members if m["id"] == transaction["member_id"]),
            {}
        )

        print(
            f"{transaction['id']:<5}"
            f"{book.get('title', 'Deleted')[:21]:<23}"
            f"{member.get('name', 'Unknown')[:16]:<18}"
            f"{transaction['status']:<12}"
            f"{transaction['issue_date']}"
        )

    print("-" * 75)