import akshare as ak
import pandas as pd

#获取当天实时行情数据
#参数：
#无
#返回值：
#包含所有股票实时行情数据的列表
def get_all_real_time():
    # 获取所有股票的实时行情数据
    try:
        stock_df = ak.stock_zh_a_spot_em()
        #遍历每只股票，过滤掉停牌和退市的股票
        # 1. 过滤掉总市值为0的股票
        stock_df = stock_df[stock_df["总市值"] != 0.0]
        
        # 2. 过滤掉名称中包含"退"的股票（退市股票）
        stock_df = stock_df[~stock_df["名称"].str.contains("退", na=False)]
        
        # 3. 过滤掉名称中包含"PT"的股票（特别处理的股票，通常是停牌或问题股票）
        stock_df = stock_df[~stock_df["名称"].str.contains("PT", na=False)]
        
        # 4. 过滤掉成交量为0的股票（可能是停牌股票）
        if "成交量" in stock_df.columns:
            stock_df = stock_df[stock_df["成交量"] > 0]
        
        # 5. 过滤掉最新价为0或NaN的股票
        if "最新价" in stock_df.columns:
            stock_df = stock_df[stock_df["最新价"] > 0]
        
        print(f"过滤后剩余 {len(stock_df)} 只股票")
    except Exception as e:
        print(f"获取股票列表失败: {e}")
    #将实时股票数据保持到csv文件中,文件名为年月日.csv
    import datetime
    now = datetime.datetime.now()
    #获取年月日分钟
    import os
    #判断"./Data/daily/"+now.strftime("%Y%m%d") 目录是否存在，如果不存在则创建
    if not os.path.exists("./Data/daily/"+now.strftime("%Y%m%d")):
        os.makedirs("./Data/daily/"+now.strftime("%Y%m%d"))
    #保存到csv文件中
    file_name = "./Data/daily/"+now.strftime("%Y%m%d") + "/" + now.strftime("%Y%m%d%H%M") + ".csv"
    stock_df.to_csv(file_name, index=False)
    print(f"实时股票数据已保存至 {file_name}")
    return stock_df

# 直接在if语句块中编写代码
if __name__ == '__main__':
    # 调用函数获取指定日期范围的数据
    # begin_date = '2023-01-01'
    # end_date = '2023-01-05'
    # get_data_by_date_range(begin_date, end_date)
    #常驻任务，每五分钟获取一次数据，并且只在开盘时间获取数据
    #获取当前时间

    
    #死循环
     while True:
        #如果当前时间小于9:15或者大于15:05，则休眠1分钟，否则则每五分钟获取一次数据
        #获取当前时间
        import datetime
        now = datetime.datetime.now()
        #如果当前时间小于9:15或者大于15:05，则休眠1分钟，否则则每五分钟获取一次数据
        import datetime
        now = datetime.datetime.now()
        if (now.hour < 9 and now.minute < 10)  or (now.hour >= 15 and now.minute > 5):
            print("当前时间不在开盘时间，休眠1分钟")
            import time
            time.sleep(60)
            continue
        if now.minute % 5 != 0:
            print("当前时间不在5分钟的倍数，休眠1分钟")
            import time
            time.sleep(60)
            continue
        else:
            print("开始获取数据：",now)
            get_all_real_time()
            print("获取数据完毕：",now)


        
