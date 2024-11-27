# import necessary packages
import flask

# create the flask app
app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def index():
   return 'Success!'

# run the app
app.run()