import MySQLdb

# Open database connection


class MySQLManager():
    MYSQL_HOST = 'vcap.cj1yc0lsubr8.us-west-1.rds.amazonaws.com'
    MYSQL_PORT = '3306'
    MYSQL_DATABASE = 'crunchbase'
    MYSQL_USER = 'microventure'
    MYSQL_PASSWORD = 'immadvcap733'

    @classmethod
    def get_connection(cls):
        return MySQLdb.connect(
            cls.MYSQL_HOST,
            cls.MYSQL_USER,
            cls.MYSQL_PASSWORD,
            cls.MYSQL_DATABASE)

    @classmethod
    def execute_query(cls, query):
        conn = cls.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        result = [item for item in result]
        conn.close()
        return result
