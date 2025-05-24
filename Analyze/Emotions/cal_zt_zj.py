# -*- coding: utf-8 -*-

#获取最高板
def get_highest_board(lbs):
    maxlb = 0
    for lb in lbs:
        if lb > maxlb:
            maxlb = lb
    return maxlb

# 序号,代码,名称,涨跌幅,最新价,成交额,流通市值,总市值,换手率,封板资金,首次封板时间,最后封板时间,炸板次数,涨停统计,连板数,所属行业
#计算涨停板股票总的封板金额，以及成交额
def cal_zt_zj(file):
    import pandas as pd
    dfs = pd.read_csv(file)
    gpmc = dfs['名称'].to_list()
    fbzj = dfs['封板资金'].to_list()
    fbcj = dfs['成交额'].to_list()
    zt = dfs['涨停统计'].to_list()
    lbs = dfs['连板数'].to_list()
    dwb = get_highest_board(lbs)/3
    zt_zj = 0
    zt_cj = 0
    #低位板股票的总资金,当天最高板的三份之一,定义为低位板股票
    dw_cj = 0
    dw_zj = 0
    #高位板股票的总资金
    gw_cj = 0
    gw_zj = 0
    for i in range(len(zt)):
        # print(gpmc[i],fbzj[i],fbcj[i],zt[i])
        zt_zj += fbzj[i]
        zt_cj += fbcj[i]
        if lbs[i] <= dwb:
            dw_cj += fbzj[i]
            dw_zj += fbcj[i]
        else:
            gw_cj += fbzj[i]
            gw_zj += fbcj[i]
    #将资金转为亿为单位
    zt_zj = zt_zj / 100000000
    zt_cj = zt_cj / 100000000
    dw_cj = dw_cj / 100000000
    dw_zj = dw_zj / 100000000
    gw_cj = gw_cj / 100000000
    gw_zj = gw_zj / 100000000
    print(f"低位板股票的总资金: {dw_cj}")
    print(f"低位板股票的总成交额: {dw_zj}")
    print(f"高位板股票的总资金: {gw_cj}")
    print(f"高位板股票的总成交额: {gw_zj}")
    print(f"涨停板股票的总资金: {zt_zj}")
    print(f"涨停板股票的总成交额: {zt_cj}")
    return zt_zj,zt_cj,dw_cj,dw_zj,gw_cj,gw_zj


#计算涨停板股票总的封板金额，以及成交额
def cal_zt_zj_simple(file):
    import pandas as pd
    dfs = pd.read_csv(file)
    gpmc = dfs['名称'].to_list()
    fbzj = dfs['封板资金'].to_list()
    fbcj = dfs['成交额'].to_list()
    zt = dfs['涨停统计'].to_list()
    lbs = dfs['连板数'].to_list()
    dwb = get_highest_board(lbs)/3
    zt_zj = 0
    zt_cj = 0
    for i in range(len(zt)):
        # print(gpmc[i],fbzj[i],fbcj[i],zt[i])
        zt_zj += fbzj[i]
        zt_cj += fbcj[i]
    #将资金转为亿为单位
    zt_zj = zt_zj / 100000000
    zt_cj = zt_cj / 100000000
    print(f"涨停板股票的总资金: {zt_zj}")
    print(f"涨停板股票的总成交额: {zt_cj}")
    return zt_zj,zt_cj

if __name__ == '__main__':
    import os
    import time
    files = os.listdir("./Data/zt")
    files.sort()
    print(files)
    fb_zj = []
    fb_cj = []
    fb_fcb = []
    for file in files:
        zt_zj,zt_cj = cal_zt_zj_simple("./Data/zt/"+file)
        fb_zj.append(zt_zj)
        fb_cj.append(zt_cj)
        fb_fcb.append(zt_zj/zt_cj)

    #画图,分割成两个图，涨停资金以及涨停成交额在一个图中，涨停资金/涨停成交额在一个图中
    import matplotlib.pyplot as plt
    import numpy as np
    #设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    #设置画布大小
    plt.figure(figsize=(10,10))
    #设置子图
    plt.subplot(2,1,1)
    #设置标题
    plt.title("涨停资金/涨停成交额")
    #设置x轴标签
    plt.xlabel("日期")
    #设置y轴标签
    plt.ylabel("资金/成交额")
    #设置x轴刻度
    plt.xticks(np.arange(0,len(files),1),files)
    #设置y轴刻度
    plt.yticks(np.arange(0,max(fb_fcb),0.01))
    #设置网格
    plt.grid(True)
    #设置线条颜色
    plt.plot(fb_fcb,color='red')
    #设置子图
    plt.subplot(2,1,2)
    #设置标题
    plt.title("涨停资金/涨停成交额")
    #设置x轴标签
    plt.xlabel("日期")
    #设置y轴标签
    plt.ylabel("资金/成交额")
    #设置x轴刻度
    plt.xticks(np.arange(0,len(files),1),files)
    #设置y轴刻度
    # plt.yticks(np.arange(0,max(fb_fcb),0.01))

    #设置网格
    plt.grid(True)
    #设置线条颜色
    plt.plot(fb_zj,color='red')
    plt.plot(fb_cj,color='blue')
    #保存图片
    # plt.savefig("./Data/zt/zt_fb_fcb.png")
    #显示图片
    plt.show()



   

   
    
    
 
