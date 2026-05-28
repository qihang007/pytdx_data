#!/usr/bin/env python3
"""
pytdx_data - 通达信行情数据获取工具
基于 pytdx 库封装常用操作，支持命令行调用。

用法:
  python pytdx_data.py quote 000001 600519          # 获取实时行情
  python pytdx_data.py kline 000001 --market 0       # 获取日K线
  python pytdx_data.py best-ip                        # 查找最优服务器
  python pytdx_data.py read-daily sz000001.day        # 读取本地日线文件
  python pytdx_data.py blocks --type GN               # 获取板块成分股
  python pytdx_data.py markets                        # 获取扩展行情市场列表
"""

import sys
import json
import argparse
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from pytdx.hq import TdxHq_API
    from pytdx.params import TDXParams
except ImportError:
    print("请先安装 pytdx: pip install pytdx")
    sys.exit(1)


# ─── 服务器列表 ───────────────────────────────────────────
DEFAULT_HOSTS = [
    ("119.147.212.81", 7709),
    ("120.76.152.87", 7709),
    ("124.71.187.72", 7709),
    ("116.128.188.228", 7709),
]

BLOCK_TYPES = {
    "SZ": TDXParams.BLOCK_SZ,     # 深圳板块
    "FG": TDXParams.BLOCK_FG,     # 概念板块
    "GN": TDXParams.BLOCK_GN,     # 行业板块
    "DEFAULT": "block.dat",       # 默认板块
}


def find_best_server():
    """自动查找最优行情服务器"""
    try:
        from pytdx.util.best_ip import select_best_ip
        info = select_best_ip()
        return info["ip"], info["port"]
    except Exception:
        return DEFAULT_HOSTS[0]


def connect_api(ip=None, port=None, auto_best=True):
    """创建并连接API"""
    if auto_best:
        ip, port = find_best_server()
        print(f"最优服务器: {ip}:{port}")
    elif ip and port:
        pass
    else:
        ip, port = DEFAULT_HOSTS[0]

    api = TdxHq_API(heartbeat=True)
    api.connect(ip, port)
    return api


def cmd_quote(args):
    """获取实时行情"""
    api = connect_api()
    codes = []
    for code in args.codes:
        code = code.strip()
        market = 0 if code.startswith(("0", "2", "3")) else 1
        codes.append((market, code))

    try:
        quotes = api.get_security_quotes(codes)
        df = api.to_df(quotes)
        if df is not None and not df.empty:
            cols = ["code", "name", "price", "last_close", "open",
                     "high", "low", "vol", "amount"]
            display_cols = [c for c in cols if c in df.columns]
            print(df[display_cols].to_string(index=False))
        if args.json:
            print(json.dumps(quotes, ensure_ascii=False, default=str, indent=2))
    finally:
        api.disconnect()


def cmd_kline(args):
    """获取K线数据"""
    api = connect_api()
    market = args.market if args.market is not None else (
        0 if args.code.startswith(("0", "2", "3")) else 1
    )

    try:
        k_lines = api.get_security_bars(args.category, market, args.code,
                                         args.start, args.count)
        df = api.to_df(k_lines)
        if df is not None and not df.empty:
            display_cols = ["datetime", "open", "close", "high", "low", "vol"]
            cols = [c for c in display_cols if c in df.columns]
            print(df[cols].to_string(index=False))
        if args.json:
            print(json.dumps(k_lines, ensure_ascii=False, default=str, indent=2))
    finally:
        api.disconnect()


def cmd_best_ip(args):
    """查找最优服务器"""
    try:
        from pytdx.util.best_ip import select_best_ip
        info = select_best_ip()
        print(f"最优服务器: {info['ip']}:{info['port']}")
        if args.json:
            print(json.dumps(info, ensure_ascii=False, default=str, indent=2))
    except Exception as e:
        print(f"查找失败: {e}")
        print(f"使用默认服务器: {DEFAULT_HOSTS[0][0]}:{DEFAULT_HOSTS[0][1]}")


def cmd_read_daily(args):
    """读取本地日线文件"""
    from pytdx.reader import TdxDailyBarReader, TdxFileNotFoundException

    reader = TdxDailyBarReader()
    try:
        df = reader.get_df(args.file)
        if df is not None:
            print(df.tail(20).to_string())
            print(f"\n总记录数: {len(df)}")
            print(f"日期范围: {df.index[0]} ~ {df.index[-1]}")
        if args.json:
            print(json.dumps(df.tail(20).to_dict(), ensure_ascii=False,
                             default=str, indent=2))
    except TdxFileNotFoundException:
        print(f"文件未找到: {args.file}")
    except Exception as e:
        print(f"读取失败: {e}")


def cmd_read_minline(args):
    """读取本地分钟线文件"""
    from pytdx.reader import TdxMinBarReader, TdxLCMinBarReader

    if args.file.lower().endswith((".lc1", ".lc5")):
        reader = TdxLCMinBarReader()
    else:
        reader = TdxMinBarReader()

    try:
        df = reader.get_df(args.file)
        if df is not None:
            print(df.tail(20).to_string())
            print(f"\n总记录数: {len(df)}")
    except Exception as e:
        print(f"读取失败: {e}")


def cmd_blocks(args):
    """获取板块成分股"""
    api = connect_api()
    block_key = args.type.upper() if args.type else "DEFAULT"
    block_file = BLOCK_TYPES.get(block_key, "block.dat")

    try:
        data = api.get_and_parse_block_info(block_file)
        df = api.to_df(data)
        if df is not None and not df.empty:
            print(df.to_string(index=False))
            print(f"\n板块内股票数: {len(df)}")
        if args.json:
            print(json.dumps(data, ensure_ascii=False, default=str, indent=2))
    finally:
        api.disconnect()


def cmd_markets(args):
    """获取扩展行情市场列表"""
    from pytdx.exhq import TdxExHq_API

    api = TdxExHq_API()
    try:
        if api.connect(DEFAULT_HOSTS[0][0], 7727):
            markets = api.get_markets()
            df = api.to_df(markets)
            if df is not None and not df.empty:
                print(df.to_string(index=False))
        else:
            print("连接扩展行情服务器失败")
    finally:
        api.disconnect()


def cmd_index_bars(args):
    """获取指数K线"""
    api = connect_api()
    try:
        data = api.get_index_bars(args.category, 1 if args.sh else 0,
                                   args.code, args.start, args.count)
        df = api.to_df(data)
        if df is not None and not df.empty:
            display_cols = ["datetime", "open", "close", "high", "low", "vol"]
            cols = [c for c in display_cols if c in df.columns]
            print(df[cols].to_string(index=False))
    finally:
        api.disconnect()


# ─── 命令行解析 ───────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="pytdx_data 通达信行情数据工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # quote - 实时行情
    p = subparsers.add_parser("quote", help="获取实时行情")
    p.add_argument("codes", nargs="+", help="股票代码，如 000001 600519")
    p.add_argument("--json", action="store_true", help="输出JSON")
    p.set_defaults(func=cmd_quote)

    # kline - K线数据
    p = subparsers.add_parser("kline", help="获取K线数据")
    p.add_argument("code", help="股票代码")
    p.add_argument("--market", type=int, choices=[0, 1], help="市场(0=深圳,1=上海)")
    p.add_argument("--category", type=int, default=9, help="K线类别(9=日线,4=日线)")
    p.add_argument("--start", type=int, default=0, help="起始位置")
    p.add_argument("--count", type=int, default=20, help="获取条数(最大800)")
    p.add_argument("--json", action="store_true", help="输出JSON")
    p.set_defaults(func=cmd_kline)

    # index-bars - 指数K线
    p = subparsers.add_parser("index-bars", help="获取指数K线")
    p.add_argument("code", help="指数代码，如000001(上证)")
    p.add_argument("--sh", action="store_true", default=True, help="上海市场")
    p.add_argument("--category", type=int, default=9, help="K线类别")
    p.add_argument("--start", type=int, default=0, help="起始位置")
    p.add_argument("--count", type=int, default=20, help="获取条数")
    p.set_defaults(func=cmd_index_bars)

    # best-ip - 最优服务器
    p = subparsers.add_parser("best-ip", help="查找最优服务器")
    p.add_argument("--json", action="store_true", help="输出JSON")
    p.set_defaults(func=cmd_best_ip)

    # read-daily - 读取日线文件
    p = subparsers.add_parser("read-daily", help="读取本地日线文件")
    p.add_argument("file", help="日线文件路径(.day)")
    p.add_argument("--json", action="store_true", help="输出JSON")
    p.set_defaults(func=cmd_read_daily)

    # read-minline - 读取分钟线文件
    p = subparsers.add_parser("read-minline", help="读取本地分钟线文件")
    p.add_argument("file", help="分钟线文件路径")
    p.set_defaults(func=cmd_read_minline)

    # blocks - 板块成分股
    p = subparsers.add_parser("blocks", help="获取板块成分股")
    p.add_argument("--type", default="DEFAULT", choices=["SZ", "FG", "GN", "DEFAULT"],
                   help="板块类型")
    p.add_argument("--json", action="store_true", help="输出JSON")
    p.set_defaults(func=cmd_blocks)

    # markets - 扩展行情市场列表
    p = subparsers.add_parser("markets", help="获取扩展行情市场列表")
    p.set_defaults(func=cmd_markets)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
