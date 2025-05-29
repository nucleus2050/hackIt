
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

class DetectFileHandler(FileSystemEventHandler):
    global sender_email
    global sender_password
    global receiver_email
    global email_subject
    def on_created(self, event):
        """当检测到新文件创建时调用此方法"""
        if not event.is_directory:
            print(f"检测到新文件: {event.src_path}")
            # time.sleep(1)
            # #如果文件时point目录下的文件，则计算当天的挣钱效应
            # if "point" in event.src_path:
            #     point = cal_today_point(event.src_path)
            #     print(event.src_path,point)
            #     if point < 30.0 and point > 0.0:
            #         email_body = "cur point is " + str(point) + " less than 30.0"
            #         send_email(sender_email, sender_password, receiver_email, email_subject, email_body)
            if "zt" in event.src_path:
                time.sleep(1)
                #如果文件时zt目录下的文件，计算总成交额和封板资金
                import cal_zt_zj
                try:
                    point_path = event.src_path.replace("zt","point")
                    zb_path = event.src_path.replace("zt","zb")
                    point = cal_today_point(point_path)
                    zt_zj,zt_cj = cal_zt_zj.cal_zt_zj_simple(event.src_path)
                    zb_cj = cal_zt_zj.cal_zb_zj_simple(zb_path)
                    email_body = "cur zt_zj is " + str(zt_zj) + " zt_cj is " + str(zt_cj) + " zt_zj/zt_cj is " + str(zt_zj/zt_cj)
                    if point < 30.0 and point > 0.0:
                        email_body = "point:" + str(point) + "\n"
                        email_body += "fb:" + str(zt_zj) + "\n" 
                        email_body += "cj:" +  str(zt_cj) + "\n"
                        email_body += "fcb:" +  str(zt_zj/zt_cj) + "\n"
                        email_body += "zb:" +  str(zb_cj) + "\n"
                        email_body += "tocal_cj:" +str(zb_cj+zt_cj) + "\n"
                        send_email(sender_email, sender_password, receiver_email, email_subject_alter, email_body)
                    else:
                        email_body = "point:" + str(point) +  "\n"
                        email_body += "fb:" + str(zt_zj) + "\n"
                        email_body += "cj:" +  str(zt_cj) + "\n"
                        email_body += "fcb:" +  str(zt_zj/zt_cj) + "\n"
                        email_body += "zb:" +  str(zb_cj) + "\n"
                        email_body += "tocal_cj:" +str(zb_cj+zt_cj) + "\n"
                        send_email(sender_email, sender_password, receiver_email, email_subject_notify, email_body)
                except Exception as e:
                    print("cal_zt_zj error",e)
                

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
