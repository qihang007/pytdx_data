# 本地数据读取 API 参考 (pytdx.reader)

解析通达信本地数据文件，无需网络连接。

## 日K线文件 (.day)

```python
from pytdx.reader import TdxDailyBarReader, TdxFileNotFoundException

reader = TdxDailyBarReader()
df = reader.get_df("D:/new_tdx/vipdoc/sz/lday/sz000001.day")
# 输出列: open, high, low, close, amount, volume
# 索引: date (datetime)

df.to_csv("000001.csv")  # 保存为CSV
```

**通达信默认路径:**
- 深圳日线: `{安装目录}/vipdoc/sz/lday/sz000001.day`
- 上海日线: `{安装目录}/vipdoc/sh/lday/sh600001.day`

## 扩展行情日线 (期货/期权等)

```python
from pytdx.reader import TdxExHqDailyBarReader

reader = TdxExHqDailyBarReader()
df = reader.get_df("/path/to/lday/29#A1801.day")
# 输出列: open, high, low, close, amount, volume, jiesuan, date
```

## 分钟K线文件

### 格式1: .1 / .5 后缀

```python
from pytdx.reader import TdxMinBarReader
reader = TdxMinBarReader()
df = reader.get_df("/path/to/sh000001.5")
```

### 格式2: .lc1 / .lc5 后缀

```python
from pytdx.reader import TdxLCMinBarReader
reader = TdxLCMinBarReader()
df = reader.get_df("/path/to/sz000001.lc5")
```

输出列: open, high, low, close, amount, volume, date

## 板块信息文件

文件通常位于 `{安装目录}/T0002/blocknew/`。

```python
from pytdx.reader import BlockReader, BlockReader_TYPE_GROUP

# 扁平格式 (每行一只股票)
df = BlockReader().get_df("C:/new_tdx/T0002/blocknew/block_zs.dat")
# 列: blockname, block_type, code_index, code

# 分组格式 (每个板块一行, code_list汇总)
df2 = BlockReader().get_df("C:/new_tdx/T0002/blocknew/block_zs.dat", BlockReader_TYPE_GROUP)
# 列: blockname, block_type, stock_count, code_list
```

## 自定义板块备份文件夹

在通达信中通过 设置→数据维护工具→数据备份 导出后读取。

```python
from pytdx.reader import CustomerBlockReader

# 扁平格式
df = CustomerBlockReader().get_df('C:/Users/fit/Desktop/TdxBak_20171011/blocknew')

# 分组格式
df = CustomerBlockReader().get_df('path/to/blocknew', BlockReader_TYPE_GROUP)
```
