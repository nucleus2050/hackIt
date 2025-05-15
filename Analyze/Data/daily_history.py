import akshare as ak
import time
import json
import pandas as pd
#获取所有股票代码
#返回值：
#包含所有股票代码的列表
def get_all_stock_code():
    # 获取所有股票的代码
    try:
        stock_df = ak.stock_zh_a_spot_em()
        # 1. 过滤掉总市值为0的股票
        stock_df = stock_df[stock_df["总市值"] != 0.0]
        
        # 2. 过滤掉名称中包含"退"的股票（退市股票）
        stock_df = stock_df[~stock_df["名称"].str.contains("退", na=False)]
        
        # 3. 过滤掉名称中包含"PT"的股票（特别处理的股票，通常是停牌或问题股票）
        stock_df = stock_df[~stock_df["名称"].str.contains("PT", na=False)]
        
        # 4. 过滤掉成交量为0的股票（可能是停牌股票）
        if "成交量" in stock_df.columns:
            stock_df = stock_df[stock_df["成交量"] > 0]
        
        # 5. 过滤掉最新价为0或NaN的股票
        if "最新价" in stock_df.columns:
            stock_df = stock_df[stock_df["最新价"] > 0]

        # 保存股票代码和名称的映射关系,名称转为utf-8编码
        names = []
        for name in stock_df["名称"].tolist():
            # 如果名称是GBK编码，先解码为Unicode，再编码为UTF-8
            try:
                if isinstance(name, str):
                    # 确保名称是UTF-8编码
                    name_utf8 = name.encode('utf-8').decode('utf-8')
                    # print(name_utf8)
                    names.append(name_utf8)
                else:
                    names.append(name)
            except Exception as e:
                print(f"转换名称编码失败: {name}, 错误: {e}")
                names.append(name)  # 保留原始名称
                
        stock_code_name_map = dict(zip(stock_df["代码"].tolist(), names))
        print(f"成功获取到 {len(stock_code_name_map)} 只股票代码和名称")
        return stock_code_name_map
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        try:
            stock_df = ak.stock_zh_a_spot()
            #从新浪获取的股票代理要去掉"sh"和"sz"前缀
            stock_df["代码"] = stock_df["代码"].str.replace("sh", "").str.replace("sz", "").str.replace("bj", "")
  
            stock_code_name_map = dict(zip(stock_df["代码"].tolist(), stock_df["名称"].tolist()))
            print(f"使用备选API成功获取到 {len(stock_code_name_map)} 只股票代码和名称")
            return stock_code_name_map
        except Exception as e:
            print(f"所有获取股票列表的方法都失败: {e}")
            return {}


#使用Akshare获取指定日期内A股所有股票的日K数据,支持断点续爬
#参数：
#begin_date：开始日期，格式为"YYYY-MM-DD"的字符串或datetime格式
#end_date：结束日期，格式为"YYYY-MM-DD"的字符串或datetime格式，开始日期和结束日期必须在同一天
#返回值：
#包含所有股票日K数据的列表
def get_all_daily(stock_code_name_map, begin_date, end_date):
    #打开文件，读取已下载的股票代码
    #文件名为时间.csv
    #如果文件不存在，创建一个空列表
    #如果文件存在，读取文件中的股票代码，将其转换为列表
    begin_date = str.replace(begin_date,'-','')
    end_date = str.replace(end_date,'-','')
    print(f"计划获取从 {begin_date} 到 {end_date} 的股票数据")
    
    import os
    file_path = f"./Data/history/{begin_date}.csv"
    if os.path.exists(file_path):
        dfs = pd.read_csv(file_path, header=None)
        daily_data = dfs[1].tolist()
    else:
        daily_data = []
    print(f"已下载 {len(daily_data)} 数据")

    # 遍历股票代码，获取每只股票的日K数据
    #每10只股票保持一次数据到文件中
    daily_df_list = []
    first_time = True
    
    for stock_code, stock_name in stock_code_name_map.items():
        #检查股票代码是否已下载，如果已下载则跳过
        if stock_code in daily_data:
            print(f"{stock_code} 数据已下载，跳过")
            continue
        try:
            # 使用akshare获取股票日K数据
            daily_df = ak.stock_zh_a_hist(symbol=stock_code,start_date=begin_date, end_date=end_date, adjust="")
            # 检查数据是否为空
            if daily_df.empty:
                print(f"{stock_code} 数据为空，跳过")
                continue
            # 将数据添加到列表中
            # daily_data.extend(daily_df.values.tolist())
            #增加股票名称列，并且调整顺序，将该列放在第三列
            daily_df["股票名"] = stock_name
            # 重新排列列顺序，将股票名放在第三列
            columns = daily_df.columns.tolist()
            # 移除股票名列
            columns.remove("股票名")
            # 在第二列后插入股票名列
            columns.insert(2, "股票名")
            # 按新顺序重排列
            daily_df = daily_df[columns]
            daily_df_list.append(daily_df)
            print(f"{stock_code} 数据已下载")
            time.sleep(1)
            #每10只股票保持一次数据到文件中
            if len(daily_df_list) % 10 == 0:
                # 以追加的形式保存数据到文件中
                daily_df_tmp = pd.concat(daily_df_list)
                if len(daily_data) == 0 and first_time:
                    daily_df_tmp.to_csv(file_path, index=False)
                    first_time = False
                else :
                    daily_df_tmp.to_csv(file_path, mode='a', header=False, index=False)
                    
                daily_df_list = []
                print(f"已保存 {len(daily_df_tmp)} 只股票数据")
                # time.sleep(1)
        except Exception as e:
            print(f"获取 {stock_code} 数据失败: {e}")
            continue

    # 保存数据到文件
    if len(daily_df_list) > 0:
        daily_df_tmp = pd.concat(daily_df_list)
        daily_df_tmp.to_csv(file_path, mode='a', header=False, index=False)
        print(f"已保存 {len(daily_df_tmp)} 只股票数据")
        daily_df_list = []

    return daily_data

   


#获取指定日期范围内的所有股票数据
#参数：
#begin_date：开始日期，格式为"YYYY-MM-DD"的字符串
#end_date：结束日期，格式为"YYYY-MM-DD"的字符串
#返回值：
#无，数据直接保存到文件
def get_data_by_date_range(begin_date, end_date):
    print(f"计划获取从 {begin_date} 到 {end_date} 的股票数据")


    #检查代码映射文件是否存在，如果不存在则创建，并且调用get_all_stock_code()获取股票代码和名称的映射，并保存到文件中
    import os
    if not os.path.exists('./Data/public/stock.csv'):
        stock_code_name_map = get_all_stock_code()
        if not stock_code_name_map:
            print("无法获取股票代码和名称列表，程序退出")
            return
        df = pd.DataFrame.from_dict(stock_code_name_map, orient='index', columns=['股票名称'])
        df.index.name = '股票代码'  # 设置索引名称
        df.to_csv("./Data/public/stock.csv", encoding="utf_8_sig")
    else:
        # 从CSV文件中读取数据,股票代码必须映射为字符串
        df = pd.read_csv("./Data/public/stock.csv", dtype={'股票代码': str}, encoding="utf_8_sig")
        stock_code_name_map = dict(zip(df['股票代码'], df['股票名称']))
        print(f"成功获取到 {len(stock_code_name_map)} 只股票代码和名称")

    # import os
    # if not os.path.exists('./Data/public/stock_code_name_map.json'):
    #     stock_code_name_map = get_all_stock_code()
    #     if not stock_code_name_map:
    #         print("无法获取股票代码和名称列表，程序退出")
    #         return
    #     with open('./Data/public/stock_code_name_map.json', 'w',encoding='utf-8') as f:
    #         json.dump(stock_code_name_map, f)
    # else:
    #     with open('./Data/public/stock_code_name_map.json', 'r',encoding='utf-8') as f:
    #         stock_code_name_map = json.load(f)
    
    # print(f"成功获取到 {len(stock_code_name_map)} 只股票代码和名称")
    # #将stock_code_name_map按照代码排序
    # stock_code_name_map = dict(sorted(stock_code_name_map.items(), key=lambda item: item[0]))
    
    # 限制股票数量，避免请求过多导致API限制
    # 可以根据需要调整或注释掉这一行
    # 从字典中取出前20个项目
    #if len(stock_code_name_map) > 20:
    #    stock_code_name_map = dict(list(stock_code_name_map.items())[:20])  # 仅获取前20只股票数据进行测试
    
    # 将日期字符串转换为datetime对象，便于循环
    from datetime import datetime, timedelta
    start_dt = datetime.strptime(begin_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # 循环每一天
    current_dt = start_dt
    while current_dt <= end_dt:
        current_date = current_dt.strftime('%Y-%m-%d')
        print(f"\n开始获取 {current_date} 的股票数据")
        
        # 创建daily_data文件夹（如果不存在）
        import os
        if not os.path.exists('Data/history'):
            os.makedirs('Data/history')

        # 获取当天的数据
        daily_data = get_all_daily(stock_code_name_map, current_date, current_date)
        
        # 移动到下一天
        current_dt += timedelta(days=1)



#初始化并设置akshare使用代理池
def init_proxy_pool():
    #https://www.docip.net/data/free.json
    #从稻壳代理获取免费代理
    url = "https://www.docip.net/data/free.json"
    import requests
    import json
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Print the raw response to debug the structure
            print("Response received from proxy service")
            
            # Parse the JSON response
            data = json.loads(response.text)
            
            # Debug: print the structure of the data
            print(f"Data type: {type(data)}")
            if isinstance(data, dict) and 'data' in data:
                # If data is in a nested 'data' field
                proxy_list = data['data']
                print(f"Found {len(proxy_list)} proxies in data field")
            elif isinstance(data, list):
                # If data is directly a list
                proxy_list = data
                print(f"Found {len(proxy_list)} proxies in list")
            else:
                # If structure is unknown, print a sample
                print(f"Unexpected data structure. Sample: {str(data)[:200]}...")
                return
            
            # Try to extract proxies based on the structure
            proxies = []
            for item in proxy_list:
                if isinstance(item, dict):
                    # Try different possible key names
                    ip = item.get('ip')
                    
                    if ip :
                        proxies.append(f"{ip}")
            
            if proxies:
                ak.set_proxy(proxies=proxies)
                print(f"成功设置代理池，代理数量：{len(proxies)}")
            else:
                print("无法从响应中提取代理信息")
                print(f"Sample data item: {str(proxy_list[0] if proxy_list else 'No items')}")
        else:
            print(f"获取代理失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"初始化代理池时出错: {e}")
        print("继续执行，但不使用代理")



#获取从start到end的所有交易日
def get_trace_date_list(start,end):
    import akshare as ak
    from datetime import datetime
    trade_date_list = ak.tool_trade_date_hist_sina()
    trade_date_list = trade_date_list['trade_date'].tolist()
    #将start和end转换为datetime格式
    start_dt = datetime.strptime(start, '%Y-%m-%d')
    end_dt = datetime.strptime(end, '%Y-%m-%d')
    #获取start和end之间的所有交易日
    date_list = []
    for date_str in trade_date_list:
        date_dt = datetime.strptime(str(date_str), '%Y-%m-%d')
        if date_dt >= start_dt and date_dt <= end_dt:
            date_list.append(date_str)  # 直接添加原始字符串
    return date_list


if __name__ == '__main__':
    import akshare as ak
    from datetime import datetime
    import datetime
    import time
    trade_date_list = ak.tool_trade_date_hist_sina()
    trade_date_list = trade_date_list['trade_date'].tolist()
    while True:
        now = datetime.datetime.now()
        now_date = now.date()
        if now_date in trade_date_list:
            if now.hour == 15 and now.minute == 0:
                #获取数据
                get_data_by_date_range(str(now_date),str(now_date))
            else:
                print("当前不是交易时间，等待1分钟")
                time.sleep(60)


# if __name__ == '__main__':
#     date_list = get_trace_date_list( '2024-09-01','2025-03-31')
#     for date in date_list:
#         get_data_by_date_range(str(date),str(date))
