import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cal_zs_emotion
import cal_zt_zj
import os
import pandas as pd

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

def cal_today_point(csv_path):
    #读取csv文件,只获取最高、最低、收盘列
    df = pd.read_csv(csv_path, usecols=[9,10,3])
    #获取最高价、最低价、收盘价
    high = df['最高'].tolist()
    low = df['最低'].tolist()
    close = df['最新价'].tolist()
    #计算当天的挣钱效应
    if len(high) != len(low) or len(high) != len(close):
        print("数据长度不一致")
        return 0
    if len(high) == 0 or len(low) == 0 or len(close) == 0:
        print("数据长度为0")
        return 0
    point = cal_daily_point(high,low,close)
    return point

def send_email(sender, password, receiver, subject, body):
    # 设置邮件内容
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    
    message.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP_SSL('smtp.139.com', 465) as server:
            server.login(sender, password)  
            server.sendmail(sender, receiver, message.as_string())  
        print("邮件发送成功!")
    except Exception as e:
        print(f"邮件发送失败: {e}")

sender_email = "15889320552@139.com"
sender_password = "99c56e7298db37305600" 
receiver_email = "15889320552@139.com"
email_subject_notify = "nofify"
email_subject_alter = "alter"


#获取上一个交易日的日期,以及最后一个交易日的日期
def get_pre_trade_date(filePath):
    #获取filePath的上上级目录
    import os
    path = os.path.dirname(os.path.dirname(filePath))
    #获取path下的所有文件
    files = os.listdir(path)
    files.sort()
    #如果files长度小于2，则返回今天的日期
    #获取path下的所有文件的日期
    if len(files) >= 2:
        return files[-2],files[-1]
    else:
        import datetime
        now = datetime.datetime.now()
        today_format = now.strftime("%Y%m%d")
        return today_format,today_format



class DetectFileHandler(FileSystemEventHandler):
    global sender_email
    global sender_password
    global receiver_email
    global email_subject
    def on_created(self, event):
        """当检测到新文件创建时调用此方法"""
        if not event.is_directory:
            print(f"检测到新文件: {event.src_path}")
            #判读是否在9:30之前，如果是则什么也不干
            import datetime
            now = datetime.datetime.now()
            if now.hour < 9 or (now.hour == 9 and now.minute < 25):
                print("9:30之前，不计算")
                return
            
            if "zt" in event.src_path:
                time.sleep(1)
                #如果文件时zt目录下的文件，计算总成交额和封板资金
                try:
                    # 处理市场数据并生成邮件内容
                    email_body,point = process_market_data_and_generate_email(event.src_path)
                    
                    if email_body is None:
                        print("邮件内容生成失败")
                        return

                    # 获取突然放量的股票
                    # stocks = get_suddenly_volume_stock(event.src_path)
                    # print(stocks)


                    if point < 30.0 and point > 0.0:
                        send_email(sender_email, sender_password, receiver_email, email_subject_alter, email_body)
                    else:
                        send_email(sender_email, sender_password, receiver_email, email_subject_notify, email_body)
                except Exception as e:
                    print("cal_zt_zj error",e)
                    #打印出堆栈信息
                    import traceback
                    traceback.print_exc()
                    






def  get_pre_5min_10min_point_path(point_path):
    """
    获取上个5min或者10min的point文件
    参数：
        event_src_path: 事件源文件路径
    返回：
        pre_5min_10min_point_path: 上个5min或者10min的point文件路径
    """
    
    #去掉.csv后缀后转换为时间，在时间上减去5min或者10min,然后转换为文件路径，格式类似于202505151010.csv，再判断文件是否存在，存在则返回文件路径，不存在则返回None
    try:
        import datetime
        import os
        
        # 从文件路径中提取时间信息
        file_name = os.path.basename(point_path)
        #提取路径部分
        filepath = os.path.dirname(point_path)
        # 提取时间部分 (例如: 202505151010)
        time_str = file_name.replace('.csv', '')
        if len(time_str) != 12:  # 确保时间格式正确
            print(f"时间格式错误: {time_str}")
            return None
        
        # 解析时间
        year = int(time_str[:4])
        month = int(time_str[4:6])
        day = int(time_str[6:8])
        hour = int(time_str[8:10])
        minute = int(time_str[10:12])
        
        current_time = datetime.datetime(year, month, day, hour, minute)
        
       
        prev_time_5min = current_time - datetime.timedelta(minutes=5)
        prev_time_10min = current_time - datetime.timedelta(minutes=10)
        
        # 生成前一个时间点的文件名
        prev_time_5min_str = prev_time_5min.strftime("%Y%m%d%H%M")
        prev_point_5min_path = filepath + "/" + point_path.replace(point_path, prev_time_5min_str) + ".csv"

        prev_time_10min_str = prev_time_10min.strftime("%Y%m%d%H%M")
        prev_point_10min_path = filepath + "/" + point_path.replace(point_path, prev_time_10min_str) + ".csv"
        
        print("prev_point_5min_path",prev_point_5min_path)
        print("prev_point_10min_path",prev_point_10min_path)

        # 判断文件是否存在
        if os.path.exists(prev_point_5min_path):
            print(f"找到前一个时间点文件: {prev_point_5min_path}")
            return prev_point_5min_path
        elif os.path.exists(prev_point_10min_path):
            print(f"找到前一个时间点文件: {prev_point_10min_path}")
            return prev_point_10min_path
        else:
            print(f"前一个时间点文件不存在")
            return None
            
    except Exception as e:
        print(f"获取前一个时间点文件路径时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_suddenly_volume_stock(event_src_path):
    """
    获取突然放量的股票
    参数：
        event_src_path: 事件源文件路径
    返回：
        suddenly_放量_股票: 突然放量的股票列表
    """
    #获取当前文件
    point_path = event_src_path.replace("zt","point")
    pre_date, today_format = get_pre_trade_date(event_src_path)
    #获取前一个交易日的point文件
    pre_day_point_path = point_path.replace(today_format, pre_date)

    #获取上个5min或者10min的point文件，格式类似于202505151010.csv
    #去掉.csv后缀后转换为时间，在时间上减去5min或者10min
    pre_point_path   = get_pre_5min_10min_point_path(point_path)
    pre_pre_day_point_path = get_pre_5min_10min_point_path(pre_day_point_path)

 
    #读取csv文件,只获取股票代码和成交量
    df_point_path = pd.read_csv(point_path, usecols=[1,2,6])
    df_pre_point_path  = pd.read_csv(pre_point_path, usecols=[1,2,6])

    
    df_pre_day_point_path = pd.read_csv(pre_day_point_path, usecols=[1,2,6])
    df_pre_pre_day_point_path  = pd.read_csv(pre_pre_day_point_path, usecols=[1,2,6])


    #根据股票代码和成交量，计算每5min或者10min的成交量
    # 合并数据框，基于股票代码
    merged_df = pd.merge(df_point_path, df_pre_point_path, on='代码', suffixes=('_current', '_prev'))
    
    # 计算成交量变化：当前成交量 - 前一时间成交量
    merged_df['成交量变化'] = merged_df['成交量_current'] - merged_df['成交量_prev']
    merged_df['成交量变化率'] = (merged_df['成交量变化'] / merged_df['成交量_prev'] * 100).fillna(0)
    
    # 筛选突然放量的股票 (成交量增加超过100%)
    suddenly_volume_stocks = merged_df[merged_df['成交量变化率'] > 500].copy()
    
    # 按成交量变化率排序
    suddenly_volume_stocks = suddenly_volume_stocks.sort_values('成交量变化率', ascending=False)
    
    print(f"发现 {len(suddenly_volume_stocks)} 只突然放量的股票")
    
    return suddenly_volume_stocks.to_dict('records')



def get_top_50_rise(point_path,pre_point_path):
    """
    参数：
        point_path: 事件源文件路径
        pre_point_path: 前一个周期的point文件路径
    返回：
        top50_str: 50个涨幅最大的股票字符串
        des50_str: 50个跌幅最大的股票字符串
    """

    #读取csv文件,代码、名称、涨跌幅
    df = pd.read_csv(point_path, usecols=[1,2,4])
    #读取前一个周期的csv文件,代码、名称、涨跌幅
    df_pre = pd.read_csv(pre_point_path, usecols=[1,2,4])
    #以代码为key，将当前的涨跌幅和前一个周期的涨跌幅相减，得到涨跌幅差值
    
    # 重命名列名以便后续操作
    df.columns = ['代码', '名称', '涨跌幅']
    df_pre.columns = ['代码', '名称', '涨跌幅']
    
    # 合并当前和前一个周期的数据，以代码为key
    merged_df = pd.merge(df, df_pre, on='代码', how='inner', suffixes=('_current', '_pre'))
    
    # 计算涨跌幅差值（当前涨跌幅 - 前一个周期涨跌幅）
    merged_df['涨跌幅差值'] = merged_df['涨跌幅_current'] - merged_df['涨跌幅_pre']
    
    # 获取涨幅最大的50只股票（涨跌幅差值最大的50只）
    top50 = merged_df.nlargest(50, '涨跌幅差值')[['代码', '名称_current', '涨跌幅差值']].copy()
    top50.columns = ['代码', '名称', '涨幅']
    
    # 获取跌幅最大的50只股票（涨跌幅差值最小的50只）
    des50 = merged_df.nsmallest(50, '涨跌幅差值')[['代码', '名称_current', '涨跌幅差值']].copy()
    des50.columns = ['代码', '名称', '跌幅']
    
    # 转换为字符串格式
    def dataframe_to_string(df, title):
        """将DataFrame转换为格式化的字符串"""
        if df.empty:
            return f"{title}:\n暂无数据\n"
        result = f"{title}:\n"
        result += "=" * 50 + "\n"
        result += f"{'代码':<10} {'名称':<15} {'涨跌幅':<10}\n"
        result += "-" * 50 + "\n"
        
        for _, row in df.iterrows():
            result += f"{row['代码']:<10} {row['名称']:<15} {row.iloc[2]:<10.2f}%\n"
        
        result += "=" * 50 + "\n\n"
        return result
    
    top50_str = dataframe_to_string(top50, "涨幅前50名股票")
    des50_str = dataframe_to_string(des50, "跌幅前50名股票")
    
    return top50_str, des50_str



def process_market_data_and_generate_email(event_src_path):
    """
    处理市场数据并生成邮件内容
    参数：
        event_src_path: 事件源文件路径
    返回：
        email_body: 邮件内容字符串，如果处理失败返回None
        point:股市打分
    """
    try:
        point_path = event_src_path.replace("zt","point")
        zb_path = event_src_path.replace("zt","zb")

        pre_date, today_format = get_pre_trade_date(event_src_path)
        pre_point_path = point_path.replace(today_format, pre_date)
        pre_zb_path = zb_path.replace(today_format, pre_date)
        pre_zt_path = event_src_path.replace(today_format, pre_date)
        
        print("pre_date:", pre_date)
        print("pre_point_path:", pre_point_path)
        print("pre_zb_path:", pre_zb_path)
        print("event.src_path:", event_src_path)

        # 计算今日数据
        zt_zj, zt_cj = cal_zt_zj.cal_zt_zj_simple(event_src_path)
        point = cal_today_point(point_path)
        zb_cj = cal_zt_zj.cal_zb_zj_simple(zb_path)

        # 判断前一天的文件是否存在，存在则计算，不存在则不计算
        if os.path.exists(pre_point_path):
            pre_point = cal_today_point(pre_point_path)
        else:
            pre_point = 0.0
        
        if os.path.exists(pre_zb_path):
            pre_zb_cj = cal_zt_zj.cal_zb_zj_simple(pre_zb_path)
        else:
            pre_zb_cj = 0.0

        if os.path.exists(pre_zt_path):
            pre_zt_zj, pre_zt_cj = cal_zt_zj.cal_zt_zj_simple(pre_zt_path)
        else:
            pre_zt_zj = 0.0
            pre_zt_cj = 0.0

        top50_rise_str, top50_des_str = get_top_50_rise(point_path,pre_point_path)

        # 计算指数情绪
        zs_emotion = cal_zs_emotion.cal_zs_emotion("./Data/zs", point_path)

        if os.path.exists(pre_point_path):
            pre_sz_emotion = cal_zs_emotion.cal_zs_emotion("./Data/zs", pre_point_path)
        else:
            pre_sz_emotion = {'SSE 50': 30.0, 'CSI 300': 30.0, 'CSI 500': 30.0, 'CSI 1000': 30.0, 'STAR 50': 30.0}

        print("zs_emotion:", zs_emotion)
        print("pre_sz_emotion:", pre_sz_emotion)

        # 生成邮件内容
        email_body = "Market Sentiment Monitor\n"
        email_body += "=" * 40 + "\n"
        email_body += f"{'Metric':<15} {'Today':<10} {'Yesterday':<10} {'Trend':<10}\n"
        email_body += "-" * 40 + "\n"
        email_body += f"{'Emotion':<15} {point:<10.2f} {pre_point:<10.2f} {'↑' if point > pre_point else '↓' if point < pre_point else '→':<6}\n"
        email_body += f"{'Seal Fund':<15} {zt_zj:<10.2f} {pre_zt_zj:<10.2f} {((zt_zj-pre_zt_zj)/pre_zt_zj*100 if pre_zt_zj else 0):<.2f}%\n"
        email_body += f"{'Limit Volume':<15} {zt_cj:<10.2f} {pre_zt_cj:<10.2f} {((zt_cj-pre_zt_cj)/pre_zt_cj*100 if pre_zt_cj else 0):<.2f}%\n"
        email_body += f"{'Seal Ratio':<15} {(zt_zj/zt_cj if zt_cj else 0):<10.2f} {(pre_zt_zj/pre_zt_cj if pre_zt_cj else 0):<10.2f} {(((zt_zj/zt_cj if zt_cj else 0)-(pre_zt_zj/pre_zt_cj if pre_zt_cj else 0))/(pre_zt_zj/pre_zt_cj if pre_zt_cj else 1)*100 if pre_zt_cj else 0):<.2f}%\n"
        email_body += f"{'Break Volume':<15} {zb_cj:<10.2f} {pre_zb_cj:<10.2f} {((zb_cj-pre_zb_cj)/pre_zb_cj*100 if pre_zb_cj else 0):<.2f}%\n"
        email_body += f"{'Total Volume':<15} {(zb_cj+zt_cj):<10.2f} {(pre_zb_cj+pre_zt_cj):<10.2f} {(((zb_cj+zt_cj)-(pre_zb_cj+pre_zt_cj))/(pre_zb_cj+pre_zt_cj)*100 if (pre_zb_cj+pre_zt_cj) else 0):<.2f}%\n"
        email_body += "=" * 40 + "\n"
        
        # 指数情绪表格
        email_body += "\nIndex Monitor\n"
        email_body += "=" * 40 + "\n"
        email_body += f"{'Metric':<15} {'Today':<10} {'Yesterday':<10} {'Trend':<10}\n"
        email_body += "-" * 40 + "\n"
        for key in zs_emotion.keys():
            email_body += f"{key:<15} {zs_emotion[key]:<10.2f} {pre_sz_emotion[key]:<10.2f} {'↑' if zs_emotion[key] > pre_sz_emotion[key] else '↓' if zs_emotion[key] < pre_sz_emotion[key] else '→':<6}\n"
        email_body += "=" * 40 + "\n"

        email_body += "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
        email_body += top50_rise_str
        email_body += top50_des_str

        return email_body,point
        
    except Exception as e:
        print("process_market_data_and_generate_email error:", e)
        import traceback
        traceback.print_exc()
        return None,None


def monitor_directory(path):
    """监控指定目录的新增文件"""
    # 验证路径是否存在
    if not os.path.exists(path):
        print(f"目录 '{path}' 不存在！")
        return
    
    print(f"开始监控目录: {path}")
    print("按 Ctrl+C 停止监控...")
    
    # 创建事件处理器和观察者
    event_handler = DetectFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)  # recursive=True 表示也监控子目录
    
    # 开始监控
    observer.start()
    
    try:
        # 持续运行直到按下 Ctrl+C
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 停止监控
        observer.stop()
        print("\n监控已停止")
    
    # 等待线程结束
    observer.join()

if __name__ == "__main__":
    # 设置要监控的目录
    directory_to_monitor = "./Data/daily"  # 替换为你要监控的目录路径
    # 开始监控
    monitor_directory(directory_to_monitor)
