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

#计算当天炸板股票的总资金，以及成交额
def cal_zb_zj_simple(file):
    import pandas as pd
    dfs = pd.read_csv(file)
    gpmc = dfs['名称'].to_list()
    fbcj = dfs['成交额'].to_list()
    zt_cj = 0
    for i in range(len(fbcj)):
        # print(gpmc[i],fbzj[i],fbcj[i],zt[i])
        zt_cj += fbcj[i]
    #将资金转为亿为单位
    zt_cj = zt_cj / 100000000
    print(f"炸板股票的总成交额: {zt_cj}")
    return zt_cj

#计算某一天中涨停的股票的总资金，以及成交额
def cal_zt_zj(filePath):
    import os
    #列出目录下的所有文件
    files = os.listdir(filePath)
    files.sort()
    print(files)
    fb_zj = []
    fb_cj = []
    for file in files:
        cur_path = filePath+"/"+file
        print(cur_path)
        try:
            zt_zj,zt_cj = cal_zt_zj_simple(cur_path)
            fb_zj.append(zt_zj)
            fb_cj.append(zt_cj)
        except Exception as e:
            print(f"读取文件{cur_path}失败: {e}")
            continue
    
    return fb_zj,fb_cj



if __name__ == '__main__':
    test,tset1 = cal_zt_zj("./Data/daily/zt/20250530")
    print(test)
    print(tset1)    



   

   
    
    
 
