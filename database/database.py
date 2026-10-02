import sqlite3

DB_NAME = "groundwater.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groundwater (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT,
            district TEXT,
            rainfall_mm REAL,
            recharge_mcm REAL,
            extraction_mcm REAL,
            groundwater_level_m REAL,
            category TEXT,
            UNIQUE(state, district)
        )
    """)

    conn.commit()
    conn.close()


def insert_groundwater_data(data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO groundwater
        (state, district, rainfall_mm, recharge_mcm,
        extraction_mcm, groundwater_level_m, category)

        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()

def get_groundwater_data():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM groundwater
    """)

    data = cursor.fetchall()

    conn.close()

    return data

def get_district_data(district):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT state, district, rainfall_mm,
               recharge_mcm, extraction_mcm,
               groundwater_level_m, category
        FROM groundwater
        WHERE LOWER(district) = LOWER(?)
    """, (district,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    return {
        "state": row[0],
        "district": row[1],
        "rainfall_mm": row[2],
        "recharge_mcm": row[3],
        "extraction_mcm": row[4],
        "groundwater_level_m": row[5],
        "category": row[6]
    }

def get_districts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT district 
        FROM groundwater""")
    districts = cursor.fetchall()
    conn.close()
    return [row[0] for row in districts]

def get_state_data(state):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT state, district, rainfall_mm,
               recharge_mcm, extraction_mcm,
               groundwater_level_m, category
        FROM groundwater
        WHERE LOWER(state) = LOWER(?)
    """, (state,))

    rows = cursor.fetchall()

    conn.close()

    data = []

    for row in rows:

        data.append({
            "state": row[0],
            "district": row[1],
            "rainfall_mm": row[2],
            "recharge_mcm": row[3],
            "extraction_mcm": row[4],
            "groundwater_level_m": row[5],
            "category": row[6]
        })

    return data