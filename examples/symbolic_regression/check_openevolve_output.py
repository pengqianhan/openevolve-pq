#!/usr/bin/env python3
"""
统计 problems 文件夹下哪些数据集有 openevolve_output
"""

import os
from pathlib import Path
from collections import defaultdict


def check_openevolve_outputs(problems_dir="problems"):
    """
    检查 problems 目录下所有数据集的 openevolve_output 情况

    Args:
        problems_dir: problems 文件夹路径

    Returns:
        dict: 包含统计信息的字典
    """
    problems_path = Path(problems_dir)

    if not problems_path.exists():
        print(f"错误: {problems_dir} 文件夹不存在")
        return None

    results = {
        'datasets': {}  # 每个数据集的详细信息
    }

    # 遍历 problems 下的所有数据集
    for dataset_dir in sorted(problems_path.iterdir()):
        if not dataset_dir.is_dir():
            continue

        dataset_name = dataset_dir.name

        # 统计该数据集下的子问题
        sub_problems = []
        sub_problems_with_output = []
        sub_problems_without_output = []

        # 遍历数据集下的所有子目录
        for sub_dir in sorted(dataset_dir.iterdir()):
            if not sub_dir.is_dir():
                continue

            sub_problem_name = sub_dir.name
            sub_problems.append(sub_problem_name)

            # 检查是否有 openevolve_output
            output_dir = sub_dir / "openevolve_output"
            if output_dir.exists() and output_dir.is_dir():
                sub_problems_with_output.append(sub_problem_name)
            else:
                sub_problems_without_output.append(sub_problem_name)

        # 保存数据集统计信息
        results['datasets'][dataset_name] = {
            'total_problems': len(sub_problems),
            'with_output': len(sub_problems_with_output),
            'without_output': len(sub_problems_without_output),
            'coverage_rate': len(sub_problems_with_output) / len(sub_problems) * 100 if sub_problems else 0,
            'problems_with_output': sub_problems_with_output,
            'problems_without_output': sub_problems_without_output
        }

    return results


def print_summary(results):
    """打印统计摘要"""
    if results is None:
        return

    print("=" * 80)
    print("OpenEvolve Output 统计结果")
    print("=" * 80)

    total_datasets = len(results['datasets'])
    total_problems = sum(d['total_problems'] for d in results['datasets'].values())
    total_with_output = sum(d['with_output'] for d in results['datasets'].values())
    total_without_output = sum(d['without_output'] for d in results['datasets'].values())

    print(f"\n【总体统计】")
    print(f"  数据集数量: {total_datasets}")
    print(f"  问题总数: {total_problems}")
    print(f"  有 openevolve_output 的问题: {total_with_output} ({total_with_output/total_problems*100:.1f}%)")
    print(f"  没有 openevolve_output 的问题: {total_without_output} ({total_without_output/total_problems*100:.1f}%)")

    print("\n" + "=" * 80)
    print("【各数据集详细统计】")
    print("=" * 80)

    for dataset_name, data in sorted(results['datasets'].items()):
        print(f"\n📊 {dataset_name}")
        print(f"  ├─ 问题总数: {data['total_problems']}")
        print(f"  ├─ 有 openevolve_output: {data['with_output']} ({data['coverage_rate']:.1f}%)")
        print(f"  └─ 没有 openevolve_output: {data['without_output']}")

        if data['without_output'] > 0:
            print(f"\n     缺失 openevolve_output 的问题:")
            for problem in data['problems_without_output']:
                print(f"       ✗ {problem}")

    print("\n" + "=" * 80)


def print_detailed_report(results):
    """打印详细报告"""
    if results is None:
        return

    print("\n" + "=" * 80)
    print("【详细报告 - 按数据集列出所有问题】")
    print("=" * 80)

    for dataset_name, data in sorted(results['datasets'].items()):
        print(f"\n{'='*80}")
        print(f"数据集: {dataset_name}")
        print(f"{'='*80}")

        if data['with_output'] > 0:
            print(f"\n✓ 有 openevolve_output 的问题 ({data['with_output']} 个):")
            for i, problem in enumerate(data['problems_with_output'], 1):
                print(f"  {i:3d}. {problem}")

        if data['without_output'] > 0:
            print(f"\n✗ 没有 openevolve_output 的问题 ({data['without_output']} 个):")
            for i, problem in enumerate(data['problems_without_output'], 1):
                print(f"  {i:3d}. {problem}")


def export_to_csv(results, output_file="openevolve_output_summary.csv"):
    """导出结果到 CSV 文件"""
    if results is None:
        return

    import csv

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['数据集', '问题名称', '有openevolve_output'])

        for dataset_name, data in sorted(results['datasets'].items()):
            for problem in data['problems_with_output']:
                writer.writerow([dataset_name, problem, 'Yes'])
            for problem in data['problems_without_output']:
                writer.writerow([dataset_name, problem, 'No'])

    print(f"\n✓ 详细结果已导出到: {output_file}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='统计 problems 文件夹下的 openevolve_output')
    parser.add_argument('--detailed', '-d', action='store_true',
                        help='显示详细报告（列出所有问题）')
    parser.add_argument('--export-csv', '-e', action='store_true',
                        help='导出结果到 CSV 文件')

    args = parser.parse_args()

    # 检查并统计
    results = check_openevolve_outputs("problems")

    # 打印摘要
    print_summary(results)

    # 打印详细报告（如果需要）
    if args.detailed:
        print_detailed_report(results)

    # 导出到 CSV（如果需要）
    if args.export_csv:
        export_to_csv(results)

    return results


if __name__ == "__main__":
    main()
