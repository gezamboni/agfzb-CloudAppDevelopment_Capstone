from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
# from .models import related models
from .models import CarModel, CarMake, CarDealer, DealerReview
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_request, get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from django.db import models
from django.core import serializers
from django.utils.timezone import now
import uuid

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/new_login.html', context)
    else:
        return render(request, 'djangoapp/new_login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/user_registration_bootstrap.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        context=dict()
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/cd2d13ac-0ce2-4152-8106-94b865fd2788/dealership-package/get-dealership"
        
        # Get dealers from the URL
        dealerships, result = get_dealers_from_cf(url)
        context["dealerships"] = dealerships
        context["result"] = result
        
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/cd2d13ac-0ce2-4152-8106-94b865fd2788/dealership-package/get-dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        print("\nget_dealer_details => dealer", dealer ,"\n")
        context["dealer"] = dealer
        #context["result"] = result
    
        review_url = "https://us-south.functions.appdomain.cloud/api/v1/web/cd2d13ac-0ce2-4152-8106-94b865fd2788/dealership-package/get_review"
        reviews = get_dealer_reviews_from_cf(review_url, id=id)
        print("\nget_dealer_details => reviews", reviews ,"\n")
        print("\nget_dealer_details => type(reviews)", type(reviews))
        print("\nget_dealer_details => len(reviews)", len(reviews))
        print("\nget_dealer_details => reviews[0]", reviews[0])
        print("\nget_dealer_details => reviews[0].dealership ", reviews[0].dealership)
        print("\nget_dealer_details => reviews[0].name ", reviews[0].name)
        print("\nget_dealer_details => reviews[0].purchase ", reviews[0].purchase)
        print("\nget_dealer_details => reviews[0].review ", reviews[0].review )
        print("\nget_dealer_details => reviews[0].purchase_date", reviews[0].purchase_date)
        print("\nget_dealer_details => reviews[0].make", reviews[0].make)
        print("\nget_dealer_details => reviews[0].car_model", reviews[0].car_model)
        print("\nget_dealer_details => reviews[0].car_year", reviews[0].car_year)
        context["reviews"] = reviews
        
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
# View to submit a new review
def add_review(request, id):
    context = {}
    dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/cd2d13ac-0ce2-4152-8106-94b865fd2788/dealership-package/get-dealership"
    dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
    context["dealer"] = dealer
    if request.method == 'GET':
        # Get cars for the dealer
        cars = CarModel.objects.all()
        print(cars)
        context["cars"] = cars
        
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            payload = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = id
            payload["id"] = id
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
            payload["purchase_date"] = request.POST["purchasedate"]
            payload["car_make"] = car.carmake.name
            payload["car_model"] = car.name
            payload["car_year"] = int(car.year.strftime("%Y"))

            new_payload = {}
            new_payload["review"] = payload
            review_post_url = "https://us-south.functions.appdomain.cloud/api/v1/web/cd2d13ac-0ce2-4152-8106-94b865fd2788/dealership-package/post-review"
            post_request(review_post_url, new_payload, id=id)
        return redirect("djangoapp:dealer_details", id=id)     

