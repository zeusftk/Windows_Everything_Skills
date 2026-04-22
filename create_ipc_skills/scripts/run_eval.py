#!/usr/bin/env python3
"""
IPC Skill Evaluator - 运行 IPC Skills 的评估测试

用法:
    python run_eval.py --skill-path <skill_directory> --evals <evals.json>

示例:
    python run_eval.py --skill-path ./skills/ipc-desktop --evals ./evals/evals.json
    python run_eval.py --skill-path ./skills/ipc-web --evals ./evals/evals.json --host 192.168.1.100
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

try:
    from ipc_client import IPCClient
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from ipc_client import IPCClient

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}")


def load_evals(evals_path: Path) -> Dict[str, Any]:
    """加载评估集"""
    if not evals_path.exists():
        raise FileNotFoundError(f"评估集文件不存在: {evals_path}")

    with open(evals_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_single_eval(eval_item: Dict[str, Any], client: IPCClient, skill_name: str) -> Dict[str, Any]:
    """运行单个评估项"""
    start_time = time.time()
    result = {
        "eval_id": eval_item.get("id"),
        "prompt": eval_item.get("prompt"),
        "expected_output": eval_item.get("expected_output"),
        "success": False,
        "error": None,
        "duration_ms": 0,
        "api_calls": [],
    }

    try:
        expectations = eval_item.get("expectations", [])

        api_action = eval_item.get("api_action")
        api_module = eval_item.get("api_module", skill_name.replace("ipc-", ""))
        api_params = eval_item.get("api_params", {})

        if api_action:
            logger.info(f"调用 API: {api_action} (模块: {api_module})")
            response = client.send(api_action, api_params)
            result["api_calls"].append({
                "action": api_action,
                "params": api_params,
                "response": response,
            })

            api_result = response.get("payload", {}).get("result", {})
            success = api_result.get("success", False)

            if not success:
                result["error"] = api_result.get("error", "API 调用失败")
            else:
                result["success"] = True
                result["actual_output"] = api_result
        else:
            logger.warning(f"评估项 {eval_item.get('id')} 未指定 api_action")
            result["error"] = "未指定 api_action"

        result["duration_ms"] = int((time.time() - start_time) * 1000)

        for expectation in expectations:
            logger.debug(f"验证期望: {expectation}")

    except Exception as e:
        result["error"] = str(e)
        result["duration_ms"] = int((time.time() - start_time) * 1000)

    return result


def run_evals(skill_path: Path, evals: List[Dict[str, Any]], host: str, port: int) -> List[Dict[str, Any]]:
    """运行所有评估项"""
    results = []

    logger.info(f"开始评估 skill: {skill_path.name}")
    logger.info(f"共 {len(evals)} 个评估项")

    try:
        with IPCClient(host=host, port=port) as client:
            logger.info("已连接到 IPC 服务")

            for eval_item in evals:
                logger.info(f"运行评估项 #{eval_item.get('id')}: {eval_item.get('prompt', '')[:50]}...")
                result = run_single_eval(eval_item, client, skill_path.name)
                results.append(result)

                status = "通过" if result["success"] else "失败"
                logger.info(f"  状态: {status} (耗时: {result['duration_ms']}ms)")
                if result["error"]:
                    logger.warning(f"  错误: {result['error']}")

    except Exception as e:
        logger.error(f"评估过程出错: {e}")
        for eval_item in evals:
            if not any(r["eval_id"] == eval_item.get("id") for r in results):
                results.append({
                    "eval_id": eval_item.get("id"),
                    "prompt": eval_item.get("prompt"),
                    "success": False,
                    "error": str(e),
                    "duration_ms": 0,
                    "api_calls": [],
                })

    return results


def generate_report(results: List[Dict[str, Any]], skill_name: str) -> Dict[str, Any]:
    """生成评估报告"""
    total = len(results)
    passed = sum(1 for r in results if r["success"])
    failed = total - passed
    pass_rate = passed / total if total > 0 else 0.0
    total_duration = sum(r["duration_ms"] for r in results)

    report = {
        "skill_name": skill_name,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "total_duration_ms": total_duration,
            "avg_duration_ms": total_duration // total if total > 0 else 0,
        },
        "results": results,
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="IPC Skill Evaluator - 运行评估测试")
    parser.add_argument("--skill-path", type=Path, required=True, help="Skill 目录路径")
    parser.add_argument("--evals", type=Path, required=True, help="评估集 JSON 文件路径")
    parser.add_argument("--host", default="127.0.0.1", help="IPC 服务主机")
    parser.add_argument("--port", type=int, default=9527, help="IPC 服务端口")
    parser.add_argument("--output", type=Path, help="输出报告路径")
    parser.add_argument("--verbose", action="store_true", help="详细日志")
    args = parser.parse_args()

    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}")

    skill_path = args.skill_path.resolve()
    if not skill_path.exists():
        logger.error(f"Skill 目录不存在: {skill_path}")
        sys.exit(1)

    try:
        eval_data = load_evals(args.evals)
    except Exception as e:
        logger.error(f"加载评估集失败: {e}")
        sys.exit(1)

    evals = eval_data.get("evals", eval_data) if isinstance(eval_data, dict) else eval_data

    if not evals:
        logger.error("评估集为空")
        sys.exit(1)

    results = run_evals(skill_path, evals, args.host, args.port)
    report = generate_report(results, skill_path.name)

    if args.output:
        output_path = args.output
    else:
        output_dir = skill_path / "evals"
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"report_{timestamp}.json"

    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = report["summary"]
    logger.info("=" * 60)
    logger.info("评估报告")
    logger.info("=" * 60)
    logger.info(f"Skill: {skill_path.name}")
    logger.info(f"总数: {summary['total']}")
    logger.info(f"通过: {summary['passed']}")
    logger.info(f"失败: {summary['failed']}")
    logger.info(f"通过率: {summary['pass_rate']:.2%}")
    logger.info(f"总耗时: {summary['total_duration_ms']}ms")
    logger.info(f"平均耗时: {summary['avg_duration_ms']}ms")
    logger.info(f"报告已保存到: {output_path}")
    logger.info("=" * 60)

    return 0 if summary["pass_rate"] >= 0.8 else 1


if __name__ == "__main__":
    sys.exit(main())
