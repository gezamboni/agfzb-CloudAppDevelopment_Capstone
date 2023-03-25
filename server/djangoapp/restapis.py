import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions
import time


def get_request(url, **kwargs):
    print("kwargs", kwargs)
    print("GET from {} ".format(url))
    api_key = kwargs.get("api_key")
    try:
        # Call get method of requests library with URL and parameters
        # response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
        # response = requests.get(url, params=params, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', api_key))
        if api_key:
            # Basic authentication GET
            response = request.get(url, params=kwargs, headers={'Content-Type': 'application/json'}, auth=HTTPBasicAuth('apikey', api_key))
        else:
            # no authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
#       e.g., response = requests.post(url, params=kwargs, json=payload)
# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    print(payload)
    response = requests.post(url, params=kwargs, json=payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
#       - Call get_request() with specified arguments
#       - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    data_list = []
    result = "ok"
    #state = kwargs.get("state")
    #if state:
        # - Call get_request() with specified state
        #json_result = get_request(url, state)
    #else:
        # - Call get_request() with url
    json_result = get_request(url)

    if json_result:
        for dealer in json_result:
            # Get the row list in JSON as dealers
            dealer_data = dealer["doc"]
                # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_data["address"], city=dealer_data["city"], full_name=dealer_data["full_name"],
                                        id=dealer_data["id"], lat=dealer_data["lat"], long=dealer_data["long"],
                                        short_name=dealer_data["short_name"],
                                        st=dealer_data["st"], zip=dealer_data["zip"])
            data_list.append(dealer_obj)

    elif json_result:
        result = json_result["message"]
    else:
        result = "Unknown error"
    
    return data_list, result

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
#   - Call get_request() with specified arguments
#   - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, **kwargs):
    result = "ok"
    id = kwargs.get("id")
    if id:
        # - Call get_request() with specified id
        json_result = get_request(url, id = id)
    else:
        # - Call get_request() with url
        json_result = get_request(url)

    for dealer in json_result:
        dealer_data = dealer["doc"]
        # Create a CarDealer object with values in `doc` object
        dealer = CarDealer(address=dealer_data["address"], city=dealer_data["city"], full_name=dealer_data["full_name"],
                                        id=dealer_data["id"], lat=dealer_data["lat"], long=dealer_data["long"],
                                        short_name=dealer_data["short_name"],
                                        st=dealer_data["st"], zip=dealer_data["zip"])

    return dealer


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    id = kwargs.get("id")
    if id:
        json_result = get_request(url, id=id)
    else:
        json_result = get_request(url)

    json_result_01 = json_result["data"]
    json_result_02 = json_result_01["docs"]
    if json_result_01:
        for dealer_review in json_result_02:
            #reviews = dealer
        #for dealer_review in reviews:
            review_obj = DealerReview(dealership=dealer_review["dealership"],
                                   name=dealer_review["name"],
                                   purchase=dealer_review["purchase"],
                                   review=dealer_review["review"])
            if "id" in dealer_review:
                review_obj.id = dealer_review["id"]
            if "purchase_date" in dealer_review:
                review_obj.purchase_date = dealer_review["purchase_date"]
            if "make" in dealer_review:
                review_obj.make = dealer_review["make"]
            if "car_model" in dealer_review:
                review_obj.car_model = dealer_review["car_model"]
            if "car_year" in dealer_review:
                review_obj.car_year = dealer_review["car_year"]
            
            sentiment = analyze_review_sentiments(review_obj.review)
            print(sentiment)
            review_obj.sentiment = sentiment
            results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
#   - Call get_request() with specified arguments
#   - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    #url e api_key from NLU service credentials
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/21413455-1e78-4ef6-92cf-06d558365ef2"
    api_key = "zJwqpFRUSvSluHiTtsqm6-5u1igGnFNlWKnkHK0fP3fq"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze( text=text+"hello hello hello",features=Features(sentiment=SentimentOptions(targets=[text+"hello hello hello"]))).get_result()
    label=json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    
    
    return(label) 