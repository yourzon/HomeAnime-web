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

    def execute_query(self, query, params=None, commit=False):
        """
        Execute INSERT, UPDATE, DELETE queries.

        :param query: SQL query string
        :param params: Tuple of parameters
        :param commit: Whether to commit changes (for INSERT, UPDATE, DELETE)
        :return: Affected rows count or last inserted ID
        """
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, params or ())
            if commit:
                self.mysql.connection.commit()
                result = cur.lastrowid if query.strip().upper().startswith("INSERT") else cur.rowcount
            else:
                result = None
            cur.close()
            return result
        except Exception as e:
            return None