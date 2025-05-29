import akshare as ak
import daily_history
import os
import datetime

#获取指定日期涨停的股票
def get_all_zt_code(date):
    #获取指定日期的股票列表
    # 修改第7行接口调用
    stock_zt_df = ak.stock_zt_pool_em(date=date)
    print(date,len(stock_zt_df))
    #将涨停股票所有信息保持到Data/history_zt/目录下
    stock_zt_df.to_csv("./Data/zt/"+date+".csv",index=False)

def get_all_zt_code_real_time(date):
    #获取当天的股票列表
    stock_zt_df = ak.stock_zt_pool_em(date=date)
    print(len(stock_zt_df))
    #将涨停股票所有信息保持到Data/daily/zt/日期 目录下,文件名为年月日时分.csv
    #判断"./Data/daily/zt/"+date 目录是否存在，如果不存在则创建
    if not os.path.exists("./Data/daily/zt/"+date):
        os.makedirs("./Data/daily/zt/"+date)
    #获取当前时间,并将时间转换为年月日时分
    now = datetime.datetime.now()
    file_name = "./Data/daily/zt/"+date + "/" + now.strftime("%Y%m%d%H%M") + ".csv"
    stock_zt_df.to_csv(file_name, index=False)
    print(f"实时股票数据已保存至 {file_name}")
    return stock_zt_df

#获取指定日期炸板的股票
def get_all_zb_code_real_time(date):
    #获取当天的股票列表
    stock_zb_df = ak.stock_zt_pool_zbgc_em(date=date)
    print(len(stock_zb_df))
    if not os.path.exists("./Data/daily/zb/"+date):
        os.makedirs("./Data/daily/zb/"+date)
    #获取当前时间,并将时间转换为年月日时分
    now = datetime.datetime.now()
    file_name = "./Data/daily/zb/"+date + "/" + now.strftime("%Y%m%d%H%M") + ".csv"
    stock_zb_df.to_csv(file_name, index=False)
    print(f"实时股票数据已保存至 {file_name}")
    return stock_zb_df

if __name__ == '__main__':
    date_list = daily_history.get_trace_date_list( '2025-05-23','2025-05-29')
    for date in date_list:
        DateForm = date.strftime('%Y%m%d')
        get_all_zt_code(DateForm)