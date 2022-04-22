import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path
from fastapi import HTTPException

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)


def get_sanctioned_people():
    try:
        con = psycopg2.connect(
            database=os.getenv("SQL_DATABASE"),
            user=os.getenv("SQL_USER"),
            password=os.getenv("SQL_PASSWORD"),
            host=os.getenv("SQL_HOST"),
            port=os.getenv("SQL_PORT")
        )

        cur = con.cursor()
        cur.execute("SELECT * FROM sanctioned_people")

        rows = cur.fetchall()

        con.close()

        return rows
    except:
        return HTTPException(status_code=500, detail="Error connect to database")
