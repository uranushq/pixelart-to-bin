"""
드론 쇼 동기 테스트 패턴: '각 드론(4x4)이 자기 4줄을 아래→위로 순환, 10번 반복'.

전체 보드를 한 번에 훑는 게 아니라, **드론 1대(4x4 타일) 단위**로 가로줄이
자기 4개 행 안에서만 움직인다. 한 사이클 = 맨 아래 행 → 맨 위 행(4스텝),
이를 cycles(기본 10)번 반복한다.

모든 드론이 동시에 같은 '로컬 행'을 켜야 하므로, 동기가 맞으면 보드 전체에
4px 간격의 가로줄들이 일제히 같은 박자로 오르내린다. 드론 하나라도 어긋나면
그 4x4 칸만 줄 높이가 달라져 한눈에 보인다.

배치(보드 좌표 row 기준, TILE=4):
  로컬 행 L(0=타일 위, 3=타일 아래)일 때, board_row % 4 == L 인 모든 행을 켠다.
  아래→위: L 시퀀스 = [3, 2, 1, 0] 을 cycles 번 반복.

총 프레임 = 4(행) × cycles × frames_per_row.
기본값: 4 × 10 × 10 = 400프레임 @ 30fps ≈ 13.3초.

출력(.bin 구조는 README '바이너리(.bin) 파일 구조' 절과 동일):
    output/<name>/<name>_sequence_full.bin
    output/<name>/<name>_sequence_tile_00.bin ... tile_NN.bin

사용 예:
    python ./src/generate/make_rising_line_bin.py
    python ./src/generate/make_rising_line_bin.py --cycles 10 --frames-per-row 10
그 다음 재생/동기 검사:
    python ./src/test/test_drone_sync.py ./output/rising_line
    python ./src/test/test_drone_sync.py ./output/rising_line --offset 7   # desync 시연
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


def build_drone_line_cycle(width: int, height: int, cycles: int,
                           frames_per_row: int, color=(255, 255, 255)) -> np.ndarray:
    """
    각 4x4 드론이 자기 4줄을 아래→위로 순환(L=3→2→1→0), cycles 번 반복.
    매 프레임 board_row % 4 == L 인 모든 행을 켠다.
    """
    steps = [3, 2, 1, 0]                       # 아래 → 위 (타일 로컬 행)
    total = len(steps) * cycles * frames_per_row
    frames = np.zeros((total, height, width, 3), dtype=np.uint8)

    # board_row % 4 == L 인 행 인덱스 미리 계산
    rows_for_L = {L: np.arange(L, height, TILE) for L in steps}

    f = 0
    for _ in range(cycles):
        for L in steps:
            rows = rows_for_L[L]
            for _ in range(frames_per_row):
                frames[f, rows, :, :] = color
                f += 1
    return frames


def main():
    ap = argparse.ArgumentParser(
        description="각 드론(4x4)이 4줄을 아래→위로 10번 순환하는 테스트 bin 생성")
    ap.add_argument('--name', default='rising_line', help='출력 이름/폴더 (기본: rising_line)')
    ap.add_argument('--width', type=int, default=40, help='보드 가로 px, 4의 배수 (기본: 40)')
    ap.add_argument('--height', type=int, default=24, help='보드 세로 px, 4의 배수 (기본: 24)')
    ap.add_argument('--cycles', type=int, default=10, help='드론별 4줄 순환 반복 횟수 (기본: 10)')
    ap.add_argument('--frames-per-row', type=int, default=10, dest='frames_per_row',
                    help='한 줄(행)을 유지할 프레임 수 = 속도 (기본: 10)')
    ap.add_argument('--fps', type=int, default=30, help='프레임레이트 (기본: 30)')
    ap.add_argument('--outdir', default='./output', help='출력 루트 (기본: ./output)')
    args = ap.parse_args()

    if args.width % TILE != 0 or args.height % TILE != 0:
        raise SystemExit(f"가로/세로는 4의 배수여야 합니다 (got {args.width}x{args.height})")

    cols, rows = args.width // TILE, args.height // TILE
    total = TILE * args.cycles * args.frames_per_row

    out = os.path.join(args.outdir, args.name)
    os.makedirs(out, exist_ok=True)

    print(f"보드 {args.width}x{args.height}px, 드론 {cols}x{rows}={cols*rows}대")
    print(f"드론별: 4줄 × {args.cycles}회 순환, 줄당 {args.frames_per_row}프레임")
    print(f"총 {total}프레임 @ {args.fps}fps = {total/args.fps:.1f}s")

    frames = build_drone_line_cycle(args.width, args.height, args.cycles,
                                    args.frames_per_row)

    # 전체 보드
    full_path = os.path.join(out, f"{args.name}_sequence_full.bin")
    write_bin(full_path, frames, args.fps)
    print(f"  full  -> {full_path}")

    # 타일(드론)별 분할: 타일 번호는 행 우선(좌→우, 상→하)
    for tr in range(rows):
        for tc in range(cols):
            tid = tr * cols + tc
            tile_frames = np.ascontiguousarray(
                frames[:, tr*TILE:(tr+1)*TILE, tc*TILE:(tc+1)*TILE, :])
            tpath = os.path.join(out, f"{args.name}_sequence_tile_{tid:02d}.bin")
            write_bin(tpath, tile_frames, args.fps)
    print(f"  tiles -> {out}\\{args.name}_sequence_tile_00.bin ... tile_{cols*rows-1:02d}.bin")
    print("재생:  python ./src/test/test_drone_sync.py " + out.replace('\\', '/'))


if __name__ == "__main__":
    main()
