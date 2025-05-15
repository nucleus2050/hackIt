def cal_zt_point(stock_df):
    return 
    # 1. 计算每个股票的平均收益
    # 2. 计算每个股票的平均收益的标准差
    # 3. 计算每个股票的平均收益的标准差的平均值


#获取所有涨停股票的代码
def get_all_zt_code(file):
    # 读取文件
    import pandas as pd
    dfs = pd.read_csv(file,dtype={'股票代码': str})
    zdfs = dfs['涨跌幅'].to_list()
    codes = dfs['股票代码'].to_list()
    names = dfs['股票名'].to_list()
    ztdict = {}
    for i in range(len(zdfs)):
        #如果是主板股票，并且涨停
        if codes[i].startswith(('00','60')) and zdfs[i] >= 9.8:
            # print(f"主板涨停股票: {codes[i]} {names[i]} 涨幅: {zdfs[i]}")
            ztdict[codes[i]] = names[i]
        #如果是创业板或者科创板股票，并且涨停
        elif codes[i].startswith(('30','688')) and zdfs[i] >= 19.8:
            # print(f"创业板/科创板涨停股票: {codes[i]} {names[i]} 涨幅: {zdfs[i]}")
            ztdict[codes[i]] = names[i]
    return ztdict


#获取所有跌停股票的代码
def get_all_dt_code(file):
    import pandas as pd
    dfs = pd.read_csv(file,dtype={'股票代码': str})
    zdfs = dfs['涨跌幅'].to_list()
    codes = dfs['股票代码'].to_list()
    names = dfs['股票名'].to_list()
    ztdict = {}
    for i in range(len(zdfs)):
        #如果是主板股票，并且涨停
        if codes[i].startswith(('00','60')) and zdfs[i] <= -9.8:
            # print(f"主板涨停股票: {codes[i]} {names[i]} 涨幅: {zdfs[i]}")
            ztdict[codes[i]] = names[i]
        #如果是创业板或者科创板股票，并且涨停
        elif codes[i].startswith(('30','688')) and zdfs[i] <= -19.8:
            # print(f"创业板/科创板涨停股票: {codes[i]} {names[i]} 涨幅: {zdfs[i]}")
            ztdict[codes[i]] = names[i]
    return ztdict

#计算涨停股票的挣钱效应
def cal_stock_point(file,stockDict):
    import pandas as pd
    df = pd.read_csv(file,dtype={'股票代码': str})
    #获取股票代码、最高价、最低价、收盘价
    code = df['股票代码'].tolist()
    high = df['最高'].tolist()
    low = df['最低'].tolist()
    close = df['收盘'].tolist()
    #遍历每一个股票,并记录index
    index = 0
    point = 0
    for c in code:
        if c in stockDict:
            h = float(high[index])
            l = float(low[index])
            c = float(close[index])
            if h == l and c == l:
                point += 100
            else :
                point += (c - l) * 100 / (h-l)
        index += 1
    return point/len(stockDict)


if __name__ == '__main__':
    import os
    import time
    files = os.listdir("./Data/history")
    files.sort()
    print(files)
    #依次计算
    points = []
    points5Days = []
    pointIndex = 0
    ztpointList = []
    dtpointList = []
    for file in files:
        # print(file)
        pointIndex += 1
        ztdict = get_all_zt_code("./Data/history/"+file)
        dtdict = get_all_dt_code("./Data/history/"+file)
        if pointIndex < len(files):
            #获取下一天的所有涨停股票实际的挣钱效应
            next_ztdict = cal_stock_point("./Data/history/"+files[pointIndex],ztdict)
            print(f"涨停股票: {file} 实际的挣钱效应: {next_ztdict}")
            ztpointList.append(next_ztdict)
            
            if len(dtdict) > 0:
                next_dtdict = cal_stock_point("./Data/history/"+files[pointIndex],dtdict)
                dtpointList.append(next_dtdict)
                # print(f"跌停股票: {file} 实际的挣钱效应: {next_dtdict}")
            else:
                dtpointList.append(0)
    # print(ztpointList)
    # print(dtpointList)


