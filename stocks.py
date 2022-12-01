import yahooquery as yf
import matplotlib.pyplot as plt
import math
import datetime as dt

def stocks(username: str, company: str, duration: str = "1 day"):
    if duration == "1 day":
        duration = "1d"
        interval = "2m"
        sfactor = 2/247.58
    elif duration == "5 days":
        duration = "5d"
        interval = "15m"
        sfactor = 7/247.58
    elif duration == "1 month":
        duration = "1mo"
        interval = "90m"
        sfactor = 25/247.58
    elif duration == "6 months":
        duration = "6mo"
        interval = "1d"
        sfactor = 60/247.58
    elif duration == "Year to Date":
        duration = "ytd"
        interval = "1wk"
        sfactor = 150/247.58
    elif duration == "1 year":
        duration = "1y"
        interval = "1wk"
        sfactor = 150/247.58
    elif duration == "5 years":
        duration = "5y"
        interval = "1mo"
        sfactor = 400/247.58
    elif duration == "Max":
        duration = "max"
        interval = "1mo"
        sfactor = 800/247.58

    ticker = yf.Ticker(company)

    try:
        history = ticker.history(period = duration, interval = interval)
        closingValues: list = history["close"].to_numpy().tolist()
        openingValues: list = history["open"].to_numpy().tolist()
        closingValues = [x for x in closingValues if x == x]
        openingValues = [x for x in openingValues if x == x]
        summary = ticker.summary_detail

        if duration == "5d":
            year, month, day = map(int, str(list(history.to_dict()["close"].keys())[0][1]).split(" ")[0].split("-"))
            date = dt.datetime(year, month, day)
            new_date = date-dt.timedelta(1)

            new_history = ticker.history(start = new_date, end = date, period = "1d", interval = "2m")
            lastMarkClose = new_history["close"].to_numpy().tolist()[-2]


    except:
        return None
    
    times = []
    time = 0
    for x in range(len(closingValues)):
        times.append(time)
        if interval == "2m":
            time += 2
        elif interval == "15m":
            time += 15
        elif interval == "90m":
            time += 90
        elif interval == "1d":
            time += 24*60
        elif interval == "1wk":
            time += 7*24*60
        elif interval == "1mo":
            time += 30*24*60

    if duration == "1d":
        if closingValues[-1] >= summary[company]["previousClose"]:
            color = "green"
        else:
            color = "red"
    
    elif duration == "5d":
        if closingValues[-1] >= lastMarkClose:
            color = "green"
        else:
            color = "red"

    else:
        if closingValues[-1] >= openingValues[0]:
            color = "green"
        else:
            color = "red"
    
    if duration == "1d":
        big_duration = "for 1 day"

        data = {"name": ticker.price[company]['shortName'], "duration": big_duration, "Last Price": "**"+str(round(closingValues[-1], 2))+"**", "Change": "**"+str(round(round(closingValues[-1], 2)-summary[company]["previousClose"], 2))+"**", "Percentage Change": f'**{round(100*(round(closingValues[-1], 2)-summary[company]["previousClose"])/summary[company]["previousClose"], 2)}%**', "Previous Close": summary[company]["previousClose"], "Open": summary[company]["open"], "Bid": f"{summary[company]['bid']} x {summary[company]['bidSize']}", "Ask": f"{summary[company]['ask']} x {summary[company]['askSize']}", "Day's Range": f"{summary[company]['dayLow']} - {summary[company]['dayHigh']}", "Volume": summary[company]["volume"], "Average Volume": summary[company]["averageVolume"], "Market Cap": f'{round((summary[company]["marketCap"])/10**(len(str(summary[company]["marketCap"]))-1), 3)} x 10^{len(str(summary[company]["marketCap"]))-1}'}

    elif duration == "5d":
        big_duration = "for 5 days"

        data = {"name": ticker.price[company]['shortName'], "duration": big_duration, "Last Price": "**"+str(round(closingValues[-1], 2))+"**", "Change": "**"+str(round(round(closingValues[-1], 2)-round(lastMarkClose, 2), 2))+"**", "Percentage Change": f'**{round(100*(round(round(closingValues[-1], 2)-round(lastMarkClose, 2), 2))/round(lastMarkClose, 2), 2)}%**'}

    elif duration == "1mo":
        big_duration = "for 1 month"

        data = {"name": ticker.price[company]['shortName'], "duration": big_duration, "Last Price": "**"+str(round(closingValues[-1], 2))+"**", "Change": "**"+str(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))+"**", "Percentage Change": f'**{round(100*(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))/round(openingValues[0], 2), 2)}%**'}

    elif duration == "6mo":
        big_duration = "for 6 months"

        data = {"name": ticker.price[company]['shortName'], "duration": big_duration, "Last Price": "**"+str(round(closingValues[-1], 2))+"**", "Change": "**"+str(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))+"**", "Percentage Change": f'**{round(100*(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))/round(openingValues[0], 2), 2)}%**'}

    elif duration == "ytd":
        big_duration = "for Year to Date"

        data = {"name": ticker.price[company]['shortName'], "duration": big_duration, "Last Price": "**"+str(round(closingValues[-1], 2))+"**", "Change": "**"+str(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))+"**", "Percentage Change": f'**{round(100*(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))/round(openingValues[0], 2), 2)}%**'}

    elif duration == "1y":
        big_duration = "for 1 year"

        data = {"name": ticker.price[company]['shortName'], "duration": big_duration, "Last Price": "**"+str(round(closingValues[-1], 2))+"**", "Change": "**"+str(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))+"**", "Percentage Change": f'**{round(100*(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))/round(openingValues[0], 2), 2)}%**'}

    elif duration == "5y":
        big_duration = "for 5 years"

        data = {"name": ticker.price[company]['shortName'], "duration": big_duration, "Last Price": "**"+str(round(closingValues[-1], 2))+"**", "Change": "**"+str(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))+"**", "Percentage Change": f'**{round(100*(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))/round(openingValues[0], 2), 2)}%**'}

    elif duration == "max":
        big_duration = "(max)"

        data = {"name": ticker.price[company]['shortName'], "duration": big_duration, "Last Price": "**"+str(round(closingValues[-1], 2))+"**", "Change": "**"+str(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))+"**", "Percentage Change": f'**{round(100*(round(round(closingValues[-1], 2)-round(openingValues[0], 2), 2))/round(openingValues[0], 2), 2)}%**'}

    plt.plot(times, closingValues, color = color)
    plt.fill_between(times, closingValues, color = color)
    plt.ylim(max(math.floor(min(closingValues))-int(sfactor*max(closingValues)), 0), math.ceil(max(closingValues))+min(sfactor*max(closingValues), 150))
    plt.title(f"Status of {ticker.price[company]['shortName']}'s shares {big_duration}")
    plt.ylabel("Share price")
    plt.xlabel("Time")
    plt.tick_params(labelbottom = False)
    plt.savefig(f"shares_{username}_{company}.png")
    plt.close()
    return data

def getTrending():
    trending = yf.get_trending()
    symbols = []
    for x in trending["quotes"]:
        symbols.append(x["symbol"])
    return symbols

def getWinners(num: int) -> list:
    screener = yf.Screener().get_screeners(["day_gainers"], num)
    gainers = screener["day_gainers"]["quotes"]
    symbols = []
    for x in gainers:
        symbols.append(x["symbol"])
    return symbols

def getLosers(num: int) -> list:
    screener = yf.Screener().get_screeners(["day_losers"], num)
    losers = screener["day_losers"]["quotes"]
    symbols = []
    for x in losers:
        symbols.append(x["symbol"])
    return symbols
    

def getCrypto(num: int) -> list:
    screener = yf.Screener().get_screeners(["all_cryptocurrencies_us"], num)
    crypto = screener["all_cryptocurrencies_us"]["quotes"]
    symbols = []
    for x in crypto:
        symbols.append(x["symbol"])
    return symbols