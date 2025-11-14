# 如何使用 Expression Atlas 工具

## ❌ 错误用法

**不要直接运行 MCP server：**
```bash
python mcp_server.py  # ❌ 这会报错！
```

MCP server 是通过 **JSON-RPC 协议**通信的，不接受直接的文本输入。

## ✅ 正确用法

### 方法1：Claude Desktop 集成（推荐）

**适合场景：** 你想通过自然语言与Claude对话来获取数据

**步骤：**

1. **安装依赖：**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置 Claude Desktop：**

   编辑配置文件（根据你的操作系统）：
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

   添加：
   ```json
   {
     "mcpServers": {
       "expression-atlas": {
         "command": "python",
         "args": [
           "/完整路径/Get_data_from_expression_atlas/mcp_server.py"
         ]
       }
     }
   }
   ```

3. **重启 Claude Desktop**

4. **开始对话：**
   - "我需要拟南芥seedling的数据"
   - "帮我找人类大脑表达数据"
   - "下载实验 E-MTAB-513 的数据"

### 方法2：交互式命令行工具

**适合场景：** 你想在命令行中交互式操作

```bash
python chat_interface.py
```

工具会引导你：
1. 输入实验ID（如果已知）
2. 或者选择物种、实验类型、关键词
3. 获取下载链接

### 方法3：Python 脚本

**适合场景：** 你知道实验ID，想直接下载

```python
from expression_atlas import ExpressionAtlasAPI

api = ExpressionAtlasAPI()

# 拟南芥组织表达数据
experiment_id = "E-MTAB-3358"

# 下载数据
files = api.download_experiment_data(
    experiment_id=experiment_id,
    output_dir="./arabidopsis_data"
)

print(f"下载的文件: {files}")
```

### 方法4：手动下载（最可靠）

**适合场景：** 自动下载失败时

由于 Expression Atlas 对自动访问有限制，**手动下载是最可靠的方法**：

1. **访问实验页面：**
   - 拟南芥：https://www.ebi.ac.uk/gxa/experiments/E-MTAB-3358
   - 人类组织：https://www.ebi.ac.uk/gxa/experiments/E-MTAB-513
   - 小鼠组织：https://www.ebi.ac.uk/gxa/experiments/E-MTAB-5214

2. **点击 "Downloads" 标签**

3. **下载你需要的文件：**
   - **TPM (Transcripts Per Million)** - 推荐用于比较不同基因
   - **FPKM (Fragments Per Kilobase Million)** - 类似TPM
   - **Raw counts** - 原始计数，用于差异表达分析

4. **使用工具加载数据：**
   ```python
   from expression_atlas import ExpressionAtlasAPI

   api = ExpressionAtlasAPI()
   df = api.load_expression_data('./downloads/E-MTAB-3358-tpms.tsv')

   # 查看数据
   print(df.head())

   # 筛选seedling相关列（如果有的话）
   seedling_cols = [col for col in df.columns if 'seedling' in col.lower()]
   if seedling_cols:
       seedling_data = df[seedling_cols]
       print(seedling_data.head())
   ```

## 📊 常见实验ID

### 拟南芥 (Arabidopsis)
- **E-MTAB-3358** - 多组织表达数据（可能包含 seedling）
- 实验页面：https://www.ebi.ac.uk/gxa/experiments/E-MTAB-3358

### 人类 (Human)
- **E-MTAB-513** - Human Body Map（多组织）
- 实验页面：https://www.ebi.ac.uk/gxa/experiments/E-MTAB-513

### 小鼠 (Mouse)
- **E-MTAB-5214** - 多组织表达数据
- 实验页面：https://www.ebi.ac.uk/gxa/experiments/E-MTAB-5214

## 🔍 如何找到更多实验

1. **浏览 Expression Atlas：**
   https://www.ebi.ac.uk/gxa/experiments

2. **筛选条件：**
   - 物种（Species）
   - 实验类型（Baseline / Differential）
   - 关键词（Gene, Tissue, Disease）

3. **记下实验ID**（格式：E-MTAB-XXXX 或 E-GEOD-XXXX）

4. **使用本工具下载或分析**

## ⚠️ 常见问题

### Q: 为什么自动下载失败？

A: Expression Atlas 对自动化访问有限制（返回 403 错误）。这是正常的，请使用手动下载。

### Q: MCP server 报 JSON 解析错误？

A: MCP server 不能直接在命令行交互。请：
- 使用 Claude Desktop 集成，或
- 使用 `python chat_interface.py`

### Q: 找不到 seedling 数据？

A: 下载后检查：
1. TSV 文件的列名（sample 名称）
2. 配套的 metadata 文件（.sdrf.txt）
3. 实验描述页面中的样本信息

## 📝 完整工作流示例：拟南芥 Seedling

```bash
# 步骤1: 访问实验页面
# https://www.ebi.ac.uk/gxa/experiments/E-MTAB-3358

# 步骤2: 查看实验描述和样本信息

# 步骤3: 下载文件
# - E-MTAB-3358-tpms.tsv (表达数据)
# - E-MTAB-3358.condensed-sdrf.tsv (样本信息)

# 步骤4: 分析数据
python
```

```python
import pandas as pd
from expression_atlas import ExpressionAtlasAPI

# 加载表达数据
api = ExpressionAtlasAPI()
expr_df = api.load_expression_data('./E-MTAB-3358-tpms.tsv')

# 加载样本信息
sample_df = pd.read_csv('./E-MTAB-3358.condensed-sdrf.tsv', sep='\t')

# 查看样本类型
print(sample_df.columns)
print(sample_df['organism part'].unique())  # 查看组织类型

# 筛选seedling样本
if 'seedling' in sample_df['organism part'].values:
    seedling_samples = sample_df[sample_df['organism part'] == 'seedling']['Sample Characteristic[individual]'].values
    seedling_data = expr_df[seedling_samples]
    print(f"找到 {len(seedling_samples)} 个 seedling 样本")
    print(seedling_data.head())
```

## 🆘 需要帮助？

1. 查看详细文档：`README.md`
2. MCP 配置：`MCP_SETUP.md`
3. 中文指南：`USAGE_GUIDE.md`
4. Expression Atlas 帮助：https://www.ebi.ac.uk/gxa/help/index.html
