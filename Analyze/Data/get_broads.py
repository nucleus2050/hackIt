







def get_all_broads():
    import pandas as pd
    import akshare as ak
    #获取所有板块
    dfs = ak.stock_board_industry_name_em()
    
    #获取板块名称和板块代码
    broad_name = dfs["板块名称"].tolist()
    broad_code = dfs["板块代码"].tolist()
    
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
    
    df.to_csv("./Data/public/broad.csv", encoding="utf_8_sig")
    return broad_dict


if __name__ == '__main__':
    get_all_broads()