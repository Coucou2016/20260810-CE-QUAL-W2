# W2LIB 假名体系（Corpus Alias）

统一代号：**`W2LIB`**  
未来 Markdown 代号：**`W2MD`**

## 命名规则

| 用途 | 模式 | 示例 |
|---|---|---|
| 单份 PDF 归档 | `W2LIB-{CAT}-{NNN}-{slug}.pdf` | `W2LIB-MAN-001-w2manual455_part1_intro_rev0.pdf` |
| 转 Markdown 目标 | `W2MD-{CAT}-{NNN}-{slug}.md` | `W2MD-MAN-001-w2manual455_part1_intro_rev0.md` |
| 分类合并 PDF | `W2LIB-MERGED-{CAT}-{Title}.pdf` | `W2LIB-MERGED-MAN-User_Manuals.pdf` |
| 全库合并 | `W2LIB-MERGED-ALL-Corpus.pdf` | 见 `03_MERGED_PDF/` |

## 分类代码 CAT

- **MAN** 用户手册
- **DOC** 技术文档 / 工具说明
- **LIT** 文献与研究报告
- **FAC** 简介 / Fact sheet / Summary
- **EXA** 算例说明 PDF
- **REL** 版本说明 / Bugfix

## 目录结构

```
00_INDEX/           假名规则、manifest、本说明与复现脚本
01_RAW_DOWNLOADS/   原始 zip 与零散下载
02_LIBRARY/         分类后的资料（含源码/算例/可执行文件）
03_MERGED_PDF/      按分类合并后的 PDF（便于备份）
04_MARKDOWN/        Mathpix 导出的 W2MD Markdown
05_REPRO_RUNS/      模型复现运行（权威目录：run_20260811_fixed）
```

可执行文件请用 `02_LIBRARY/07_executables/v4.5.5/w2_v455_ifx.exe`，不要用 GitHub 包内 LFS 指针 exe。

## PDF → Markdown 建议流程

1. 读取 `manifest.csv`（每行一个 `alias` / `md_target` / `library_path`）
2. 对 `library_path` 做 OCR/文本抽取
3. 输出到例如 `04_MARKDOWN/{md_target}`
4. 保持 `CAT-NNN-slug` 不变，仅前缀 `W2LIB`→`W2MD`

生成时间（UTC）：2026-08-10T14:00:42.918459+00:00
