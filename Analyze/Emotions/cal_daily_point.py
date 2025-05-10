
#计算当天挣钱效应
#参数：
#high：最高价,数组
#low：最低价,数组
#close：收盘价,数组
#返回值：
#point：挣钱效应
def cal_daily_point(high,low,close):
    #遍历每一个股票
    point = 0
    for i in range(len(high)):
        #计算当天的挣钱效应
        #close/low/high转为float
        # print(high[i],low[i],close[i])
        h = float(high[i])
        l = float(low[i])
        c = float(close[i])
        if h == l and c == l:
            point += 100
        else :
            point += (c - l) * 100 / (h-l)
        
    return point/len(high)


def cal_history_point(csv_path):
    import os
    import pandas as pd
    #读取csv文件,只获取最高、最低、收盘列
    df = pd.read_csv(csv_path, usecols=[4,5,6])
    #获取最高价、最低价、收盘价
    high = df['最高'].tolist()
    low = df['最低'].tolist()
    close = df['收盘'].tolist()
    #计算当天的挣钱效应
    point = cal_daily_point(high,low,close)
    return point


def cal_today_point(csv_path):
    import os
    import pandas as pd
    #读取csv文件,只获取最高、最低、收盘列
    df = pd.read_csv(csv_path, usecols=[9,10,3])
    #获取最高价、最低价、收盘价
    high = df['最高'].tolist()
    low = df['最低'].tolist()
    close = df['最新价'].tolist()
    #计算当天的挣钱效应
    point = cal_daily_point(high,low,close)
    return point

if __name__ == '__main__':
    point = cal_history_point("./Data/history/20250509.csv")
    print(point)
    # point = cal_today_point("./Data/daily/20250509.csv")
    # print(point)