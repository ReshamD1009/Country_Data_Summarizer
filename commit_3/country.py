from flask import Flask, jsonify, request
import requests
from database import get_db_connection  
import os

app = Flask(__name__) 
API_KEY = os.getenv("API_KEY")

# Function to fetch data from API-Ninjas
# Processes the response and extracts relevant information
def fetch_country_data(country_name):
    try:
        api_url = f"https://api.api-ninjas.com/v1/country?name={country_name}"
        headers = {'X-Api-Key': API_KEY}
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and isinstance(data, list) and len(data) > 0:
            country_data = data[0]
            return {
                'name': country_name, 
                'gdp': country_data.get('gdp'),
                'imports': country_data.get('imports'),
                'tourists': country_data.get('tourists'),
                'surface_area': country_data.get('surface_area'),
                'population': country_data.get('population'),
                'pop_growth': country_data.get('pop_growth'),
                'pop_density': country_data.get('pop_density'),
                'sex_ratio': country_data.get('sex_ratio'),
                'gdp_growth': country_data.get('gdp_growth'),
                'currency': country_data.get('currency', {}).get('name'),
                'exports': country_data.get('exports')
            }
        else:
            print(f"No data found for {country_name}")
            return None
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        raise

# Function to store data in PostgreSQL
# Connects to the PostgreSQL database
# Checks if the country already exists
# If it does, it updates the existing record
# If it doesn't, it inserts a new record
def store_country_data(country_data):
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                # Check if the country already exists
                check_query = "SELECT COUNT(*) FROM country_table_2 WHERE country_name = %s"
                cursor.execute(check_query, (country_data.get('name'),))
                exists = cursor.fetchone()[0]

                if exists:
                    # Update existing record
                    update_query = """
                        UPDATE country_table_2 SET
                        gdp = %s, imports = %s, tourists = %s, surface_area = %s,
                        population = %s, pop_growth = %s, pop_density = %s,
                        sex_ratio = %s, gdp_growth = %s, currency = %s, exports = %s
                        WHERE country_name = %s
                    """
                    cursor.execute(update_query, (
                        country_data.get('gdp'),
                        country_data.get('imports'),
                        country_data.get('tourists'),
                        country_data.get('surface_area'),
                        country_data.get('population'),
                        country_data.get('pop_growth'),
                        country_data.get('pop_density'),
                        country_data.get('sex_ratio'),
                        country_data.get('gdp_growth'),
                        country_data.get('currency'),
                        country_data.get('exports'),
                        country_data.get('name')
                    ))
                else:
                    # Insert new record
                    insert_query = """
                        INSERT INTO country_table_2 
                        (country_name, gdp, imports, tourists, surface_area, population, 
                        pop_growth, pop_density, sex_ratio, gdp_growth, currency, exports)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        country_data.get('name'),
                        country_data.get('gdp'),
                        country_data.get('imports'),
                        country_data.get('tourists'),
                        country_data.get('surface_area'),
                        country_data.get('population'),
                        country_data.get('pop_growth'),
                        country_data.get('pop_density'),
                        country_data.get('sex_ratio'),
                        country_data.get('gdp_growth'),
                        country_data.get('currency'),
                        country_data.get('exports')
                    ))

                connection.commit()
                print(f"Data {'updated' if exists else 'inserted'} successfully for {country_data.get('name')}")
        except Exception as e:
            connection.rollback()
            print(f"Error storing data: {str(e)}")
            raise
        finally:
            connection.close()
    else:
        raise Exception("Failed to connect to the database")

# Route to fetch and store country data
@app.route('/fetch_country/<string:country_name>', methods=['GET'])
def fetch_and_store_country(country_name):
    try:
        country_data = fetch_country_data(country_name)
        if country_data:
            try:
                store_country_data(country_data)
                return jsonify({
                    'message': f"Data for {country_name} fetched and stored successfully.",
                    'data': country_data
                }), 200
            except Exception as store_error:
                print(f"Error storing data: {str(store_error)}")
                return jsonify({
                    'error': f"Data fetched but failed to store: {str(store_error)}"
                }), 500
        else:
            return jsonify({
                'error': f"No data found for {country_name}"
            }), 404
    except Exception as fetch_error:
        print(f"Error fetching data: {str(fetch_error)}")
        return jsonify({
            'error': f"Failed to fetch country data: {str(fetch_error)}"
        }), 500
    

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)


