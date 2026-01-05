# MoocScript

使用 Python 抽离了 [mooc-helper](https://github.com/whale4113/mooc-helper) 核心 API 请求逻辑。将请求结果保存为 Json，方便后续处理成 markdown 和 pdf 供复习使用。此项目初衷完全是为了方便复习使用。

该脚本会将一门课程的所有测验和考试 md 文件进行合并，然后转成 pdf 供打印。 
如果你对导出 pdf 的颜值有较高要求，也可以将合并的 md 放到你喜欢的应用里进行 pdf 转换。

> [!CAUTION]
> 注意，对于限时作业和考试，一旦进行了请求，就会开始计时。务必谨慎使用。

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
uv run python fetch_json.py      # 获取 JSON（交互式选择课程，--all 下载全部）
uv run python convert_markdown.py # 转换为 Markdown
uv run python convert_pdf.py     # 转换为 PDF

uv run python fetch_all.py        # 一键运行（交互式选择，--all 下载全部，--skip-markdown/--skip-pdf 跳过步骤）
```

## 免责声明

本项目（以下简称"项目"）仅供参考和学习使用。作者尽力确保项目的准确性和可靠性，但不提供任何明示或暗示的保证，包括但不限于对项目的适销性、特定用途的适用性或无侵权的保证。

作者不对因使用本项目而产生的任何直接、间接、偶然、特殊、惩罚性或结果性损害承担任何责任，包括但不限于因使用、误用、或依赖项目中的信息而导致的利润损失、业务中断或数据丢失。

本项目中的所有内容均基于作者的个人见解和经验，不代表任何组织或公司的观点。

使用者应自行承担使用本项目所产生的一切风险。在任何情况下，作者均不对使用本项目而导致的任何损失或损害承担责任。
