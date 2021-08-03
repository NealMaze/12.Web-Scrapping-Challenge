import pandas as pd
from bs4 import BeautifulSoup
import pymongo
from webdriver_manager.chrome import ChromeDriverManager
import time
from splinter import Browser

def scrape(urls):
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    client.drop_database('mars_db')
    db = client.mars_db
    collection = db.articles

    executable_path = {'executable_path' : ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless = False)

    mars = {}
    soupDatas = []

    for i in urls:
        browser.visit(i)
        html = browser.html
        soup = BeautifulSoup(html, "html.parser")
        urlData = {
            "url": i,
            "html": html,
            "soup": soup
        }
        soupDatas.append(urlData)


    # get the news
    newsSoup = soupDatas[0]
    newsResults = newsSoup["soup"].find_all('div', class_='content_title')
    newsTitle = newsResults[0].a.text
    newsResults = newsSoup["soup"].find_all('div', class_= 'article_teaser_body')
    paragraph = newsResults[1].text
    mars['news_title'] = newsTitle
    mars['news_paragraph'] = paragraph


    # get dat image
    imageSoup = soupDatas[1]
    browser.visit(imageSoup["url"])
    imageResults = browser.find_by_tag('button')[1]
    imageResults.click()
    imgResults = soup.find_all('img')[1]['src']
    mars['featured_image_url'] = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/' + imgResults


    # grab facts
    factSoup = soupDatas[2]
    factTable = pd.read_html(factSoup["url"])[0]
    factTable.columns=['Description', 'Mars']
    factTable.set_index('Description', inplace = True)
    marsFacts = factTable.to_html()
    mars['mars_facts'] = marsFacts

    # you know I gotta habe dem hemisphere infos
    hemiSoup = soupDatas[3]
    browser.visit(hemiSoup["url"])
    hemiResults = hemiSoup["soup"].find_all('div', class_='description')

    imgUrls = []

    for i in hemiResults:
        varTwo = {}
        hemiTemp = i.find('h3').text
        hemiTitle = hemiTemp[:-9]
        varTwo['title'] = hemiTitle

        browser.click_link_by_partial_text(hemiTemp)
        img = hemiSoup["soup"].find_all('img')[5]['src']
        base_url = 'https://astrogeology.usgs.gov'
        imgUrl = base_url + img
        varTwo['img_urls'] = imgUrl
        imgUrls.append(varTwo)
        browser.back()

    mars["hemishperes"] = imgUrls

    browser.quit()

    collection.insert_one(mars)

    return(mars)



























