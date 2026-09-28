"""Install and enable the current checkout's user-level systemd daily timer."""

import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    unit_directory = Path.home() / ".config/systemd/user"
    unit_directory.mkdir(parents=True, exist_ok=True)
    # systemd expands percent specifiers even inside quoted arguments.
    quote = lambda value: json.dumps(str(value), ensure_ascii=False).replace("%", "%%")
    (unit_directory / "oversold-931743.service").write_text(
        "[Unit]\nDescription=CSI 931743 close-of-day oversold report\n\n"
        "[Service]\nType=oneshot\n"
        f"WorkingDirectory={str(root).replace('%', '%%')}\n"
        f"ExecStart={quote(Path(sys.executable).resolve())} -m oversold\n"
        "TimeoutStartSec=120\nUMask=0077\n",
        encoding="utf-8",
    )
    (unit_directory / "oversold-931743.timer").write_text(
        "[Unit]\nDescription=Check CSI 931743 at 18:00 Shanghai on weekdays\n\n"
        "[Timer]\nOnCalendar=Mon..Fri *-*-* 18:00:00 Asia/Shanghai\n"
        "Persistent=true\nAccuracySec=1min\n\n"
        "[Install]\nWantedBy=timers.target\n",
        encoding="utf-8",
    )
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", "oversold-931743.timer"], check=True)
    subprocess.run(["systemctl", "--user", "is-active", "--quiet", "oversold-931743.timer"], check=True)
    print("已启用：每周一至五北京时间 18:00 检查；节假日无当日日线时明确标注，不虚构信号。")
    subprocess.run(["systemctl", "--user", "list-timers", "oversold-931743.timer", "--no-pager"], check=True)
    print("退出登录后持续运行需启用用户 linger；查看：loginctl show-user $USER -p Linger")


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"定时任务安装失败：{error}", file=sys.stderr)
        raise SystemExit(1)
