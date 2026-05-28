---
name: pytdx_data
description: 通达信行情数据接口 - 使用 pytdx 获取标准行情、扩展行情、本地数据文件读取、板块数据、财务数据。当用户提到通达信数据、股票行情、K线数据、pytdx、tdx数据、板块成分股、本地日线读取时使用此技能。
---

# pytdx_data — 通达信行情数据接口

纯 Python 实现的通达信行情数据接口。支持 A股实时行情、期货/期权/外盘扩展行情、本地日线/分钟线文件解析、板块成分股读取。

## 安装

```bash
pip install pytdx pandas
```

## 模块速览

| 模块 | 导入 | 用途 | 详细文档 |
|------|------|------|----------|
| 标准行情 | `pytdx.hq.TdxHq_API` | A股行情、K线、分时、除权除息 | [references/pytdx_hq_api.md](references/pytdx_hq_api.md) |
| 扩展行情 | `pytdx.exhq.TdxExHq_API` | 期货、期权、外盘、港股 | [references/pytdx_exhq_api.md](references/pytdx_exhq_api.md) |
| 本地读取 | `pytdx.reader` | .day/.lc1/.lc5 文件解析 | [references/pytdx_reader_api.md](references/pytdx_reader_api.md) |
| 连接池 | `pytdx.pool` | 多IP故障转移 | [references/pytdx_pool_api.md](references/pytdx_pool_api.md) |
| 最佳IP | `pytdx.util.best_ip` | 自动选最优服务器 | [references/pytdx_pool_api.md](references/pytdx_pool_api.md) |

## 核心工作流

### 工作流 1: 获取实时行情

```python
from pytdx.hq import TdxHq_API
from pytdx.util.best_ip import select_best_ip

best = select_best_ip()
api = TdxHq_API(heartbeat=True)
try:
    if api.connect(best['ip'], best['port']):
        quotes = api.get_security_quotes([(0, '000001'), (1, '600519')])
        print(api.to_df(quotes)[['code', 'name', 'price', 'open', 'high', 'low', 'vol']])
finally:
    api.disconnect()
```

**关键参数:**
- `heartbeat=True` — 长时间不操作自动发心跳包保持连接
- `auto_retry=True` — 连接断开后自动重连
- `raise_exception=True` — 失败时抛异常而非返回 None

**端口约定:** 标准行情 `7709`, 扩展行情 `7727`.

### 工作流 2: 获取历史K线

```python
from pytdx.hq import TdxHq_API

api = TdxHq_API()
try:
    if api.connect('119.147.212.81', 7709):
        # category=9(日线), 0(深圳), 代码, 起始位置, 条数(最大800)
        data = api.get_security_bars(9, 0, '000001', 0, 100)
        df = api.to_df(data)
        print(df[['datetime', 'open', 'close', 'high', 'low', 'vol']])
finally:
    api.disconnect()
```

**K线周期:** 0=5分钟, 1=15分钟, 3=1小时, 4/9=日线, 5=周线, 6=月线, 10=季线, 11=年线。
**单次最大:** 800条。循环获取可下载全部历史（日线约8000条）。

### 工作流 3: 读取本地日线文件

```python
from pytdx.reader import TdxDailyBarReader, TdxFileNotFoundException

reader = TdxDailyBarReader()
try:
    df = reader.get_df("D:/new_tdx/vipdoc/sz/lday/sz000001.day")
    print(df.tail())
except TdxFileNotFoundException:
    print("文件不存在")
```

通达信默认路径: `{安装目录}/vipdoc/{sz|sh}/lday/{代码}.day`

### 工作流 4: 获取板块成分股

```python
from pytdx.hq import TdxHq_API
from pytdx.params import TDXParams

api = TdxHq_API()
try:
    if api.connect('119.147.212.81', 7709):
        # GN=行业板块, FG=概念板块, SZ=深圳板块
        block_info = api.get_and_parse_block_info(TDXParams.BLOCK_GN)
        print(api.to_df(block_info))
finally:
    api.disconnect()
```

### 工作流 5: 获取扩展行情（期货/港股）

```python
from pytdx.exhq import TdxExHq_API

api = TdxExHq_API()
try:
    if api.connect('61.152.107.141', 7727):
        # 获取可用市场列表
        markets = api.to_df(api.get_markets())
        print(markets)
        # 获取期货K线 (47=股指期货)
        bars = api.get_instrument_bars(9, 47, "IF1709", 0, 10)
        print(api.to_df(bars))
finally:
    api.disconnect()
```

## CLI 工具

安装后，任意目录下直接运行 `pytdx-data`：

```bash
pytdx-data quote 000001 600519              # 实时行情
pytdx-data kline 000001 --count 100          # K线数据
pytdx-data index-bars 000001                 # 指数K线
pytdx-data best-ip                           # 查找最优服务器
pytdx-data read-daily "D:/path/to/sz000001.day"   # 读取日线
pytdx-data read-minline "D:/path/to/sz000001.lc5" # 读取分钟线
pytdx-data blocks --type GN                  # 板块成分股
pytdx-data markets                           # 扩展行情市场列表
```

## 注意事项

- **连接兼容性:** 部分旧版 pytdx 的 `connect()` 返回 bool, 不支持 `with` 语句, 使用 `try/finally` + `disconnect()` 更兼容
- **Tushare 冲突:** 若安装 Tushare, 其内置 pytdx 版本较旧, 执行 `pip uninstall pytdx && pip install pytdx` 重装
- **多线程:** Python GIL 限制, 推荐多进程而非多线程获取并发
- **非股票品种:** 可转债等价格可能为实际 ×10（TDX内部整数存储）
- **分笔翻页:** `get_transaction_data` 最多返回 1800 条, 用 `start` 参数翻页
- **官方文档:** https://pytdx-docs.readthedocs.io/zh-cn/latest/
- **GitHub:** https://github.com/rainx/pytdx

## 输出规范

完成数据获取后:
1. 报告连接服务器 IP 和端口
2. 展示数据前5行预览
3. 说明各字段含义
4. 如有异常, 报告具体错误信息
