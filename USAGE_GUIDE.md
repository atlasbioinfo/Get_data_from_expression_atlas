# Expression Atlas Data Retrieval - 使用指南

## 目录
1. [快速开始](#快速开始)
2. [交互式对话工具](#交互式对话工具)
3. [程序化访问](#程序化访问)
4. [数据类型说明](#数据类型说明)
5. [常见物种列表](#常见物种列表)
6. [实验ID格式](#实验id格式)
7. [故障排除](#故障排除)

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 最简单的使用方式

```python
from expression_atlas import get_expression_data

# 下载指定实验的数据
files = get_expression_data('E-MTAB-513', output_dir='./data')
```

---

## 交互式对话工具

这是最推荐的使用方式，特别适合不熟悉 Expression Atlas 的用户。

### 启动交互式界面

```bash
python chat_interface.py
```

或者在 Python 中：

```python
from chat_interface import ExpressionAtlasChat

chat = ExpressionAtlasChat()
chat.start()
```

### 对话流程

工具会依次询问以下问题：

#### 1️⃣ 实验ID（可选）
如果你已经知道想要的实验ID（如 E-MTAB-513），直接输入即可。

**示例实验ID：**
- `E-MTAB-513` - 人类组织基线表达
- `E-MTAB-5214` - 小鼠组织基线表达
- `E-GEOD-21860` - 癌症 vs 正常组织差异表达

如果不知道，按 Enter 跳过，工具会帮你搜索。

#### 2️⃣ 物种/生物
选择你感兴趣的物种：
- Human / 人类
- Mouse / 小鼠
- Rat / 大鼠
- Arabidopsis / 拟南芥
- Zebrafish / 斑马鱼
- 等等...

#### 3️⃣ 实验类型

**选项1 - Baseline（基线实验）：**
- 显示正常、未处理条件下的基因表达
- 适合回答："这个基因在哪里表达？"
- 数据包括：不同组织、细胞类型、发育阶段等

**选项2 - Differential（差异实验）：**
- 比较不同条件下的基因表达差异
- 适合回答："哪些基因在疾病中上调/下调？"
- 数据包括：处理 vs 对照、疾病 vs 健康等

**选项3 - 两者都可以**

#### 4️⃣ 搜索关键词

可以输入：
- 基因名称（如：BRCA1, TP53, APOE）
- 组织名称（如：brain, liver, heart）
- 疾病名称（如：cancer, diabetes, Alzheimer）
- 其他关键词（如：drug treatment, stress）

#### 5️⃣ 输出目录

指定下载文件的保存位置（默认：`./expression_atlas_data`）

---

## 程序化访问

适合需要批量处理或集成到其他程序的场景。

### 方式1：使用便捷函数

```python
from expression_atlas import get_expression_data

# 下载所有可用文件
files = get_expression_data(
    experiment_id='E-MTAB-513',
    output_dir='./data/human_tissues'
)

# 只下载特定类型的文件
files = get_expression_data(
    experiment_id='E-MTAB-513',
    output_dir='./data',
    file_types=['analytics', 'tpms']  # 只下载这两种文件
)
```

### 方式2：使用 API 类

```python
from expression_atlas import ExpressionAtlasAPI

api = ExpressionAtlasAPI()

# 获取实验信息
info = api.get_experiment_info('E-MTAB-513')
print(info)

# 下载数据
files = api.download_experiment_data(
    experiment_id='E-MTAB-513',
    output_dir='./data'
)

# 加载数据到 pandas DataFrame
if 'analytics' in files:
    df = api.load_expression_data(files['analytics'])
    print(df.head())
```

### 方式3：使用查询构建器

```python
from expression_atlas import ExpressionAtlasQuery

# 构建查询
query = ExpressionAtlasQuery()
query.set_species("homo sapiens") \
     .set_experiment_type("baseline") \
     .set_keyword("brain")

# 执行搜索
results = query.execute()

# 或者直接下载
query.set_experiment_id("E-MTAB-513")
files = query.download(output_dir="./data")
```

---

## 数据类型说明

### 下载的文件类型

| 文件类型 | 说明 | 用途 |
|---------|------|-----|
| **analytics** | 分析结果文件（TSV格式） | 主要的表达数据，包含统计结果 |
| **expression** | 表达查询结果 | 特定查询的表达数据 |
| **tpms** | TPM标准化数据 | 转录本每百万（Transcripts Per Million） |
| **fpkms** | FPKM标准化数据 | 每百万片段每千碱基片段（FPKM） |
| **counts** | 原始计数数据 | RNA-seq 的原始 read counts |
| **r-object** | R数据对象（.Rdata） | 可在R中直接加载的数据对象 |
| **design** | 实验设计文件（SDRF） | 样本注释和实验设计信息 |

### Baseline 实验数据格式

典型的 baseline 数据包含：
- 基因ID（Gene ID）
- 基因名称（Gene Name）
- 各个组织/条件的表达值（TPM 或 FPKM）

### Differential 实验数据格式

典型的 differential 数据包含：
- 基因ID（Gene ID）
- 基因名称（Gene Name）
- log2 fold change（对数倍数变化）
- p-value / adjusted p-value（显著性）
- 比较的条件（对照 vs 实验）

---

## 常见物种列表

| 中文名 | 英文名 | 学名 | 支持的关键词 |
|--------|--------|------|-------------|
| 人类 | Human | *Homo sapiens* | human, humans, homo sapiens |
| 小鼠 | Mouse | *Mus musculus* | mouse, mice, mus musculus |
| 大鼠 | Rat | *Rattus norvegicus* | rat |
| 拟南芥 | Arabidopsis | *Arabidopsis thaliana* | arabidopsis, thale cress |
| 斑马鱼 | Zebrafish | *Danio rerio* | zebrafish |
| 果蝇 | Fruit fly | *Drosophila melanogaster* | drosophila, fruit fly |
| 酵母 | Yeast | *Saccharomyces cerevisiae* | yeast |
| 线虫 | Worm | *Caenorhabditis elegans* | worm, c. elegans |
| 鸡 | Chicken | *Gallus gallus* | chicken |
| 猪 | Pig | *Sus scrofa* | pig |
| 牛 | Cattle | *Bos taurus* | cow, cattle |

---

## 实验ID格式

Expression Atlas 的实验ID遵循特定格式：

```
E-<数据库>-<编号>
```

### 常见的数据库前缀

- **E-MTAB-** - ArrayExpress 数据库
- **E-GEOD-** - GEO (Gene Expression Omnibus) 数据库
- **E-MEXP-** - 旧的 ArrayExpress 格式
- **E-TABM-** - 另一种 ArrayExpress 格式

### 示例

- `E-MTAB-513` ✓
- `E-GEOD-21860` ✓
- `E-MEXP-1234` ✓
- `EMTAB513` ✗ (缺少连字符)
- `E-MTAB513` ✗ (缺少连字符)

---

## 在Python中分析数据

### 加载和查看数据

```python
import pandas as pd
from expression_atlas import ExpressionAtlasAPI

api = ExpressionAtlasAPI()

# 下载数据
files = api.download_experiment_data('E-MTAB-513', './data')

# 加载到 DataFrame
if 'analytics' in files:
    df = pd.read_csv(files['analytics'], sep='\t')

    # 查看数据结构
    print(f"数据维度: {df.shape}")
    print(f"\n列名: {df.columns.tolist()}")
    print(f"\n前几行:\n{df.head()}")

    # 基本统计
    print(f"\n数值列的统计:\n{df.describe()}")
```

### 筛选高表达基因

```python
# 假设有一列叫 'brain' 表示大脑中的表达
if 'brain' in df.columns:
    high_expr = df[df['brain'] > 10]  # TPM > 10
    print(f"高表达基因数量: {len(high_expr)}")
    print(high_expr[['Gene Name', 'brain']].head(10))
```

### 可视化

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 绘制表达分布
plt.figure(figsize=(10, 6))
df['brain'].hist(bins=50)
plt.xlabel('Expression (TPM)')
plt.ylabel('Frequency')
plt.title('Gene Expression Distribution in Brain')
plt.show()

# 热图（如果有多个组织）
tissue_cols = ['brain', 'liver', 'heart', 'kidney']  # 示例
if all(col in df.columns for col in tissue_cols):
    plt.figure(figsize=(12, 8))
    sns.heatmap(df[tissue_cols].head(50), cmap='viridis')
    plt.title('Top 50 Genes Expression Across Tissues')
    plt.show()
```

---

## 故障排除

### 问题1：无法下载文件

**可能原因：**
- 实验ID不存在或格式错误
- 网络连接问题
- 文件在FTP上不可用

**解决方案：**
1. 检查实验ID格式是否正确
2. 访问实验页面确认数据可用：`https://www.ebi.ac.uk/gxa/experiments/<实验ID>`
3. 检查网络连接

### 问题2：API搜索返回空结果

**可能原因：**
- Expression Atlas 的 JSON API 可能不公开或有限制
- 搜索参数不匹配任何实验

**解决方案：**
1. 直接使用已知的实验ID
2. 访问 Expression Atlas 网站手动搜索：https://www.ebi.ac.uk/gxa/home
3. 浏览实验列表：https://www.ebi.ac.uk/gxa/experiments

### 问题3：下载的文件无法打开

**可能原因：**
- 文件损坏或下载不完整
- R对象需要在R中打开

**解决方案：**
1. 重新下载文件
2. 对于 .Rdata 文件，在R中使用 `load()` 函数
3. 对于 TSV 文件，使用文本编辑器或 pandas 打开

### 问题4：数据文件很大

**解决方案：**
1. 只下载需要的文件类型：
   ```python
   files = get_expression_data(
       'E-MTAB-513',
       file_types=['analytics']  # 只下载分析结果
   )
   ```
2. 使用 pandas 分块读取：
   ```python
   for chunk in pd.read_csv('large_file.tsv', sep='\t', chunksize=1000):
       # 处理每个数据块
       process(chunk)
   ```

---

## 更多资源

- **Expression Atlas 官网:** https://www.ebi.ac.uk/gxa/home
- **帮助文档:** https://www.ebi.ac.uk/gxa/help/index.html
- **浏览实验:** https://www.ebi.ac.uk/gxa/experiments
- **FTP服务器:** ftp://ftp.ebi.ac.uk/pub/databases/microarray/data/atlas/experiments/

---

## 示例工作流程

### 完整的分析流程示例

```python
from expression_atlas import ExpressionAtlasAPI
import pandas as pd
import matplotlib.pyplot as plt

# 1. 初始化API
api = ExpressionAtlasAPI()

# 2. 下载数据
print("下载数据...")
files = api.download_experiment_data(
    'E-MTAB-513',  # 人类组织基线表达
    output_dir='./data/human_tissues',
    file_types=['analytics']
)

# 3. 加载数据
print("加载数据...")
df = api.load_expression_data(files['analytics'])

# 4. 数据探索
print(f"\n数据维度: {df.shape}")
print(f"列名: {df.columns.tolist()[:10]}...")  # 显示前10列

# 5. 筛选感兴趣的基因
genes_of_interest = ['BRCA1', 'TP53', 'APOE', 'APP']
if 'Gene Name' in df.columns:
    gene_data = df[df['Gene Name'].isin(genes_of_interest)]
    print(f"\n找到 {len(gene_data)} 个目标基因")

# 6. 可视化
# （这里添加你的可视化代码）

# 7. 导出结果
gene_data.to_csv('./results/genes_of_interest.csv', index=False)
print("\n分析完成！结果已保存。")
```

---

## 贡献和反馈

如有问题或建议，请在 GitHub 上提交 issue。
