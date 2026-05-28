# 标准行情 API 参考 (pytdx.hq)

## 导入与连接

```python
from pytdx.hq import TdxHq_API
from pytdx.params import TDXParams

api = TdxHq_API(
    multithread=True,       # 多线程支持
    heartbeat=True,         # 心跳包（自动启用multithread）
    auto_retry=True,        # 自动重连
    raise_exception=False   # True=抛异常, False=返回None
)

# 连接 (部分旧版本connect()返回bool不支持with, 用try/finally更兼容)
try:
    if api.connect('119.147.212.81', 7709):
        # ... use API ...
        pass
finally:
    api.disconnect()
```

## 服务器列表

```python
from pytdx.config.hosts import hq_hosts
# 预置服务器列表, 每个元素为 (name, ip, port)
```

## 参数常量

### K线周期 (category)

| 值 | 含义 | 值 | 含义 |
|----|------|----|------|
| 0 | 5分钟 | 6 | 月K线 |
| 1 | 15分钟 | 7 | 1分钟 |
| 2 | 30分钟 | 8 | 1分钟 |
| 3 | 1小时 | 9 | 日K线 |
| 4 | 日K线 | 10 | 季K线 |
| 5 | 周K线 | 11 | 年K线 |

### 市场代码

- `TDXParams.MARKET_SZ` = 0 (深圳)
- `TDXParams.MARKET_SH` = 1 (上海)

### 板块文件

- `TDXParams.BLOCK_SZ` = `"block_zs.dat"`
- `TDXParams.BLOCK_FG` = `"block_fg.dat"`
- `TDXParams.BLOCK_GN` = `"block_gn.dat"`
- `TDXParams.BLOCK_DEFAULT` = `"block.dat"`

## API 方法列表

### 1. get_security_quotes — 获取股票实时行情

获取多只股票的实时行情。

```python
quotes = api.get_security_quotes([(0, '000001'), (1, '600519')])
df = api.to_df(quotes)
```

**注意:** 非股票品种（如可转债）价格可能为实际价格 ×10（TDX内部整数存储）。

### 2. get_security_bars — 获取K线

```python
# category, market, stockcode, start, count
k_lines = api.get_security_bars(9, 0, '000001', 4, 3)
# count 最大 800
```

### 3. get_security_count — 获取市场股票数量

```python
count = api.get_security_count(0)  # 0=深圳, 1=上海
```

### 4. get_index_bars — 获取指数K线

```python
index_bars = api.get_index_bars(9, 1, '000001', 1, 2)  # 上证指数日K
```

### 5. get_minute_time_data — 查询分时行情

```python
minute_data = api.get_minute_time_data(1, '600300')
```

### 6. get_history_minute_time_data — 查询历史分时行情

```python
history_minute = api.get_history_minute_time_data(TDXParams.MARKET_SH, '600300', 20161209)
# 日期格式: YYYYMMDD
```

### 7. get_transaction_data — 查询分笔成交

```python
transactions = api.get_transaction_data(TDXParams.MARKET_SZ, '000001', 0, 30)
# 参数: 市场, 代码, 起始位置, 数量
```

### 8. get_history_transaction_data — 查询历史分笔成交

```python
transactions = api.get_history_transaction_data(TDXParams.MARKET_SZ, '000001', 0, 10, 20170209)
```

### 9. get_company_info_category — 查询公司信息目录

```python
info = api.get_company_info_category(TDXParams.MARKET_SZ, '000001')
```

### 10. get_company_info_content — 读取公司信息详情

```python
content = api.get_company_info_content(0, '000001', '000001.txt', 0, 100)
```

### 11. get_xdxr_info — 读取除权除息信息

```python
xdxr = api.get_xdxr_info(1, '600300')
```

### 12. get_finance_info — 读取财务信息

```python
finance = api.get_finance_info(0, '000001')
```

### 13. get_k_data — 读取K线数据（按日期范围）

```python
k_data = api.get_k_data('000001', '2017-07-03', '2017-07-10')
```

### 14. get_and_parse_block_info — 读取板块信息

```python
block_info = api.get_and_parse_block_info(TDXParams.BLOCK_GN)
```

## 辅助方法

```python
df = api.to_df(data)          # 转换为DataFrame
stats = api.get_traffic_stats() # 流量统计
```

## 重连机制

默认重试策略: `[0.1, 0.5, 1, 2]` 秒间隔, 重试4次。
自定义策略需继承 `RetryStrategy`, 实现 `gen()` 生成器方法。
