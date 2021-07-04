import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json
import pandas as pd
import nltk
import os.path


SEARCH_URL = 'https://fptshop.com.vn/apiFPTShop/Product/GetProductList?url=https:%2F%2Ffptshop.com.vn%2F{0}%3Fsort%3Dban-chay-nhat%26trang%3D{1}'
REVIEW_URL = 'https://fptshop.com.vn/apiFPTShop/Product/GetReviewAndRateByProduct?ProductId={0}&PageIndex={1}'
HEADERS = {
    'Content-Type': 'text/html',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'
}

# 
#   CHANGE THESE.
#
SEARCH_PROPS = ['product_id', 'product_name', 'review']

PROD_OBJ = {
    'phone': 'dien-thoai',
    'laptop': 'may-tinh-xach-tay'
}

REVIEW_FILE_NAME = 'test_rv.csv'
#
#
#

Options = Options()
Options.headless = True

driver = webdriver.Firefox(options= Options)


def saveReviews(reviews, firstSave = False):
    reviewDf = pd.DataFrame(reviews, columns = SEARCH_PROPS)

    if firstSave:
        reviewDf.to_csv(REVIEW_FILE_NAME, header=True, index=False)
    else:
        reviewDf.to_csv(REVIEW_FILE_NAME, mode='a', header=False, index=False)


def getReviewPage(prodId, review_page):
    reviewReq = requests.get(REVIEW_URL.format(prodId, str(review_page)))
    reviews = json.loads(reviewReq.content.decode())['datas']['listReview']['listItems']
    return reviews


def getReviewOfProd(prodName, prodId):
    review_page = 1
    data = []

    while (True):
        reviews = getReviewPage(prodId, review_page)
                
        if len(reviews) == 0: break

        for rv in reviews:
            data += [[prodId, prodName, sentence] for sentence in nltk.sent_tokenize(rv['commentCustomer'])]

        review_page += 1

        saveReviews(data, firstRvCollected)


def getProducts(currentProd, page):
    searchReq = requests.get(SEARCH_URL.format(currentProd, str(page)))
    products = json.loads(searchReq.content.decode())['datas']['filterModel']['listDefault']['list']
    return products

if __name__ == '__main__':
    for currentKey, currentProd in PROD_OBJ.items():
        while (True):
            page = 1

            firstRvCollected = not os.path.isfile(REVIEW_FILE_NAME)

            products = getProducts(currentProd, page)

            if len(products) == 0: break

            print('--------- Crawling for product {0} on page {1}'.format(currentKey, page))

            for prod in products:
                getReviewOfProd(prod['nameAscii'], prod['id'])

            page += 1



