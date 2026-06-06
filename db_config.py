import pyodbc

# ============================================================
# CONNECTION SETTINGS (for same laptop)
# ============================================================
SERVER = "localhost\\SQLEXPRESS"   # or ".\\SQLEXPRESS"
DATABASE = "FinanceManager"
# ============================================================

def get_connection():
    """Create and return a database connection."""
    conn_str = f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={SERVER};
        DATABASE={DATABASE};
        Trusted_Connection=yes;
    """
    return pyodbc.connect(conn_str)

def run_query(sql, params=None):
    """Execute SELECT and return list of dictionaries."""
    conn = get_connection()
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return results

def run_insert(sql, params):
    """Execute INSERT, UPDATE, DELETE. Returns number of affected rows."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows

def run_insert_and_get_id(sql, params):
    """Execute INSERT and return the new identity ID (for Goals, etc.)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    cursor.execute("SELECT SCOPE_IDENTITY()")
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return new_id