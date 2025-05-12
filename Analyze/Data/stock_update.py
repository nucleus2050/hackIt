import akshare as ak
import pandas as pd


def get_all_stock_code():
    # 获取所有股票的代码
    try:
        stock_df = ak.stock_zh_a_spot_em()
        # 1. 过滤掉总市值为0的股票
        # stock_df = stock_df[stock_df["总市值"] != 0.0]
        
        # # 2. 过滤掉名称中包含"退"的股票（退市股票）
        # stock_df = stock_df[~stock_df["名称"].str.contains("退", na=False)]
        
        # # 3. 过滤掉名称中包含"PT"的股票（特别处理的股票，通常是停牌或问题股票）
        # stock_df = stock_df[~stock_df["名称"].str.contains("PT", na=False)]
        
        # # 4. 过滤掉成交量为0的股票（可能是停牌股票）
        # if "成交量" in stock_df.columns:
        #     stock_df = stock_df[stock_df["成交量"] > 0]
        
        # # 5. 过滤掉最新价为0或NaN的股票
        # if "最新价" in stock_df.columns:
        #     stock_df = stock_df[stock_df["最新价"] > 0]

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


#获取当前所有股票代码以及名称,并保存到csv文件中
def get_all_stock_code_name():
    stock_code_name_map = get_all_stock_code()
    if not stock_code_name_map:
        print("无法获取股票代码和名称列表，程序退出")
        return
    df = pd.DataFrame.from_dict(stock_code_name_map, orient='index', columns=['股票名称'])
    df.index.name = '股票代码'  # 设置索引名称
    df.to_csv("./Data/public/stock.csv", encoding="utf_8_sig")




if __name__ == '__main__':
    get_all_stock_code_name()