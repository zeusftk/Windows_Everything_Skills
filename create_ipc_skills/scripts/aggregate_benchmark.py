#!/usr/bin/env python3
"""
IPC Benchmark Aggregator - 聚合多个 IPC Skill 评估报告

用法:
    python aggregate_benchmark.py <reports_directory> --skill-name <name>

示例:
    python aggregate_benchmark.py ./skills/ipc-desktop/evals --skill-name ipc-desktop
    python aggregate_benchmark.py ./evals --skill-name ipc-web --output benchmark.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}")


def load_reports(reports_dir: Path) -> List[Dict[str, Any]]:
    """加载目录下所有评估报告"""
    reports = []

    for report_file in sorted(reports_dir.glob("report_*.json")):
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                report = json.load(f)
                reports.append(report)
                logger.info(f"加载报告: {report_file.name}")
        except Exception as e:
            logger.warning(f"加载报告失败 {report_file.name}: {e}")

    return reports


def aggregate_reports(reports: List[Dict[str, Any]], skill_name: str) -> Dict[str, Any]:
    """聚合多个报告为基准测试结果"""
    if not reports:
        return {
            "skill_name": skill_name,
            "timestamp": datetime.now().isoformat(),
            "total_runs": 0,
            "summary": {},
        }

    pass_rates = [r["summary"]["pass_rate"] for r in reports if "summary" in r]
    total_times = [r["summary"]["total_duration_ms"] for r in reports if "summary" in r]
    total_evals = [r["summary"]["total"] for r in reports if "summary" in r]

    aggregated = {
        "skill_name": skill_name,
        "timestamp": datetime.now().isoformat(),
        "total_runs": len(reports),
        "summary": {
            "pass_rate": {
                "mean": statistics.mean(pass_rates) if pass_rates else 0,
                "stddev": statistics.stdev(pass_rates) if len(pass_rates) > 1 else 0,
                "min": min(pass_rates) if pass_rates else 0,
                "max": max(pass_rates) if pass_rates else 0,
            },
            "total_duration_ms": {
                "mean": statistics.mean(total_times) if total_times else 0,
                "stddev": statistics.stdev(total_times) if len(total_times) > 1 else 0,
            },
            "total_evals": {
                "mean": statistics.mean(total_evals) if total_evals else 0,
            },
        },
        "runs": [
            {
                "run_number": i + 1,
                "timestamp": r.get("timestamp"),
                "pass_rate": r["summary"]["pass_rate"],
                "passed": r["summary"]["passed"],
                "failed": r["summary"]["failed"],
                "total": r["summary"]["total"],
                "duration_ms": r["summary"]["total_duration_ms"],
            }
            for i, r in enumerate(reports)
            if "summary" in r
        ],
    }

    return aggregated


def main():
    parser = argparse.ArgumentParser(description="IPC Benchmark Aggregator - 聚合评估报告")
    parser.add_argument("reports_dir", type=Path, help="评估报告目录")
    parser.add_argument("--skill-name", required=True, help="Skill 名称")
    parser.add_argument("--output", type=Path, help="输出基准测试结果路径")
    parser.add_argument("--verbose", action="store_true", help="详细日志")
    args = parser.parse_args()

    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}")

    reports_dir = args.reports_dir.resolve()
    if not reports_dir.exists():
        logger.error(f"目录不存在: {reports_dir}")
        sys.exit(1)

    reports = load_reports(reports_dir)

    if not reports:
        logger.error("未找到评估报告")
        sys.exit(1)

    logger.info(f"聚合 {len(reports)} 个报告...")
    aggregated = aggregate_reports(reports, args.skill_name)

    if args.output:
        output_path = args.output
    else:
        output_path = reports_dir / "benchmark.json"

    output_path.write_text(
        json.dumps(aggregated, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logger.info("=" * 60)
    logger.info("基准测试结果")
    logger.info("=" * 60)
    logger.info(f"Skill: {args.skill_name}")
    logger.info(f"运行次数: {aggregated['total_runs']}")

    summary = aggregated["summary"]
    logger.info(f"通过率: {summary['pass_rate']['mean']:.2%} (±{summary['pass_rate']['stddev']:.2%})")
    logger.info(f"总耗时: {summary['total_duration_ms']['mean']:.0f}ms (±{summary['total_duration_ms']['stddev']:.0f}ms)")
    logger.info(f"评估项数: {summary['total_evals']['mean']:.0f}")
    logger.info(f"结果已保存到: {output_path}")
    logger.info("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
