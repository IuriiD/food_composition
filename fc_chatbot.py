#!/usr/bin/venv python

import urllib
import json
import os
from flask import Flask
from flask import request
from flask import make_response

nutrionix_app_id = '2afa5e8d' # App ID
nutrionix_app_key = '70ac89bcc5e869c98cd1eaa6dec5573e' # App key

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") != "foodcomposition":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    foodlabel = parameters.get("food")

    myoutput = nutrionix_requests(foodlabel)['average_percents']
    #cost = {'Andhra Bank':'6.85%', 'Allahabad Bank':'6.75%', 'Axis Bank':'6.5%', 'Bandhan bank':'7.15%', 'Bank of Maharashtra':'6.50%', 'Bank of Baroda':'6.90%', 'Bank of India':'6.60%', 'Bharatiya Mahila Bank':'7.00%', 'Canara Bank':'6.50%', 'Central Bank of India':'6.60%', 'City Union Bank':'7.10%', 'Corporation Bank':'6.75%', 'Citi Bank':'5.25%', 'DBS Bank':'6.30%', 'Dena Bank':'6.80%', 'Deutsche Bank':'6.00%', 'Dhanalakshmi Bank':'6.60%', 'DHFL Bank':'7.75%', 'Federal Bank':'6.70%', 'HDFC Bank':'5.75% to 6.75%', 'Post Office':'7.10%', 'Indian Overseas Bank':'6.75%', 'ICICI Bank':'6.25% to 6.9%', 'IDBI Bank':'6.65%', 'Indian Bank':'4.75%', 'Indusind Bank':'6.85%', 'J&K Bank':'6.75%', 'Karnataka Bank':'6.50 to 6.90%', 'Karur Vysya Bank':'6.75%', 'Kotak Mahindra Bank':'6.6%', 'Lakshmi Vilas Bank':'7.00%', 'Nainital Bank':'7.90%', 'Oriental Bank of Commerce':'6.85%', 'Punjab National Bank':'6.75%', 'Punjab and Sind Bank':'6.4% to 6.80%', 'Saraswat bank':'6.8%', 'South Indian Bank':'6% to 6.75%', 'State Bank of India':'6.75%', 'Syndicate Bank':'6.50%', 'Tamilnad Mercantile Bank Ltd':'6.90%', 'UCO bank':'6.75%', 'United Bank Of India':'6%', 'Vijaya Bank':'6.50%', 'Yes Bank':'7.10%'}

    herewego = "Fats: {}, carbohydrates: {}, proteins: {}".format(myoutput[0], myoutput[1], myoutput[2])
    print("Response:")
    print(herewego)

    return {
        "speech": herewego,
        "displayText": herewego,
        #"data": {},
        #"contextOut": [],
        "source": "FoodComposition"
    }

################### Nutrionix ###################
def nutrionix_requests(label_list):
    ''' Function takes a list of products' labels got using Google Vision API or a label submitted by user and for [products_n] products (in case of user's label products_n=1)
        from this list tries to find foods in Nutrionix DB.
        For each food product (for eg., 'sausage') [how_many_terms] quantity of items are requested (for eg., items 'Sausage, Peppers and Onions - 1 serving', 'Sausage - 2, links' for a term 'sausage)
        For each food item (for eg., 'Sausage - 2, links') id, name, [relevance] score and abs. quantity (in grams) of fats, carbohydrates and proteins per serving is requested
        Then percentages of fats, carbohydrates and proteins in each food item are calculated and their average values in all food items analysed.
        Returns a dictionary with 3 percentages (for fats, carbohydrates and proteins) and also containing all 'raw' data (food labels, products names, products IDs, fat/carb/prot percent) -
        see structure of 'main_output' dictionary
    '''

    # Structure of the dictionary ('main_output') with data from Nutrionix (example) which is used to calculate final average percentages of fats, carbohydrates and proteins
    '''
    main_output = {
                    'sausage':  [
                                    ['5678284a770861aa38abc48f', 'Sausage, Peppers and Onions - 1 serving', 54.338682037700586, 11.559432933478735, 34.10188502882069],
                                    ['571e5413153244e3606d2b1b', 'Sausage - 2 links', 57.76140027637033, 2.9940119760479043, 39.24458774758176]
                                ],
                    'italian sausage':  
                                [
                                    ['57603ccc65a4e69d77ea3fda', 'Italian Sausage - 1 link', 53.866386112572336, 8.416622830089427, 37.71699105733825],
                                    ['513fceb475b8dbbc21000d27', 'Italian Sausage - 1 link, 5/lb', 53.87106270238446, 8.419193405946423, 37.70974389166912]
                                ]
    }
    '''

    print('################ Nutrionix ################')
    main_output = {}
    products_n = session['products_n']
    for n in range(products_n):
        # Get IDs for items for each product
        # Request 'hits' (foods) list
        n1 = requests.get('https://api.nutritionix.com/v1_1/search/' + label_list[n] + '?results=0%3A' + str(how_many_terms) + '&cal_min=0&cal_max=50000&fields=item_name%2Cbrand_name%2Citem_id%2Cbrand_id&appId=' + nutrionix_app_id + '&appKey=' + nutrionix_app_key)
        ids = json.loads(n1.text)
        #print(ids)

        # Get foods id, name, [relevance] score
        #total_hits = ids['total_hits']
        hits = ids['hits']
        sub_output = []  # data for specific food item ID, [id, name, id_score, fats%, carbohydrates%, proteins%]
        for hit in hits:
            #print(('%s: %s') % ('Hit', hit))
            id = ''
            name = ''
            id_score = 0
            id = hit['fields']['item_id']
            name = hit['fields']['item_name']
            id_score = hit['_score']
            #print(('%s - %s - %s') % (id, name, id_score))
            #flash('<a href="https://www.nutritionix.com/food/' + name + '">' + name + '</a>', 'alert alert-warning alert-dismissible fade show')

            # For each food ID request nutrition data (fats, carbohydrates and proteins content in grams)
            n2 = requests.get('https://api.nutritionix.com/v1_1/item?id=' + str(id) + '&appId=' + nutrionix_app_id + '&appKey=' + nutrionix_app_key)
            nutr_data = json.loads(n2.text)

            fat_g, carbo_g, protein_g = 0, 0, 0
            fat_g = nutr_data['nf_total_fat']
            carbo_g = nutr_data['nf_total_carbohydrate']
            protein_g = nutr_data['nf_protein']
            #print(('%s - %s - %s') % (fat_g, carbo_g, protein_g))

            # Calculate percentage content of fats, carbohydrates and proteins
            sum_g = fat_g + carbo_g + protein_g
            if sum_g == 0:
                sum_g = 1

            fat_perc, carbo_perc, protein_perc = 0, 0, 0
            fat_perc = fat_g * 100 / sum_g
            carbo_perc = carbo_g * 100 / sum_g
            protein_perc = protein_g * 100 / sum_g

            # Load data to list
            sub_output.append([id, name, id_score, fat_perc, carbo_perc, protein_perc])
            #print(sub_output)

        # Load lists of lists with data for each food item id into final dictionary with food terms
        main_output[label_list[n]] = sub_output
        #print(main_output)

    # Calculate average nutrienst percent across all food items for all terms in our main_output dictionary (for eg., if we requested 3 terms [with 3 items for each one], then
    # average will be calculated for 3 * 3 = 9 values for each nutrient
    fat_sum, carbo_sum, prot_sum = 0, 0, 0
    for key, value in main_output.items():
        #print('')
        #print('Here!')
        #print(key)
        #print(value)
        items_per_term = len(value)
        for item in value:
            #print(item)
            #print(('%s %s') % ('Fats: ', item[3]))
            fat_sum = fat_sum + item[3]
            #print(('%s %s') % ('Carbohydrates: ', item[4]))
            carbo_sum = carbo_sum + item[4]
            #print(('%s %s') % ('Proteins: ', item[5]))
            prot_sum = prot_sum + item[5]

    #print(('%s - %s') % (products_n, how_many_terms))

    divider = how_many_terms * products_n
    #print('Divider: ' + str(divider))
    #print(fat_sum, carbo_sum, prot_sum)

    av_fat, av_carbo, av_prot = 0, 0, 0

    av_fat = fat_sum / divider
    av_carbo = carbo_sum / divider
    av_prot = prot_sum / divider

    print('Fats %: ', av_fat)
    print('Carbohydrates %: ', av_carbo)
    print('Proteins %: ', av_prot)

    main_output['average_percents'] = [round(av_fat, 2), round(av_carbo, 2), round(av_prot, 2)]

    return(main_output)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 80))
    print ("Starting app on port %d" %(port))
    app.run(debug=True, port=port, host='0.0.0.0')