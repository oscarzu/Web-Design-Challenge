
from bs4 import BeautifulSoup as bs
from splinter import Browser
import os
import pandas as pd
import time
import requests
from sqlalchemy import create_engine
from urllib.parse import urlsplit
from selenium import webdriver

def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape ():
    browser = init_browser()
    marsinfo = {}

    # Visit the web page
    mars_url = 'https://mars.nasa.gov/news/'
    browser.visit(mars_url)
    
    # give page time to load
    time.sleep(4)

    #using bs to write it into html
    html = browser.html
    soup = bs(html,'html.parser')

    news_title = soup.find('div',class_= 'content_title').text
    news_paragraph = soup.find('div', class_= 'article_teaser_body').text

    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)
    time.sleep(2)
    
    #Base url
    base_url = 'https://www.jpl.nasa.gov'

    #get image url using BeautifulSoup
    image_url = browser.html
    soup = bs(image_url, 'html.parser')
    img_url = soup.find(id='full_image').get('data-fancybox-href')
    fullimgurl = base_url + img_url

    #get mars weather's latest tweet from the website
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)
    time.sleep(2)
    weather_html = browser.html
    soup = bs(weather_html, 'html.parser')
    marsweather = soup.find('p', class_= 'TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text

    marsfacts_url = 'https://space-facts.com/mars/'

    table = pd.read_html(marsfacts_url)
    table[0]

    marsfacts_df = table[1]
    marsfacts_df.columns = ['Parameter', 'Values']
    marsfacts_df.set_index(['Parameter'])

    marsfacts_html = marsfacts_df.to_html(index=False)
    marsfacts_html = marsfacts_html.replace("\n", "")
    marsfacts_html

    hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemisphere_url)
    time.sleep(2)
    #Getting the base url
    # hemisphere_base_url = 'https://astrogeology.usgs.gov'
    

    # scrape images of Mars' hemispheres from the USGS site
    mars_hemisphere_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    hemisphere_results = []

    for i in range(1,9,2):
        hemisphere_dict = {}
        
        browser.visit(mars_hemisphere_url)
        time.sleep(1)
        hemispheres_html = browser.html
        hemispheres_soup = bs(hemispheres_html, 'html.parser')
        hemispherenamelinks = hemispheres_soup.find_all('a', class_='product-item')
        hemispherename = hemispherenamelinks[i].text.strip('Enhanced')
        
        linkdetail = browser.find_by_css('a.product-item')
        linkdetail[i].click()
        time.sleep(1)
        browser.find_link_by_text('Sample').first.click()
        time.sleep(1)
        browser.windows.current = browser.windows[-1]
        hemisphereimgage_html = browser.html
        browser.windows.current = browser.windows[0]
        browser.windows[-1].close()
        
        hemisphereimgage_soup = bs(hemisphereimgage_html, 'html.parser')
        hemisphereimage_path = hemisphereimgage_soup.find('img')['src']

        hemisphere_dict['title'] = hemispherename.strip()
        
        hemisphere_dict['img_url'] = hemisphereimage_path

        hemisphere_results.append(hemisphere_dict)

    # create a dictionary containing the collected data for later use in flask app
    marsinfo={"news_title":news_title,
            "news_paragraph":news_paragraph,
            "fullimgurl":fullimgurl,
            "marsweather":marsweather,
            "marsfacts_html":marsfacts_html,
            "hemisphere_results":hemisphere_results  
            }
    #Close the browser after scraping
    browser.quit()

    #Return data
    return marsinfo