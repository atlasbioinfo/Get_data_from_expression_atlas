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
from vector_search import ExperimentVectorSearch


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
        'baseline': 'E-CURD-1',  # Arabidopsis tissues (whole organism, floral bud, rosette)
    },
}


class SmartChatParser:
    """智能解析用户输入，提取意图和参数"""

    def __init__(self):
        self.api = ExpressionAtlasAPI()
        # Initialize vector search (lazy loading)
        self.vector_search = None
        self._init_vector_search()

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

    def _init_vector_search(self):
        """Initialize vector search system."""
        try:
            self.vector_search = ExperimentVectorSearch()
            print("🔍 Initializing experiment database...")
            self.vector_search.build_index()
            print(f"✅ Loaded {len(self.vector_search.experiments)} experiments")
        except Exception as e:
            print(f"⚠ Vector search initialization failed: {e}")
            print("  Using fallback recommendation system")
            self.vector_search = None

    def recommend_experiment(self, parsed: Dict) -> Optional[str]:
        """根据解析结果推荐实验ID（使用vector search）"""
        species = parsed.get('species')
        keywords = parsed.get('keywords', [])
        exp_type = parsed.get('experiment_type', 'baseline')

        # Try vector search first
        if self.vector_search:
            try:
                results = self.vector_search.search_by_keywords(
                    species=species,
                    keywords=keywords,
                    experiment_type=exp_type,
                    top_k=1
                )
                if results:
                    return results[0]['accession']
            except Exception as e:
                print(f"⚠ Vector search failed: {e}")

        # Fallback to hardcoded experiments
        if species and species in KNOWN_EXPERIMENTS:
            if exp_type in KNOWN_EXPERIMENTS[species]:
                return KNOWN_EXPERIMENTS[species][exp_type]

        # 如果没有直接匹配，返回该类型的热门实验
        popular = self.api.get_popular_experiments(exp_type)
        if popular:
            return popular[0]

        return None

    def get_top_experiments(self, parsed: Dict, top_k: int = 3) -> List[Dict]:
        """获取top-k个最佳匹配的实验"""
        species = parsed.get('species')
        keywords = parsed.get('keywords', [])
        exp_type = parsed.get('experiment_type', 'baseline')

        if self.vector_search:
            try:
                results = self.vector_search.search_by_keywords(
                    species=species,
                    keywords=keywords,
                    experiment_type=exp_type,
                    top_k=top_k
                )
                return results
            except Exception as e:
                print(f"⚠ Vector search failed: {e}")

        return []


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
        print(f"💬 Your request: {user_input}")
        print("=" * 80)

        # 解析输入
        parsed = self.parser.parse_user_input(user_input)

        print("\n🔍 Understanding your needs:")
        if parsed['species']:
            print(f"  • Species: {parsed['species']}")
        if parsed['keywords']:
            print(f"  • Keywords: {', '.join(parsed['keywords'])}")
        if parsed['experiment_type']:
            print(f"  • Experiment type: {parsed['experiment_type']}")
        if parsed['experiment_id']:
            print(f"  • Experiment ID: {parsed['experiment_id']}")

        # 确定实验ID
        experiment_id = parsed.get('experiment_id')
        if not experiment_id:
            # 获取top-3匹配的实验
            top_experiments = self.parser.get_top_experiments(parsed, top_k=3)

            if top_experiments:
                print(f"\n🎯 Found {len(top_experiments)} matching experiments:")
                print("=" * 80)
                for exp in top_experiments:
                    print(f"\n  {exp['rank']}. {exp['accession']} (similarity: {exp['similarity_score']:.2%})")
                    print(f"     Species: {exp['species']}")
                    desc = exp['description'][:100]
                    if len(exp['description']) > 100:
                        desc += "..."
                    print(f"     Description: {desc}")

                print("\n" + "=" * 80)

                # 默认使用第一个（最佳匹配）
                experiment_id = top_experiments[0]['accession']
                print(f"\n✨ Auto-selected best match: {experiment_id}")
                print(f"   (For other experiments, please re-run with specific experiment ID)")
            else:
                # Fallback to single recommendation
                experiment_id = self.parser.recommend_experiment(parsed)
                if experiment_id:
                    print(f"\n✨ Recommended experiment: {experiment_id}")

        if not experiment_id:
            print("\n❌ Sorry, couldn't find a suitable experiment")
            print("Please provide more information or visit: https://www.ebi.ac.uk/gxa/experiments")
            return

        # 获取实验信息
        print(f"\n📊 Experiment details:")
        print(f"  Experiment ID: {experiment_id}")
        print(f"  Experiment page: https://www.ebi.ac.uk/gxa/experiments/{experiment_id}")

        # 浏览FTP目录
        print(f"\n🔎 Browsing FTP directory...")
        ftp_result = self.browse_ftp_directory(experiment_id)

        if ftp_result.get('success'):
            files = ftp_result.get('files', [])
            print(f"  ✓ Found {len(files)} files")
            print(f"  FTP URL: {ftp_result['ftp_url']}")

            # 识别表达数据文件
            print(f"\n🧠 Intelligently identifying gene expression data files...")
            identified = self.identify_expression_files(files)

            categorized = identified.get('categorized', {})

            # 显示找到的表达数据文件
            found_expr_files = False
            for category in ['tpms', 'fpkms', 'counts']:
                file_list = categorized.get(category, [])
                if file_list:
                    found_expr_files = True
                    print(f"\n  {category.upper()} files:")
                    for f in file_list:
                        if isinstance(f, dict):
                            print(f"    • {f.get('name')} ({f.get('size')} bytes)")
                        else:
                            print(f"    • {f}")

            # 推荐下载
            recommended = identified.get('recommended')
            if recommended:
                print("\n" + "=" * 80)
                print("🎯 Recommended download:")
                print("=" * 80)

                if isinstance(recommended, dict):
                    rec_name = recommended.get('name')
                    rec_url = recommended.get('url')
                    rec_size = recommended.get('size')
                    print(f"  File: {rec_name}")
                    print(f"  Size: {rec_size} bytes")
                    print(f"  URL: {rec_url}")
                else:
                    print(f"  File: {recommended}")
                    print(f"  URL: {ftp_result['ftp_url']}{recommended}")

                # 询问是否下载
                print("\n" + "=" * 80)
                response = input("Download this file? (yes/no): ").strip().lower()

                if response in ['yes', 'y', 'YES']:
                    print("\n📥 Starting download...")
                    output_dir = './expression_atlas_data'

                    downloaded = self.api.download_experiment_data(
                        experiment_id=experiment_id,
                        output_dir=output_dir
                    )

                    if downloaded:
                        print(f"\n✅ Download successful!")
                        print(f"  Saved to: {output_dir}")
                        for file_type, path in downloaded.items():
                            print(f"    • {file_type}: {path}")

                        # 提供后续分析建议
                        self._show_analysis_guide(downloaded, parsed.get('keywords', []))
                    else:
                        print("\n⚠ Automatic download failed")
                        self._show_manual_download_guide(experiment_id, ftp_result)
                else:
                    print("\nSkipping download")
                    self._show_manual_download_guide(experiment_id, ftp_result)

            elif found_expr_files:
                print("\nFound expression data files, but cannot automatically determine the best choice")
                self._show_manual_download_guide(experiment_id, ftp_result)
            else:
                print("\nNo standard gene expression data files found")
                self._show_manual_download_guide(experiment_id, ftp_result)

        else:
            print(f"  ✗ Cannot automatically browse FTP: {ftp_result.get('message')}")
            self._show_manual_download_guide(experiment_id, ftp_result)

    def _show_manual_download_guide(self, experiment_id: str, ftp_result: dict):
        """显示手动下载指南"""
        print("\n" + "=" * 80)
        print("📖 Manual Download Guide")
        print("=" * 80)
        print(f"\n1. Visit the experiment page:")
        print(f"   {ftp_result.get('experiment_page', f'https://www.ebi.ac.uk/gxa/experiments/{experiment_id}')}")
        print(f"\n2. Click the 'Downloads' tab")
        print(f"\n3. Download the files you need:")
        print(f"   • TPM (Transcripts Per Million) - recommended")
        print(f"   • FPKM (Fragments Per Kilobase Million)")
        print(f"   • Raw counts")

    def _show_analysis_guide(self, downloaded_files: dict, keywords: List[str]):
        """显示数据分析指南"""
        print("\n" + "=" * 80)
        print("📊 Next step: Data Analysis")
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
            print(f"# Load data")
            print(f"api = ExpressionAtlasAPI()")
            print(f"df = api.load_expression_data('{expr_file}')")
            print(f"")
            print(f"# View data")
            print(f"print(df.head())")
            print(f"print(f'Data shape: {{df.shape}}')")

            if keywords:
                print(f"")
                print(f"# Filter {keywords[0]} related data")
                print(f"keyword_cols = [col for col in df.columns if '{keywords[0]}' in col.lower()]")
                print(f"if keyword_cols:")
                print(f"    keyword_data = df[keyword_cols]")
                print(f"    print(keyword_data.head())")

            print(f"```")

    def start(self):
        """启动智能对话"""
        print("=" * 80)
        print("🤖 Expression Atlas Smart Assistant")
        print("=" * 80)
        print("\nTell me what data you need, and I'll help you find and download it!")
        print("\nExamples:")
        print("  • I need Arabidopsis seedling data")
        print("  • I want human brain gene expression data")
        print("  • Help me download experiment E-MTAB-513")
        print("  • Mouse liver expression data")
        print("\nType 'quit' or 'exit' to exit\n")

        while True:
            try:
                user_input = input("💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nGoodbye! 👋")
                    break

                self.process_query(user_input)

                print("\n" + "=" * 80)

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error occurred: {e}")
                print("Please try again or rephrase your request")


def main():
    """主函数"""
    chat = SmartChat()
    chat.start()


if __name__ == "__main__":
    main()
