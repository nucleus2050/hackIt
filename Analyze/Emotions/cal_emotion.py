
import cal_history_point
import cal_history_zt


if __name__ == '__main__':
    import os
    files = os.listdir("./Data/history")
    files.sort()
    print(files)
    points_all = []
    points_zt  = []
    cnt_zt     = []
    fileIndex = 0
    for file in files:
        fileIndex += 1
        point = cal_history_point.cal_history_point("./Data/history/"+file)
        points_all.append(point)
        #如果不是第一个数据文件，计算涨停股票，否则则将涨停挣钱效应默认赋值为50.0
        if fileIndex > 1:
            pre_file = files[fileIndex-2]
            ztdict = cal_history_zt.get_all_zt_code("./Data/history/"+pre_file)
            #计算涨停股票的平均收益
            ztpoint = cal_history_zt.cal_stock_point("./Data/history/"+file,ztdict)
            points_zt.append(ztpoint)
            cnt_zt.append(len(ztdict))
        else:
            points_zt.append(50.0)
            cnt_zt.append(50)
    #将所有股票和涨停股票的挣钱效应各自绘制到一个子图中,将两者的差值也绘制到另外一个子图中，横轴为时间，纵轴为挣钱效应
    import matplotlib.pyplot as plt
    import numpy as np
    files = [file[:-4] for file in files]
    #获取横轴
    x = np.arange(len(points_all))
    #获取纵轴
    y_all = points_all
    y_zt = points_zt
    #画图
    
    # plt.figure(figsize=(20,10))
    plt.subplot(2,1,1)
    plt.xticks(x,files,rotation=90)
    plt.plot(x,y_all,label='all')
    plt.plot(x,y_zt,label='zt')
    plt.legend()
    #计算差值
    y_diff = []
    for i in range(len(y_all)):
        y_diff.append(y_zt[i]-y_all[i])
    plt.subplot(2,1,2)
    plt.xticks(x,files,rotation=90)
    plt.plot(x,y_diff,label='diff')
    plt.plot(x,cnt_zt,label='cnt')
    plt.legend()
    plt.show()


