# 扩展行情 API 参考 (pytdx.exhq)

用于外盘、期货、期权、港股、美股等非A股品种。连接端口为 `7727`。

## 导入与连接

```python
from pytdx.exhq import TdxExHq_API
from pytdx.params import TDXParams

api = TdxExHq_API(heartbeat=True)
try:
    if api.connect('61.152.107.141', 7727):
        # ... use API ...
        pass
finally:
    api.disconnect()
```

## API 方法列表

### 1. get_markets — 获取市场代码

```python
markets = api.get_markets()
df = api.to_df(markets)
# 列: market, category, name, short_name
```

常见市场ID:
| ID | 名称 | ID | 名称 |
|----|------|----|------|
| 1 | 临时股 | 31 | 香港主板 |
| 28 | 郑州商品 | 47 | 股指期货 |
| 29 | 大连商品 | 8 | 上海个股期权 |
| 30 | 上海期货 | 71 | 港股通 |

### 2. get_instrument_info — 查询代码列表

```python
instruments = api.get_instrument_info(0, 100)  # 起始位置, 数量
```

### 3. get_instrument_count — 查询市场中商品数量

```python
count = api.get_instrument_count()
```

### 4. get_instrument_quote — 查询五档行情

```python
quote = api.get_instrument_quote(47, "IF1709")  # 市场ID, 代码
```

### 5. get_minute_time_data — 查询分时行情

```python
minute = api.get_minute_time_data(47, "IF1709")
```

### 6. get_history_minute_time_data — 查询历史分时行情

```python
history = api.get_history_minute_time_data(31, "00020", 20170811)
# 日期格式: YYYYMMDD
```

### 7. get_instrument_bars — 查询K线数据

```python
bars = api.get_instrument_bars(TDXParams.KLINE_TYPE_DAILY, 8, "10000843", 0, 100)
```

### 8. get_transaction_data — 查询分笔成交

最多返回 1800 条，使用 `start` 参数翻页。

```python
transactions = api.get_transaction_data(31, "00020")
# 翻页:
transactions = api.get_transaction_data(47, "IFL0", 20170810, start=1800)
```

### 9. get_history_transaction_data — 查询历史分笔成交

```python
history = api.get_history_transaction_data(31, "00020", 20170810)
```

## 配置选项

扩展行情 API 同样支持 `multithread`, `heartbeat`, `auto_retry`, `raise_exception` 参数，用法与标准行情一致。
