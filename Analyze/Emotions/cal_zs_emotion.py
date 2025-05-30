import akshare as ak
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 获取指定指数成分股
def get_zs_cf(zhs_code='399006'):
    try:
        # 尝试直接获取数据
        index_stock_info_df = ak.index_stock_cons_csindex(zhs_code)
        
        # 检查返回的是否为DataFrame
        if isinstance(index_stock_info_df, pd.DataFrame):
            return index_stock_info_df
        
        # 如果返回的是二进制数据或其他格式，尝试使用BytesIO处理
        from io import BytesIO
        import warnings
        warnings.filterwarnings('ignore')
        
        # 尝试使用不同的引擎读取Excel
        try:
            # 首先尝试openpyxl引擎
            df = pd.read_excel(BytesIO(index_stock_info_df), engine='openpyxl')
        except Exception as e:
            print(f"尝试使用openpyxl引擎失败: {e}")
            try:
                # 然后尝试xlrd引擎
                df = pd.read_excel(BytesIO(index_stock_info_df), engine='xlrd')
            except Exception as e:
                print(f"尝试使用xlrd引擎失败: {e}")
                raise ValueError(f"无法读取指数{zhs_code}的成分股数据")
        
        return df
    except Exception as e:
        print(f"获取指数{zhs_code}成分股时出错: {e}")
        return pd.DataFrame()  # 返回空DataFrame而不是None，便于后续处理

# 计算指数成分股的情绪指标
def cal_zs_emotion(zhs_code, zhs_name):
    # 获取指数成分股
    zs_cf = get_zs_cf(zhs_code)
    # 提取成分股代码列表
    stock_codes = zs_cf['成分券代码'].tolist()
    
    # 获取最新的历史数据文件
    history_files = os.listdir("./Data/history")
    history_files.sort()
    latest_file = history_files[-1] if history_files else None
    print(latest_file)
    if not latest_file:
        print(f"未找到历史数据文件")
        return None
    
    # 读取历史数据
    df = pd.read_csv(f"./Data/history/{latest_file}", dtype={'股票代码': str})
    
    # 筛选出指数成分股的数据
    df_zs = df[df['股票代码'].isin(stock_codes)]
    
    # 计算指数成分股的挣钱效应
    high = df_zs['最高'].tolist()
    low = df_zs['最低'].tolist()
    close = df_zs['收盘'].tolist()
    
    if len(high) == 0:
        print(f"{zhs_name}({zhs_code})没有找到成分股数据")
        return None
    
    # 计算挣钱效应
    point = 0
    for i in range(len(high)):
        h = float(high[i])
        l = float(low[i])
        c = float(close[i])
        if h == l and c == l:
            point += 100
        else:
            point += (c - l) * 100 / (h-l)
    
    emotion_point = point / len(high)
    print(f"{zhs_name}({zhs_code})的情绪指标: {emotion_point:.2f}")
    return emotion_point

if __name__ == '__main__':
    # 定义要分析的指数代码和名称
    index_list = [
        {'code': '000016', 'name': '上证50'},
        {'code': '000300', 'name': '沪深300'},
        {'code': '000905', 'name': '中证500'},
        {'code': '000852', 'name': '中证1000'},

        {'code': '399006', 'name': '创业板指'},
        # {'code': '399005', 'name': '中小板指'},
        {'code': '000688', 'name': '科创50'}
    ]
    test = get_zs_cf('399006')
    print(test)
    # 存储各指数的情绪指标
    # emotion_results = {}
    
    # # 计算各指数的情绪指标
    # for index in index_list:
    #     emotion_point = cal_zs_emotion(index['code'], index['name'])
    #     if emotion_point is not None:
    #         emotion_results[index['name']] = emotion_point
    
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
    