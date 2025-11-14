#!/usr/bin/env python3
"""
快速测试：查找拟南芥 (Arabidopsis) seedling 基因表达数据

这个脚本演示如何使用工具找到并下载拟南芥幼苗的表达数据
"""

import json
import re
import requests
from expression_atlas import ExpressionAtlasAPI

# Species mapping (copied from mcp_server.py)
SPECIES_MAP = {
    'human': 'homo sapiens',
    'mouse': 'mus musculus',
    'rat': 'rattus norvegicus',
    'arabidopsis': 'arabidopsis thaliana',
    'zebrafish': 'danio rerio',
    'fruit fly': 'drosophila melanogaster',
    'drosophila': 'drosophila melanogaster',
    'yeast': 'saccharomyces cerevisiae',
    'c. elegans': 'caenorhabditis elegans',
}


def browse_ftp_directory(experiment_id: str) -> dict:
    """Browse FTP directory for experiment files."""
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
    except Exception as e:
        pass

    # Try common patterns
    common_patterns = [
        f"{experiment_id}-tpms.tsv",
        f"{experiment_id}-fpkms.tsv",
        f"{experiment_id}-raw-counts.tsv",
        f"{experiment_id}.condensed-sdrf.tsv",
        f"{experiment_id}.sdrf.txt",
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
        'message': 'Could not automatically list files.',
        'experiment_page': f"https://www.ebi.ac.uk/gxa/experiments/{experiment_id}"
    }


def identify_expression_files(files_list: list) -> dict:
    """Identify gene expression data files."""
    expression_files = {
        'tpms': [],
        'fpkms': [],
        'counts': [],
        'analytics': [],
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
        elif 'analytics' in filename_lower:
            expression_files['analytics'].append(file_item)
        elif 'sdrf' in filename_lower or 'metadata' in filename_lower:
            expression_files['metadata'].append(file_item)
        else:
            expression_files['other'].append(file_item)

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
        'categorized_files': expression_files,
        'recommended_file': recommended,
        'recommended_type': recommended_type,
        'summary': {
            'total_files': len(files_list),
            'expression_files': len(expression_files['tpms']) + len(expression_files['fpkms']) + len(expression_files['counts']),
            'metadata_files': len(expression_files['metadata'])
        }
    }


def main():
    print("=" * 80)
    print("🌱 查找拟南芥 (Arabidopsis) Seedling 基因表达数据")
    print("=" * 80)

    # 初始化API
    api = ExpressionAtlasAPI()

    # 步骤1: 映射物种名称
    print("\n步骤 1: 物种识别")
    print("-" * 80)
    species_input = "arabidopsis"
    species = SPECIES_MAP.get(species_input.lower(), species_input)
    print(f"输入: {species_input}")
    print(f"标准名称: {species}")

    # 步骤2: 推荐实验
    print("\n步骤 2: 推荐的拟南芥实验")
    print("-" * 80)

    # E-MTAB-3358 是拟南芥组织的经典数据集
    recommended_exp = "E-MTAB-3358"
    print(f"✅ 推荐实验: {recommended_exp}")
    print(f"描述: Arabidopsis thaliana baseline expression in various tissues")
    print(f"实验页面: https://www.ebi.ac.uk/gxa/experiments/{recommended_exp}")

    # 步骤3: 获取实验详情
    print("\n步骤 3: 获取实验信息")
    print("-" * 80)
    info = api.get_experiment_info(recommended_exp)

    if 'error' in info:
        print(f"⚠ API无法获取详细信息: {info.get('error')}")
        print(f"但你仍然可以访问实验页面下载数据")
    else:
        print(f"实验类型: {info.get('type', 'Unknown')}")
        print(f"物种: {info.get('species', 'Unknown')}")

    # 步骤4: 浏览FTP目录
    print("\n步骤 4: 浏览FTP目录查看可用文件")
    print("-" * 80)
    ftp_result = browse_ftp_directory(recommended_exp)

    if ftp_result.get('success'):
        print(f"✅ 成功访问FTP")
        print(f"FTP URL: {ftp_result['ftp_url']}")
        print(f"发现方法: {ftp_result['method']}\n")

        files = ftp_result.get('files', [])
        print(f"找到 {len(files)} 个文件:")
        for i, file_item in enumerate(files[:15], 1):  # 显示前15个
            if isinstance(file_item, dict):
                name = file_item.get('name', '')
                size = file_item.get('size', 'unknown')
                print(f"  {i:2d}. {name:50s} ({size} bytes)")
            else:
                print(f"  {i:2d}. {file_item}")

        # 步骤5: 智能识别表达数据文件
        print("\n步骤 5: 智能识别基因表达数据")
        print("-" * 80)
        identification = identify_expression_files(files)

        categorized = identification.get('categorized_files', {})

        # 显示各类文件
        print("\n📊 文件分类:")
        for category in ['tpms', 'fpkms', 'counts', 'analytics']:
            file_list = categorized.get(category, [])
            if file_list:
                print(f"\n  {category.upper()} 文件:")
                for f in file_list:
                    if isinstance(f, dict):
                        print(f"    ✓ {f.get('name')}")
                    else:
                        print(f"    ✓ {f}")

        # 显示推荐文件
        recommended_file = identification.get('recommended_file')
        recommended_type = identification.get('recommended_type')

        if recommended_file:
            print("\n" + "=" * 80)
            print("🎯 推荐下载的文件:")
            print("=" * 80)

            if isinstance(recommended_file, dict):
                print(f"  文件名: {recommended_file.get('name')}")
                print(f"  类型: {recommended_type}")
                print(f"  URL: {recommended_file.get('url')}")
                print(f"  大小: {recommended_file.get('size', 'unknown')} bytes")
            else:
                print(f"  文件名: {recommended_file}")
                print(f"  类型: {recommended_type}")

            # 步骤6: 提供下载方式
            print("\n步骤 6: 下载数据")
            print("-" * 80)
            print("你有两种下载方式:\n")

            print("方式1 - 使用本工具下载:")
            print("```python")
            print("from expression_atlas import ExpressionAtlasAPI")
            print("api = ExpressionAtlasAPI()")
            print(f"files = api.download_experiment_data('{recommended_exp}', output_dir='./arabidopsis_data')")
            print("```\n")

            print("方式2 - 手动下载 (推荐):")
            print(f"1. 访问: https://www.ebi.ac.uk/gxa/experiments/{recommended_exp}")
            print("2. 点击 'Downloads' 标签")
            print("3. 下载 TPM 或 FPKM 文件")

        # 显示seedling相关信息
        print("\n" + "=" * 80)
        print("🌱 关于 Seedling (幼苗) 数据")
        print("=" * 80)
        print("E-MTAB-3358 包含多个拟南芥组织的表达数据，可能包括:")
        print("  - Seedling (幼苗)")
        print("  - Root (根)")
        print("  - Leaf (叶)")
        print("  - Flower (花)")
        print("  - Shoot (芽)")
        print("\n下载数据后，你可以筛选 seedling 相关的列进行分析")

    else:
        print(f"❌ 无法自动浏览FTP: {ftp_result.get('message')}")
        print(f"\n请手动访问实验页面:")
        print(f"  {ftp_result.get('experiment_page')}")

    print("\n" + "=" * 80)
    print("✅ 分析完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
