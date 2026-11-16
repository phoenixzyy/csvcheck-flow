# csvcheck-flow 学习说明

这是基于 wireservice/csvkit 的作品集增强，已发布为 [phoenixzyy/csvcheck-flow](https://github.com/phoenixzyy/csvcheck-flow)，保留正常 Fork 关系。上游负责 CSV、Excel、SQL 工具主体；本次实际贡献是可选 JSON Lines 错误报告、13 项 CLI 回归用例、验证脚本及文档。不要把上游功能表述为自己从零开发。实现有 Codex 辅助，适合逐行复查、复现和讲解，不等于已经独立掌握全部代码。

## 结构与执行过程

- `pyproject.toml`：依赖、包信息和命令行入口，`csvclean` 指向 `launch_new_instance`。
- `csvkit/cli.py`：通用参数、输入输出、生命周期和异常呈现。
- `csvkit/cleanup.py`：`RowChecker` 读取表头，检查和修复数据行，保存错误对象；空列判断需等输入完成。
- `csvkit/utilities/csvclean.py`：组织检查器，将清洗结果写 stdout，错误报告写 stderr，存在检查错误则退出 1。
- `csvkit/utilities/csvsql.py`：agate 表到 SQLAlchemy 连接，导入前后 SQL、查询及事务提交。本次没有修改。
- `tests/test_utilities/test_csvclean_jsonl.py`：真正启动 CLI 子进程，分别检查退出码、stdout、stderr。
- `scripts/verify_portfolio.py`：临时生成 Excel，转换 CSV，验证并导入 SQLite，再查询回 CSV；不启动网络服务。

流程是“参数解析 → 打开输入 → RowChecker → 写 CSV → 按选项序列化错误 → 返回状态”。本次只改最后的错误序列化边界。检查规则、修复次序和 SQL 导入都继续使用上游实现。

## 为什么这样设计

原来 stderr 是 CSV，本来就能被程序读取。问题是错误行本身可能过长或过短，报告也随之不等宽；重复列名无法安全作为字典键。JSONL 使用独立的 `column_names` 和 `row` 数组，不使用 `dict(zip(...))`，避免重复键覆盖和多余值丢失。

每个错误对象都有 `line_number`、`msg`、`column_names`、`row`，非空标签另加 `label`。JSON 转义让含换行字段仍只占一行日志。没有错误时保持静默，默认仍是 CSV，退出 1 表示检查发现问题。新参数不隐式开启检查，和上游要求一致。

这是小范围边界设计，不是重构全部数据管道。不要说 JSONL 已实现低内存流式处理：检查器仍会缓存错误，移除空列还会缓存输出行。也不要说所有 stderr 都是 JSON：参数、解码、解析、I/O 失败仍可能输出普通文本。

## 复现与验证

先按 `PORTFOLIO.md` 建立虚拟环境并安装，再执行：

```sh
pytest -q tests/test_utilities/test_csvclean_jsonl.py
pytest -q
python scripts/verify_portfolio.py
csvclean --length-mismatch --error-format jsonl examples/bad.csv > cleaned.csv 2> errors.jsonl
```

最后一条命令预期退出 1，不能当作安装失败。查看两个输出文件，确认正常数据和错误报告分离。把格式切到 `csv`，对照默认格式逐字节兼容的测试。

固定基线 `43d09bf1f39382bc2d66c4f892c9814901179ff8` 原有测试为 367 通过、4 跳过；新增 13 项测试先在原生产代码上全部失败（不认识新参数），实现后全套为 380 通过、4 跳过，另有 31 子测试通过。不是“修复了 13 个缺陷”。35 条警告在前后都存在。完整范围与构建结果见英文说明和进度文件。

多行字段的行号沿用上游“读取到的物理行号减一”，跳过的前置行不包含在此读数中；空列错误用合成行号 1。`--zero` 修改列号提示，不改变错误行号。`--remove-empty-columns` 后 stdout 可能减少列，但错误报告仍保留检查器的表头与错误行，这一点有测试覆盖。

## 可用于面试的讨论题

1. 为什么不是用列名到值的字典？请用重复列名和超长行演示数据丢失。
2. 为什么 stdout 和 stderr 分离？如何区分“发现坏数据”和“程序无法运行”？
3. 为什么选择 JSONL 而非整个 JSON 数组？怎样处理单元格内部换行？内存是否因此降低？
4. 为什么子进程测试比仅调用序列化函数更适合本次变更？测试有没有覆盖已安装 wheel？
5. 空列检查为什么不能仅看当前一行？移除空列对内存和错误报告意味着什么？
6. `csvsql` 已有事务，为什么不能声称所有数据库 DDL 都原子回滚？需要哪些独立数据库实验？
7. 这次工作如何保留开源版权、上游历史、来源和真实贡献边界？

回答时展示代码和复现结果，不把“约十年开发、另十年管理销售客服”的背景扩写成未经证实的技术熟练程度或项目业绩。可以解释错误报告如何用于数据导入批次的排查，但不要编造生产使用经历。

## 练习

1. 增加一个含引号、逗号和制表符的坏数据样例，先写预期，再运行命令验证。
2. 为 `--header-normalize-space` 和 `--skip-lines` 的 JSONL 组合补充测试，并解释行号语义。
3. 写一个消费 JSONL 的小脚本按 label 统计错误数量；遇到非 JSON 诊断时明确失败，不静默丢弃。
4. 在单独分支比较错误量增大时的内存开销，用真实测量决定是否需要改 RowChecker。
5. 用临时 SQLite 表设计“第二个文件失败时第一个文件是否回滚”的实验；区分 DML 与 DDL，不将结果直接推广到 PostgreSQL/MySQL。

远端 Fork 已通过 phoenixzyy 登录会话创建，功能提交为 `65eb3941c251bb60a751e72f0c33ff12c27d05e4`，远端 Git tree 与本地验证版本一致。CI 结果见 Actions 和进度文件，不能将本地测试结果冒充远端 CI 结果。没有部署、购买服务、联系上游或修改其他候选项目。
