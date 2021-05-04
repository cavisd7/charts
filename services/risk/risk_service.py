import math
from datetime import datetime
import numpy as np
from flask import Flask, request
from matplotlib.figure import Figure
import base64
from io import BytesIO
import matplotlib.dates as mdates
import matplotlib.ticker as tick
import yfinance as yf

app = Flask(__name__)

def smav2(data, window):
    res = []
    s = 0

    for i, day in enumerate(data):
        s += day
        if i < window - 1:
            res.append(math.nan)
        elif i + 1 == window:
            ma = s / window
            res.append(ma)
        else:
            s -= data[i - window]
            ma = s / window
            res.append(ma)
    
    return res

def normalize(val, minVal, maxVal, newMin, newMax):
    return newMin + (val - minVal) * (newMax - newMin) / (maxVal - minVal)

@app.route('/', methods=['GET'])
def risk():
    sym = request.args.get('sym')
    ticker = request.args.get('sym') + '-USD'
    coin = yf.Ticker(ticker)
    data = coin.history(period="max")

    close_prices = [c for c in data['Close']]
    dates = [d.to_pydatetime() for d in data.index]

    risk = []
    for i in range(len(dates)):
        sma50 = smav2(close_prices, 50)
        sma350 = smav2(close_prices, 350)
        risk.append(sma50[i] / sma350[i])

    minR = np.nanmin(risk)
    maxR = np.nanmax(risk)

    normalized_risk = []
    for r in risk:
        normalized_risk.append(normalize(r, minR, maxR, 0, 1))

    # Chart
    fig     = Figure()
    ax1     = fig.subplots()
    yLabel  = sym + '/USD'
    
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
    ax1.set_yscale('log')
    ax1.set_ylabel(yLabel, color="black")
    ax1.plot(dates, close_prices, color="black")

    ax2 = ax1.twinx()
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
    ax2.yaxis.set_ticks(np.arange(0, 1.1, 0.1))
    ax2.yaxis.set_major_formatter(tick.FormatStrFormatter('%0.1f'))
    ax2.yaxis.grid(linestyle="dashed")
    ax2.set_ylabel('RISK', color="red")
    ax2.plot(dates, normalized_risk, color="red")
    ax2.tick_params(axis='y', labelcolor="red")

    for i in range(10):
        if i == 3:
            # Grey Zone
            ax2.axhspan(i / 10, (i / 10) + 0.1, facecolor ='grey', alpha = 0.7)
        elif i < 3:
            # Buy Zone 
            ax2.axhspan(i / 10, (i / 10) + 0.1, facecolor ='green', alpha = (i / 10) + 0.3)
        elif i > 3:
            # Sell Zone
            ax2.axhspan(i / 10, (i / 10) + 0.1, facecolor ='red', alpha = 1 - (i / 10))

    buffer = BytesIO()
    fig.savefig(buffer, format = 'png')
    data = base64.b64encode(buffer.getbuffer()).decode('ascii')
    
    return data
    #return f"<img src='data:image/png;base64,{data}'/>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
