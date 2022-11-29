import mysql.connector as db
import yahooquery as yf
import os
import dotenv

dotenv.load_dotenv()

h = os.getenv("HOST")
u = os.getenv("USER")
p = os.getenv("PASSWORD")
d = os.getenv("DATABASE")

conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
)
c = conn.cursor()

try:
    c.execute('''CREATE TABLE user_portfolios (
        user_id BIGINT NOT NULL PRIMARY KEY,
        ticker_1 VARCHAR,
        ticker_2 VARCHAR,
        ticker_3 VARCHAR,
        ticker_4 VARCHAR,
        ticker_5 VARCHAR
        )''')
    conn.commit()

except db.errors.ProgrammingError:
    pass

def isCompany(company: str) -> bool:
    ticker = yf.Ticker(company)
    try:
        history = ticker.history(period = "ytd", interval = "1d")
        history["close"]
    except:
        return False
    return True

def add_ticker(id: int, company: str):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()

    if isCompany(company):
        try:
            c.execute(f'''INSERT INTO user_portfolios
            (user_id, ticker_1)
            VALUES ({id}, '{company}')
            ''')
            conn.commit()
            c.close()
            conn.close()
            return None
        except db.errors.IntegrityError:
            c.execute(f"SELECT * FROM user_portfolios WHERE user_id = {id}")
            all_tickers = c.fetchone()
            if len(all_tickers) == 5:
                c.close()
                conn.close()
                return 1
            elif company in all_tickers:
                c.close()
                conn.close()
                return 2
            else:
                c.execute(f"UPDATE user_portfolios SET ticker_{len(all_tickers)+1} = '{company}' WHERE user_id = {id}")
                conn.commit()
                c.close()
                conn.close()
                return None
    else:
        c.close()
        conn.close()
        return 0

def remove_ticker(id: int, company: str):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()

    if isCompany(company):
        try:
            c.execute(f"SELECT * FROM user_portfolios WHERE user_id = {id}")
            all_tickers: list = c.fetchone()
            try:
                count = all_tickers.index(company)
            except ValueError:
                c.close()
                conn.close()
                return 1
            c.execute(f"UPDATE user_portfolios SET ticker_{count} = {None} WHERE user_id = {id}")
            conn.commit()
            c.close()
            conn.close()
            return None

        except db.errors.OperationalError:
            return 2
    
    else:
        c.close()
        conn.close()
        return 0

def get_portfolio(id: int):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()

    try:
        c.execute(f"SELECT * FROM user_portfolios WHERE user_id = {id}")
        portfolio = c.fetchone()
        c.close()
        conn.close()
        return portfolio
    
    except db.errors.OperationalError:
        return False

c.close()
conn.close()