from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/getInput', methods=['POST', 'GET'])
def request_prediction():
    multidict = request.form

    strdt = multidict['dateTime']
    strgc = multidict['garageCode']

    print("received from web:")
    # print(multidict)
    print(strdt)
    print(strgc)

    try:
        pred = {'date': strdt,
                'vehicleCount': [1],
                'totalSpaces': [1],
                'garageCode': strgc}

        nnresult = str(pnn.predict(pred))
        return render_template('result.html', predictionResult=nnresult)

    except Exception as e:
        print(e)
        return render_template('result.html', predictionResult="unexpected exception occurred in model")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # start flask

