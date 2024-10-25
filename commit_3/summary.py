from flask import Flask, jsonify, request
from groq import Groq
from database import get_db_connection
from prompts import get_population_density_prompt, get_trade_prompt, get_import_export_prompt, get_general_prompt
import os
# Initialize Groq client
app = Flask(__name__) 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)


# Function to fetch country summary
# Retrieves country data from the database and generates summary using Groq API
# Determines the type of summary to generate (all, population_density, trade, import_export, or general)
def generate_summary(data):
    prompt = f"I am going to provide you with details about a country. Based on the information I give you, please generate a summary that includes key aspects such as country name, gdp, imports, exports, population, and any other important features. Here are the details: {data}."
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


# Route to generate summary based on country data
@app.route('/generate_summary/<string:country_name>', methods=['GET'])
def generate_summary_route(country_name, summary_type='all'):
    if not country_name:
        return jsonify({'error': 'Country name is required'}), 400

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()

        query = """
            SELECT country_name, gdp, imports, tourists, surface_area, 
                   population, pop_growth, pop_density, sex_ratio, 
                   gdp_growth, currency, exports 
            FROM country_table_2
            WHERE country_name = %s;
        """
        cursor.execute(query, (country_name,))
        rows = cursor.fetchall()

        if rows:
            country_data = {
                'country_name': rows[0][0],
                'gdp': rows[0][1],
                'imports': rows[0][2],
                'tourists': rows[0][3],
                'surface_area': rows[0][4],
                'population': rows[0][5],
                'pop_growth': rows[0][6],
                'pop_density': rows[0][7],
                'sex_ratio': rows[0][8],
                'gdp_growth': rows[0][9],
                'currency': rows[0][10],
                'exports': rows[0][11]
            }

            summaries = {}
            parameters = ['population_density', 'trade', 'import_export', 'general']

            if summary_type == 'all':
                for parameter in parameters:
                    summaries[parameter] = generate_specific_summary(country_data, parameter)
                return jsonify(summaries), 200
            elif summary_type in parameters:
                summary = generate_specific_summary(country_data, summary_type)
                return jsonify({summary_type: summary}), 200
            else:
                return jsonify({'error': 'Invalid summary type'}), 400
        else:
            return jsonify({'message': 'No data available for the specified country.'}), 404
    else:
        return jsonify({'error': 'Database connection error'}), 500


def generate_specific_summary(country_data, summary_type):
    if summary_type == 'population_density':
        prompt = get_population_density_prompt(country_data)
    elif summary_type == 'trade':
        prompt = get_trade_prompt(country_data)
    elif summary_type == 'import_export':
        prompt = get_import_export_prompt(country_data)
    else:  # general summary
        prompt = get_general_prompt(country_data)

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        summary = completion.choices[0].message.content
        return summary

    except Exception as e:
        print(f"Error during summarization: {e}")
        return f"Unable to generate {summary_type} summary"

if __name__ == '__main__':
    app.run(debug=True)
    
