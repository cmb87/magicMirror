import sys
import os
import logging
import psycopg2
from configparser import ConfigParser



### Database object ###
class Database(object):

    DBCONFIG = "./settings.ini"

    @staticmethod
    def connect():
        logging.info(f"Using the settings from {Database.DBCONFIG}")
        parser = ConfigParser()
        parser.read(Database.DBCONFIG)
        dbconfig = dict(parser._sections['postgresql'])
        #print(dbconfig)
        con = psycopg2.connect(**dbconfig)
        return con


    @staticmethod
    def checkIfTableExists(tablename):
        """Check whether a table exists or not
        Args:
            tablename (TYPE): Table name
        Returns:
            TYPE: Description
        """
        con = Database.connect()

        # "SELECT to_regclass('public.{}')".format(tablename)
        # 
        try:
            with con:
                cur = con.cursor()
                cur.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{}')".format(tablename))
                if cur.fetchone()[0] == 1:
                    return True
        except psycopg2.DatabaseError as e:
            logging.warning("{}".format(e))
        except Exception as e:
            logging.warning("{}".format(e))

        return False

    @staticmethod
    def delete_table(tablename):
        """
        """
        con = Database.connect()

        try:
            with con:
                # From the connection, we get the cursor object. The cursor is used
                # to traverse the records from the result set. We call the execute()
                # method of the cursor and execute the SQL statement.
                cur = con.cursor()
                cur.execute("DROP TABLE IF EXISTS {}".format(tablename))
                logging.info("Deleting table {}.".format(tablename))
                return True
        except psycopg2.DatabaseError as e:
            logging.warning("{}".format(e))
        except Exception as e:
            logging.warning("{}".format(e))
        return False

    @staticmethod
    def create_table(tablename, columnsdict):
        """
        Create table
        columnsdict must be of the form
        columns = {"id": "INT", "name": "TEXT", "price": "INT"}
        """
        columns = ["{} {}".format(key, columnsdict[key]) for key in columnsdict.keys()]

        if not Database.checkIfTableExists(tablename):
            con = Database.connect()

            try:
                with con:
                    # From the connection, we get the cursor object. The cursor is used
                    # to traverse the records from the result set. We call the execute()
                    # method of the cursor and execute the SQL statement.
                    cur = con.cursor()
                    cur.execute("CREATE TABLE {}({})".format(tablename, ', '.join(columns)))
                    logging.info("New table {} created sucessfully.".format(tablename))
                    return True
            except psycopg2.DatabaseError as e:
                logging.warning("{}".format(e))
            except Exception as e:
                logging.warning("{}".format(e))
        else:
            logging.info("Table {} already exists. Reusing...".format(tablename))
        return False


    @staticmethod
    def insertMany(tablename, rows, columnNames):
        """
        Insert multiple entries
        """
        placeholder1 = tablename+"("+', '.join(columnNames)+")"
        placeholder2 = ', '.join(['%('+column+")s" for column in columnNames])
        con = Database.connect()
        try:
            with con:
                cur = con.cursor()
                cur.executemany("INSERT INTO {} VALUES({})".format(placeholder1, placeholder2), rows)
                return True

        except psycopg2.DatabaseError as e:
            logging.warning("{}".format(e))
        except Exception as e:
            logging.warning("{}".format(e))
        return False

    @staticmethod
    def insert(tablename, rows, returncol=None):
        """
        Insert a list of dictionaries
        """
        con = Database.connect()
        for row in rows:
            placeholders = ', '.join(['%s' for key, val in row.items()])
            vals = [val for key, val in row.items()]
            keys = list(row.keys())

            try:
                with con:
                    cur = con.cursor()
                    if returncol == None:
                        cur.execute("INSERT INTO {}({}) VALUES({})".format(tablename, ', '.join(keys), placeholders), vals)
                        return True
                    else:
                        cur.execute("INSERT INTO {}({}) VALUES({}) RETURNING {};".format(tablename, ', '.join(keys), placeholders, returncol), vals)
                        return cur.fetchone()
            except psycopg2.DatabaseError as e:
                logging.warning("{}".format(e))
            except Exception as e:
                logging.warning("{}".format(e))
            return False

    @staticmethod
    def update(tablename, row, query):
        """
        Insert a list of dictionaries
        """
        qkeys, qvals = Database._queryProcessor(query)

        vals, keys = [], []
        for key, val in row.items():
            keys.append("{} = %s".format(key))
            vals.append(val)

        con = Database.connect()
        try:
            with con:
                cur = con.cursor()
                cur.execute("UPDATE {} SET {} WHERE {}".format(tablename, ', '.join(keys), ' AND '.join(qkeys)), vals + qvals)
                return True
        except psycopg2.DatabaseError as e:
            logging.warning("{}".format(e))

        except Exception as e:
            logging.warning("{}".format(e))

        return False

    @staticmethod
    def getColumnNames(tablename):
        """
        Get ColumnsNames of DB
        """
        con = Database.connect()
        try:
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM {0} LIMIT 1".format(tablename))
                columns = [c[0] for c in cur.description]
                return columns

        except psycopg2.DatabaseError as e:
            logging.warning("{}".format(e))
        except Exception as e:
            logging.warning("{}".format(e))

    @staticmethod
    def _queryProcessor(query):
        vals, keys = [], []
        for key, val in query.items():
            keys.append('({} {} %s)'.format(key, val[0]))
            vals.append(val[1])
        return keys, vals

    @staticmethod
    def find(tablename, query=None, one=False):
        """Summary
        Args:
            tablename (TYPE): Description
            query (TYPE): Description
        Returns:
            TYPE: Description
        """
        if not query is None:
            keys, vals = Database._queryProcessor(query)

        con = Database.connect()
        try:
            with con:
                cur = con.cursor()
                if not query is None:
                    cur.execute("SELECT {} FROM {} WHERE {};".format('*', tablename, ' AND '.join(keys)), vals)
                else:
                    cur.execute("SELECT {} FROM {}".format('*', tablename))

                if one:
                    return cur.fetchone()
                else:
                    return cur.fetchall()

        except psycopg2.DatabaseError as e:
            logging.warning("{}".format(e))
        except Exception as e:
            logging.warning("{}".format(e))

        return None


    @staticmethod
    def remove(tablename, query):
        """
        Args:
            tablename (TYPE): Description
            query (TYPE): Description
        """
        keys, vals = Database._queryProcessor(query)

        con = Database.connect()
        try:
            with con:
                cur = con.cursor()
                cur.execute("DELETE FROM {} WHERE {}".format(tablename, ' AND '.join(keys)), vals)
                return True
        except psycopg2.DatabaseError as e:
            logging.warning("{}".format(e))
        except Exception as e:
            logging.warning("{}".format(e))
        return False

