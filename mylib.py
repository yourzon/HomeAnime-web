#import

#TODO mysql class

class MariaDBConnection:
    """
    A class to manage MariaDB database operations using Flask-MySQLdb.
    """
    def __init__(self, mysql):
        """
        Initializes the database connection.

        :param mysql: Flask-MySQLdb MySQL instance
        :param logger: Logger instance (optional)
        """
        self.mysql = mysql
        
    def fetch_one(self, query, params=None):
        """Fetch a single row from a query result."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, params or ())
            result = cur.fetchone()
            cur.close()
            return result
        except Exception as e:
            return None
    def fetch_one_column(self, query, params=None):
        """Fetch one rows from a query result and retrun row + columns."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, params or ())
            result = cur.fetchone()
            columns = [col[0] for col in cur.description]
            cur.close()
            return result, columns
        except Exception as e:
            return None 
    
    def fetch_all(self, query, params=None):
        """Fetch all rows from a query result."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, params or ())
            result = cur.fetchall()
            cur.close()
            return result
        except Exception as e:
            return None
        
    def fetch_all_column(self, query, params=None):
        """Fetch all rows from a query result and retrun row + columns."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, params or ())
            result = cur.fetchall()
            columns = [col[0] for col in cur.description]
            cur.close()
            return result, columns
        except Exception as e:
            return None 
        
    def insert(self, query, params=None):
        """Execute an INSERT query."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, params or ())
            self.mysql.connection.commit()
            last_inserted_id = cur.lastrowid
            cur.close()
            return last_inserted_id
        except Exception as e:
            return None

    def update(self, query, params=None):
        """Execute an UPDATE query."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, params or ())
            self.mysql.connection.commit()
            affected_rows = cur.rowcount
            cur.close()
            return affected_rows
        except Exception as e:
            if e.args[0] == 1265:
                return "Error: data types, exceeding column length, or violating constraints like ENUM or NOT NULL"
            else:
                return f"Error:{e}"

    def delete(self, query, params=None):
        """Execute a DELETE query."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, params or ())
            self.mysql.connection.commit()
            affected_rows = cur.rowcount
            cur.close()
            return affected_rows
        except Exception as e:
            return None