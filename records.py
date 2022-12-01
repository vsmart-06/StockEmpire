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
        ticker_1 VARCHAR(10),
        ticker_2 VARCHAR(10),
        ticker_3 VARCHAR(10),
        ticker_4 VARCHAR(10),
        ticker_5 VARCHAR(10)
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
            all_tickers = list(c.fetchone()[1:])
            while True:
                try:
                    all_tickers.remove(None)
                except ValueError:
                    break
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
            all_tickers = list(c.fetchone()[1:])
            while True:
                try:
                    all_tickers.remove(None)
                except ValueError:
                    break
            try:
                count = all_tickers.index(company)
                all_tickers.pop(count)
            except ValueError:
                c.close()
                conn.close()
                return 1
            for x in range(5):
                try:
                    obj = '"'+all_tickers[x]+'"'
                except IndexError:
                    obj = "NULL"
                c.execute(f"UPDATE user_portfolios SET ticker_{x+1} = {obj} WHERE user_id = {id}")
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
        portfolio = list(c.fetchone()[1:])
        while True:
            try:
                portfolio.remove(None)
            except ValueError:
                break
        c.close()
        conn.close()
        return portfolio
    
    except:
        return False

c.close()
conn.close()