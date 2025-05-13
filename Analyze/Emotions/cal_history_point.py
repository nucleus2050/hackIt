
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
    #获取Data目录下的所有csv文件，并且按照日期排序，依次计算
    #获取Data目录下的所有csv文件
    import os
    files = os.listdir("./Data/history")
    files.sort()
    print(files)
    #依次计算
    points = []
    points5Days = []
    pointIndex = 0
    for file in files:
        # print(file)
        pointIndex += 1
        point = cal_history_point("./Data/history/"+file)
        print(file,point)
        points.append(point)
        #计算最近5天的平均挣钱效应，并且将结果保存到points5Days数组中，如果不足5天，则计算最近的天数的平均挣钱效应
        #如果不足5天，则计算最近的天数的平均挣钱效应
        if pointIndex < 5:
            points5Days.append(sum(points)/pointIndex)
        else:
            points5Days.append(sum(points[pointIndex-5:pointIndex])/5)
        


    #画曲线图，横轴为日期，纵轴为挣钱效应，最低0，最高100,并且在横轴上标注日期,并且在纵轴上标注最近5天的平均挣钱效应
    #使用matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    #获取横轴
    x = np.arange(len(points))
    #获取纵轴
    y = points
    #画图
    plt.plot(x,y)
    #标注日期
    #将files中的.csv去掉
    files = [file[:-4] for file in files]
    plt.xticks(x,files,rotation=50)
    #标注最近5天的平均挣钱效应
    plt.plot(x,points5Days)
    #显示图形
    plt.show()