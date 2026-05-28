# pytdx-data — 通达信行情数据 CLI 工具

基于 [pytdx](https://github.com/rainx/pytdx) 封装的命令行工具，任意目录下直接调用。也可作为 Claude Code 技能使用。

## 功能

- **实时行情** - A股实时五档行情获取
- **K线数据** - 日线/周线/月线/分钟线（最大800条/次）
- **扩展行情** - 期货、期权、外盘、港股
- **本地数据** - 通达信 .day/.lc1/.lc5 文件解析
- **板块数据** - 行业/概念/地区板块成分股

## 安装

```bash
git clone https://github.com/qihang007/pytdx_data.git
pip install ./pytdx_data
```

一行即可，依赖 `pytdx` 和 `pandas` 会自动安装。

## CLI 使用

安装后，任意目录下直接运行 `pytdx-data`：

```bash
pytdx-data quote 000001 600519              # 实时行情
pytdx-data kline 000001 --count 100          # K线数据
pytdx-data index-bars 000001                 # 指数K线
pytdx-data best-ip                           # 查找最优服务器
pytdx-data read-daily "D:/path/to/sz000001.day"   # 读取日线
pytdx-data read-minline "D:/path/to/sz000001.lc5" # 读取分钟线
pytdx-data blocks --type GN                  # 板块成分股（GN=行业,FG=概念,SZ=深圳）
pytdx-data markets                           # 扩展行情市场列表
```

## 模块

| 模块 | 导入 | 用途 |
|------|------|------|
| 标准行情 | `pytdx.hq.TdxHq_API` | A股行情、K线、分时、除权除息 |
| 扩展行情 | `pytdx.exhq.TdxExHq_API` | 期货、期权、外盘、港股 |
| 本地读取 | `pytdx.reader` | .day/.lc1/.lc5 文件解析 |
| 连接池 | `pytdx.pool` | 多IP故障转移 |
| 最佳IP | `pytdx.util.best_ip` | 自动选最优服务器 |

## 作为 Claude Code Skill 使用

将此目录放入 `~/.claude/skills/` 下，技能名称为 `pytdx_data`。当用户提到通达信数据、股票行情、K线数据、pytdx、板块成分股等内容时自动触发。

详细 API 参考见 `references/` 目录。

## 注意事项

- 部分旧版 pytdx 的 `connect()` 返回 bool，不支持 `with` 语句，使用 `try/finally` + `disconnect()` 更兼容
- 若安装 Tushare，其内置 pytdx 版本较旧，执行 `pip uninstall pytdx && pip install pytdx` 重装
- 非股票品种（可转债等）价格可能为实际 ×10（TDX内部整数存储）
- 分笔成交 `get_transaction_data` 最多返回 1800 条，用 `start` 参数翻页

## 参考

- [pytdx 官方文档](https://pytdx-docs.readthedocs.io/zh-cn/latest/)
- [pytdx GitHub](https://github.com/rainx/pytdx)
