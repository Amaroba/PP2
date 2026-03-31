from connect import get_connection

def search_pattern(pattern):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
    for row in cur.fetchall():
        print(row)
    cur.close()
    conn.close()

def upsert_user(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()

def upsert_many(names, phones):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL upsert_many_contacts(%s, %s)", (names, phones))
    conn.commit()
    cur.close()
    conn.close()

def delete_user(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL delete_contact(%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    upsert_user("Alice", "12345")
    search_pattern("Al")
    upsert_many(["Bob","Eve"], ["abc","6789"])
    delete_user("Eve","6789")