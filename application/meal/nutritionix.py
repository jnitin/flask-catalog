import json
import requests
from flask import current_app


def get_calories_from_nutritionix(description):
    """Get the calories from nutritionix, based on a description.

    Usage:
     get_calories_from_nutritionix('Potatoes, a Veggie Patty and a Milk')


    Returns:
        number of calories if correctly found the calories of the meal
        0 if it failed

    """
    app_id = current_app.config['NUTRINIONIX_APP_ID']
    app_key = current_app.config['NUTRINIONIX_APP_KEY']

    url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
    headers = {
        'Content-Type': 'application/json',
        'x-app-id': '{}'.format(app_id),
        'x-app-key': '{}'.format(app_key),
        'Accept': 'application/vnd.api+json'
        }
    payload = {
        "query": description
    }

    calories = 0
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        r_json = json.loads(r.text)
        foods = r_json['foods']
        for food in foods:
            calories += food['nf_calories']

    return calories
