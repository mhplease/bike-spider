#this script goes through and searches all the listing titles for their makes and includes them in the column
#this should be added to the main script to do this in real time too.

import sqlite3
from flashtext import KeywordProcessor

keywordprocessor = KeywordProcessor()


#connect to sqlite
conn = sqlite3.connect('bikes3.sqlite')
cur = conn.cursor()


#store the makes in a tuple that's ordered by most common
cur.execute('SELECT make FROM countMakes ORDER BY count DESC')
makeList=cur.fetchall()

newList=[]

for item in makeList:
    newList.append(item[0])

keywordprocessor.add_keywords_from_list(newList)


# makeTup=[]

# for item in makeList:
#     makeTup.append(item[0])

# makeTup=tuple(makeTup)
    
   
#get the listings
cur.execute('SELECT * FROM Listings')
data=cur.fetchall()

inc=0

#go through all the listings
for x in data:
    # try:
    if x[0] != None:
        #get the stripped title
        stripped=x[0].strip().lower()
        # print(stripped)
        
        Extractedkeywords = keywordprocessor.extract_keywords(stripped)
        print(Extractedkeywords)
        if len(Extractedkeywords) > 0:
            cur.execute("UPDATE Listings SET brand = ? WHERE title = ?", (Extractedkeywords[0],x[0]))
        else:
            cur.execute("UPDATE Listings SET brand = ? WHERE title = ?", ('other',x[0]))
    inc+=1
    print(inc)
    conn.commit()
    
conn.close()
print('connection closed')