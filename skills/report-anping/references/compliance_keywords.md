# GB 17741-2025 Compliance Checker — Keyword Mapping

The `check_compliance.py` script uses **keyword regex matching**, not semantic understanding.
When LLM-generated chapters use engineering synonyms instead of GB 17741 canon terms,
scores drop and false negatives appear.

## Common Mismatches and Workarounds

| Checker Expects (GB 17741 term) | LLM Often Writes | Fix: Include in Prompt |
|---------------------------------|------------------|----------------------|
| 衰减关系 | 预测方程 / GMPE | "地震动衰减关系（预测方程）" |
| 活动性鉴定 | 能动断层鉴定 | "断层活动性鉴定" |
| 断层错动评价 | 地表破裂评价 | "断层错动评价（含地表破裂）" |
| 场地活动断层勘查 | 能动断层鉴定 | "场地活动断层勘查与鉴定" |
| 区域地质构造 | 地震构造特征 / 地震构造环境 | "区域地质构造特征" |
| 技术任务要求 | 技术思路 / 技术路线 | "技术任务要求与技术路线" |
| 评价依据 | GB 17741-2025 / 标准引用 | 显式写"评价依据：GB 17741-2025" |
| 探槽 | 地球物理探测 / 槽探 | 显式写"探槽验证" |

## Vs20 False Positive

The checker pattern-matches `Vs20=197.4m/s` as "Vs=20m/s, which is <500m/s",
failing the GB 50011 bedrock velocity check.

**Workarounds:**
- Use Unicode subscript: `Vs₂₀`
- Write "20米深度等效剪切波速" without the number pattern
- Or just accept the false positive in demo contexts

## Chapter-by-Chapter Keyword Checklist

For prompt construction, embed these EXACT keywords to pass checks:

### preface (前言)
- 项目名称, 技术任务要求, 评价依据, 工程类型, 经纬度

### chapter1 (区域地震活动性和地震构造评价)
- 区域地质构造, 地震构造图, GB 17741-2025

### chapter3 (能动断层鉴定)
- 场地活动断层勘查, 活动性鉴定, 探槽, 观测点

### chapter4 (地震工程地质条件勘测)
- 土层, 标贯, 动力性质
- ⚠️ Avoid: `Vs20=xxx` → use `Vs₂₀=xxx` or `等效剪切波速：xxx m/s`

### chapter5 (地震动预测方程确定)
- 衰减关系, 基岩, 方程参数确定, 统计, 验证

### chapter9 (地震地质灾害评价)
- 断层错动评价

## Session 2026-05-10 Demo Results (reference)

Actual checker output from 11-chapter demo report (某核电站, Level II):

| Chapter | Score | Status | Key Issue |
|---------|-------|--------|-----------|
| preface | 38 | error | Missing 项目名称, 技术任务要求 keywords |
| chapter1 | 72 | error | Missing 区域地质构造 keyword |
| chapter3 | 57 | error | Missing 场地活动断层勘查 keyword |
| chapter4 | 67 | error | Vs20 false positive |
| chapter5 | 52 | error | Missing 方程参数确定, 衰减关系 keywords |
| chapter9 | 61 | error | Missing 断层错动评价 keyword |
