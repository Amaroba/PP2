import json
from connect import get_connection
import psycopg2


def add_contact(conn):
    name = input("Name: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group = input("Group: ")

    cur = conn.cursor()

    cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
    g = cur.fetchone()

    if not g:
        cur.execute("INSERT INTO groups(name) VALUES (%s) RETURNING id", (group,))
        g = cur.fetchone()

    cur.execute("""
        INSERT INTO contacts(name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s)
    """, (name, email, birthday, g[0]))

    conn.commit()


def search(conn):
    q = input("Search: ")
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (q,))
    print(cur.fetchall())


def filter_by_group(conn):
    group = input("Group: ")
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name, c.email
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name=%s
    """, (group,))
    print(cur.fetchall())

def sort_contacts(conn):
    field = input("Sort by (name/birthday/id): ")

    if field not in ["name", "birthday", "id"]:
        field = "name"

    cur = conn.cursor()
    cur.execute(f"SELECT * FROM contacts ORDER BY {field}")
    print(cur.fetchall())


def paginate(conn):
    limit = 3
    offset = 0

    while True:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM contacts
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (limit, offset))

        rows = cur.fetchall()
        for r in rows:
            print(r)

        cmd = input("next / prev / quit: ")

        if cmd == "next":
            offset += limit
        elif cmd == "prev" and offset > 0:
            offset -= limit
        elif cmd == "quit":
            break


# ---------------- EXPORT JSON ----------------
def export_json(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts")
    data = cur.fetchall()

    with open("export.json", "w") as f:
        json.dump(data, f, default=str)


def import_json(conn):
    with open("export.json") as f:
        data = json.load(f)

    cur = conn.cursor()

    for row in data:
        name = row[1]

        cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
        exists = cur.fetchone()

        if exists:
            choice = input(f"{name} exists (skip/overwrite): ")
            if choice == "skip":
                continue

        # simplified insert
        cur.execute("""
            INSERT INTO contacts(name, email)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (name, row[2]))

    conn.commit()


def menu():
    conn = get_connection()

    while True:
        print("""
1. Add contact
2. Search
3. Filter by group
4. Sort
5. Paginate
6. Export JSON
7. Import JSON
0. Exit
""")

        choice = input("> ")

        if choice == "1":
            add_contact(conn)
        elif choice == "2":
            search(conn)
        elif choice == "3":
            filter_by_group(conn)
        elif choice == "4":
            sort_contacts(conn)
        elif choice == "5":
            paginate(conn)
        elif choice == "6":
            export_json(conn)
        elif choice == "7":
            import_json(conn)
        elif choice == "0":
            break


if __name__ == "__main__":
    menu()