# 连接池 & 批量下载 API 参考

## 连接池 (pytdx.pool) — 实验性

提供多IP故障转移机制，提升API调用可靠性。

**架构:**
- **M** (主连接): 正在通讯
- **H** (热备): 心跳包维持, 故障时提升为M
- **P** (备选池): 周期性重排, 随时准备替换

```python
from pytdx.hq import TdxHq_API
from pytdx.pool.ippool import AvailableIPPool
from pytdx.config.hosts import hq_hosts
import random

# 随机选取5个IP作为连接池
ips = [(v[1], v[2]) for v in hq_hosts]
random.shuffle(ips)
ips5 = ips[:5]

# 创建IP池
ippool = AvailableIPPool(TdxHq_API, ips5)
primary_ip, hot_backup_ip = ippool.sync_get_top_n(2)

# 使用连接池API
api = TdxHqPool_API(TdxHq_API, ippool)
try:
    if api.connect(primary_ip, hot_backup_ip):
        ret = api.get_xdxr_info(0, '000001')
        print(ret)
finally:
    api.disconnect()
```

## 批量下载完整K线数据

日线级别约8000条覆盖全部历史。每次请求最多800条，需循环获取。

```python
from pytdx.hq import TdxHq_API

def get_all_day_data(api, market, code):
    """批量下载某只股票全部日K线数据"""
    data = []
    for i in range(10):
        # start逆序: 7200-7999, ..., 最后0-799
        data += api.get_security_bars(9, market, code, (9 - i) * 800, 800)
    return api.to_df(data)

api = TdxHq_API()
try:
    if api.connect('119.147.212.81', 7709):
        df = get_all_day_data(api, 0, '000001')
        print(df)
finally:
    api.disconnect()
```

## 通过 select_best_ip 自动选最优服务器

```python
from pytdx.util.best_ip import select_best_ip

info = select_best_ip()
print(f"最优: {info['ip']}:{info['port']}")
# 返回 dict: {'ip': '...', 'port': 7709}
```
