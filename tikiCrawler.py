import requests
import json
import pandas as pd
import nltk
import os.path

URL_SEARCH = 'https://tiki.vn/api/v2/products?page={0}&limit={1}&include=sale-attrs,badges,product_links,brand,category,stock_item,advertisement&aggregations=1&q={2}'
URL_REVIEW = 'https://tiki.vn/api/v2/reviews?product_id={0}&sort=score%7Cdesc,id%7Cdesc%7Call&page={1}&limit=50'

#
#   Tiki doesn't allow requests lack of User-Agent header. 
#
HEADERS = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0' }


#
#   CHANGE THESE.
#
SEARCH_PROPS = [ 'id', 'name','url_path', 'brand_name', 'category' ]
REVIEW_PROPS = [ 'id', 'product_id', 'content' ]
SEARCH_LIMIT = 20
PROD_FILE_NAME = 'test.csv'
REVIEW_FILE_NAME = 'test_rv.csv'

searchQuery = {
    'laptop': 'laptop'
}
#
#
#

#
#   If this is not the first time data is crawled and append mode is in need. 
#
firstProdCollected = not os.path.isfile(PROD_FILE_NAME)
firstRvCollected = not os.path.isfile(REVIEW_FILE_NAME)
 

def getProductAmount(search):
    searchUrl = URL_SEARCH.format(1, SEARCH_LIMIT, search)
    searchPage = requests.get(searchUrl, headers = HEADERS)
    searchResults = json.loads(searchPage.content.decode())
    return searchResults['paging']['last_page']

def getReviewAmount(productId):
    productUrl = URL_REVIEW.format(productId, 1)
    productPage = requests.get(productUrl, headers = HEADERS)
    reviewResults = json.loads(productPage.content.decode())
    return reviewResults['paging']['last_page']

def searchProduct(search, currentProdPage, lastProdPage, category):
    if (lastProdPage and currentProdPage >= lastProdPage):
        return

    searchUrl = URL_SEARCH.format(currentProdPage, SEARCH_LIMIT, search)
    searchPage = requests.get(searchUrl, headers = HEADERS)
    searchResults = json.loads(searchPage.content.decode())
    lastProdPage = searchResults['paging']['last_page']
    data = searchResults['data']

    for i in range(len(data)):
        getProductPage(data[i], category)
    # searchProduct(search, currentProdPage + 1, lastProdPage, category)


def getProductPage(data, category):
    global firstProdCollected

    productProps = {
        'productId': data['id'],
        'productName': data['name'],
        'productUrlPath': data['url_path'],
        'productBrandName': data['brand_name'],
        'productCategory': category
    }

    products = [[ productProps['productId'], productProps['productName'], productProps['productUrlPath'], productProps['productBrandName'], productProps['productCategory']]]

    print('Saving:', productProps['productName'])
    saveProducts(products, firstProdCollected)
    firstProdCollected = False

    reviewAmount = getReviewAmount(productProps['productId'])
    for i in range(1, reviewAmount):
        getReviewsPage(productId = productProps['productId'], currentPage = i, lastPage = None)

def getReviewsPage(productId, currentPage, lastPage):
    if (lastPage and currentPage >= lastPage):
        return
    productUrl = URL_REVIEW.format(productId, currentPage)
    productPage = requests.get(productUrl, headers = HEADERS)
    reviewResults = json.loads(productPage.content.decode())
    lastPage = reviewResults['paging']['last_page']
    data = reviewResults['data']

    for i in range(len(data)):
        getReviewSentences(productId, data[i])

    # getReviewsPage(productId, currentPage + 1, lastPage)


def getReviewSentences(productId, data):
    global firstRvCollected

    reviewProps = {
        'reviewId': data['id'],
        'reviewProductId': productId,
        'reviewContent': data['content']
    }    

    sentences = nltk.sent_tokenize(reviewProps['reviewContent'])
    reviews = [[ reviewProps['reviewId'], reviewProps['reviewProductId'], review ] for review in sentences]
    saveReviews(reviews, firstRvCollected)
    firstRvCollected = False


def saveProducts(products, firstSave = False):
    productDf = pd.DataFrame(products, columns = SEARCH_PROPS)

    if firstSave:
        productDf.to_csv(PROD_FILE_NAME, header=True, index=False)
    else:
        productDf.to_csv(PROD_FILE_NAME, mode='a', header=False, index=False)

def saveReviews(reviews, firstSave = False):
    reviewDf = pd.DataFrame(reviews, columns = REVIEW_PROPS)

    if firstSave:
        reviewDf.to_csv(REVIEW_FILE_NAME, header=True, index=False)
    else:
        reviewDf.to_csv(REVIEW_FILE_NAME, mode='a', header=False, index=False)



if __name__ == '__main__':
    for key in searchQuery:
        print('Start searching ' + searchQuery[key] + '...')
        productAmount = getProductAmount(searchQuery[key])
        for i in range(1, productAmount):
            searchProduct(searchQuery[key], i, None, key)
        print('End searching ' + searchQuery[key] + ' .')







