from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)
riskEndpoint = os.environ['RISK_SRV_ENDPOINT']
print(riskEndpoint)

@app.route("/")
def index():
    return render_template('content.html')

@app.route("/data", methods=['POST'])
def data():
    sym = request.form['sym']
    print(sym)
    riskData = requests.get(f'{riskEndpoint}/?sym={sym}')
    #regData = requests.post('service-name', data = { 'sym': sym })
    
    return f"<img src='data:image/png;base64,{riskData}'/>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
