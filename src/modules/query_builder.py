class QueryBuilder:
    """Utility class for building parametrized SQL statements."""

    def __init__(self, table):
        self.table = table

    def select_all(self):
        return f"SELECT * FROM {self.table}"

    def select_one(self):
        return f"SELECT * FROM {self.table} WHERE id=%s"

    def insert(self, data):
        columns = list(data.keys())
        placeholders = ','.join(['%s'] * len(columns))
        cols_sql = ','.join(columns)
        sql = f"INSERT INTO {self.table} ({cols_sql}) VALUES ({placeholders})"
        values = [data[c] for c in columns]
        return sql, values

    def update(self, id_value, data):
        columns = list(data.keys())
        assignments = ','.join([f"{c}=%s" for c in columns])
        sql = f"UPDATE {self.table} SET {assignments} WHERE id=%s"
        values = [data[c] for c in columns] + [id_value]
        return sql, values

    def delete(self):
        return f"DELETE FROM {self.table} WHERE id=%s"
