#!/usr/bin/env python3
"""
Test script for MCP server tools without requiring MCP client.

This script directly calls the functions used by the MCP server,
allowing you to test functionality without setting up Claude Desktop.
"""

import json
from expression_atlas import ExpressionAtlasAPI
from mcp_server import browse_ftp_directory, identify_expression_files, SPECIES_MAP


def test_search_experiments():
    """Test searching for experiments."""
    print("=" * 70)
    print("测试1: 搜索拟南芥 (Arabidopsis) 实验")
    print("=" * 70)

    api = ExpressionAtlasAPI()

    # 映射物种名称
    species = SPECIES_MAP.get('arabidopsis', 'arabidopsis')
    print(f"\n物种: {species}")

    # 获取热门实验
    popular = api.get_popular_experiments('baseline')
    print(f"\n热门实验:")
    for exp_id in popular:
        print(f"  - {exp_id}")

    # 对于拟南芥，E-MTAB-3358 是一个很好的例子
    arabidopsis_exp = "E-MTAB-3358"
    print(f"\n推荐的拟南芥实验: {arabidopsis_exp}")

    return arabidopsis_exp


def test_get_experiment_info(experiment_id):
    """Test getting experiment information."""
    print("\n" + "=" * 70)
    print(f"测试2: 获取实验 {experiment_id} 的信息")
    print("=" * 70)

    api = ExpressionAtlasAPI()
    info = api.get_experiment_info(experiment_id)

    print(f"\n实验详情:")
    print(json.dumps(info, indent=2, ensure_ascii=False))

    return info


def test_browse_ftp(experiment_id):
    """Test browsing FTP directory."""
    print("\n" + "=" * 70)
    print(f"测试3: 浏览实验 {experiment_id} 的FTP目录")
    print("=" * 70)

    result = browse_ftp_directory(experiment_id)

    print(f"\nFTP 浏览结果:")
    if result.get('success'):
        print(f"  FTP URL: {result.get('ftp_url')}")
        print(f"  方法: {result.get('method')}")
        print(f"\n  找到 {len(result.get('files', []))} 个文件:")

        files = result.get('files', [])
        for file_item in files[:10]:  # 只显示前10个
            if isinstance(file_item, dict):
                print(f"    - {file_item.get('name')} ({file_item.get('size', 'unknown')} bytes)")
            else:
                print(f"    - {file_item}")
    else:
        print(f"  失败: {result.get('message')}")
        print(f"  实验页面: {result.get('experiment_page')}")

    return result


def test_identify_files(ftp_result):
    """Test identifying expression files."""
    print("\n" + "=" * 70)
    print("测试4: 智能识别基因表达数据文件")
    print("=" * 70)

    files = ftp_result.get('files', [])
    if not files:
        print("\n没有文件可供分析")
        return None

    result = identify_expression_files(files)

    print(f"\n文件分类结果:")
    categorized = result.get('categorized_files', {})

    for category, file_list in categorized.items():
        if file_list:
            print(f"\n  {category.upper()}:")
            for f in file_list:
                if isinstance(f, dict):
                    print(f"    - {f.get('name')}")
                else:
                    print(f"    - {f}")

    recommended = result.get('recommended_file')
    if recommended:
        print(f"\n  ✅ 推荐下载:")
        if isinstance(recommended, dict):
            print(f"    文件: {recommended.get('name')}")
            print(f"    URL: {recommended.get('url')}")
        else:
            print(f"    文件: {recommended}")
        print(f"    类型: {result.get('recommended_type')}")

    summary = result.get('summary', {})
    print(f"\n  统计:")
    print(f"    总文件数: {summary.get('total_files')}")
    print(f"    表达数据文件: {summary.get('expression_files')}")
    print(f"    元数据文件: {summary.get('metadata_files')}")

    return result


def test_download_data(experiment_id, output_dir='./test_data'):
    """Test downloading expression data."""
    print("\n" + "=" * 70)
    print(f"测试5: 下载实验 {experiment_id} 的数据")
    print("=" * 70)

    print(f"\n目标目录: {output_dir}")
    print("开始下载...")

    api = ExpressionAtlasAPI()
    downloaded = api.download_experiment_data(
        experiment_id=experiment_id,
        output_dir=output_dir
    )

    if downloaded:
        print(f"\n✅ 下载成功! 共 {len(downloaded)} 个文件:")
        for file_type, path in downloaded.items():
            print(f"  - {file_type}: {path}")
    else:
        print("\n⚠ 未能自动下载文件")
        print(f"请手动访问: https://www.ebi.ac.uk/gxa/experiments/{experiment_id}")

    return downloaded


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("Expression Atlas MCP Server 功能测试")
    print("=" * 80)
    print("\n这个脚本演示了 MCP server 的所有功能，无需配置 Claude Desktop\n")

    # 测试1: 搜索实验
    experiment_id = test_search_experiments()

    # 测试2: 获取实验信息
    test_get_experiment_info(experiment_id)

    # 测试3: 浏览FTP目录
    ftp_result = test_browse_ftp(experiment_id)

    # 测试4: 识别表达文件
    if ftp_result.get('success'):
        test_identify_files(ftp_result)

    # 测试5: 询问是否下载
    print("\n" + "=" * 70)
    response = input(f"\n是否要下载实验 {experiment_id} 的数据? (yes/no): ").strip().lower()
    if response in ['yes', 'y', 'YES', 'YES']:
        test_download_data(experiment_id)
    else:
        print("\n跳过下载")

    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)
    print("\n要使用 MCP server 的完整功能,请:")
    print("1. 配置 Claude Desktop (参见 MCP_SETUP.md)")
    print("2. 或者使用交互式CLI: python chat_interface.py")


if __name__ == "__main__":
    main()
