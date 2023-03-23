from django.db import models
from django.utils.timezone import now


# Create your models here.

#            <HINT> Create a Car Make model `class CarMake(models.Model)`:
#                   - Name
#                   - Description
#                   - Any other fields you would like to include in car make model
#                   - __str__ method to print a car make object

class CarMake(models.Model):
    name = models.CharField(null=False, max_length=60, default='Car name')
    description = models.CharField(null=True, max_length=1000)

    def __str__(self):
        return "Name: " + self.name


#            <HINT> Create a Car Model model `class CarModel(models.Model):`:
#                   - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
#                   - Name
#                   - Dealer id, used to refer a dealer created in cloudant database
#                   - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
#                   - Year (DateField)
#                   - Any other fields you would like to include in car model
#                   - __str__ method to print a car make object

class CarModel(models.Model):
    carmake = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=60, default='Car model')
    id = models.IntegerField(default=1, primary_key=True)  
    SUV = 'SUV'
    HATCHBACK = 'Hatchback'
    CONVERTIBLE = 'Convertible'
    SEDAN = 'Sedan'
    SPORT = 'Sport'
    COUPE = 'Coupe'
    STATIONWAGON = 'Station Wagon'
    MINIVAN = 'Minivan'
    CAR_TYPES = [
        (SUV, 'SUV'),
        (HATCHBACK, 'Hatchback'),
        (CONVERTIBLE,'Convertible'),
        (SEDAN, 'Sedan'),
        (SPORT, 'Sport'),
        (COUPE, 'Coupe'),
        (STATIONWAGON, 'Station Wagon'),
        (MINIVAN, 'Minivan')
    ]
    type = models.CharField(null=False, max_length=60, choices=CAR_TYPES, default=SEDAN)
    year = models.DateField(default=now)

    def __str__(self):
        return "Name: " + self.name


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:
    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        self.address = address
        self.city = city
        self.full_name = full_name
        self.id = id
        self.lat = lat
        self.long = long
        self.short_name = short_name
        self.st = st
        self.zip = zip

    def __str__(self):
        return self.full_name


# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:
    def __init__(self, dealership, name, purchase, review):
        self.car_make = ""
        self.car_model = ""
        self.car_year = ""
        self.dealership = dealership
        self.id = ""  # The id of the review
        self.name = name  # Name of the reviewer
        self.purchase = purchase  # Did the reviewer purchase the car? bool
        self.purchase_date = ""
        self.review = review  # The actual review text
        self.sentiment = ""  # Watson NLU sentiment analysis of review

    def __str__(self):
        return "Reviewer: " + self.name + " Review: " + self.review
