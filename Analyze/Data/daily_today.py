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
    file_name = "./Data/daily/" + now.strftime("%Y%m%d") + ".csv"
    stock_df.to_csv(file_name, index=False)
    print(f"实时股票数据已保存至 {file_name}")
    return stock_df

# 直接在if语句块中编写代码
if __name__ == '__main__':
    # 调用函数获取指定日期范围的数据
    # begin_date = '2023-01-01'
    # end_date = '2023-01-05'
    # get_data_by_date_range(begin_date, end_date)
    get_all_real_time()
