from database import (
    load_records, add_book, update_book, delete_book,
    search_books, add_member, issue_book, return_book,
    import_books_csv, export_csv, add_sample_data
)

from reports import (
    show_dashboard, show_category_report,
    show_transaction_history
)


def heading(title):
    print("\n" + "=" * 58)
    print(f"                 {title}")
    print("=" * 58)


def pause():
    input("\nPress Enter to continue...")


def get_text(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("Input cannot be empty.")


def get_number(prompt, minimum=1):
    while True:
        try:
            value = int(input(prompt))

            if value >= minimum:
                return value

            print(f"Enter a number greater than or equal to {minimum}.")

        except ValueError:
            print("Invalid input. Enter a whole number.")


def show_books(records=None):
    books = records if records is not None else load_records("books")

    heading("BOOK COLLECTION")

    print(
        f"{'ID':<5}{'TITLE':<23}{'AUTHOR':<18}"
        f"{'CATEGORY':<14}{'AVAILABLE':>10}"
    )
    print("-" * 70)

    if not books:
        print("No books found.")
    else:
        for book in books:
            print(
                f"{book['id']:<5}"
                f"{book['title'][:21]:<23}"
                f"{book['author'][:16]:<18}"
                f"{book['category'][:12]:<14}"
                f"{book['available']:>10}"
            )

    print("-" * 70)


def show_members():
    members = load_records("members")

    heading("REGISTERED MEMBERS")
    print(f"{'ID':<6}{'NAME':<22}{'EMAIL':<27}{'PHONE'}")
    print("-" * 70)

    if not members:
        print("No members registered.")
    else:
        for member in members:
            print(
                f"{member['id']:<6}"
                f"{member['name'][:20]:<22}"
                f"{member['email'][:25]:<27}"
                f"{member['phone']}"
            )

    print("-" * 70)


def book_menu():
    while True:
        heading("BOOK MANAGEMENT")
        print("1. Add new book")
        print("2. View all books")
        print("3. Update book details")
        print("4. Delete book")
        print("5. Search books")
        print("6. Back to main menu")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            title = get_text("Book title: ")
            author = get_text("Author name: ")
            category = get_text("Category: ")
            quantity = get_number("Quantity: ")

            book = add_book(title, author, category, quantity)
            print(f"\nBook added successfully! ID: {book['id']}")

        elif choice == "2":
            show_books()

        elif choice == "3":
            show_books()
            book_id = get_number("Enter book ID: ")

            title = get_text("New title: ")
            author = get_text("New author: ")
            category = get_text("New category: ")

            if update_book(book_id, title, author, category):
                print("Book details updated successfully.")
            else:
                print("Book ID not found.")

        elif choice == "4":
            show_books()
            book_id = get_number("Enter book ID to delete: ")

            if delete_book(book_id):
                print("Book deleted successfully.")
            else:
                print("Book not found or copies are currently issued.")

        elif choice == "5":
            keyword = get_text("Search title, author or category: ")
            results = search_books(keyword)
            show_books(results)
            print(f"Search results: {len(results)} book(s) found.")

        elif choice == "6":
            break

        else:
            print("Invalid choice. Select from 1 to 6.")

        pause()


def member_menu():
    while True:
        heading("MEMBER MANAGEMENT")
        print("1. Register new member")
        print("2. View all members")
        print("3. Back to main menu")

        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            name = get_text("Member name: ")
            email = get_text("Email address: ")
            phone = get_text("Phone number: ")

            if "@" not in email or "." not in email:
                print("Please enter a valid email address.")
            else:
                member = add_member(name, email, phone)

                if member:
                    print(
                        f"Member registered successfully! "
                        f"Member ID: {member['id']}"
                    )
                else:
                    print("This email is already registered.")

        elif choice == "2":
            show_members()

        elif choice == "3":
            break

        else:
            print("Invalid choice.")

        pause()


def issue_menu():
    heading("ISSUE A BOOK")

    show_books()
    show_members()

    book_id = get_number("Enter book ID: ")
    member_id = get_number("Enter member ID: ")

    success, message = issue_book(book_id, member_id)

    print("\n" + message)


def return_menu():
    heading("RETURN A BOOK")

    transactions = [
        t for t in load_records("transactions")
        if t["status"] == "Issued"
    ]

    if not transactions:
        print("There are no active book issues.")
        return

    books = load_records("books")
    members = load_records("members")

    print(
        f"{'TRANS ID':<12}{'BOOK':<24}"
        f"{'MEMBER':<20}{'ISSUE DATE'}"
    )
    print("-" * 75)

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
            f"{transaction['id']:<12}"
            f"{book.get('title', 'Unknown')[:22]:<24}"
            f"{member.get('name', 'Unknown')[:18]:<20}"
            f"{transaction['issue_date']}"
        )

    transaction_id = get_number("\nEnter transaction ID: ")
    success, message = return_book(transaction_id)

    print("\n" + message)


def import_menu():
    heading("IMPORT BOOKS FROM CSV")

    path = get_text("Enter CSV file path: ")

    added, errors = import_books_csv(path)

    print(f"\nSuccessfully imported: {added} book(s)")

    if errors:
        print("\nImport warnings:")
        for error in errors:
            print("-", error)


def export_menu():
    heading("EXPORT LIBRARY RECORDS")
    print("1. Export books")
    print("2. Export members")
    print("3. Export transactions")

    choice = input("\nChoose an option: ").strip()

    names = {
        "1": "books",
        "2": "members",
        "3": "transactions"
    }

    if choice not in names:
        print("Invalid choice.")
        return

    name = names[choice]
    filename = name + "_export.csv"

    try:
        if export_csv(name, filename):
            print(f"\nExport completed: {filename}")
        else:
            print("No records available to export.")

    except OSError as error:
        print("Export failed:", error)


def main():
    while True:
        heading("CAMPUSSOLVE LIBRARY SYSTEM")

        print("1.  Dashboard")
        print("2.  Book Management")
        print("3.  Member Management")
        print("4.  Issue a Book")
        print("5.  Return a Book")
        print("6.  Transaction History")
        print("7.  Category-wise Report")
        print("8.  Import Books from CSV")
        print("9.  Export Records to CSV")
        print("10. Load Sample Books")
        print("11. Exit")

        print("-" * 58)
        choice = input("Enter your choice (1-11): ").strip()

        try:
            if choice == "1":
                show_dashboard()

            elif choice == "2":
                book_menu()
                continue

            elif choice == "3":
                member_menu()
                continue

            elif choice == "4":
                issue_menu()

            elif choice == "5":
                return_menu()

            elif choice == "6":
                show_transaction_history()

            elif choice == "7":
                show_category_report()

            elif choice == "8":
                import_menu()

            elif choice == "9":
                export_menu()

            elif choice == "10":
                if add_sample_data():
                    print("Sample books added successfully.")
                else:
                    print("Books already exist. Sample data not added.")

            elif choice == "11":
                print("\nThank you for using CampusSolve!")
                print("Your library records are saved.")
                break

            else:
                print("Invalid choice. Please select 1 to 11.")

        except (OSError, ValueError, KeyError) as error:
            print(f"\nOperation failed: {error}")

        pause()


if __name__ == "__main__":
    main()