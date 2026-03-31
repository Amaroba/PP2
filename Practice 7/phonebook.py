from connect import get_connection
import csv


def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        phone VARCHAR(20)
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


def insert_contact(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()


def import_csv(filename):
    conn = get_connection()
    cur = conn.cursor()

    with open(filename, newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cur.execute(
                "INSERT INTO contacts (name, phone) VALUES (%s, %s)",
                (row["name"], row["phone"])
            )

    conn.commit()
    cur.close()
    conn.close()


def show_contacts():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM contacts")

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def search_contact(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contacts WHERE name = %s",
        (name,)
    )

    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def update_phone(name, phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE contacts SET phone = %s WHERE name = %s",
        (phone, name)
    )

    conn.commit()
    cur.close()
    conn.close()


def delete_contact(name):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM contacts WHERE name = %s",
        (name,)
    )

    conn.commit()
    cur.close()
    conn.close()


create_table()

while True:
    print("\nPhoneBook Menu")
    print("1 - Add contact")
    print("2 - Show contacts")
    print("3 - Search contact")
    print("4 - Update phone")
    print("5 - Delete contact")
    print("6 - Import from CSV")
    print("0 - Exit")

    choice = input("Choose: ")

    if choice == "1":
        name = input("Name: ")
        phone = input("Phone: ")
        insert_contact(name, phone)

    elif choice == "2":
        show_contacts()

    elif choice == "3":
        name = input("Enter name: ")
        search_contact(name)

    elif choice == "4":
        name = input("Name: ")
        phone = input("New phone: ")
        update_phone(name, phone)

    elif choice == "5":
        name = input("Name to delete: ")
        delete_contact(name)

    elif choice == "6":
        import_csv("contacts.csv")

    elif choice == "0":
        break