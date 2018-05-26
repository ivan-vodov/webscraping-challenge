# Dependencies
from bs4 import BeautifulSoup
from splinter import Browser
from math import trunc
import requests
import pymongo
import time
import pandas as pd

# browser init for splinter

def scrape(db):
# open browser window using splinter
    try:
        executable_path = {"executable_path": r"C:/chromedriver.exe"}
        browser=Browser("chrome", **executable_path, headless=False)
    except Exception as e:
        print(e)
        raise Exception("Error while initiating the scraping driver.")


    # # Scraping

    # ## NASA Mars News
    # Note: the content (list of news) is parsed using Splinter as using just page source with BeautifulSoup returns narrower and not the latest results

    # open page with splinter
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    # wait for page content to be generated
    time.sleep(5)


    # get into b/s, get list of elements to extract the data from
    soup = BeautifulSoup(browser.html, 'lxml')
    result=soup.find('div', class_='list_text')
    
    #Extract title and teaser into variables
    news_title=result.find('div', class_='content_title',recursive=True).text
    news_title=news_title.replace('\n', ' ').replace('\r', '').strip()
    news_p=result.find('div', class_='article_teaser_body',recursive=True).text
    news_p=news_p.replace('\n', ' ').replace('\r', '').strip()

    # ## JPL Mars Space Images - Featured Image

    # open page with splinter
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=mars'
    browser.visit(url)
    # click the button opening the featured image
    browser.click_link_by_id('full_image')
    # wait for page content to be generated
    time.sleep(5)
    # click the button opening details page for the featured image
    browser.click_link_by_partial_text('more info')

    soup = BeautifulSoup(browser.html, 'lxml')
    results=soup.find_all('div', class_='download_tiff')
    featured_image_url=''

    for result in results:
        if ('jpg' in result.find('a').text):
            featured_image_url= 'https:'+result.find('a')['href']    
      

    # ## Mars Weather

    # In[13]:


    url='https://twitter.com/marswxreport?lang=en'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    # get into b/s, get list of elements to extract the data from
    mars_weather=soup.find('p', class_='TweetTextSize').text

    # ## Mars Facts

    url = 'https://space-facts.com/mars/s'
    tables = pd.read_html(url)
    df = tables[0]
    df.columns = ['Parameter', 'Value']
    df.set_index('Parameter',inplace=True)
    mars_facts = df.to_html().replace('\n', '').\
    replace('<tr style="text-align: right;">      <th></th>      <th>Value</th>    </tr>','').\
    replace('<thead>        <tr>      <th>Parameter</th>      <th></th>    </tr>  </thead>','').\
    replace('border="1" class="dataframe"','')


    # ## Mars Hemisperes

    # open page with splinter
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    host= 'https://astrogeology.usgs.gov'
    browser.visit(url)
    time.sleep(5)

    #extract links to Mars Hemispehere images
    soup = BeautifulSoup(browser.html, 'lxml')
    results=soup.find_all('a', class_='product-item',recursive=True)

    mars_hemispheres=[]
    thumb_urls=[]
    titles=[]
    img_page_urls=[]


    # locate and extract hemisphere's names and a links to pages with full-size images
    for i in range(trunc(len(results)/2)):
        # Error handling
        try:
            thumb_url=host + results[2*i].img['src']
            title = results[2*i+1].text         
            img_page_url= host + results[2*i+1]['href']
            # Run only if all is available
            if (title and img_page_url and thumb_url):
                thumb_urls.append(thumb_url)
                titles.append(title)
                img_page_urls.append(img_page_url)
        except Exception as e:
            print(e)
            raise Exception("Error occurred while scraping data")

    print(thumb_urls)
    print(titles)
    print(img_page_urls)


    # Extract full res image URL from each hemisphere's page
    img_urls=[]
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    for img_page_url in img_page_urls:
        browser.visit(img_page_url)
        soup = BeautifulSoup(browser.html, 'lxml')
        result=soup.find('a', text='Original', recursive=True)
        img_urls.append(result['href'])
        browser.visit(url)

    # create a dictionary with Mars hemispheres data via a dataframe 
    mars_hemispheres_imgs={}
    mars_hemispheres_imgs=pd.DataFrame.from_items([('title', titles), ('img_url',img_urls)]).to_dict('records')

    # create a dictionary with all the data collected
    mars_record= {
            'news_title': news_title,
            'news_p': news_p,
            'featured_image_url': featured_image_url,
            'mars_weather': mars_weather,
            'mars_facts': mars_facts,
            'hemisphere_image_urls': mars_hemispheres_imgs
        }

    # Delete previous data and insert new into Mongo DB
    db.items.delete_many({})
    db.items.insert_one(mars_record)



