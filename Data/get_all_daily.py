import akshare as ak
import pandas as pd
import time  # 添加时间模块用于延迟请求



#获取所有股票代码
#返回值：
#包含所有股票代码的列表
def get_all_stock_code():
    # 获取所有股票的代码
    try:
        stock_df = ak.stock_zh_a_spot_em()
        # 保存股票代码和名称的映射关系
        stock_code_name_map = dict(zip(stock_df["代码"].tolist(), stock_df["名称"].tolist()))
        print(f"成功获取到 {len(stock_code_name_map)} 只股票代码和名称")
        return stock_code_name_map
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        try:
            stock_df = ak.stock_zh_a_spot()
            stock_code_name_map = dict(zip(stock_df["代码"].tolist(), stock_df["名称"].tolist()))
            print(f"使用备选API成功获取到 {len(stock_code_name_map)} 只股票代码和名称")
            return stock_code_name_map
        except Exception as e:
            print(f"所有获取股票列表的方法都失败: {e}")
            return {}


#获取当天实时行情数据
#参数：
#无
#返回值：
#包含所有股票实时行情数据的列表
def get_all_real_time():
    # 获取所有股票的实时行情数据
    try:
        stock_df = ak.stock_zh_a_spot_em()
        print(stock_df.head())
        # 保存股票代码和名称的映射关系
        stock_code_name_map = dict(zip(stock_df["代码"].tolist(), stock_df["名称"].tolist()))
        print(f"成功获取到 {len(stock_code_name_map)} 只股票代码和名称")
        return stock_code_name_map
    except Exception as e:
        print(f"获取股票列表失败: {e}")

#使用Akshare获取指定日期内A股所有股票的日K数据
#参数：
#begin_date：开始日期，格式为"YYYY-MM-DD"的字符串或datetime格式
#end_date：结束日期，格式为"YYYY-MM-DD"的字符串或datetime格式
#返回值：
#包含所有股票日K数据的列表
def get_all_daily(stock_code_name_map, begin_date, end_date):
    # 获取所有股票的日K数据
    daily_data = []
    success_count = 0
    
    for i, (stock_code, stock_name) in enumerate(stock_code_name_map.items()):
        # 尝试获取日K数据，如果获取失败则跳过该股票
        try:
            # 确保日期格式正确
            formatted_begin = begin_date.replace('-', '')
            formatted_end = end_date.replace('-', '')
            
            # 尝试使用不同的API函数获取数据
            try:
                df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                        start_date=formatted_begin, end_date=formatted_end, 
                                        adjust="")
            except:
                # 备选方法
                df = ak.stock_zh_a_daily(symbol=stock_code, start_date=begin_date, end_date=end_date)
            
            # 检查数据是否为空
            if df.empty:
                print(f"股票 {stock_code} ({stock_name}) 在指定日期范围内没有数据")
                continue
                
            # 将股票代码和名称添加到数据中
            df["code"] = stock_code
            df["name"] = stock_name  # 添加股票名称
            daily_data.append(df)
            success_count += 1
            
            # 打印进度
            if i % 5 == 0:
                print(f"已处理 {i+1}/{len(stock_code_name_map)} 只股票，成功获取 {success_count} 只")
                
            # 添加短暂延迟，避免请求过快被限制
            time.sleep(0.5)
            
        except Exception as e:
            print(f"获取股票 {stock_code} ({stock_name}) 数据失败: {e}")
            continue
    
    # 检查是否有数据
    if not daily_data:
        print("没有获取到任何股票数据")
        return pd.DataFrame()
    
    print(f"成功获取 {success_count}/{len(stock_code_name_map)} 只股票的数据")
    
    # 将所有股票的日K数据合并成一个DataFrame
    try:
        daily_data = pd.concat(daily_data, ignore_index=True)
        return daily_data
    except Exception as e:
        print(f"合并数据失败: {e}")
        return pd.DataFrame()


#获取指定日期范围内的所有股票数据
#参数：
#begin_date：开始日期，格式为"YYYY-MM-DD"的字符串
#end_date：结束日期，格式为"YYYY-MM-DD"的字符串
#返回值：
#无，数据直接保存到文件
def get_data_by_date_range(begin_date, end_date):
    print(f"计划获取从 {begin_date} 到 {end_date} 的股票数据")
    
    # 获取所有股票代码和名称的映射
    stock_code_name_map = get_all_stock_code()
    if not stock_code_name_map:
        print("无法获取股票代码和名称列表，程序退出")
        return
    
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
        
        # 获取当天的数据
        daily_data = get_all_daily(stock_code_name_map, current_date, current_date)
        
        if not daily_data.empty:
            print(f"成功获取 {current_date} 数据，共 {len(daily_data)} 条记录")
            
            # 创建daily_data文件夹（如果不存在）
            import os
            if not os.path.exists('daily_data'):
                os.makedirs('daily_data')
            
            # 保存数据，文件名格式为日期.csv，如20230101.csv
            file_date = current_date.replace('-', '')
            file_path = os.path.join('daily_data', f"{file_date}.csv")
            daily_data.to_csv(file_path, index=False)
            print(f"数据已保存至 {file_path}")
        else:
            print(f"{current_date} 未能获取任何数据")
        
        # 移动到下一天
        current_dt += timedelta(days=1)


# 直接在if语句块中编写代码
if __name__ == '__main__':
    # 调用函数获取指定日期范围的数据
    # begin_date = '2023-01-01'
    # end_date = '2023-01-05'
    # get_data_by_date_range(begin_date, end_date)
    get_all_real_time()
