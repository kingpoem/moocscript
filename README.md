# MoocScript

Python 抽离了 mooc-helper 核心 API 请求逻辑。将请求结果保存为 Json，方便后续处理成 markdown 和 pdf 供复习使用。

注意，对于限时作业，一旦进行了请求，就将会开始计时。

## 环境搭建

```bash
uv sync
```

### 配置认证令牌

获取 MOB_TOKEN 教程 [youtube视频链接](https://www.youtube.com/watch?v=WrZi3_1TSA4)


```bash
export MOOC_MOB_TOKEN=xxx
```

## 运行方法

```bash
uv run python fetch_json.py      # 获取 JSON 数据
uv run python convert_markdown.py # 转换为 Markdown
uv run python fetch_all.py        # 一次性运行前两个任务
```
