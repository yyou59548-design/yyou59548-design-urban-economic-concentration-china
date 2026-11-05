# 《中国城市经济集聚：空间结构与城市贡献的变化》科研复现候选仓库

**状态（2026年11月5日）：仓库现已Public，公开范围仅为可运行的核心复现子集；并非整篇论文的完整原始资料到结果复现归档。** 代码及衍生数据尚无明确再使用许可，部分上游数据的再分发权限和作者共同许可需要核实。当前公共访问状态详见 [PUBLIC_ACCESS_STATUS_20261105.md](docs/PUBLIC_ACCESS_STATUS_20261105.md)。

### 本次实际完成的验证

原始 `joint_state_audit.py` 读取295城市的质量及代表点，从WGS84椭球Albers投影重新计算坐标和带宽矩阵，在已归档的150个连续峰位置重新计算各城市贡献，组成120组相邻年度比较和30条规格序列。输入压缩后，输出的四份CSV在本地核验时与完整归档结果逐字节相同；跨环境验收另外逐格核查数值容差与严格的标签/状态/行列一致性，不将数值近似一致冒充为字节一致。4个规格共8次贡献者转换，转换组最低Jaccard为0.9689207388，120条有限变化分解的最大恒等式残差为6.31e-15。

独立编写的 `experiment_b_reproduce.py` 直接利用四城市高斯场及驻点方程，对81个周围GDP分配状态重新求平局门槛和连续峰位置，逐行与历史参考结果比较。81次求解均通过，门槛最大差约为6.9e-15，且每个解具有负定Hessian及A、B为前两大贡献者。

运行：

```bash
python -m pip install -r requirements-core.txt
python tests/run_core_checks.py
```


### 2026年11月4日新增独立数学验收

`tests/run_independent_oracles.py` 不调用历史峰值位置或原生产计算器，而是重新求解四城市实验B的81个平局根、两种相反的事件顺序、无标签拓扑反射构造的数值等价性，以及295城GDP与经纬度输入所确定的2021年珠三角名义GDP及可比增长链的峰值与门槛。另用 `tests/run_prd_150_fresh_peaks.py` 从295城质量及三类经纬度重新求出150个目标峰，并独立验证4规格8次领先者转换及30/30的有符号贡献差时序；存档峰坐标只用于求解后的对照，未参与初值设置。另增加四种篡改情形的完整性拒绝测试，并以 `tests/run_table_contract_tests.py` 检查微小浮点差异可识别而实质性差异必须拒绝。上述测试已在本地实际执行，属于**新增的独立检验**，但不是2,062个完整空间场和全部轮廓的从零再计算。

10月28日完整科研归档的三卷ZIP已实际检查：5,403个互不重复路径、全部ZIP CRC及5,401个已解压科研文件SHA256通过，原输入保护清单也通过。完整归档本身不放入这个公开GitHub；`scripts/audit_full_archive.py` 可在本地重复检查。当前执行环境因缺少 `xlrd==2.0.1` 未能运行完整四阶段compact，所以不将其记为本轮通过。具体证据、操作和局限见 `docs/REPRODUCTION_COVERAGE_20261104.md`。

新增执行命令：

```bash
python -m pip install -r requirements-core.txt
python scripts/verify_manifest.py
python tests/run_table_contract_tests.py
python tests/run_core_checks.py
python tests/run_independent_oracles.py
python tests/run_prd_150_fresh_peaks.py
python tests/run_integrity_negative_tests.py
```

### 公开核心仓库与上游完整复算的区别

另据2026年11月4日独立验收记录，作者保留的三卷完整研究归档已重新完成2,062条七尺度场记录、150个主要连通轮廓及273条P₂来源版本情形的数值计算。详细证据见 [UPSTREAM_REEXECUTION_20261104.md](docs/UPSTREAM_REEXECUTION_20261104.md)。这些完整程序和数据**未全部包含在当前公开仓库中**；来源审计中2项历史代码/输入身份FAIL、冻结Excel环境及第三方材料许可仍待解决。

### 不能据此宣称的事项

其中原有joint-state核查使用已归档峰位置和组件记录，另有150个目标峰的独立新求解测试。公开GitHub没有全部上游七尺度场、轮廓和P₂计算所需的完整输入及程序；亦未独立逐条认证2,950项原始统计出版物。完整研究归档中实际进行的新计算须与本公开仓库的核心测试分别列示。

仓库已经公开，但衍生数据与代表点坐标的再分发权限、作者同意、代码及数据许可证和永久归档标识仍须确认。审稿意见和回复、第三方原始出版物以及历史缓存均不放入这一公开候选包。具体见 `docs/PUBLICATION_GATE_CN.md`。

### 新增完整性核验

运行 `python scripts/verify_manifest.py` 核对当前仓库的全部科研文件SHA-256，再运行 `python tests/run_core_checks.py`。原始CSV的UTF-8 BOM及行尾均是归档字节的一部分。该仓库现可公开浏览，但尚未明确授予开源许可或数据再使用许可，也不能作为全论文完整科研归档引用。
