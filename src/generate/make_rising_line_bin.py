"""
'가로줄 하나가 아래에서 위로 올라가는' 30초 테스트 애니메이션 생성기.

드론 쇼 동기 테스트용 패턴. 한 줄의 직선은 사람 눈이 '곧음(straightness)'을
가장 민감하게 판별하는 패턴이라, 드론(타일)이 하나라도 동기에서 어긋나면
줄이 계단처럼 끊겨 보인다 → desync 가 한눈에 보인다.

- 배경: 검정
- 가로줄: 보드 전체 폭, 1px 높이, 밝은 색 → 매 프레임 한 행(row)만 켜짐
- 움직임: frame 0 에서 맨 아래(y=H-1) → 마지막 프레임에서 맨 위(y=0)
- 길이: duration 초 × fps 프레임 (기본 30초 × 30fps = 900프레임)

출력(.bin 구조는 README '바이너리(.bin) 파일 구조' 절과 동일):
    output/<name>/<name>_sequence_full.bin
    output/<name>/<name>_sequence_tile_00.bin ... tile_NN.bin

사용 예:
    python ./src/generate/make_rising_line_bin.py
    python ./src/generate/make_rising_line_bin.py --width 40 --height 24 --duration 30 --fps 30
그 다음 재생/동기 검사:
    python ./src/test/test_drone_sync.py ./output/rising_line
    python ./src/test/test_drone_sync.py ./output/rising_line --offset 60   # desync 시연
"""
import struct
import os
import time
import argparse

import numpy as np

TILE = 4
END_MARKER = 0xDEADBEEF


def write_bin(path: str, frames: np.ndarray, fps: int):
    """
    frames: ndarray(total, H, W, 3) uint8 RGB.
    README 의 포맷대로 헤더(<IIII) + 프레임데이터(row-major RGB) + 트레일러(<IQI) 기록.
    ndarray 의 C-order tobytes() 가 곧 (frame, row, col, channel) = 우리 포맷과 동일.
    """
    total, h, w, _ = frames.shape
    header = struct.pack('<IIII', total, h, w, fps)
    body = frames.tobytes()
    trailer = struct.pack('<IQI', total, int(time.time()), END_MARKER)
    with open(path, 'wb') as f:
        f.write(header + body + trailer)


def build_rising_line(width: int, height: int, total: int,
                      color=(255, 255, 255)) -> np.ndarray:
    """아래(y=H-1)에서 위(y=0)로 올라가는 1px 가로줄 프레임 생성."""
    frames = np.zeros((total, height, width, 3), dtype=np.uint8)
    denom = max(1, total - 1)
    for i in range(total):
        progress = i / denom            # 0.0 → 1.0
        # progress 0 → 맨 아래, 1 → 맨 위
        y = int(round((1.0 - progress) * (height - 1)))
        frames[i, y, :, :] = color
    return frames


def main():
    ap = argparse.ArgumentParser(description="아래→위로 올라가는 가로줄 30초 테스트 bin 생성")
    ap.add_argument('--name', default='rising_line', help='출력 이름/폴더 (기본: rising_line)')
    ap.add_argument('--width', type=int, default=40, help='보드 가로 px, 4의 배수 (기본: 40)')
    ap.add_argument('--height', type=int, default=24, help='보드 세로 px, 4의 배수 (기본: 24)')
    ap.add_argument('--duration', type=float, default=30.0, help='길이(초) (기본: 30)')
    ap.add_argument('--fps', type=int, default=30, help='프레임레이트 (기본: 30)')
    ap.add_argument('--outdir', default='./output', help='출력 루트 (기본: ./output)')
    args = ap.parse_args()

    if args.width % TILE != 0 or args.height % TILE != 0:
        raise SystemExit(f"가로/세로는 4의 배수여야 합니다 (got {args.width}x{args.height})")

    total = int(round(args.duration * args.fps))
    cols, rows = args.width // TILE, args.height // TILE

    out = os.path.join(args.outdir, args.name)
    os.makedirs(out, exist_ok=True)

    print(f"보드 {args.width}x{args.height}px, 드론 {cols}x{rows}={cols*rows}대, "
          f"{total}프레임 @ {args.fps}fps = {total/args.fps:.1f}s")

    frames = build_rising_line(args.width, args.height, total)

    # 전체 보드
    full_path = os.path.join(out, f"{args.name}_sequence_full.bin")
    write_bin(full_path, frames, args.fps)
    print(f"  full  -> {full_path}")

    # 타일(드론)별 분할: 타일 번호는 행 우선(좌→우, 상→하)
    for tr in range(rows):
        for tc in range(cols):
            tid = tr * cols + tc
            tile_frames = frames[:, tr*TILE:(tr+1)*TILE, tc*TILE:(tc+1)*TILE, :]
            tile_frames = np.ascontiguousarray(tile_frames)
            tpath = os.path.join(out, f"{args.name}_sequence_tile_{tid:02d}.bin")
            write_bin(tpath, tile_frames, args.fps)
    print(f"  tiles -> {out}\\{args.name}_sequence_tile_00.bin ... tile_{cols*rows-1:02d}.bin")
    print("재생:  python ./src/test/test_drone_sync.py " + out.replace('\\', '/'))


if __name__ == "__main__":
    main()
