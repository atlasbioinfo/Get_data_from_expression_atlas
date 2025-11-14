#!/usr/bin/env python3
"""
Smart Chat Interface for Expression Atlas

像和AI对话一样，直接说一句话就能获取数据。
例如："我需要拟南芥seedling的数据"
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from expression_atlas import ExpressionAtlasAPI


# 物种名称映射（中英文）
SPECIES_MAP = {
    # 中文名称
    '人': 'homo sapiens',
    '人类': 'homo sapiens',
    '小鼠': 'mus musculus',
    '老鼠': 'mus musculus',
    '大鼠': 'rattus norvegicus',
    '拟南芥': 'arabidopsis thaliana',
    '斑马鱼': 'danio rerio',
    '果蝇': 'drosophila melanogaster',
    '酵母': 'saccharomyces cerevisiae',
    '线虫': 'caenorhabditis elegans',
    '鸡': 'gallus gallus',
    '猪': 'sus scrofa',
    '牛': 'bos taurus',

    # English names
    'human': 'homo sapiens',
    'humans': 'homo sapiens',
    'homo sapiens': 'homo sapiens',
    'mouse': 'mus musculus',
    'mice': 'mus musculus',
    'mus musculus': 'mus musculus',
    'rat': 'rattus norvegicus',
    'arabidopsis': 'arabidopsis thaliana',
    'thale cress': 'arabidopsis thaliana',
    'zebrafish': 'danio rerio',
    'fruit fly': 'drosophila melanogaster',
    'drosophila': 'drosophila melanogaster',
    'yeast': 'saccharomyces cerevisiae',
    'c. elegans': 'caenorhabditis elegans',
    'worm': 'caenorhabditis elegans',
    'chicken': 'gallus gallus',
    'pig': 'sus scrofa',
    'cow': 'bos taurus',
    'cattle': 'bos taurus',
}

# 常见组织/关键词（中英文）
TISSUE_KEYWORDS = {
    'brain', 'liver', 'heart', 'kidney', 'lung', 'muscle', 'skin',
    'seedling', 'root', 'leaf', 'flower', 'shoot', 'stem',
    '大脑', '肝脏', '心脏', '肾脏', '肺', '肌肉', '皮肤',
    '幼苗', '根', '叶', '花', '芽', '茎',
}

# 实验类型关键词
EXPERIMENT_TYPE_KEYWORDS = {
    'baseline': ['baseline', 'normal', 'tissue', '正常', '组织', '基线'],
    'differential': ['differential', 'disease', 'treatment', 'cancer', '差异', '疾病', '治疗', '癌症'],
}

# 知名实验ID映射
KNOWN_EXPERIMENTS = {
    'homo sapiens': {
        'baseline': 'E-MTAB-513',  # Human Body Map
    },
    'mus musculus': {
        'baseline': 'E-MTAB-5214',  # Mouse tissues
    },
    'arabidopsis thaliana': {
        'baseline': 'E-MTAB-3358',  # Arabidopsis tissues
    },
}


class SmartChatParser:
    """智能解析用户输入，提取意图和参数"""

    def __init__(self):
        self.api = ExpressionAtlasAPI()

    def parse_user_input(self, user_input: str) -> Dict:
        """
        解析用户输入，提取关键信息

        返回:
        {
            'species': str,  # 物种
            'keywords': List[str],  # 关键词
            'experiment_type': str,  # baseline or differential
            'experiment_id': str,  # 如果提到了具体ID
            'intent': str,  # download, search, browse
        }
        """
        user_input_lower = user_input.lower()

        result = {
            'species': None,
            'keywords': [],
            'experiment_type': 'baseline',  # 默认baseline
            'experiment_id': None,
            'intent': 'search',  # 默认是搜索
        }

        # 1. 检测实验ID
        exp_id_match = re.search(r'E-(MTAB|GEOD|MEXP|TABM)-\d+', user_input, re.IGNORECASE)
        if exp_id_match:
            result['experiment_id'] = exp_id_match.group(0).upper()
            result['intent'] = 'download'

        # 2. 检测物种
        for species_name, scientific_name in SPECIES_MAP.items():
            if species_name in user_input_lower:
                result['species'] = scientific_name
                break

        # 3. 检测实验类型
        for exp_type, keywords in EXPERIMENT_TYPE_KEYWORDS.items():
            if any(kw in user_input_lower for kw in keywords):
                result['experiment_type'] = exp_type
                break

        # 4. 提取关键词（组织、条件等）
        for keyword in TISSUE_KEYWORDS:
            if keyword in user_input_lower:
                result['keywords'].append(keyword)

        # 5. 判断意图
        if any(word in user_input_lower for word in ['下载', 'download', '获取', 'get']):
            result['intent'] = 'download'
        elif any(word in user_input_lower for word in ['浏览', 'browse', '查看', 'view', '有什么文件']):
            result['intent'] = 'browse'

        return result

    def recommend_experiment(self, parsed: Dict) -> Optional[str]:
        """根据解析结果推荐实验ID"""
        species = parsed.get('species')
        exp_type = parsed.get('experiment_type', 'baseline')

        if species and species in KNOWN_EXPERIMENTS:
            if exp_type in KNOWN_EXPERIMENTS[species]:
                return KNOWN_EXPERIMENTS[species][exp_type]

        # 如果没有直接匹配，返回该类型的热门实验
        popular = self.api.get_popular_experiments(exp_type)
        if popular:
            return popular[0]

        return None


class SmartChat:
    """智能对话界面"""

    def __init__(self):
        self.parser = SmartChatParser()
        self.api = ExpressionAtlasAPI()

    def browse_ftp_directory(self, experiment_id: str) -> dict:
        """浏览FTP目录（从mcp_server.py复制）"""
        import requests

        https_ftp_base = f"https://ftp.ebi.ac.uk/pub/databases/microarray/data/atlas/experiments/{experiment_id}/"

        try:
            response = requests.get(https_ftp_base, timeout=30)
            if response.status_code == 200:
                files = []
                links = re.findall(r'<a href="([^"]+)">', response.text)
                for link in links:
                    if not link.startswith('?') and link != '../':
                        files.append(link)

                if files:
                    return {
                        'success': True,
                        'experiment_id': experiment_id,
                        'ftp_url': https_ftp_base,
                        'files': files,
                        'method': 'https_ftp_browse'
                    }
        except Exception:
            pass

        # 尝试常见文件模式
        common_patterns = [
            f"{experiment_id}-tpms.tsv",
            f"{experiment_id}-fpkms.tsv",
            f"{experiment_id}-raw-counts.tsv",
            f"{experiment_id}.condensed-sdrf.tsv",
        ]

        available_files = []
        for filename in common_patterns:
            file_url = https_ftp_base + filename
            try:
                head_response = requests.head(file_url, timeout=10)
                if head_response.status_code == 200:
                    available_files.append({
                        'name': filename,
                        'url': file_url,
                        'size': head_response.headers.get('Content-Length', 'unknown')
                    })
            except:
                continue

        if available_files:
            return {
                'success': True,
                'experiment_id': experiment_id,
                'ftp_url': https_ftp_base,
                'files': available_files,
                'method': 'pattern_matching'
            }

        return {
            'success': False,
            'experiment_id': experiment_id,
            'ftp_url': https_ftp_base,
            'message': 'Could not list files automatically.',
            'experiment_page': f"https://www.ebi.ac.uk/gxa/experiments/{experiment_id}"
        }

    def identify_expression_files(self, files_list: list) -> dict:
        """智能识别表达数据文件"""
        expression_files = {
            'tpms': [],
            'fpkms': [],
            'counts': [],
            'metadata': [],
            'other': []
        }

        for file_item in files_list:
            if isinstance(file_item, dict):
                filename = file_item.get('name', '')
            else:
                filename = str(file_item)

            filename_lower = filename.lower()

            if 'tpm' in filename_lower and filename_lower.endswith('.tsv'):
                expression_files['tpms'].append(file_item)
            elif 'fpkm' in filename_lower and filename_lower.endswith('.tsv'):
                expression_files['fpkms'].append(file_item)
            elif 'count' in filename_lower and filename_lower.endswith('.tsv'):
                expression_files['counts'].append(file_item)
            elif 'sdrf' in filename_lower:
                expression_files['metadata'].append(file_item)
            else:
                expression_files['other'].append(file_item)

        # 推荐文件
        recommended = None
        recommended_type = None

        if expression_files['tpms']:
            recommended = expression_files['tpms'][0]
            recommended_type = 'tpms'
        elif expression_files['fpkms']:
            recommended = expression_files['fpkms'][0]
            recommended_type = 'fpkms'
        elif expression_files['counts']:
            recommended = expression_files['counts'][0]
            recommended_type = 'counts'

        return {
            'categorized': expression_files,
            'recommended': recommended,
            'recommended_type': recommended_type,
        }

    def process_query(self, user_input: str):
        """处理用户查询"""
        print("\n" + "=" * 80)
        print(f"💬 你的请求: {user_input}")
        print("=" * 80)

        # 解析输入
        parsed = self.parser.parse_user_input(user_input)

        print("\n🔍 理解你的需求:")
        if parsed['species']:
            print(f"  • 物种: {parsed['species']}")
        if parsed['keywords']:
            print(f"  • 关键词: {', '.join(parsed['keywords'])}")
        if parsed['experiment_type']:
            print(f"  • 实验类型: {parsed['experiment_type']}")
        if parsed['experiment_id']:
            print(f"  • 实验ID: {parsed['experiment_id']}")

        # 确定实验ID
        experiment_id = parsed.get('experiment_id')
        if not experiment_id:
            experiment_id = self.parser.recommend_experiment(parsed)
            if experiment_id:
                print(f"\n✨ 推荐实验: {experiment_id}")

        if not experiment_id:
            print("\n❌ 抱歉，无法找到合适的实验")
            print("请提供更多信息或访问: https://www.ebi.ac.uk/gxa/experiments")
            return

        # 获取实验信息
        print(f"\n📊 实验详情:")
        print(f"  实验ID: {experiment_id}")
        print(f"  实验页面: https://www.ebi.ac.uk/gxa/experiments/{experiment_id}")

        # 浏览FTP目录
        print(f"\n🔎 正在浏览FTP目录...")
        ftp_result = self.browse_ftp_directory(experiment_id)

        if ftp_result.get('success'):
            files = ftp_result.get('files', [])
            print(f"  ✓ 找到 {len(files)} 个文件")
            print(f"  FTP URL: {ftp_result['ftp_url']}")

            # 识别表达数据文件
            print(f"\n🧠 智能识别基因表达数据文件...")
            identified = self.identify_expression_files(files)

            categorized = identified.get('categorized', {})

            # 显示找到的表达数据文件
            found_expr_files = False
            for category in ['tpms', 'fpkms', 'counts']:
                file_list = categorized.get(category, [])
                if file_list:
                    found_expr_files = True
                    print(f"\n  {category.upper()} 文件:")
                    for f in file_list:
                        if isinstance(f, dict):
                            print(f"    • {f.get('name')} ({f.get('size')} bytes)")
                        else:
                            print(f"    • {f}")

            # 推荐下载
            recommended = identified.get('recommended')
            if recommended:
                print("\n" + "=" * 80)
                print("🎯 推荐下载:")
                print("=" * 80)

                if isinstance(recommended, dict):
                    rec_name = recommended.get('name')
                    rec_url = recommended.get('url')
                    rec_size = recommended.get('size')
                    print(f"  文件: {rec_name}")
                    print(f"  大小: {rec_size} bytes")
                    print(f"  URL: {rec_url}")
                else:
                    print(f"  文件: {recommended}")
                    print(f"  URL: {ftp_result['ftp_url']}{recommended}")

                # 询问是否下载
                print("\n" + "=" * 80)
                response = input("是否要下载这个文件? (yes/no): ").strip().lower()

                if response in ['yes', 'y', '是', 'YES']:
                    print("\n📥 开始下载...")
                    output_dir = './expression_atlas_data'

                    downloaded = self.api.download_experiment_data(
                        experiment_id=experiment_id,
                        output_dir=output_dir
                    )

                    if downloaded:
                        print(f"\n✅ 下载成功!")
                        print(f"  保存位置: {output_dir}")
                        for file_type, path in downloaded.items():
                            print(f"    • {file_type}: {path}")

                        # 提供后续分析建议
                        self._show_analysis_guide(downloaded, parsed.get('keywords', []))
                    else:
                        print("\n⚠ 自动下载失败")
                        self._show_manual_download_guide(experiment_id, ftp_result)
                else:
                    print("\n跳过下载")
                    self._show_manual_download_guide(experiment_id, ftp_result)

            elif found_expr_files:
                print("\n找到了表达数据文件，但无法自动确定最佳选择")
                self._show_manual_download_guide(experiment_id, ftp_result)
            else:
                print("\n未找到标准的基因表达数据文件")
                self._show_manual_download_guide(experiment_id, ftp_result)

        else:
            print(f"  ✗ 无法自动浏览FTP: {ftp_result.get('message')}")
            self._show_manual_download_guide(experiment_id, ftp_result)

    def _show_manual_download_guide(self, experiment_id: str, ftp_result: dict):
        """显示手动下载指南"""
        print("\n" + "=" * 80)
        print("📖 手动下载指南")
        print("=" * 80)
        print(f"\n1. 访问实验页面:")
        print(f"   {ftp_result.get('experiment_page', f'https://www.ebi.ac.uk/gxa/experiments/{experiment_id}')}")
        print(f"\n2. 点击 'Downloads' 标签")
        print(f"\n3. 下载你需要的文件:")
        print(f"   • TPM (Transcripts Per Million) - 推荐")
        print(f"   • FPKM (Fragments Per Kilobase Million)")
        print(f"   • Raw counts")

    def _show_analysis_guide(self, downloaded_files: dict, keywords: List[str]):
        """显示数据分析指南"""
        print("\n" + "=" * 80)
        print("📊 下一步：数据分析")
        print("=" * 80)

        # 找到主要的表达数据文件
        expr_file = None
        for file_type in ['tpms', 'fpkms', 'counts', 'analytics']:
            if file_type in downloaded_files:
                expr_file = downloaded_files[file_type]
                break

        if expr_file:
            print(f"\n```python")
            print(f"from expression_atlas import ExpressionAtlasAPI")
            print(f"import pandas as pd")
            print(f"")
            print(f"# 加载数据")
            print(f"api = ExpressionAtlasAPI()")
            print(f"df = api.load_expression_data('{expr_file}')")
            print(f"")
            print(f"# 查看数据")
            print(f"print(df.head())")
            print(f"print(f'数据维度: {{df.shape}}')")

            if keywords:
                print(f"")
                print(f"# 筛选 {keywords[0]} 相关数据")
                print(f"keyword_cols = [col for col in df.columns if '{keywords[0]}' in col.lower()]")
                print(f"if keyword_cols:")
                print(f"    keyword_data = df[keyword_cols]")
                print(f"    print(keyword_data.head())")

            print(f"```")

    def start(self):
        """启动智能对话"""
        print("=" * 80)
        print("🤖 Expression Atlas 智能助手")
        print("=" * 80)
        print("\n直接告诉我你需要什么数据，我会帮你找到并下载！")
        print("\n示例:")
        print("  • 我需要拟南芥seedling的数据")
        print("  • 我想要人类大脑的基因表达数据")
        print("  • 帮我下载实验 E-MTAB-513 的数据")
        print("  • 小鼠肝脏表达数据")
        print("\n输入 'quit' 或 'exit' 退出\n")

        while True:
            try:
                user_input = input("💬 你: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', '退出', 'bye']:
                    print("\n再见! 👋")
                    break

                self.process_query(user_input)

                print("\n" + "=" * 80)

            except KeyboardInterrupt:
                print("\n\n再见! 👋")
                break
            except Exception as e:
                print(f"\n❌ 出错了: {e}")
                print("请重试或换一种表达方式")


def main():
    """主函数"""
    chat = SmartChat()
    chat.start()


if __name__ == "__main__":
    main()
