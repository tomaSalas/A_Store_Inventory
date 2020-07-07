
from datetime import datetime
from collections import OrderedDict
import csv
import copy
import os
import re

from peewee import *


def currency_to_cents(currency):
    try:
        cents = int(float(currency.strip('$')) * 100)
    except ValueError:
        cents = 0
    return cents

def date_time_format(date):
    xc = datetime.strptime(date, '%m/%d/%Y')
    return xc

def read_csv(name_of_file):
    products = []
    with open(name_of_file, mode='r', newline="") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            products.append({"product_name": row["product_name"],
                             "product_price": currency_to_cents(row["product_price"]),
                             "product_quantity": int(row["product_quantity"]),
                             "date_updated": date_time_format(row['date_updated'])})
    return products


def add_csv_to_db(data):
    """Add the data from dic to the database"""
    # only if there is nothing in the table
    if len(Product.select()) == 0:
        try:
            for product in data:
                Product.create(**product)
        except IntegrityError:
            product = Product.get(product_name=product_name)
            product.update = product.update
            product.product_price = int(float(product_price) * 100)
            product.product_quantity = int(product_quantity)
            product.save()


db = SqliteDatabase("inventory.db")


class Product(Model):
    id_product = AutoField()
    product_name = CharField(unique=True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateTimeField(default=datetime.now)

    class Meta:
        database = db


def initialize():
    """create the database and tables if they do not exist already"""
    db.connect()
    db.create_tables([Product], safe=True)


def menu_loop():
    """Show the menu"""
    choice = None

    while choice != "q":
        clear()
        print("-" * 6 + "MENU" + "-" * 6)
        
        print("enter 'q' to quit.")
        for key, value in menu.items():
            print("{}) {}".format(key, value.__doc__))
        choice = input("Action: ").lower().strip()
        if bool(re.search(r'[^abvq]', choice)) == True:
            print("Oh no! That is not a valid input. Please try again")
            menu_loop()


        if choice in menu:
            clear()
            menu[choice]()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def add_entry():
    """add an entry"""
    print("-" * 6 + "ADD PRODUCT" + "-" * 6)
    print("What is the product name?")
    product_name = input(">   ")
    print("What is the product_price?")
    product_price = input(">   ")
    print("What is the product_quantity?")
    product_quantity = input(">   ")
    print("name: {}, price ${}, quantity {} ".format(
        product_name, product_price, product_quantity))
    
    if input("Save entry? [Yn]:   ").lower() != "n":
        try:
            product = Product()
            Product.create(
            product_name = product_name, 
            product_quantity = int(float(product_price) * 100), 
            product_price = int(product_quantity))
            product.save()
            print("Successfully Created!")
        except ValueError:
            print("One of the following inputs is incorrect 'product quantity', product_price or product.product_name!"
                  "please try again!")
            add_entry()
        except IntegrityError:
            product = Product.get(product_name=product_name)
            product.update = product.update
            product.product_price = int(float(product_price) * 100)
            product.product_quantity = int(product_quantity)
            product.save()
            print("Successfully Updated!")


def view_entries():
    """view previews entry"""
    print("-" * 6 + "VIEW PRODUCT" + "-" * 6)
    try:
        product_id = int(input("Please select a product id:  "))
        product = Product.get_by_id(product_id)
    except ValueError:
        print("Please input integer for product id!")
        view_entries()
    except:
        print("That record does not seem to exist!")
        view_entries()
    else:
        print("*" * 6 + "Here are product details" + "*" * 6)
        print("\n")
        print("Product: {}".format(product.product_name))
        print("product_price: {}".format(product.product_price))
        print("product_quantity: {}".format(product.product_quantity))
        print("date_updated: {}".format(product.date_updated))
        print("There are {} items in this table".format(len(Product.select())))
        print("input 'n' for veiw new record or 'd' to delete a product. Input \
any other letter to go back to the main menu")
        next_action = input("Action:  ").lower().strip()
        if next_action == "n":
            view_entries()
        elif next_action == "d":
            delete_entry(product)
            print("The entry was deleted sucessfully!")


def backup_db():
    """To export the db as CSV)"""
    print("-" * 6 + "BACKUP" + "-" * 6)
    with open('backup.csv', 'w') as csv_file:
        headers = ['product_name', 'product_price',
                   'product_quantity', 'date_updated']
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        products = Product.select()
        for product in products:
            writer.writerow({
                "product_name": product.product_name,
                "product_price": "${}".format(product.product_price / 100),
                "product_quantity": product.product_quantity,
                "date_updated": datetime.strftime(product.date_updated, '%m/%d/%Y'),
            })

        print('Backup was done succssfully!')


def delete_entry(product):
    """delete_product"""
    if input("Are you sure you want delete a product[yn]?").lower() == "y":
        product.delete.instance()


menu = OrderedDict([("a", add_entry),
                    ("v", view_entries),
                    ("b", backup_db),
                    ])

if __name__ == "__main__":
    initialize()
    Product.delete()
    add_csv_to_db(read_csv("inventory.csv"))
    menu_loop()
