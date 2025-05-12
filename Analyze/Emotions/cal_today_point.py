

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
    #获取当天日期
    import datetime
    now = datetime.datetime.now()
    #获取Data目录下的所有csv文件，并且按照日期排序，依次计算
    #获取Data目录下的所有csv文件

    import os
    files = os.listdir("./Data/daily/"+datetime.datetime.now().strftime("%Y%m%d"))
    files.sort()
    print(files)
    #依次计算
    points = []
    for file in files:
        # print(file)
        point = cal_history_point("./Data/daily/"+datetime.datetime.now().strftime("%Y%m%d")+file)
        print(file,point)
        points.append(point)
    #画曲线图，横轴为日期，纵轴为挣钱效应，最低0，最高100,并且在横轴上标注日期
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
    plt.xticks(x,files,rotation=50)
    #显示图形
    plt.show()