
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cal_zs_emotion

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
    import os
    import pandas as pd
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
                import cal_zt_zj
                try:
                    point_path = event.src_path.replace("zt","point")
                    zb_path = event.src_path.replace("zt","zb")

                    pre_date,today_format = get_pre_trade_date(event.src_path)
                    pre_point_path = point_path.replace(today_format,pre_date)
                    pre_zb_path = zb_path.replace(today_format,pre_date)
                    pre_zt_path = event.src_path.replace(today_format,pre_date)
                    
                    print("pre_date:",pre_date)
                    print("pre_point_path:",pre_point_path)
                    print("pre_zb_path:",pre_zb_path)
                    print("event.src_path:",event.src_path)

                    zt_zj,zt_cj = cal_zt_zj.cal_zt_zj_simple(event.src_path)
                    point = cal_today_point(point_path)
                    zb_cj = cal_zt_zj.cal_zb_zj_simple(zb_path)

                    #判断前一天的文件是否存在,存在着计算,不存在着不计算
                    if os.path.exists(pre_point_path) :
                        pre_point = cal_today_point(pre_point_path)
                    else:
                        pre_point = 0.0
                    
                    if os.path.exists(pre_zb_path) :
                        pre_zb_cj = cal_zt_zj.cal_zb_zj_simple(pre_zb_path)
                    else:
                        pre_zb_cj = 0.0

                    if os.path.exists(pre_zt_path) :
                        pre_zt_zj,pre_zt_cj = cal_zt_zj.cal_zt_zj_simple(pre_zt_path)
                    else:
                        pre_zt_zj = 0.0
                        pre_zt_cj = 0.0

                    #计算指数情绪
                    zs_emotion = cal_zs_emotion.cal_zs_emotion("./Data/zs",point_path)

                    if os.path.exists(pre_point_path):
                        pre_sz_emotion = cal_zs_emotion.cal_zs_emotion("./Data/zs",pre_point_path)
                    else:
                        pre_sz_emotion = {'SSE 50': 0.0, 'CSI 300': 0.0, 'CSI 500': 0.0, 'CSI 1000': 0.0, 'STAR 50': 0.0}

                    print("zs_emotion:",zs_emotion)
                    print("pre_sz_emotion:",pre_sz_emotion)

                    # 简单表格化邮件内容
                    email_body = "Market Sentiment Monitor\n"
                    email_body += "=" * 40 + "\n"
                    email_body += f"{'Metric':<15} {'Today':<10} {'Yesterday':<10} {'Trend':<6}\n"
                    email_body += "-" * 40 + "\n"
                    email_body += f"{'Emotion':<15} {point:<10.2f} {pre_point:<10.2f} {'↑' if point > pre_point else '↓' if point < pre_point else '→':<6}\n"
                    email_body += f"{'Seal Fund':<15} {zt_zj:<10.2f} {pre_zt_zj:<10.2f} {'↑' if zt_zj > pre_zt_zj else '↓' if zt_zj < pre_zt_zj else '→':<6}\n"
                    email_body += f"{'Limit Volume':<15} {zt_cj:<10.2f} {pre_zt_cj:<10.2f} {'↑' if zt_cj > pre_zt_cj else '↓' if zt_cj < pre_zt_cj else '→':<6}\n"
                    email_body += f"{'Seal Ratio':<15} {(zt_zj/zt_cj if zt_cj else 0):<10.2f} {(pre_zt_zj/pre_zt_cj if pre_zt_cj else 0):<10.2f} {'↑' if (zt_zj/zt_cj if zt_cj else 0) > (pre_zt_zj/pre_zt_cj if pre_zt_cj else 0) else '↓' if (zt_zj/zt_cj if zt_cj else 0) < (pre_zt_zj/pre_zt_cj if pre_zt_cj else 0) else '→':<6}\n"
                    email_body += f"{'Break Volume':<15} {zb_cj:<10.2f} {pre_zb_cj:<10.2f} {'↑' if zb_cj > pre_zb_cj else '↓' if zb_cj < pre_zb_cj else '→':<6}\n"
                    email_body += f"{'Total Volume':<15} {(zb_cj+zt_cj):<10.2f} {(pre_zb_cj+pre_zt_cj):<10.2f} {'↑' if (zb_cj+zt_cj) > (pre_zb_cj+pre_zt_cj) else '↓' if (zb_cj+zt_cj) < (pre_zb_cj+pre_zt_cj) else '→':<6}\n"
                    email_body += "=" * 40 + "\n"
                    # email_body += str(zs_emotion) + "\n"
                    # email_body += str(pre_sz_emotion) + "\n"
                    #zs_emotion和pre_sz_emotion均为字典类型,将其转换为表格
                    email_body += "\nIndex Monitor\n"
                    email_body += "=" * 40 + "\n"
                    email_body += f"{'Metric':<15} {'Today':<10} {'Yesterday':<10} {'Trend':<6}\n"
                    email_body += "-" * 40 + "\n"
                    for key in zs_emotion.keys():
                        email_body += f"{key:<15} {zs_emotion[key]:<10.2f} {pre_sz_emotion[key]:<10.2f} {'↑' if zs_emotion[key] > pre_sz_emotion[key] else '↓' if zs_emotion[key] < pre_sz_emotion[key] else '→':<6}\n"
                    email_body += "=" * 40 + "\n"


                    if (point < 30.0 and point > 0.0) or (pre_zb_cj+pre_zt_cj)/(zb_cj+zt_cj) > 1.5 or (zb_cj+zt_cj)/(pre_zb_cj+pre_zt_cj) > 1.5:
                        send_email(sender_email, sender_password, receiver_email, email_subject_alter, email_body)
                    else:
                        send_email(sender_email, sender_password, receiver_email, email_subject_notify, email_body)
                except Exception as e:
                    print("cal_zt_zj error",e)
                    #打印出堆栈信息
                    import traceback
                    traceback.print_exc()
                    
                

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
