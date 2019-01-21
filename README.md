# KuAnDA
抓取酷安数据进行分析<br>
酷安是目前比较活跃的安卓应用市场，本次抓取的是网页端

一、scrapy抓取数据：<br>
本次抓取采用了scrapy框架，其中kuspider文件夹就是所有的程序文件，<br>
1、从应用页面开始抓取，响应内容传到parse函数进行应用列表采集，然后采用循环的方式对所有页面进行采集：<br>

```Python
def start_requests(self):

        pages = []
        for page in range(1,570):
            url = 'https://www.coolapk.com/apk?p=%s' % page
            page = scrapy.Request(url,callback=self.parse)
            pages.append(page)
        return pages


def parse(self, response):
        contents = response.css('.app_left_list>a')
        for content in contents:
            url = content.css('::attr("href")').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(url,callback=self.parse_url,dont_filter=True)
```            
 2、抓取关键字段，创建数据处理的item，数据入库：<br>
 ```Python
class KuspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    volume = scrapy.Field()
    download = scrapy.Field()
    follow = scrapy.Field()
    comment = scrapy.Field()
    tags = scrapy.Field()
    score = scrapy.Field()
    num_score = scrapy.Field()
 
 def parse_url(self,response):
        item = KuspiderItem()
        item['name'] = response.css('.detail_app_title::text').extract_first()
        results = self.get_comment(response)
        item['volume'] = results[0]
        item['download'] = results[1]
        item['follow'] = results[2]
        item['comment'] = results[3]
        item['tags'] = self.get_tags(response)
        item['score'] = response.css('.rank_num::text').extract_first().encode('utf-8')
        num_socore = response.css('.apk_rank_p1::text').extract_first().encode('utf-8')
        item['num_score'] = re.search('共(.*?)个评分',num_socore).group(1)
        yield item
```

其中get_comment和get_tags函数对特殊字段进行抓取转换：<br>
```Python
def get_comment(self,response):
        message = response.css('.apk_topba_message::text').extract_first().encode('utf-8')
        result = re.findall(r'\s+(.*?)\s+/\s+(.*?)下载\s+/\s+(.*?)人关注\s+/\s+(.*?)个评论.*?',message)
        if result:
            results = list(result[0])
            return results

def get_tags(self,response):
        data = response.css('.apk_left_span2')
        tags = [item.css('::text').extract_first() for item in data]
        return tags
```

3、将数据存入mongodb：<br>
```Python
import pymongo

class KuspiderPipeline(object):
    def __init__(self,mongo_url,mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            mongo_url= crawler.settings.get('MONGO_URL'),
            mongo_db= crawler.settings.get('MONGO_DB')
        )

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        name = item.__class__.__name__
        self.db[name].insert(dict(item))
        return item

    def close_spider(self,spider):
        self.client.close()
 ```
        
二、利用pandas, matplotlib进行数据可视化呈现：<br>
kuandata.py为主要的数据清理分析代码，<br>
主要分析了下载量、评分、标签等字段，从区间分布和排名等角度分析，文件中的png图片是最终的可视化效果。<br>
```Python
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
    plt.savefig('/Users/Desktop/kuan/app下载量排名.png')
```


