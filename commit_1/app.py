from flask import Flask, jsonify
import psycopg2
import requests
from groq import Groq

# Initialize Flask app
app = Flask(__name__)

# Database connection parameters
DB_NAME = "country_db"
DB_USER = "postgres"
DB_PASS = "Resham@1009"
DB_HOST = "localhost"
DB_PORT = "5432"

# API Ninja API Key (provided by user)
API_KEY = "QRcS8mMo2+PAmjj0mNAhWQ==N6CfqoAQQ9IAxmLj"

# Groq API Key
GROQ_API_KEY = "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"

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Function to fetch country data from API Ninjas
def fetch_country_data(country_name):
    try:
        api_url = f"https://api.api-ninjas.com/v1/country?name={country_name}"
        headers = {'X-Api-Key': API_KEY}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print(data, "hi")
            if data:
                country_data = {
                    'country_name': data[0]['name'],
                    'gdp': data[0].get('gdp', 0),
                    'imports': data[0]['imports'],
                    'tourists': data[0].get('tourists', 0),
                    'surface_area': data[0].get('surface_area', 0)
                }
                return country_data
            else:
                print("No data found for the country.")
                return None
        else:
            print(f"Error fetching data: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Function to store data in PostgreSQL
def store_country_data(country_data):
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO country_table (country_name, gdp, imports, tourists, surface_area)
            VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (
            country_data['country_name'],
            country_data['gdp'],
            country_data['imports'],
            country_data['tourists'],
            country_data['surface_area']
        ))
        connection.commit()
        print("Data stored successfully")
    except Exception as error:
        print("Error while storing data:", error)

# Function to fetch country summary
def generate_summary(data):
    prompt = f"I am going to provide you with details about a country. Based on the information I give you, please generate a summary that includes key aspects such as country name, gdp, imports, and any other important features. Here are the details: {data}."
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Correctly access the summary from the response
        summary = completion.choices[0].message.content 
        return summary


    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Unable to generate summary"

# Route to fetch and store country data
@app.route('/fetch_country/<string:country_name>', methods=['GET'])
def fetch_and_store_country(country_name):
    country_table = fetch_country_data(country_name)
    if country_table:
        store_country_data(country_table)
        return jsonify({'message': f"Data for {country_name} fetched and stored successfully.", 'data': country_table}), 200
    else:
        return jsonify({'error': 'Failed to fetch country data'}), 500




# Route to generate summary based on country data
@app.route('/generate_summary/<string:country_name>', methods=['GET'])
def generate_summary_route(country_name):
    try:
        connection = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = connection.cursor()

        query = f"SELECT country_name, gdp, imports, tourists, surface_area FROM country_table WHERE country_name = '{country_name}';"
        cursor.execute(query)
        rows = cursor.fetchall()

        # Prepare data for summarization
        summary_data = []
        for row in rows:
            country_data = {
                'country_name': row[0],
                'gdp': row[1],
                'imports': row[2],
                'tourists': row[3],
                'surface_area': row[4]
            }
            summary_data.append(country_data)

        cursor.close()
        connection.close()

        if summary_data:
            summary = generate_summary(summary_data)
            return jsonify({'summary': summary}), 200
        else:
            return jsonify({'message': 'No data available for summarization.'}), 404

    except Exception as error:
        print("Error while generating summary:", error)
        return jsonify({'error': 'Unable to generate summary'}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)









































