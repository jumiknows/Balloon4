from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class CameraUnavailable(RuntimeError):
    pass


def capture_video(
    output: Path,
    duration_ms: int,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
) -> None:
    executable = shutil.which("rpicam-vid")
    if executable is None:
        raise CameraUnavailable(
            "rpicam-vid was not found. Install the Raspberry Pi camera applications first."
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        executable,
        "--width",
        str(width),
        "--height",
        str(height),
        "--framerate",
        str(fps),
        "-t",
        str(duration_ms),
        "-o",
        str(output),
    ]
    subprocess.run(command, check=True)
