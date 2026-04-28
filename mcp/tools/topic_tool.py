from core.database import cursor

def get_next_topic():
    cursor.execute("SELECT id, content FROM topics WHERE used=0 LIMIT 1")
    row = cursor.fetchone()

    if not row:
        return None

    return row