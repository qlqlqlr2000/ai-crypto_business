#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time


# In[2]:


import requests


# In[3]:


import pandas as pd


# In[4]:


from datetime import datetime
import time


# In[ ]:


with open("2022-11-10-bithumb-BTC-orderbook.csv", "w") as file:
    file.write("price,quantity,type,timestamp\n")
    
while(1):
 
    book = {}
    response = requests.get('https://api.bithumb.com/public/orderbook/BTC_KRW/?count=10')
    book = response.json()

    data = book['data']

    bids = pd.DataFrame(data['bids']).apply(pd.to_numeric, errors='ignore')
    bids.sort_values('price', ascending=False, inplace=True)
    bids = bids.reset_index(drop=True)  # Reset index without creating a new column
    bids['type'] = 0

    asks = pd.DataFrame(data['asks']).apply(pd.to_numeric, errors='ignore')
    asks.sort_values('price', ascending=True, inplace=True)
    asks['type'] = 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.concat([bids, asks], ignore_index=True)  # Concatenate bids and asks
    df['timestamp'] = timestamp
    print(df, timestamp)
    
    
    df.to_csv("2022-11-10-bithumb-BTC-orderbook.csv", mode='a')

    time.sleep(5)


# In[ ]:




