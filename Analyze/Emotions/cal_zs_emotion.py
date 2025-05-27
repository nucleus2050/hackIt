import akshare as ak


def get_zs_cf():
    index_stock_info_df = ak.index_stock_cons_csindex('000001')
    print(index_stock_info_df)

if __name__ == '__main__':
    get_zs_cf()