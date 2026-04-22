#!/usr/bin/env python3
"""
Trigger Word Evaluator - 评估和优化 IPC Skills 的触发词

用于生成触发词评估集、运行评估并优化触发词配置。

用法:
    python eval_triggers.py <skill_directory> --mode generate|evaluate|optimize

示例:
    python eval_triggers.py ./skills/ipc-desktop --mode generate
    python eval_triggers.py ./skills/ipc-desktop --mode evaluate --eval-set evals/trigger_evals.json
    python eval_triggers.py ./skills/ipc-desktop --mode optimize --eval-set evals/trigger_evals.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}")

try:
    from ipc_skills_creator import TriggerWordExtractor
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from ipc_skills_creator import TriggerWordExtractor


TRIGGER_STOPWORDS_CN = {
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
    '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
    '自己', '这',
}

TRIGGER_STOPWORDS_EN = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used',
    'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'between', 'out',
    'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
    'when', 'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
    'than', 'too', 'very', 'just', 'because', 'but', 'and', 'or', 'if', 'while',
    'about', 'against', 'up', 'down', 'that', 'this', 'these', 'those', 'it', 'its',
}


class TriggerEvalGenerator:
    """生成触发词评估集"""

    @staticmethod
    def extract_api_actions(skill_dir: Path) -> List[Dict[str, Any]]:
        """从 skill 目录提取 API 操作信息"""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return []

        content = skill_md.read_text(encoding="utf-8")
        apis = []

        api_pattern = re.compile(r'### (\w+)\s*\n.*?描述:\s*(.*?)\n', re.DOTALL)
        for match in api_pattern.finditer(content):
            action = match.group(1)
            description = match.group(2).strip()
            apis.append({"action": action, "description": description})

        return apis

    @staticmethod
    def generate_positive_queries(apis: List[Dict[str, Any]], skill_name: str) -> List[Dict[str, Any]]:
        """生成应该触发该 skill 的查询"""
        queries = []

        for api in apis:
            action = api["action"]

            if "click" in action.lower():
                queries.append({
                    "query": f"帮我点击屏幕上的位置，使用 {skill_name}",
                    "should_trigger": True,
                    "category": "mouse_click",
                })
                queries.append({
                    "query": "鼠标左键单击操作",
                    "should_trigger": True,
                    "category": "mouse_click",
                })

            if "screenshot" in action.lower():
                queries.append({
                    "query": "截取当前屏幕",
                    "should_trigger": True,
                    "category": "screenshot",
                })
                queries.append({
                    "query": "截图并保存",
                    "should_trigger": True,
                    "category": "screenshot",
                })

            if "keyboard" in action.lower() or "type" in action.lower():
                queries.append({
                    "query": "模拟键盘输入文字",
                    "should_trigger": True,
                    "category": "keyboard",
                })

            if "window" in action.lower():
                queries.append({
                    "query": "打开新的浏览器窗口",
                    "should_trigger": True,
                    "category": "window",
                })

            if "ocr" in action.lower():
                queries.append({
                    "query": "识别图片中的文字内容",
                    "should_trigger": True,
                    "category": "ocr",
                })
                queries.append({
                    "query": "从截图中提取文本",
                    "should_trigger": True,
                    "category": "ocr",
                })

            if "web" in action.lower() or "browser" in action.lower():
                queries.append({
                    "query": "打开网页并导航到指定 URL",
                    "should_trigger": True,
                    "category": "web",
                })

            if "file" in action.lower() or "read" in action.lower():
                queries.append({
                    "query": "读取本地文件内容",
                    "should_trigger": True,
                    "category": "file",
                })

            if "process" in action.lower() or "system" in action.lower():
                queries.append({
                    "query": "查看当前运行的进程列表",
                    "should_trigger": True,
                    "category": "system",
                })

        if not queries and apis:
            api = apis[0]
            queries.append({
                "query": f"执行 {api['action']} 操作",
                "should_trigger": True,
                "category": "generic",
            })

        return queries[:15]

    @staticmethod
    def generate_negative_queries(skill_name: str) -> List[Dict[str, Any]]:
        """生成不应该触发该 skill 的查询"""
        return [
            {
                "query": "帮我写一段 Python 代码",
                "should_trigger": False,
                "category": "coding",
            },
            {
                "query": "解释一下这个算法的时间复杂度",
                "should_trigger": False,
                "category": "explanation",
            },
            {
                "query": "翻译这段文字为英文",
                "should_trigger": False,
                "category": "translation",
            },
            {
                "query": "总结一下这篇文章的主要内容",
                "should_trigger": False,
                "category": "summarization",
            },
            {
                "query": "帮我分析一下这份数据",
                "should_trigger": False,
                "category": "analysis",
            },
        ]

    @staticmethod
    def generate_eval_set(skill_dir: Path) -> List[Dict[str, Any]]:
        """生成完整的触发词评估集"""
        skill_name = skill_dir.name.replace("ipc-", "")
        apis = TriggerEvalGenerator.extract_api_actions(skill_dir)

        if not apis:
            logger.warning("未能从 skill 文件中提取到 API 信息")
            return []

        positive_queries = TriggerEvalGenerator.generate_positive_queries(apis, skill_name)
        negative_queries = TriggerEvalGenerator.generate_negative_queries(skill_name)

        eval_set = positive_queries + negative_queries

        return eval_set


class TriggerOptimizer:
    """触发词优化器"""

    @staticmethod
    def evaluate_triggers(skill_dir: Path, eval_set: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估当前触发词的效果"""
        skill_md = skill_dir / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")

        trigger_section = re.search(r'## 触发词\s*\n- 中文:\s*(.*?)\n- 英文:\s*(.*?)\n', content)
        if not trigger_section:
            return {
                "accuracy": 0.0,
                "total": len(eval_set),
                "correct": 0,
                "false_positives": 0,
                "false_negatives": 0,
            }

        cn_triggers = set(trigger_section.group(1).split(", "))
        en_triggers = set(trigger_section.group(2).split(", "))

        correct = 0
        false_positives = 0
        false_negatives = 0

        for eval_item in eval_set:
            query = eval_item["query"].lower()
            should_trigger = eval_item["should_trigger"]

            query_has_trigger = any(
                trigger.lower() in query for trigger in cn_triggers | en_triggers
            )

            if query_has_trigger == should_trigger:
                correct += 1
            elif should_trigger and not query_has_trigger:
                false_negatives += 1
            else:
                false_positives += 1

        total = len(eval_set)
        accuracy = correct / total if total > 0 else 0.0

        return {
            "accuracy": accuracy,
            "total": total,
            "correct": correct,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
        }

    @staticmethod
    def optimize_from_evals(skill_dir: Path, eval_set: List[Dict[str, Any]], max_iterations: int = 5) -> Dict[str, Any]:
        """基于评估集优化触发词"""
        skill_md = skill_dir / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")

        apis = TriggerEvalGenerator.extract_api_actions(skill_dir)
        all_triggers_cn = set()
        all_triggers_en = set()

        for api in apis:
            action_triggers = TriggerWordExtractor.extract_from_api_action(api["action"])
            desc_triggers = TriggerWordExtractor.extract_from_description(api["description"])
            all_triggers_en.update(action_triggers)
            all_triggers_cn.update(desc_triggers)

        all_triggers_en -= TRIGGER_STOPWORDS_EN
        all_triggers_cn -= TRIGGER_STOPWORDS_CN

        best_triggers_cn = sorted(all_triggers_cn)[:10]
        best_triggers_en = sorted(all_triggers_en)[:10]
        best_accuracy = 0.0

        for iteration in range(max_iterations):
            test_triggers_cn = set(best_triggers_cn)
            test_triggers_en = set(best_triggers_en)

            for trigger in all_triggers_cn:
                test_triggers_cn.add(trigger)
                test_triggers_en.update(all_triggers_en)

                test_content = re.sub(
                    r'- 中文:\s*.*?\n- 英文:\s*.*?\n',
                    f'- 中文: {", ".join(sorted(test_triggers_cn)[:15])}\n- 英文: {", ".join(sorted(test_triggers_en)[:15])}\n',
                    content,
                )

                correct = 0
                for eval_item in eval_set:
                    query = eval_item["query"].lower()
                    should_trigger = eval_item["should_trigger"]

                    has_trigger = any(
                        trigger.lower() in query for trigger in sorted(test_triggers_cn)[:15]
                    ) or any(
                        trigger.lower() in query for trigger in sorted(test_triggers_en)[:15]
                    )

                    if has_trigger == should_trigger:
                        correct += 1

                accuracy = correct / len(eval_set) if eval_set else 0

                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_triggers_cn = sorted(test_triggers_cn)[:15]
                    best_triggers_en = sorted(test_triggers_en)[:15]

                test_triggers_cn.discard(trigger)

        return {
            "triggers_cn": best_triggers_cn,
            "triggers_en": best_triggers_en,
            "accuracy": best_accuracy,
            "iterations": max_iterations,
        }


def main():
    parser = argparse.ArgumentParser(description="Trigger Word Evaluator - 评估和优化触发词")
    parser.add_argument("skill_directory", type=Path, help="Skill 目录路径")
    parser.add_argument(
        "--mode",
        choices=["generate", "evaluate", "optimize"],
        required=True,
        help="运行模式",
    )
    parser.add_argument("--eval-set", type=Path, help="评估集 JSON 文件路径")
    parser.add_argument("--output", type=Path, help="输出文件路径")
    parser.add_argument("--max-iterations", type=int, default=5, help="优化最大迭代次数")
    parser.add_argument("--verbose", action="store_true", help="详细日志")
    args = parser.parse_args()

    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}")

    skill_dir = args.skill_directory.resolve()
    if not skill_dir.exists():
        logger.error(f"Skill 目录不存在: {skill_dir}")
        sys.exit(1)

    if args.mode == "generate":
        logger.info("生成触发词评估集...")
        eval_set = TriggerEvalGenerator.generate_eval_set(skill_dir)

        if not eval_set:
            logger.error("未能生成评估集")
            sys.exit(1)

        if args.output:
            output_path = args.output
        else:
            evals_dir = skill_dir / "evals"
            evals_dir.mkdir(exist_ok=True)
            output_path = evals_dir / "trigger_evals.json"

        output_path.write_text(
            json.dumps(eval_set, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        logger.info(f"评估集已保存到: {output_path}")
        logger.info(f"共 {len(eval_set)} 条评估项")
        logger.info(f"  - 应该触发: {sum(1 for e in eval_set if e['should_trigger'])}")
        logger.info(f"  - 不应该触发: {sum(1 for e in eval_set if not e['should_trigger'])}")

    elif args.mode == "evaluate":
        if not args.eval_set or not args.eval_set.exists():
            logger.error("评估集文件不存在")
            sys.exit(1)

        logger.info("评估当前触发词...")
        eval_set = json.loads(args.eval_set.read_text(encoding="utf-8"))
        result = TriggerOptimizer.evaluate_triggers(skill_dir, eval_set)

        logger.info("评估结果:")
        logger.info(f"  - 准确率: {result['accuracy']:.2%}")
        logger.info(f"  - 总数: {result['total']}")
        logger.info(f"  - 正确: {result['correct']}")
        logger.info(f"  - 误报: {result['false_positives']}")
        logger.info(f"  - 漏报: {result['false_negatives']}")

        if args.output:
            args.output.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.info(f"结果已保存到: {args.output}")

    elif args.mode == "optimize":
        if not args.eval_set or not args.eval_set.exists():
            logger.error("评估集文件不存在")
            sys.exit(1)

        logger.info("优化触发词...")
        eval_set = json.loads(args.eval_set.read_text(encoding="utf-8"))
        result = TriggerOptimizer.optimize_from_evals(skill_dir, eval_set, args.max_iterations)

        logger.info("优化结果:")
        logger.info(f"  - 准确率: {result['accuracy']:.2%}")
        logger.info(f"  - 迭代次数: {result['iterations']}")
        logger.info(f"  - 优化后中文触发词: {', '.join(result['triggers_cn'])}")
        logger.info(f"  - 优化后英文触发词: {', '.join(result['triggers_en'])}")

        if args.output:
            args.output.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            logger.info(f"结果已保存到: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
