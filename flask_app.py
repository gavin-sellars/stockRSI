from flask import Flask, render_template, make_response, request


from processing import RSICalculation

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/", methods=["GET", "POST"])
def getTickers():
    if request.method == "POST":


        input_file = request.files["input_file"]
        rsi_qty = request.form.get("rsi_qty")
        input_data = input_file.stream.read().decode("utf-8")

        return render_template("result.html", output_data = RSICalculation(input_data, rsi_qty))

    return '''
        <html>
            <body>

                <p>Select the file containing your tickers:</p>
                <form method="post" action="." enctype="multipart/form-data">
                    <p><input type="file" name="input_file" /></p>
                    <p><input type="text" name="rsi_qty" /></p>
                    <p><input type="submit" value="Process the file" /></p>
                </form>
            </body>
        </html>
    '''
