# Software Challenge 

"""
Created on : Thur 17 14:03:01 2020
Author : Karol

"""


# Import Dependencies
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib
import csv
import pandas as pd
import os
import argparse


def argsparser():
    global extends
    parser = argparse.ArgumentParser(description='Web Price Scraper.')
    parser.add_argument('--extend', '--e', help='Do you want to add more balls ? 1 for Yes, 0 for No.', required = False)

    args = parser.parse_args()
    try:
        extends = int(args.extend)
    except:
        # By default set extends to 0, i.e. No additional data to be entered.
        extends	= 0
        print("User does not want to add more Marke")


def add_marke(marke):
    print("User wants to add more Marke")
    choice = 1
    while choice == 1:
        a = input("Enter the marke (eg : 'dmc') : ")
        marke.append(a)
        choice = int(input("Enter do you want to enter more ? 1 for Yes ,  0 for No : "))

    print("Final List of Marke :  ",  marke)
    print("Inputs Succesfully Taken !!")
    return marke


def main() :

    base_url = "https://www.wollplatz.de/"
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36"
    }
    driver = webdriver.Chrome(executable_path="chromedriver.exe")

    products = [] # List to store name of the product
    prices = [] # List to store price of the product
    needle_size = [] # List to store needle size of the product
    composition = [] # List to store composition of the product

    marke = ["dmc", "drops", "hanf", "stylecraft", "hahn"]
    #marke = ["dmc"]
    bezeichnung = ["Natura XL","Safran", "Baby Merino Mix", "Alpacca Speciale", "Special double knit"]
    #bezeichnung = ["Natura XL"]
    category = "/wolle/"

    if extends == 1:
        marke = add_marke(marke)

    print("Retrieving Data ......")
    for item in marke :

        r = requests.get(base_url + category + item )

        # Check if Item is avaiable or not
        if r.ok:
            pass
        else:
            print("Following Item is unavailable or not reachable : ", item)
        soup = BeautifulSoup(r.content,"lxml")
            
        productlist = soup.find_all("div", class_ = "productlistholder productlist25")
        productlinks = []
        for item in productlist:
            for link in item.find_all("a", href = True):
                productlinks.append(link["href"])

        
        for link in productlinks:
            r = requests.get(link, headers = headers)

            try: 
                soup = BeautifulSoup(r.content, "lxml")
                name = soup.find("h1", id = "pageheadertitle").text.strip()
                price = soup.find("span", class_= "product-price-amount").text.strip()
                comp = soup.find("td", text ="Zusammenstellung").find_next_sibling("td").text
                size = soup.find("td", text ="Nadelstärke").find_next_sibling("td").text
            except:
                pass

            for brand in bezeichnung:
                if brand in name :

                    products.append(name)
                    prices.append(price)
                    needle_size.append(size)
                    composition.append(comp)

    # Append data lists to pandas dataframe
    df = pd.DataFrame(list(zip(*[products, prices, needle_size, composition]))).add_prefix('Col')
    try :
        data_to_csv(df)
    except :
        print("No Data to Store")
    

# Function to write collected data to csv
def data_to_csv(df):

    file_path = 'collected_data.csv'
    column_names = ["Product Name", "Price (Euros)", "Needle Size", "Composition"]
    df.columns = column_names
    if os.path.exists(file_path):
        os.remove(file_path)
    df.to_csv(file_path, index=False)

    print("Succesfully Retrieved and Stored Data!!")


if __name__ == "__main__":
    argsparser()
    main()
