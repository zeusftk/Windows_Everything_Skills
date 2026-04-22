#!/usr/bin/env python3
"""
IPC Eval Viewer - 生成 IPC Skill 评估报告的 HTML 查看器

用法:
    python eval_viewer.py <report_json> [--output <html_output>]

示例:
    python eval_viewer.py ./skills/ipc-desktop/evals/report.json
    python eval_viewer.py ./skills/ipc-desktop/evals/report.json --output report.html
"""

import argparse
import sys
import webbrowser
from pathlib import Path

VIEWER_TEMPLATE = Path(__file__).parent.parent / "assets" / "eval_viewer.html"


def generate_viewer(report_path: Path, output_path: Path = None) -> Path:
    """生成 HTML 评估报告查看器"""
    if not report_path.exists():
        print(f"[ERROR] 报告文件不存在: {report_path}")
        return None

    with open(report_path, "r", encoding="utf-8") as f:
        report_json = f.read()

    if not VIEWER_TEMPLATE.exists():
        print(f"[ERROR] 查看器模板不存在: {VIEWER_TEMPLATE}")
        return None

    template = VIEWER_TEMPLATE.read_text(encoding="utf-8")
    html_content = template.replace("{{ report_json }}", report_json)

    if output_path is None:
        output_path = report_path.parent / "eval_report.html"

    output_path.write_text(html_content, encoding="utf-8")
    print(f"[OK] 评估报告已生成: {output_path}")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="IPC Eval Viewer - 生成评估报告查看器")
    parser.add_argument("report", type=Path, help="评估报告 JSON 文件路径")
    parser.add_argument("--output", type=Path, help="输出 HTML 文件路径")
    parser.add_argument("--open", action="store_true", help="在浏览器中打开")
    args = parser.parse_args()

    output_path = generate_viewer(args.report, args.output)

    if output_path and args.open:
        print(f"在浏览器中打开: {output_path}")
        webbrowser.open(f"file://{output_path.resolve()}")

    sys.exit(0 if output_path else 1)


if __name__ == "__main__":
    main()
