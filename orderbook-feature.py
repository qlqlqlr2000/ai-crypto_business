#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

# CSV 파일을 DataFrame으로 로드합니다.
df = pd.read_csv('2023-11-15-upbit-BTC-book.csv').apply(pd.to_numeric, errors='ignore')
gr_o = df.groupby(['timestamp'])

# 가상의 cal_mid_price 함수 정의
def cal_mid_price(bid_level, ask_level):
    mid_price = (bid_level['price'].max() + ask_level['price'].min()) / 2
    bid = bid_level['price'].max()
    ask = ask_level['price'].min()
    bid_qty = bid_level['quantity'].sum()
    ask_qty = ask_level['quantity'].sum()

    return mid_price, bid, ask, bid_qty, ask_qty

def compute_book_imbalance(df, ratio, level, interval):
    result_df = pd.DataFrame()

    for timestamp, group in df.groupby(['timestamp']):
        bid_levels = group[group['type'] == 0].head(level)
        ask_levels = group[group['type'] == 1].head(level)

        bid_qty_sum = (bid_levels['quantity'] ** ratio).sum()
        bid_price_sum = (bid_levels['price'] * (bid_levels['quantity'] ** ratio)).sum()

        ask_qty_sum = (ask_levels['quantity'] ** ratio).sum()
        ask_price_sum = (ask_levels['price'] * (ask_levels['quantity'] ** ratio)).sum()

        book_price = (bid_qty_sum * ask_price_sum / ask_qty_sum) + (ask_qty_sum * bid_price_sum / bid_qty_sum) / (bid_qty_sum + ask_qty_sum)

        # mid_price 계산 및 DataFrame에 추가
        mid_price, _, _, _, _ = cal_mid_price(bid_levels, ask_levels)

        book_imbalance = book_price - mid_price

        result_df = pd.concat([result_df, pd.DataFrame({
            'timestamp': [timestamp],
            'mid_price': [mid_price],
            'book_imbalance': [book_imbalance]
            # 다른 특징들을 여기에 추가
        })], ignore_index=True)

    return result_df

# CSV로 쓰기 전용 DataFrame 초기화
output_df = pd.DataFrame()

# 하나씩(매초데이터)읽어오기
for timestamp, group in gr_o:
    gr_bid_level = group[(group.type == 0)]
    gr_ask_level = group[(group.type == 1)]
    
    # calculate_mid_price 함수 호출
    mid_price, bid, ask, bid_qty, ask_qty = cal_mid_price(gr_bid_level, gr_ask_level)
    
    # Compute book imbalance
    ratio = 0.2
    level = 5
    interval = 1
    result_df_book = compute_book_imbalance(group, ratio, level, interval)

    # 결과를 DataFrame에 추가
    result_df = pd.DataFrame({
        'timestamp': [timestamp],
        'mid_price': [mid_price],
        'book_imbalance': result_df_book['book_imbalance'].values[0]
        # 다른 특징들을 여기에 추가
    })

    # DataFrame을 output_df에 추가
    output_df = pd.concat([output_df, result_df], ignore_index=True)

# 결과를 CSV로 저장
output_df.to_csv('output3.csv', mode='a', header=False, index=False)

