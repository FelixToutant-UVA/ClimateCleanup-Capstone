from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    # Home (splash) page with scroll down to the landing section
    return render_template("index.html")

@app.route("/food_forests")
def food_forests():
    return render_template("food_forests.html")

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

@app.route("/articles")
def articles():
    return render_template("articles.html")

if __name__ == "__main__":
    app.run(debug=True)
