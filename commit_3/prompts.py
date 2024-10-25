def get_population_density_prompt(country_data):
    prompt = """
    Provide a detailed analysis of the population for {country_name}. 
    The population is {population}. 
    The population density is {pop_density} people per square kilometer. 
    The sex ratio is {sex_ratio}. 
    
    """.format(**country_data)
    return prompt

def get_trade_prompt(country_data):
    prompt = """
    Generate a summary for the tourism sector in {country_name}.
    The country has welcomed {tourists} tourists. Analyze how tourism impacts the GDP, which is {gdp}, and how it contributes to the country's economy.
    Include any known challenges or growth trends in the tourism sector of {country_name}. Only provide the details of the data that are mentioned as parameters.
    """.format(**country_data)
    return prompt

def get_import_export_prompt(country_data):
    prompt = """
    Summarize the import-export data for {country_name}.
    The country imports goods worth {imports} and exports goods worth {exports}. Discuss the trade balance and how it affects the economic stability of {country_name}.
    Include information on the GDP growth rate, which is {gdp_growth}%, and how it relates to the country's trade activities.
    """.format(**country_data)
    return prompt

def get_general_prompt(country_data):
    prompt = """
    Population: {population}
    GDP: {gdp}
    GDP Growth: {gdp_growth}%
    Imports: {imports}
    Exports: {exports}
    Tourists: {tourists}
    Surface Area: {surface_area} sq km
    Population Growth: {pop_growth}%
    Population Density: {pop_density} people per sq km
    Sex Ratio: {sex_ratio}
    Currency: {currency}
    """.format(**country_data)
    return prompt
