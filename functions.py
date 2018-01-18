# To read next & just links
# https://cloud.google.com/vision/docs/internet-detection
# https://github.com/andresgarcia29/Python-Google-Vision-Api/blob/master/vision.py
# https://developers.google.com/knowledge-graph/reference/rest/v1/

import io
import requests
import json
import mimetypes
from flask import session, flash
from google.cloud import vision
from google.cloud.vision import types

# Nutrionix API credentials
from keys import nutrionix_app_id, nutrionix_app_key

# Analysis parameters
from parameters import products_n, how_many_terms

VALID_IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    "bmp"
]

VALID_IMAGE_MIMETYPES = [
    "image"
]

################ Image URL validation ################
# Validating the URL’s extension
def valid_url_extension(url, extension_list=VALID_IMAGE_EXTENSIONS):
    '''
    A simple method to make sure the URL the user has supplied has
    an image-like file at the tail of the path
    '''
    return any([url.endswith(e) for e in extension_list])

# Validating the URL mimetype
def valid_url_mimetype(url, mimetype_list=VALID_IMAGE_MIMETYPES):
    # http://stackoverflow.com/a/10543969/396300
    mimetype, encoding = mimetypes.guess_type(url)
    if mimetype:
        return any([mimetype.startswith(m) for m in mimetype_list])
    else:
        return False

# Validating that the image exists on the server
def image_exists(url):
    try:
        r = requests.get(url)
    except:
        return False
    return r.status_code == 200

################ Google Vision ################
def google_vision(image_path):
    ''' Function takes an image (link to file on server, GC or on the web) and
     returns labels for it using Google Vision API '''

    label_list = [] # output list with terms got from GV (for eg., ['spaghetti', 'al dente', ...]
    vision_client = vision.ImageAnnotatorClient()

    if image_path.startswith('http') or image_path.startswith('gs:'):
        image = types.Image()
        image.source.image_uri = image_path

    else:
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)

    response = vision_client.label_detection(image=image)

    labels = response.label_annotations

    label_list = []
    print('################ Google Vision ################')
    print(response)
    print(response.error)
    print(response.error.message)

    for label in labels:
        label_list.append(label.description)
        print(label.description, label.score)
    return label_list


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

#print(nutrionix_requests(google_vision('static/uploads/pasta.jpg')))

''' Alternative variants of request to Nutrionix (in order to get more relevant results)
    (from https://developer.nutritionix.com/docs/v1_1):

# Variant 1

myquery1 = {
  "appId": nutrionix_app_id,
  "appKey":nutrionix_app_key,  
  "fields":['item_name', 'item_id', 'nf_total_fat', 'nf_total_carbohydrate', 'nf_protein'],
  "limit": 3,
  "sort":{
    "field":"_score", # sort by relevance
    "order":"desc"
  },
  "min_score": 0.5,
  "query": "sausage",
  "filters":{
    "item_type":3 # USDA products
  }
}

n3 = requests.post('https://api.nutritionix.com/v1_1/search', data = myquery1)

# Variant 2: Nutritionix Search: You can use the default search where we apply boosting, and multi search factors to yield the most relevant results to your users.

myquery2 = {
  "appId": nutrionix_app_id,
  "appKey": nutrionix_app_key,
  "query":"sausage"
}

n3 = requests.post('https://api.nutritionix.com/v1_1/search', data = myquery2)
'''