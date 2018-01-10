# https://cloud.google.com/vision/docs/internet-detection
# https://github.com/andresgarcia29/Python-Google-Vision-Api/blob/master/vision.py
# https://developers.google.com/knowledge-graph/reference/rest/v1/

import io
import requests, json
from google.cloud import vision
from google.cloud.vision import types

vision_client = vision.ImageAnnotatorClient()
file_name = 'static/uploads/sausage.jpg'

with io.open(file_name,'rb') as image_file:
    content = image_file.read()

image = types.Image(content=content)

response = vision_client.label_detection(image=image)
labels = response.label_annotations

label_list = []
print('################ Google Vision ################')
for label in labels:
    label_list.append(label.description)
    print(label.description, label.score)

# Nutrionix (protein - carbohydrate - fat)
    # sausage - 23 - 2 - 75
    # italian sausage - 22 - 5 - 71
    # mettwurst - 16 - 4 - 80

# Nutrionix App ID
nutrionix_app_id = '2afa5e8d'

# Nutrionix App Key
nutrionix_app_key = '70ac89bcc5e869c98cd1eaa6dec5573e'

# Get food ID
products_n = 1
n1 = requests.get('https://api.nutritionix.com/v1_1/search/' + label_list[0] + '?results=0%3A' + str(products_n) + '&cal_min=0&cal_max=50000&fields=item_name%2Cbrand_name%2Citem_id%2Cbrand_id&appId=' + nutrionix_app_id + '&appKey=' + nutrionix_app_key)
data1 = json.loads(n1.text)

print('################ Nutrionix ################')
print('data1: ', data1)

id = data1['hits'][0]['fields']['item_id']
print('id: ', id)

n2 = requests.get('https://api.nutritionix.com/v1_1/item?id=' + str(id) + '&appId=' + nutrionix_app_id + '&appKey=' + nutrionix_app_key)
data2 = json.loads(n2.text)

print('data2: ', data2)

fat_g = data2['nf_total_fat']
carbo_g = data2['nf_total_carbohydrate']
protein_g = data2['nf_protein']

sum_g = fat_g + carbo_g + protein_g

fat_perc = fat_g * 100 / sum_g
carbo_perc = carbo_g * 100 / sum_g
protein_perc = protein_g * 100 / sum_g

print('Fats, g (%): ' + str(fat_g) + ' (' + str(fat_perc) + ')')
print('Carbohydrates, g (%): ' + str(carbo_g) + ' (' + str(carbo_perc) + ')')
print('Proteins, g (%): ' + str(protein_g) + ' (' + str(protein_perc) + ')')
print(fat_perc + carbo_perc + protein_perc)

'''
hello = {
 "item_id": "5678284a770861aa38abc48f",
 "item_name": "Sausage, Peppers and Onions - 1 serving",
 "brand_id": "546a4142413b47f7107aed0c",
 "brand_name": "Nutritionix",
 "updated_at": "2015-12-21T16:26:50.000Z",
 "nf_calories": 435.42,
 "nf_calories_from_fat": 313.94,
 "nf_total_fat": 34.88,
 "nf_saturated_fat": 12.47,
 "nf_trans_fatty_acid": 0.29,
 "nf_polyunsaturated_fat": 5.98,
 "nf_monounsaturated_fat": 14.09,
 "nf_cholesterol": 107.69,
 "nf_sodium": 956.88,
 "nf_total_carbohydrate": 7.42,
 "nf_dietary_fiber": 1.39,
 "nf_sugars": 3.84,
 "nf_protein": 21.89,
 "nf_vitamin_a_dv": 19,
 "nf_vitamin_c_dv": 73,
 "nf_calcium_dv": 3,
 "nf_iron_dv": 10
}

print(hello['nf_total_fat'])

'''
'''
input = {
    "total_hits":10096,
    "max_score":12.383535,
    "hits":
        [
            {
                "_index":"f762ef22-e660-434f-9071-a10ea6691c27",
                "_type":"item","_id":"5678284a770861aa38abc48f",
                "_score":12.383535,
                "fields":
                    {
                        "item_id":"5678284a770861aa38abc48f",
                        "item_name":"Sausage, Peppers and Onions - 1 serving",
                        "brand_id":"546a4142413b47f7107aed0c",
                        "brand_name":"Nutritionix",
                        "nf_serving_size_qty":1,
                        "nf_serving_size_unit":"serving"
                    }
            }
        ]
}

id = input['hits'][0]['fields']['item_id']
print(input)
print(id)

'''
'''

{
 "old_api_id": null,
 "item_id": "5678284a770861aa38abc48f",
 "item_name": "Sausage, Peppers and Onions - 1 serving",
 "leg_loc_id": null,
 "brand_id": "546a4142413b47f7107aed0c",
 "brand_name": "Nutritionix",
 "item_description": null,
 "updated_at": "2015-12-21T16:26:50.000Z",
 "nf_ingredient_statement": null,
 "nf_water_grams": null,
 "nf_calories": 435.42,
 "nf_calories_from_fat": 313.94,
 "nf_total_fat": 34.88,
 "nf_saturated_fat": 12.47,
 "nf_trans_fatty_acid": 0.29,
 "nf_polyunsaturated_fat": 5.98,
 "nf_monounsaturated_fat": 14.09,
 "nf_cholesterol": 107.69,
 "nf_sodium": 956.88,
 "nf_total_carbohydrate": 7.42,
 "nf_dietary_fiber": 1.39,
 "nf_sugars": 3.84,
 "nf_protein": 21.89,
 "nf_vitamin_a_dv": 19,
 "nf_vitamin_c_dv": 73,
 "nf_calcium_dv": 3,
 "nf_iron_dv": 10,
 "nf_refuse_pct": null,
 "nf_servings_per_container": null,
 "nf_serving_size_qty": 1,
 "nf_serving_size_unit": "serving",
 "nf_serving_weight_grams": 197.54,
 "allergen_contains_milk": null,
 "allergen_contains_eggs": null,
 "allergen_contains_fish": null,
 "allergen_contains_shellfish": null,
 "allergen_contains_tree_nuts": null,
 "allergen_contains_peanuts": null,
 "allergen_contains_wheat": null,
 "allergen_contains_soybeans": null,
 "allergen_contains_gluten": null,
 "usda_fields": {
  "PROCNT": {
   "value": 21.888332776083335,
   "desc": "Protein",
   "uom": "g"
  },
  "FAT": {
   "value": 34.881826276400005,
   "desc": "Total lipid (fat)",
   "uom": "g"
  },
  "CHOCDF": {
   "value": 7.424500228249999,
   "desc": "Carbohydrate, by difference",
   "uom": "g"
  },
  "ASH": {
   "value": 3.738539596316667,
   "desc": "Ash",
   "uom": "g"
  },
  "ENERC_KCAL": {
   "value": 435.4180044549999,
   "desc": "Energy",
   "uom": "kcal"
  },
  "STARCH": {
   "value": 0,
   "desc": "Starch",
   "uom": "g"
  },
  "SUCS": {
   "value": 0.44421672733333334,
   "desc": "Sucrose",
   "uom": "g"
  },
  "GLUS": {
   "value": 1.8880729050333331,
   "desc": "Glucose (dextrose)",
   "uom": "g"
  },
  "FRUS": {
   "value": 1.0285361870333332,
   "desc": "Fructose",
   "uom": "g"
  },
  "LACS": {
   "value": 0,
   "desc": "Lactose",
   "uom": "g"
  },
  "MALS": {
   "value": 0.37422000000000005,
   "desc": "Maltose",
   "uom": "g"
  },
  "ALC": {
   "value": 1.0093999999999999,
   "desc": "Alcohol, ethyl",
   "uom": "g"
  },
  "WATER": {
   "value": 128.59006823376666,
   "desc": "Water",
   "uom": "g"
  },
  "CAFFN": {
   "value": 0,
   "desc": "Caffeine",
   "uom": "mg"
  },
  "THEBRN": {
   "value": 0,
   "desc": "Theobromine",
   "uom": "mg"
  },
  "ENERC_KJ": {
   "value": 1821.4454654566666,
   "desc": "Energy",
   "uom": "kJ"
  },
  "SUGAR": {
   "value": 3.8406894481666662,
   "desc": "Sugars, total",
   "uom": "g"
  },
  "GALS": {
   "value": 0.0008475179500000001,
   "desc": "Galactose",
   "uom": "g"
  },
  "FIBTG": {
   "value": 1.3930251026666665,
   "desc": "Fiber, total dietary",
   "uom": "g"
  },
  "CA": {
   "value": 30.591361678333335,
   "desc": "Calcium, Ca",
   "uom": "mg"
  },
  "FE": {
   "value": 1.7477419911166667,
   "desc": "Iron, Fe",
   "uom": "mg"
  },
  "MG": {
   "value": 27.736158773333333,
   "desc": "Magnesium, Mg",
   "uom": "mg"
  },
  "P": {
   "value": 192.54978929333336,
   "desc": "Phosphorus, P",
   "uom": "mg"
  },
  "K": {
   "value": 524.8620649083333,
   "desc": "Potassium, K",
   "uom": "mg"
  },
  "NA": {
   "value": 956.8837656733331,
   "desc": "Sodium, Na",
   "uom": "mg"
  },
  "ZN": {
   "value": 2.9488956198499996,
   "desc": "Zinc, Zn",
   "uom": "mg"
  },
  "CU": {
   "value": 0.11653852575833332,
   "desc": "Copper, Cu",
   "uom": "mg"
  },
  "FLD": {
   "value": 20.627583333333334,
   "desc": "Fluoride, F",
   "uom": "µg"
  },
  "MN": {
   "value": 0.16839947757999998,
   "desc": "Manganese, Mn",
   "uom": "mg"
  },
  "SE": {
   "value": 23.9861669755,
   "desc": "Selenium, Se",
   "uom": "µg"
  },
  "VITA_IU": {
   "value": 931.6081159416667,
   "desc": "Vitamin A, IU",
   "uom": "IU"
  },
  "RETOL": {
   "value": 63.48470833333333,
   "desc": "Retinol",
   "uom": "µg"
  },
  "VITA_RAE": {
   "value": 99.45151344,
   "desc": "Vitamin A, RAE",
   "uom": "µg"
  },
  "CARTB": {
   "value": 378.84063187000004,
   "desc": "Carotene, beta",
   "uom": "µg"
  },
  "CARTA": {
   "value": 8.191668,
   "desc": "Carotene, alpha",
   "uom": "µg"
  },
  "TOCPHA": {
   "value": 1.5801256853333334,
   "desc": "Vitamin E (alpha-tocopherol)",
   "uom": "mg"
  },
  "VITD": {
   "value": 1.6585374999999998,
   "desc": "Vitamin D (D2 + D3)",
   "uom": "µg"
  },
  "ERGCAL": {
   "value": 0,
   "desc": "Vitamin D2 (ergocalciferol)",
   "uom": "µg"
  },
  "CHOCAL": {
   "value": 1.6585374999999998,
   "desc": "Vitamin D3 (cholecalciferol)",
   "uom": "µg"
  },
  "CRYPX": {
   "value": 98.66039071000002,
   "desc": "Cryptoxanthin, beta",
   "uom": "µg"
  },
  "LYCPN": {
   "value": 0,
   "desc": "Lycopene",
   "uom": "µg"
  },
  "LUT+ZEA": {
   "value": 93.17001491666667,
   "desc": "Lutein + zeaxanthin",
   "uom": "µg"
  },
  "TOCPHB": {
   "value": 0.03259666666666667,
   "desc": "Tocopherol, beta",
   "uom": "mg"
  },
  "TOCPHG": {
   "value": 0.15796385493333337,
   "desc": "Tocopherol, gamma",
   "uom": "mg"
  },
  "TOCPHD": {
   "value": 0.004743394666666666,
   "desc": "Tocopherol, delta",
   "uom": "mg"
  },
  "TOCTRA": {
   "value": 0.045020000000000004,
   "desc": "Tocotrienol, alpha",
   "uom": "mg"
  },
  "TOCTRB": {
   "value": 0,
   "desc": "Tocotrienol, beta",
   "uom": "mg"
  },
  "TOCTRG": {
   "value": 0.06803999999999999,
   "desc": "Tocotrienol, gamma",
   "uom": "mg"
  },
  "TOCTRD": {
   "value": 0,
   "desc": "Tocotrienol, delta",
   "uom": "mg"
  },
  "VITC": {
   "value": 43.96556735,
   "desc": "Vitamin C, total ascorbic acid",
   "uom": "mg"
  },
  "THIA": {
   "value": 0.33027652669,
   "desc": "Thiamin",
   "uom": "mg"
  },
  "RIBF": {
   "value": 0.23639450966000003,
   "desc": "Riboflavin",
   "uom": "mg"
  },
  "NIA": {
   "value": 7.302032863670001,
   "desc": "Niacin",
   "uom": "mg"
  },
  "PANTAC": {
   "value": 1.0538045119983335,
   "desc": "Pantothenic acid",
   "uom": "mg"
  },
  "VITB6A": {
   "value": 0.389373810275,
   "desc": "Vitamin B-6",
   "uom": "mg"
  },
  "FOL": {
   "value": 18.576670580000002,
   "desc": "Folate, total",
   "uom": "µg"
  },
  "VITB12": {
   "value": 1.1193595833333332,
   "desc": "Vitamin B-12",
   "uom": "µg"
  },
  "CHOLN": {
   "value": 76.41536915566665,
   "desc": "Choline, total",
   "uom": "mg"
  },
  "VITK1D": {
   "value": 0,
   "desc": "Dihydrophylloquinone",
   "uom": "µg"
  },
  "VITK1": {
   "value": 5.429573104666667,
   "desc": "Vitamin K (phylloquinone)",
   "uom": "µg"
  },
  "FOLAC": {
   "value": 0,
   "desc": "Folic acid",
   "uom": "µg"
  },
  "FOLFD": {
   "value": 18.576670580000002,
   "desc": "Folate, food",
   "uom": "µg"
  },
  "FOLDFE": {
   "value": 18.576670580000002,
   "desc": "Folate, DFE",
   "uom": "µg"
  },
  "BETN": {
   "value": 0.11134372066666667,
   "desc": "Betaine",
   "uom": "mg"
  },
  "TRP_G": {
   "value": 0.2209539313483334,
   "desc": "Tryptophan",
   "uom": "g"
  },
  "THR_G": {
   "value": 0.7243145523066667,
   "desc": "Threonine",
   "uom": "g"
  },
  "ILE_G": {
   "value": 0.8578950185733332,
   "desc": "Isoleucine",
   "uom": "g"
  },
  "LEU_G": {
   "value": 1.577235460401667,
   "desc": "Leucine",
   "uom": "g"
  },
  "LYS_G": {
   "value": 1.440916522683333,
   "desc": "Lysine",
   "uom": "g"
  },
  "MET_G": {
   "value": 0.4891594678600001,
   "desc": "Methionine",
   "uom": "g"
  },
  "CYS_G": {
   "value": 0.27805589704666667,
   "desc": "Cystine",
   "uom": "g"
  },
  "PHE_G": {
   "value": 0.7928837143166665,
   "desc": "Phenylalanine",
   "uom": "g"
  },
  "TYR_G": {
   "value": 0.6022583415116667,
   "desc": "Tyrosine",
   "uom": "g"
  },
  "VAL_G": {
   "value": 1.0229049732949997,
   "desc": "Valine",
   "uom": "g"
  },
  "ARG_G": {
   "value": 1.361994325045,
   "desc": "Arginine",
   "uom": "g"
  },
  "HISTN_G": {
   "value": 0.6208838027683333,
   "desc": "Histidine",
   "uom": "g"
  },
  "ALA_G": {
   "value": 1.324475495553333,
   "desc": "Alanine",
   "uom": "g"
  },
  "ASP_G": {
   "value": 1.923797881685,
   "desc": "Aspartic acid",
   "uom": "g"
  },
  "GLU_G": {
   "value": 3.378139795378333,
   "desc": "Glutamic acid",
   "uom": "g"
  },
  "GLY_G": {
   "value": 1.458336232503333,
   "desc": "Glycine",
   "uom": "g"
  },
  "PRO_G": {
   "value": 1.4358171449733335,
   "desc": "Proline",
   "uom": "g"
  },
  "SER_G": {
   "value": 0.9009748571816667,
   "desc": "Serine",
   "uom": "g"
  },
  "HYP": {
   "value": 0.48421800000000004,
   "desc": "Hydroxyproline",
   "uom": "g"
  },
  "CHOLE": {
   "value": 107.69170833333334,
   "desc": "Cholesterol",
   "uom": "mg"
  },
  "FATRN": {
   "value": 0.2911020833333333,
   "desc": "Fatty acids, total trans",
   "uom": "g"
  },
  "FASAT": {
   "value": 12.472864132384998,
   "desc": "Fatty acids, total saturated",
   "uom": "g"
  },
  "F4D0": {
   "value": 0.15256291666666666,
   "desc": "4:0",
   "uom": "g"
  },
  "F6D0": {
   "value": 0.09491437500000001,
   "desc": "6:0",
   "uom": "g"
  },
  "F8D0": {
   "value": 0.05741108333333332,
   "desc": "8:0",
   "uom": "g"
  },
  "F10D0": {
   "value": 0.14686862526666666,
   "desc": "10:0",
   "uom": "g"
  },
  "F12D0": {
   "value": 0.14576155806666669,
   "desc": "12:0",
   "uom": "g"
  },
  "F14D0": {
   "value": 0.7179208336000001,
   "desc": "14:0",
   "uom": "g"
  },
  "F16D0": {
   "value": 7.342511345526667,
   "desc": "16:0",
   "uom": "g"
  },
  "F18D0": {
   "value": 3.5948411032583327,
   "desc": "18:0",
   "uom": "g"
  },
  "F20D0": {
   "value": 0.08250425,
   "desc": "20:0",
   "uom": "g"
  },
  "F18D1": {
   "value": 12.947484897279999,
   "desc": "18:1 undifferentiated",
   "uom": "g"
  },
  "F18D2": {
   "value": 5.200917190905,
   "desc": "18:2 undifferentiated",
   "uom": "g"
  },
  "F18D3": {
   "value": 0.19083414792666664,
   "desc": "18:3 undifferentiated",
   "uom": "g"
  },
  "F20D4": {
   "value": 0.139482,
   "desc": "20:4 undifferentiated",
   "uom": "g"
  },
  "F22D6": {
   "value": 0.0034019999999999996,
   "desc": "22:6 n-3 (DHA)",
   "uom": "g"
  },
  "F22D0": {
   "value": 0.010205999999999998,
   "desc": "22:0",
   "uom": "g"
  },
  "F14D1": {
   "value": 0.006803999999999999,
   "desc": "14:1",
   "uom": "g"
  },
  "F16D1": {
   "value": 0.6774939586000001,
   "desc": "16:1 undifferentiated",
   "uom": "g"
  },
  "F18D4": {
   "value": 0,
   "desc": "18:4",
   "uom": "g"
  },
  "F20D1": {
   "value": 0.38348516666666665,
   "desc": "20:1",
   "uom": "g"
  },
  "F20D5": {
   "value": 0.002268,
   "desc": "20:5 n-3 (EPA)",
   "uom": "g"
  },
  "F22D1": {
   "value": 0.006803999999999999,
   "desc": "22:1 undifferentiated",
   "uom": "g"
  },
  "F22D5": {
   "value": 0.028350000000000004,
   "desc": "22:5 n-3 (DPA)",
   "uom": "g"
  },
  "PHYSTR": {
   "value": 6.519013533333333,
   "desc": "Phytosterols",
   "uom": "mg"
  },
  "STID7": {
   "value": 0,
   "desc": "Stigmasterol",
   "uom": "mg"
  },
  "CAMD5": {
   "value": 0,
   "desc": "Campesterol",
   "uom": "mg"
  },
  "SITSTR": {
   "value": 0.18916666666666665,
   "desc": "Beta-sitosterol",
   "uom": "mg"
  },
  "FAMS": {
   "value": 14.089866397546666,
   "desc": "Fatty acids, total monounsaturated",
   "uom": "g"
  },
  "FAPU": {
   "value": 5.984833338831667,
   "desc": "Fatty acids, total polyunsaturated",
   "uom": "g"
  },
  "F15D0": {
   "value": 0.017009999999999997,
   "desc": "15:0",
   "uom": "g"
  },
  "F17D0": {
   "value": 0.10813133333333332,
   "desc": "17:0",
   "uom": "g"
  },
  "F24D0": {
   "value": 0.002268,
   "desc": "24:0",
   "uom": "g"
  },
  "F16D1T": {
   "value": 0.009072,
   "desc": "16:1 t",
   "uom": "g"
  },
  "F18D1T": {
   "value": 0.23627975,
   "desc": "18:1 t",
   "uom": "g"
  },
  "F22D1T": {
   "value": 0,
   "desc": "22:1 t",
   "uom": "g"
  },
  "F18D2CLA": {
   "value": 0.05004887500000001,
   "desc": "18:2 CLAs",
   "uom": "g"
  },
  "F24D1C": {
   "value": 0.001134,
   "desc": "24:1 c",
   "uom": "g"
  },
  "F20D2CN6": {
   "value": 0.28009799999999996,
   "desc": "20:2 n-6 c,c",
   "uom": "g"
  },
  "F16D1C": {
   "value": 0.6680132916666667,
   "desc": "16:1 c",
   "uom": "g"
  },
  "F18D1C": {
   "value": 12.705249964133332,
   "desc": "18:1 c",
   "uom": "g"
  },
  "F18D2CN6": {
   "value": 5.07502375,
   "desc": "18:2 n-6 c,c",
   "uom": "g"
  },
  "F22D1C": {
   "value": 0.006803999999999999,
   "desc": "22:1 c",
   "uom": "g"
  },
  "F18D3CN6": {
   "value": 0.006803999999999999,
   "desc": "18:3 n-6 c,c,c",
   "uom": "g"
  },
  "F17D1": {
   "value": 0.065772,
   "desc": "17:1",
   "uom": "g"
  },
  "F20D3": {
   "value": 0.07824600000000001,
   "desc": "20:3 undifferentiated",
   "uom": "g"
  },
  "FATRNM": {
   "value": 0.24535174999999998,
   "desc": "Fatty acids, total trans-monoenoic",
   "uom": "g"
  },
  "FATRNP": {
   "value": 0.04461633333333333,
   "desc": "Fatty acids, total trans-polyenoic",
   "uom": "g"
  },
  "F13D0": {
   "value": 0,
   "desc": "13:0",
   "uom": "g"
  },
  "F15D1": {
   "value": 0,
   "desc": "15:1",
   "uom": "g"
  },
  "F18D3CN3": {
   "value": 0.17438591640000004,
   "desc": "18:3 n-3 c,c,c (ALA)",
   "uom": "g"
  },
  "F20D3N3": {
   "value": 0.034019999999999995,
   "desc": "20:3 n-3",
   "uom": "g"
  },
  "F20D3N6": {
   "value": 0.044226,
   "desc": "20:3 n-6",
   "uom": "g"
  },
  "F22D4": {
   "value": 0.057833999999999997,
   "desc": "22:4",
   "uom": "g"
  }
 }
}
'''