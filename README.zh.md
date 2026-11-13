# CKD Cohort Lab

[English](README.md) · [Tiếng Việt](README.vi.md) · [日本語](README.ja.md) · **中文** · [Français](README.fr.md)

**分析前先检查肾脏数据，再判断哪些患者真正需要实验室尿白蛋白检测。**

CKD Cohort Lab 是一个浏览器工具和一组Python脚本，配套论文稿 *“One value or a distribution? Routine urine dipsticks to target albuminuria testing for kidney failure risk”*（已投稿）。研究对象为越南胡志明市Lanh Binh Thang General Hospital的129名慢性肾脏病（CKD）G3–G5门诊患者。

- **在线工具：** https://ckdco.netlify.app/?lang=zh
- **源代码：** https://github.com/lamkienthanh92/ckdcohortlab
- **存档与引用：** https://doi.org/10.5281/zenodo.24189503（1.2.0版；Zenodo页面列出所有版本）

> 本工具用于研究和教学，不是医疗器械。肾衰竭风险方程（KFRE）尚未在越南患者中验证。

## 工具功能

界面支持英语、越南语、日语、中文和法语五种语言。可在顶部栏选择语言，或在网址后加 `?lang=en`、`vi`、`ja`、`zh` 或 `fr`；默认语言为英语，浏览器会记住您的选择。

1. **载入数据：** Excel（.xlsx、.xls、.ods）或CSV文件，每行一名患者。可按患者ID合并第二个文件（例如尿常规结果）。常用列名（英文）会自动匹配，也可手动调整；名为“Unit <列名>”（例如“Unit PRO”）的单位列会逐行读取。
2. **检查分布：** 计算前先汇总每一列：完整性、分布、被Excel存为日期的数值、超出范围的数值、重复ID、录入ACR与白蛋白÷肌酐的比较、录入eGFR与CKD-EPI 2021的比较。可下载清理后的CSV数据。
3. **结果：** KFRE（4变量，非北美校准）、KDIGO 2024分级、尿试纸相对于ACR的准确性（总体及按分析仪），以及基于分布的分诊：
   - 仅当KFRE的整个预测区间位于阈值一侧时才省略实验室ACR（5年 ≥3% 和 >5%；2年 >10% 和 >40%）；
   - 与将试纸换算为单一ACR值的方法比较；
   - 可选80/90/95/99%区间，是否纳入分析仪变量；
   - 随机70/30拆分和跨分析仪验证；
   - 可编辑价格的直接检测费用；
   - 5年KFRE在人群层面与个体层面的一致性；
   - 超出99%区间的尿白蛋白结果，用于复核标本身份。

**隐私：** 文件仅在浏览器中读取，不会上传或保存在服务器上，关闭页面即清除。载入前请删除姓名等身份信息。

可用 `examples/example_synthetic.csv`（140名模拟患者，非真实数据）试用。

## 重现论文分析

```bash
cd analysis
pip install -r requirements.txt
python triage_analysis.py --data ../examples/example_synthetic.csv --out results
python make_figures.py   --data ../examples/example_synthetic.csv --out figures
```

在研究数据上，脚本可重现论文报告的数值（例如：采用90%区间时，129名患者中66名需要实验室ACR，2名出现错误决策；换算为单一值时25名出现错误决策）。仓库不含研究数据，见“数据”一节。输入格式和选项见 `analysis/README.md`（英文）。

## 方法简介

采用最小二乘法和留一法交叉验证，根据年龄、性别、eGFR和糖尿病（临床模型），以及另加的试纸蛋白等级、比重和分析仪（试纸模型）预测log ACR。预测区间为 预测值 ± z·s·√(1 + x′(X′X)⁻¹x)。由于KFRE随ACR增加，在区间两端分别计算KFRE；只有两端位于阈值同一侧时，才无需实验室ACR即可作出该阈值的决策。

## 仓库结构

| 路径 | 内容 |
|---|---|
| `index.html` | 浏览器工具（单个文件，无需构建） |
| `vendor/` | React 18.3.1 和 SheetJS 0.18.5，随包附带，不依赖外部脚本服务器 |
| `examples/` | 模拟示例数据及生成脚本 |
| `analysis/` | 重现论文表格和图形的Python脚本 |
| `netlify.toml` | Netlify设置（静态网站，无构建） |
| `CITATION.cff`、`.zenodo.json` | 供GitHub和Zenodo使用的引用元数据 |

## 数据

仓库不含患者数据。经Lanh Binh Thang General Hospital伦理审查委员会批准后，可向通讯作者合理申请获取去标识化的研究数据。

## 引用

> Nguyen ATT, Pham TA, Phan HD, Phan TC, Lam TH, Huynh NH, Tran HNT, Lam TK, Le CV. CKD Cohort Lab: browser tool and analysis code for distribution-based albuminuria triage (version 1.3.0). Zenodo; 2026. https://doi.org/10.5281/zenodo.24189503

## 许可

代码：MIT（见 `LICENSE`）。第三方组件遵循各自的许可（见 `ATTRIBUTION.md`）。
