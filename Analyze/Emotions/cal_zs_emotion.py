import akshare as ak

#获取指定指数成分股
def get_zs_cf(zhs_code='399006'):
    index_stock_info_df = ak.index_stock_cons_csindex('399006')
    return index_stock_info_df

if __name__ == '__main__':
    get_zs_cf()