"""一次性获取所有课程数据并转换为 Markdown 格式。

该脚本依次执行 fetch_json.py 和 convert_markdown.py，提供便捷的一键运行方式。
"""

import argparse
import subprocess
import sys
from pathlib import Path

def main():
    """主函数 - 依次执行 fetch_json 和 convert_markdown。"""
    parser = argparse.ArgumentParser(
        description="获取所有 MOOC 课程、测验、考试并转换为 Markdown 格式"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output directory (default: output)",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="MOOC mob token (overrides environment variable)",
    )
    parser.add_argument(
        "--skip-markdown",
        action="store_true",
        help="Skip Markdown conversion (only fetch JSON)",
    )
    
    args = parser.parse_args()
    
    # Build command for fetch_json
    cmd = [sys.executable, "fetch_json.py", "--output", args.output]
    if args.token:
        cmd.extend(["--token", args.token])
    
    print("Step 1: Fetching JSON data...")
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("Failed to fetch JSON data")
        return
    
    # Convert to Markdown if requested
    if not args.skip_markdown:
        print("\nStep 2: Converting to Markdown...")
        cmd = [
            sys.executable,
            "convert_markdown.py",
            "--input", str(Path(args.output) / "json"),
            "--output", str(Path(args.output) / "markdown"),
        ]
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            print("Failed to convert to Markdown")
            return
    
    print("\nAll done!")


if __name__ == "__main__":
    main()
