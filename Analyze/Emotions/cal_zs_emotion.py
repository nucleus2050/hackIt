import akshare as ak
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime



# 计算指数成分股的情绪指标
def cal_zs_emotion(zscfPath,filePath):
    # 获取指数成分股
    index_list = [
        {'code': '000016', 'name': 'SSE 50'},
        {'code': '000300', 'name': 'CSI 300'},
        {'code': '000905', 'name': 'CSI 500'},
        {'code': '000852', 'name': 'CSI 1000'},
        {'code': '000688', 'name': 'STAR 50'}
    ]
    emotion_results = {}
    # 计算各指数的情绪指标
    for index in index_list:
        #读取存储指数成分股的csv文件
        df = pd.read_csv(zscfPath + '/' + index['code'] + '.csv')
        stock_codes = df['成分券代码'].tolist()
        # print(stock_codes)
        #读取当前行数文件
        df5min = pd.read_csv(filePath)
        df_zs = df5min[df5min['代码'].isin(stock_codes)]
        # print(df_zs)
        high = df_zs['最高'].tolist()
        low = df_zs['最低'].tolist()
        close = df_zs['最新价'].tolist()
        import cal_history_point
        point = cal_history_point.cal_daily_point(high,low,close)
        emotion_results[index['name']] = point
    return emotion_results

if __name__ == '__main__':
    # 定义要分析的指数代码和名称
    index_list = [
        {'code': '000016', 'name': '上证50'},
        {'code': '000300', 'name': '沪深300'},
        {'code': '000905', 'name': '中证500'},
        {'code': '000852', 'name': '中证1000'},
        {'code': '000688', 'name': '科创50'}
    ]
    # test = get_zs_cf('399006')
    # print(test)
    # 存储各指数的情绪指标
    emotion_results = {}
    
    # 计算各指数的情绪指标
    for index in index_list:
        emotion_point = cal_zs_emotion("./Data/zs", "./Data/daily/point/20250530/202505301500.csv")
        if emotion_point is not None:
            emotion_results[index['name']] = emotion_point
    print(emotion_results)
    
    # # 绘制柱状图展示各指数的情绪指标
    # if emotion_results:
    #     plt.figure(figsize=(12, 6))
    #     names = list(emotion_results.keys())
    #     values = list(emotion_results.values())
        
    #     bars = plt.bar(names, values, color='skyblue')
    #     plt.axhline(y=50, color='r', linestyle='-', alpha=0.3)
        
    #     # 在柱状图上标注具体数值
    #     for bar in bars:
    #         height = bar.get_height()
    #         plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
    #                 f'{height:.2f}', ha='center', va='bottom')
        
    #     plt.title('各指数成分股情绪指标对比')
    #     plt.xlabel('指数名称')
    #     plt.ylabel('情绪指标值')
    #     plt.ylim(0, 100)
    #     plt.xticks(rotation=45)
    #     plt.tight_layout()
        
    #     # 保存图表
    #     today = datetime.now().strftime("%Y%m%d")
    #     plt.savefig(f"./Data/daily/zs_emotion_{today}.png", dpi=300)
    #     plt.show()
    