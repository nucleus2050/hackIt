#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时行情获取系统 - 使用akshare
获取主要指数的实时行情并在终端显示
"""

import time
import os
import sys
from datetime import datetime

class RealTimeMarket:
    def __init__(self):
        self.market_data = {}
        self.running = False
        self.update_interval = 60  # 更新间隔（秒）
        
        # 主要指数代码配置
        self.indexes = {
            'szzs': '000001',
            'szcz': '399001', 
            'cybz': '399006',
            'kc50': '000688',
            'hs300': '000300',
            'zz500': '000905',
            'sz50': '000016',
            'zz1000': '000852',
            'hszs': 'HSI',
            'hskj': 'HSTECH'
        }
        
        # 颜色配置
        self.colors = {
            'red': '\033[91m',      # 红色（上涨）
            'green': '\033[92m',    # 绿色（下跌）
            'yellow': '\033[93m',   # 黄色
            'blue': '\033[94m',     # 蓝色
            'purple': '\033[95m',   # 紫色
            'cyan': '\033[96m',     # 青色
            'white': '\033[97m',    # 白色
            'bold': '\033[1m',      # 粗体
            'end': '\033[0m'        # 结束
        }

    def get_akshare_data(self):
        """使用akshare获取所有A股指数数据，优先使用新浪API"""
        try:
            import akshare as ak
            
            result = {}
            
            # 优先使用新浪API
            # print("优先使用新浪API获取A股指数数据...")
            result = self.get_sina_data()
            
            # 如果新浪API获取失败或数据不足，使用东财API作为备用
            if len(result) < 6:  # 期望至少获取6个主要指数
                print(f"新浪API获取数据不足({len(result)}个)，使用东财API作为备用...")
                eastmoney_result = self.get_eastmoney_data()
                result.update(eastmoney_result)  # 合并结果，新浪数据优先
            
            # print(f"总共获取到 {len(result)} 个指数数据:", result)
            return result
            
        except ImportError:
            print("akshare未安装，请运行: pip install akshare")
            return {}
        except Exception as e:
            print(f"获取akshare数据失败: {e}")
            return {}

    def get_sina_data(self):
        """使用新浪API获取A股指数数据"""
        try:
            import akshare as ak
            
            result = {}
            
            # 使用新浪API获取所有指数数据
            data = ak.stock_zh_index_spot_sina()
            # print(f"新浪API获取数据: {len(data)}条记录")
            # print(f"新浪API列名: {list(data.columns)}")
            
            # 定义需要的指数代码
            target_codes = ['sh000001', 'sh000016', 'sh000688', 'sh000300', 'sh000905', 'sh000852', 'sz399001', 'sz399006']
            
            for _, row in data.iterrows():
                # 新浪API的字段名可能不同，需要适配
                code = row.get('代码')
                # print('row：',row,'code：',code)
                if str(code) in target_codes:
                    # 适配不同的字段名
                    name = row.get('名称')
                    price = row.get('最新价')
                    change = row.get('涨跌幅')
                    change_amount = row.get('涨跌额')
                    volume = row.get('成交量')
                    amount = row.get('成交额')
                    #实际代码需要将sh或者sz去掉
                    realcode = code.replace('sh', '').replace('sz', '')
                    result[realcode] = {
                        'name': row['名称'],
                        'price': row['最新价'],
                        'change': row['涨跌幅'],
                        'change_amount': row['涨跌额'],
                        'volume': row['成交量'],
                        'amount': row['成交额']
                    }
                    # print(f"成功获取 {name} ({realcode}): {price} ({change:+.2f}%)")
            return result
            
        except Exception as e:
            print(f"新浪API获取失败: {e}")
            return {}

    def get_eastmoney_data(self):
        """使用东财API获取A股指数数据"""
        try:
            import akshare as ak
            
            result = {}
            
            # 定义不同系列的指数
            index_series = {
                '上证系列指数': ['000001', '000016', '000688', '000300', '000905', '000852'],
                '深证系列指数': ['399001', '399006'],
            }
            
            # 获取不同系列的指数数据
            for series_name, codes in index_series.items():
                try:
                    print(f"获取{series_name}数据...")
                    data = ak.stock_zh_index_spot_em(symbol=series_name)
                    print(f"获取{series_name}数据成功: {len(data)}条记录")
                    
                    for _, row in data.iterrows():
                        code = row['代码']
                        if code in codes:
                            result[code] = {
                                'name': row['名称'],
                                'price': row['最新价'],
                                'change': row['涨跌幅'],
                                'change_amount': row['涨跌额'],
                                'volume': row['成交量'],
                                'amount': row['成交额']
                            }
                            print(f"成功获取 {row['名称']} ({code}): {row['最新价']} ({row['涨跌幅']:+.2f}%)")
                    time.sleep(3)  # 成功获取后等待3秒
                    
                except Exception as e:
                    print(f"获取{series_name}失败: {e}")
            
            return result
            
        except Exception as e:
            print(f"东财API获取失败: {e}")
            return {}

    def get_overseas_data(self):
        """获取海外指数数据，优先使用新浪API"""
        try:
            import akshare as ak
            
            result = {}
            
            # 优先使用新浪API
            # print("优先使用新浪API获取港股指数数据...")
            result = self.get_sina_hk_data()
            
            # 如果新浪API获取失败或数据不足，使用东财API作为备用
            if len(result) < 2:  # 期望至少获取2个港股指数
                # print(f"新浪API获取港股数据不足({len(result)}个)，使用东财API作为备用...")
                eastmoney_result = self.get_eastmoney_hk_data()
                result.update(eastmoney_result)  # 合并结果，新浪数据优先
            
            return result
            
        except Exception as e:
            print(f"获取海外数据失败: {e}")
            return {}

    def get_sina_hk_data(self):
        """使用新浪API获取港股指数数据"""
        try:
            import akshare as ak
            
            result = {}
            
            # 使用新浪API获取港股指数数据
            hk_data = ak.stock_hk_index_spot_sina()
            # print(f"新浪API获取港股数据: {len(hk_data)}条记录")
            # print(f"新浪港股API列名: {list(hk_data.columns)}",hk_data)
            
            # 查找恒生指数
            hsi_row = hk_data[hk_data.get('代码', hk_data.get('symbol', '')) == 'HSI']
            if not hsi_row.empty:
                row = hsi_row.iloc[0]
                # 适配不同的字段名
                name = row.get('名称', row.get('name', ''))
                price = row.get('最新价', row.get('price', row.get('current', 0)))
                change = row.get('涨跌幅', row.get('change_pct', row.get('pct_chg', 0)))
                change_amount = row.get('涨跌额', row.get('change', row.get('change_amount', 0)))
                volume = row.get('成交量', row.get('volume', row.get('vol', 0)))
                amount = row.get('成交额', row.get('amount', row.get('turnover', 0)))
                
                result['HSI'] = {
                    'name': name,
                    'price': price,
                    'change': change,
                    'change_amount': change_amount,
                    'volume': volume,
                    'amount': amount
                }
                # print(f"成功获取恒生指数: {price} ({change:+.2f}%)")
            else:
                print("未找到恒生指数数据")
            
            # 查找恒生科技指数
            hstech_row = hk_data[hk_data.get('代码', hk_data.get('symbol', '')) == 'HSTECH']
            if not hstech_row.empty:
                row = hstech_row.iloc[0]
                # 适配不同的字段名
                name = row.get('名称', row.get('name', ''))
                price = row.get('最新价', row.get('price', row.get('current', 0)))
                change = row.get('涨跌幅', row.get('change_pct', row.get('pct_chg', 0)))
                change_amount = row.get('涨跌额', row.get('change', row.get('change_amount', 0)))
                volume = row.get('成交量', row.get('volume', row.get('vol', 0)))
                amount = row.get('成交额', row.get('amount', row.get('turnover', 0)))
                
                result['HSTECH'] = {
                    'name': name,
                    'price': price,
                    'change': change,
                    'change_amount': change_amount,
                    'volume': volume,
                    'amount': amount
                }
                # print(f"成功获取恒生科技指数: {price} ({change:+.2f}%)")
            else:
                print("未找到恒生科技指数数据")
            
            return result
            
        except Exception as e:
            print(f"新浪API获取港股数据失败: {e}")
            return {}

    def get_eastmoney_hk_data(self):
        """使用东财API获取港股指数数据"""
        try:
            import akshare as ak
            
            result = {}
            
            # 使用东财API获取港股指数数据
            hk_data = ak.stock_hk_index_spot_em()
            # print(f"东财API获取港股数据: {len(hk_data)}条记录")
            
            # 查找恒生指数
            hsi_row = hk_data[hk_data['代码'] == 'HSI']
            if not hsi_row.empty:
                row = hsi_row.iloc[0]
                result['HSI'] = {
                    'name': row['名称'],
                    'price': row['最新价'],
                    'change': row['涨跌幅'],
                    'change_amount': row['涨跌额'],
                    'volume': row.get('成交量', 0),
                    'amount': row.get('成交额', 0)
                }
                # print(f"成功获取恒生指数: {row['最新价']} ({row['涨跌幅']:+.2f}%)")
            else:
                print("未找到恒生指数数据")
            
            # 查找恒生科技指数
            hstech_row = hk_data[hk_data['代码'] == 'HSTECH']
            if not hstech_row.empty:
                row = hstech_row.iloc[0]
                result['HSTECH'] = {
                    'name': row['名称'],
                    'price': row['最新价'],
                    'change': row['涨跌幅'],
                    'change_amount': row['涨跌额'],
                    'volume': row.get('成交量', 0),
                    'amount': row.get('成交额', 0)
                }
                print(f"成功获取恒生科技指数: {row['最新价']} ({row['涨跌幅']:+.2f}%)")
            else:
                print("未找到恒生科技指数数据")
            
            return result
            
        except Exception as e:
            print(f"东财API获取港股数据失败: {e}")
            return {}

    def format_number(self, num, decimal_places=2, is_price=False):
        """格式化数字显示"""
        if num is None:
            return "N/A"
        
        if isinstance(num, (int, float)):
            # 如果是价格数据，不进行单位转换，直接显示原始数值
            if is_price:
                return f"{num:.{decimal_places}f}"
            # 其他数据（成交量、成交额）才进行单位转换
            elif abs(num) >= 1e8:
                return f"{num/1e8:.2f}亿"
            elif abs(num) >= 1e4:
                return f"{num/1e4:.2f}万"
            else:
                return f"{num:.{decimal_places}f}"
        return str(num)

    def get_color(self, change):
        """根据涨跌获取颜色"""
        if change is None:
            return self.colors['white']
        elif change > 0:
            return self.colors['red']
        elif change < 0:
            return self.colors['green']
        else:
            return self.colors['white']

    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        """显示表头"""
        print(f"{self.colors['bold']}{self.colors['cyan']}")
        print("=" * 120)
        print(f"{'实时行情监控系统 (akshare)':^120}")
        print(f"{'更新时间: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^120}")
        print("=" * 120)
        print(f"{self.colors['end']}")

    def display_market_data(self):
        """显示市场数据"""
        print(f"{self.colors['bold']}")
        print(f"{'index name':<12} {'price':<12} {'change_amount':<12} {'change':<10} {'volume':<15} {'amount':<15}")
        print("-" * 120)
        print(f"{self.colors['end']}")
        
        for name, symbol in self.indexes.items():
            data = self.market_data.get(symbol, {})
            
            if data:
                price = self.format_number(data.get('price'), 2, is_price=True)
                change_amount = self.format_number(data.get('change_amount'), 2)
                change_pct = self.format_number(data.get('change'), 2)
                volume = self.format_number(data.get('volume'))
                amount = self.format_number(data.get('amount'))
                
                # 获取颜色
                color = self.get_color(data.get('change'))
                
                # 状态显示
                # status = "🔴" if data.get('change', 0) > 0 else "🟢" if data.get('change', 0) < 0 else "⚪"
                
                print(f"{name:<12} {color}{price:<12}{self.colors['end']} "
                      f"{color}{change_amount:<12}{self.colors['end']} "
                      f"{color}{change_pct:<4}%    {self.colors['end']} "
                      f"{volume:<15} {amount:<15}")
            else:
                print(f"{name:<12} {'N/A':<12} {'N/A':<12} {'N/A':<10} {'N/A':<15} {'N/A':<15} {'❌':<8}")

    def update_data(self):
        """更新数据"""
        # print(f"{self.colors['yellow']}正在更新数据...{self.colors['end']}")
        
        # 获取A股数据
        a_stock_data = self.get_akshare_data()
        self.market_data.update(a_stock_data)
        
        # 获取海外数据
        overseas_data = self.get_overseas_data()
        self.market_data.update(overseas_data)
        
        success_count = len(self.market_data)
        total_count = len(self.indexes)
        # print(f"{self.colors['green']}数据更新完成: {success_count}/{total_count} 个指数获取成功{self.colors['end']}")

    def run(self):
        """运行实时监控"""
        self.running = True
        # print(f"{self.colors['bold']}{self.colors['blue']}启动实时行情监控系统...{self.colors['end']}")
        
        try:
            while self.running:
                self.clear_screen()
                # self.display_header()
                self.update_data()
                self.display_market_data()
                
                print(f"\n{self.colors['yellow']}按 Ctrl+C 退出程序{self.colors['end']}")
                print(f"{self.colors['cyan']}下次更新: {self.update_interval} 秒后{self.colors['end']}")
                
                # 等待更新间隔
                for i in range(self.update_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print(f"\n{self.colors['yellow']}程序被用户中断{self.colors['end']}")
        except Exception as e:
            print(f"\n{self.colors['red']}程序运行出错: {e}{self.colors['end']}")
        finally:
            self.running = False
            print(f"{self.colors['blue']}实时行情监控系统已停止{self.colors['end']}")

    def stop(self):
        """停止监控"""
        self.running = False

def main():
    # """主函数"""
    # print("实时行情监控系统 (akshare)")
    # print("支持的指数:")
    # print("- 上证指数 (000001)")
    # print("- 深证成指 (399001)")
    # print("- 创业板指 (399006)")
    # print("- 科创50 (000688)")
    # print("- 沪深300 (000300)")
    # print("- 中证500 (000905)")
    # print("- 上证50 (000016)")
    # print("- 中证1000 (000852)")
    # print("- 恒生指数 (HSI)")
    # print("- 恒生科技 (HSTECH)")
    # print()
    
    # 检查依赖
    # try:
    #     import akshare as ak
    #     print("✓ akshare 已安装")
    # except ImportError:
    #     print("✗ akshare 未安装，请运行: pip install akshare")
    #     return
    
    # print()
    # input("按回车键开始监控...")
    
    # 启动监控
    market = RealTimeMarket()
    market.run()

if __name__ == "__main__":
    main()