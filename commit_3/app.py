from flask import Flask, request
from summary import generate_summary_route
from country import fetch_and_store_country

# Initialize Flask app
app = Flask(__name__)

@app.route('/fetch_country/<string:country_name>', methods=['GET'])
def fetch_country(country_name):
    return fetch_and_store_country(country_name)

@app.route('/generate_summary/<string:country_name>', methods=['GET'])
def summary(country_name):
    summary_type = request.args.get('type', 'all')
    return generate_summary_route(country_name, summary_type)

if __name__ == '__main__':
    app.run(debug=True)



























































