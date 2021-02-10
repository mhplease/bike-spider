#this script grabs all the bike prices from craigslist and puts them into a database
#another script was used to build the table of bike makers

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import re
import numpy as np
import sqlite3


# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#get all the US CL cities
cityurl='https://www.craigslist.org/about/sites'
html = urllib.request.urlopen(cityurl, context=ctx).read()
soup = BeautifulSoup(html, 'html.parser')
countries = soup.find_all('div', 'colmask')
citytags=countries[0].find_all('a')
citylink=[]

#connect to sqlite
conn = sqlite3.connect('bikes3.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Listings')
cur.execute('CREATE TABLE IF NOT EXISTS Listings (title TEXT, location TEXT, price INTEGER, brand TEXT)')

#open the csv writer
# with open('bikecounts.csv', 'w', newline='') as csvfile:
# writez=csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    
#iterate through cities
for x in citytags:
    citylink = x.get('href')
    citylink = re.findall('(.*//.*?/)', citylink)
    citylink=citylink[0]
    region=str(x.text)
  
    url=citylink+'search/bik?query=-kids+-girls+-boys+-electric&min_price=2&max_price=20000'
    # print(url)
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    
    #find the total number of posts to find the limit of the pagination
    results_num = soup.find('div', class_= 'search-legend')
    # print(results_num)
    
    #check for more than one page of results
    if results_num.find('span', class_='totalcount') is not None:
        results_total = int(results_num.find('span', class_='totalcount').text) #pulled the total count of posts as the upper bound of the pages array
        
        #each page has 119 [ed: each page shows 120] posts so each new page is defined as follows: s=120, s=240, s=360, and so on. So we need to step in size 120 in the np.arange function
        pages = np.arange(0, results_total+1, 120)
    
        iterations = 0 
        count=0
        
        #variable for summing prices
        summer=0    
        
        
        #how this should work:
        
        #get the listing title and check if it's in database
        #if not, add it to the database with listing city
        #add the listing price in the next column
        
        
        #iterate through all the pages of results
        for page in pages:
            
            #get all the listings
            posts = soup.find_all('li', class_= 'result-row')
            
            #iterate through the listings        
            for post in posts:
                
                #get the listing title
                tyte=post.find('h3', class_='result-heading').text
                tyte=tyte.strip()
                                    
                #get the price from the listing
                price=re.findall('\$(.*)', post.a.text.strip().replace(',',''))
                if price == []:
                    continue
                #store it in the database
                cur.execute('INSERT INTO Listings (title, location, price, brand) VALUES (?, ?, ?, 0)', (tyte, region, int(price[0])))
                conn.commit()
                count+=1
                summer=summer+int(price[0])
            iterations+=1
        
        # writez.writerow([citylink,count,int(summer/count)])
        print(count, "bikes counted on", iterations, "pages. Average price: $", int(summer/count), "in", citylink)
    else:
        continue

#play a bell
print('\a')

#close sqlite connection
conn.close()
