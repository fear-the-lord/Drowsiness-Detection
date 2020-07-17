from flask import Flask,redirect, url_for,render_template,request
import os
from index import d_dtcn

app = Flask(__name__)
# Defining the home page of our site
@app.route("/",methods=['GET', 'POST'])
def home():
    print(request.method)
    if request.method == 'POST':
        if request.form.get('Continue') == 'Continue':
           return render_template("test1.html")
    else:
        # pass # unknown
        return render_template("index.html")

@app.route("/start", methods=['GET', 'POST'])
def index():
    print(request.method)
    if request.method == 'POST':
        if request.form.get('Start') == 'Start':
            # pass
            d_dtcn()
            return render_template(url_for('templates', filename = "index.html"))
    else:
        # pass # unknown
        return render_template(url_for('templates', filename = "index.html"))

@app.route('/contact', methods=['GET', 'POST'])
def cool_form():
    if request.method == 'POST':
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('contact.html')

if __name__ == "__main__":
    app.run()
    
