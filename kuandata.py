import pymongo
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import font_manager
from collections import Counter

my_font = font_manager.FontProperties(fname='/Library/Fonts/MFLangQian_Noncommercial-Bold.otf',size=12)

def data_processing(df):
    str = '_ori'
    cols = ['comment', 'download', 'follow', 'num_score', 'volume']
    for col in cols:
        colori = col + str
        df[colori] = df[col]
        if not (col == 'volume'):
            df[col] =clean_symbol(df,col)
        else:
            df[col] = clean_symbol2(df,col)
    df['download'] = df['download'].apply(lambda x:x/10000)
    df = df.apply(pd.to_numeric,errors='ignore')
    #以同名为标准进行去重
    df = df.drop_duplicates(['name'])
    df = df.sort_values(by='download',ascending=False)
    return df

def clean_symbol(df,col):
    con = df[col].str.contains('万$')
    df.loc[con,col] = pd.to_numeric(df.loc[con,col].str.replace('万','')) * 10000
    df[col] = pd.to_numeric(df[col])
    return df[col]

def clean_symbol2(df,col):
    df[col] = df[col].str.replace('M$','')
    con = df[col].str.contains('K$')
    df.loc[con,col] = pd.to_numeric(df.loc[con,col].str.replace('K$',''))/1024
    df[col] = pd.to_numeric(df[col])
    return df[col]

#绘制下载量排名
def download_distribute(df):
    bins = [0,10,100,500,10000]
    group_names = ['<=10万','10-100万','100-500万','>500万']
    y_ticks = [0,1000,2000,3000,4000,5000,6000]
    cats = pd.cut(df['download'],bins,labels=group_names)
    cats = pd.value_counts(cats)
    plt.figure(figsize=(24,12))
    ax = cats.plot(kind='bar',width=0.3)
    plt.title('App下载量区间分布',fontproperties=my_font,fontsize=24,color='#C71585')
    ax.set_xticklabels(group_names,rotation=45,fontproperties=my_font,fontsize=20)
    ax.set_yticklabels(y_ticks,fontsize=20)
    plt.legend(loc='upper right',prop=my_font)
    for x,y in zip(ax.get_xticks(),cats.values):
        plt.text(x,y+0.1,y,ha='center',fontsize=20)
    plt.savefig('/Users/xiangchao/Desktop/kuan/app下载量排名.png')

#下载量最多的app
def download_ranking(df):
    most_down = df.loc[:,['download','name']].sort_values(by='download',ascending=False).head(20)
    most_down = most_down.sort_values(by='download',ascending=True)
    x_ticks = list(most_down['download'])
    y_ticks = list(most_down['name'])
    plt.figure(figsize=(18,72),dpi=80)
    ax = most_down.plot(kind='barh',width=0.5)
    plt.title('App下载量排名前20位(单位：万)',fontproperties=my_font,fontsize=16,color='#C71585')
    ax.set_yticklabels(y_ticks,fontproperties=my_font,fontsize=8)
    plt.legend(loc='lower right',prop=my_font)
    for x,y in zip(x_ticks,ax.get_yticks()):
        plt.text(x+10,y,int(x),ha='center',fontsize=8)
    plt.savefig('/Users/xiangchao/Desktop/kuan/app下载量排名前20.png')

#评分区间分布
def score_ditribute(df):
    bins = [0,3,4,4.5,5]
    group_names = ['0~3分','3~4分','4~4.5分','4.5~5分']
    cats = pd.cut(df['score'],bins,labels=group_names)
    cats = pd.value_counts(cats)
    plt.figure(figsize=(24,12))
    ax = cats.plot(kind='bar',width=0.3)
    plt.title('App评分区间分布',fontproperties=my_font,fontsize=24,color='#C71585')
    ax.set_xticklabels(group_names,rotation=45,fontproperties=my_font,fontsize=20)
    plt.legend(loc='upper right',prop=my_font)
    for x,y in zip(ax.get_xticks(),cats.values):
        plt.text(x,y+0.1,y,ha='center',fontsize=20)
    plt.savefig('/Users/xiangchao/Desktop/kuan/app评分区间分布.png')

#评分排名
def score_ranking(df):
    most_score = df.loc[:,['download','score','name']].sort_values(by='download',ascending=False).sort_values(by='score',ascending=False).head(20)
    most_score = most_score.sort_values(by='download',ascending=True)
    x_ticks = list(most_score['score'])
    y_ticks = list(most_score['name'])
    ax = most_score.plot(kind='barh')
    ax.set_title('评分排名前20的APP',fontproperties=my_font,fontsize=12,color='#C71585')
    ax.set_yticklabels(y_ticks,fontproperties=my_font,fontsize=8)
    for x,y in zip(x_ticks,ax.get_yticks()):
        plt.text(x+5,y,x,ha='center',fontsize=8)
    plt.savefig('/Users/xiangchao/Desktop/kuan/app评分前20.png')



if __name__ == '__main__':
    client = pymongo.MongoClient(host='localhost',port=27017)
    db = client['KuAn']
    collection = db['KuspiderItem']
    data = pd.DataFrame(list(collection.find()))
    df = data_processing(data)
    # download_distribute(df)
    # download_ranking(df)
    # score_ditribute(df)
    # score_ranking(df)
    hot_tag_distribute(df)


