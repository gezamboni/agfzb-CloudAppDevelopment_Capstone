import requests
import json
from .models import CarDealer
from requests.auth import HTTPBasicAuth


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
#       e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
#       - Call get_request() with specified arguments
#       - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    data_list = []
    result = "ok"
    state = kwargs.get("state")
    if state:
        # - Call get_request() with specified state
        json_result = get_request(url, state)
    else:
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
def get_dealer_by_id_from_cf(url, id):
    result = "ok"
    json_result = get_request(url, id=id)

    if json_result:
        dealer_data = dealer["doc"]
        # Create a CarDealer object with values in `doc` object
        dealer_obj = CarDealer(address=dealer_data["address"], city=dealer_data["city"], full_name=dealer_data["full_name"],
                                        id=dealer_data["id"], lat=dealer_data["lat"], long=dealer_data["long"],
                                        short_name=dealer_data["short_name"],
                                        st=dealer_data["st"], zip=dealer_data["zip"])

    elif json_result:
        result = json_result["message"]
    else:
        result = "Unknown error"
    
    return dealer_obj, result


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

    if json_result:
        reviews = json_result["body"]["data"]["docs"]
        for dealer_review in reviews:
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
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
