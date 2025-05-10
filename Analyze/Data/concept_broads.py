
def get_all_broads():
    import pandas as pd
    import akshare as ak
    #获取所有板块
    dfs = ak.stock_board_concept_name_ths()

    print(dfs)
    
    #获取板块名称和板块代码
    broad_name = dfs["name"].tolist()
    broad_code = dfs["code"].tolist()
    
    #将板块名称和板块代码转换为字典
    broad_dict = dict(zip(broad_code, broad_name))
    
    #将字典保存到csv文件中
    # 方法1：使用一个列名
    df = pd.DataFrame.from_dict(broad_dict, orient='index', columns=['板块名称'])
    df.index.name = '板块代码'  # 设置索引名称
    
    # 或者方法2：创建包含两列的DataFrame
    # data = []
    # for code, name in zip(broad_code, broad_name):
    #     data.append({'板块代码': code, '板块名称': name})
    # df = pd.DataFrame(data)
    
    df.to_csv("./Data/public/concept_broad.csv", encoding="utf_8_sig")
    return broad_dict


def get_broads_codes(broadFilePath):
    import pandas as pd
    import akshare as ak
    #读取csv文件
    df = pd.read_csv(broadFilePath)
    #获取板块代码和板块名称
    broad_code = df['板块代码'].tolist()
    broad_name = df['板块名称'].tolist()
    #将板块代码和板块名称转换为字典
    broad_dict = dict(zip(broad_code, broad_name))

    #遍历所有板块，获取每个板块包含的股票代码，并将股票代码保存到csv文件中
    for code in broad_code:
        #获取每个板块包含的股票代码
        stock_df = ak.stock_board_concept_info_ths(symbol=code)
        stock_code = stock_df['代码'].tolist()
        stock_name = stock_df['名称'].tolist()
        #将股票代码和股票名称转换为字典
        stock_dict = dict(zip(stock_code, stock_name))
        #将字典保存到csv文件中
        df = pd.DataFrame.from_dict(stock_dict, orient='index', columns=['名称'])
        df.index.name = '代码'  # 设置索引名称
        #csv文件为板块代码.csv
        df.to_csv("./Data/public/concept_broads/" + code + ".csv", encoding="utf_8_sig")


if __name__ == '__main__':
    get_all_broads()
    # get_broads_codes("./Data/public/concept_broad.csv")