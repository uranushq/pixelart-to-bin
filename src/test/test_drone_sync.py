"""
Drone-show sync simulator / tester.

한 장의 픽셀아트를 4x4 타일(= 드론 1대)로 쪼갠 .bin 들을 각각 '독립된 드론'처럼
재생하고, 매 디스플레이 틱마다 전체 보드로 재조립해서 30FPS로 보여 준다.

목적: 여러 드론(타일)을 따로 재생할 때 서로 동기가 어긋나(desync) 사람 눈에
화면이 찢어져(tearing) 보이는지를 실시간으로 눈으로 확인하기 위한 도구.

- 드론 1대  = tile_XX.bin 1개 (4x4)
- 보드 배치 = full.bin 헤더의 (width, height) 로부터 grid(cols x rows) 계산,
              타일 번호는 행 우선(좌→우, 상→하) — tile_splitter.py 규칙과 동일
- 기본 동작 = 모든 드론이 같은 벽시계(wall clock)를 참조 → 이상적 동기(찢어짐 없음)
- --jitter  = 각 드론에 독립적인 클럭 드리프트/프레임 드롭을 주입 → 실제 desync 재현
- --offset  = 각 드론에 무작위 시작 오프셋 → desync 재현

사용 예:
    python ./src/test/test_drone_sync.py ./output/alphawave
    python ./src/test/test_drone_sync.py ./output/alphawave --fps 30 --scale 24
    python ./src/test/test_drone_sync.py ./output/alphawave --jitter 0.4    # desync 시연
    python ./src/test/test_drone_sync.py ./output/alphawave --offset 3      # desync 시연

조작키: q/ESC 종료 · space 일시정지 · g 타일 격자 토글 · r 전체 재동기(리셋)
        d 데모용 desync 토글(--jitter 값 사용)
"""
import struct
import sys
import os
import re
import time
import glob
import argparse
import random
from typing import List, Optional

import numpy as np
import cv2

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

TILE = 4  # 타일 한 변(px) = 드론 격자 한 변


def _natural_key(text: str):
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]


def read_header(path: str):
    """헤더 16바이트 → (total_frames, height, width, fps)."""
    with open(path, 'rb') as f:
        data = f.read(16)
    if len(data) != 16:
        raise ValueError(f"{path}: 헤더 16바이트를 읽지 못함")
    return struct.unpack('<IIII', data)


def load_all_frames(path: str) -> np.ndarray:
    """
    .bin 전체 프레임을 메모리에 적재 → ndarray(frames, height, width, 3) RGB(uint8).

    트레일러/헤더가 가리키는 값과 실제 파일 크기가 어긋나도 안전하게,
    파일 크기로 실제 프레임 수를 다시 계산해서 그만큼만 읽는다.
    """
    total, height, width, fps = read_header(path)
    frame_size = height * width * 3
    file_size = os.path.getsize(path)
    real_frames = max(0, (file_size - 32) // frame_size)  # 헤더16 + 트레일러16 제외
    n = min(total, real_frames)
    with open(path, 'rb') as f:
        f.seek(16)
        buf = f.read(n * frame_size)
    arr = np.frombuffer(buf, dtype=np.uint8).reshape((n, height, width, 3))
    return arr


class Drone:
    """독립 재생되는 드론 1대 = 타일 1개."""

    def __init__(self, tile_id: int, path: str, grid_cols: int):
        self.id = tile_id
        self.path = path
        total, h, w, fps = read_header(path)
        self.frames = load_all_frames(path)
        self.count = self.frames.shape[0]
        self.h, self.w = h, w
        self.fps = fps
        # 보드 내 픽셀 위치 (행 우선 번호 → 좌상단 픽셀 좌표)
        self.row = tile_id // grid_cols
        self.col = tile_id % grid_cols
        self.y0 = self.row * TILE
        self.x0 = self.col * TILE
        # desync 시뮬레이션용 상태
        self.offset = 0          # 시작 프레임 오프셋
        self.drift = 0.0         # 누적 클럭 드리프트(프레임 단위)
        self.last_index = 0

    def index_at(self, master_frame: int) -> int:
        """이 드론이 master_frame 시점에 표시할 자기 프레임 인덱스."""
        if self.count <= 0:
            return 0
        idx = int(master_frame + self.offset + self.drift) % self.count
        self.last_index = idx
        return idx

    def frame_at(self, master_frame: int) -> np.ndarray:
        return self.frames[self.index_at(master_frame)]


def discover(directory: str):
    """디렉터리에서 full.bin 과 tile_XX.bin 들을 찾는다."""
    full = sorted(glob.glob(os.path.join(directory, '*_full.bin')))
    tiles = sorted(glob.glob(os.path.join(directory, '*_tile_*.bin')), key=_natural_key)
    return (full[0] if full else None), tiles


def build_board_layout(full_path: Optional[str], tiles: List[str]):
    """전체 보드의 (cols, rows, board_w, board_h) 계산."""
    if full_path:
        _, h, w, _ = read_header(full_path)
        return w // TILE, h // TILE, w, h
    # full.bin 이 없으면 타일 개수로 정사각형에 가깝게 추정
    n = len(tiles)
    cols = int(round(n ** 0.5))
    while cols > 1 and n % cols != 0:
        cols -= 1
    rows = n // cols
    return cols, rows, cols * TILE, rows * TILE


def draw_grid(img: np.ndarray, scale: int, cols: int, rows: int,
              warn_ids=None) -> np.ndarray:
    """타일 경계선(드론 경계)을 그린다. warn_ids 의 타일은 빨간 테두리."""
    warn_ids = warn_ids or set()
    out = img.copy()
    color = (60, 60, 60)
    for c in range(cols + 1):
        x = c * TILE * scale
        cv2.line(out, (x, 0), (x, rows * TILE * scale), color, 1)
    for r in range(rows + 1):
        y = r * TILE * scale
        cv2.line(out, (0, y), (cols * TILE * scale, y), color, 1)
    for tid in warn_ids:
        r, c = tid // cols, tid % cols
        x0, y0 = c * TILE * scale, r * TILE * scale
        cv2.rectangle(out, (x0, y0), (x0 + TILE * scale - 1, y0 + TILE * scale - 1),
                      (0, 0, 255), 2)
    return out


def run(directory: str, fps: int, scale: int, jitter: float,
        offset_max: int, show_grid: bool, loop: bool):
    full_path, tile_paths = discover(directory)
    if not tile_paths:
        print(f"타일 .bin 을 찾지 못했습니다: {directory}\\*_tile_*.bin")
        return

    cols, rows, board_w, board_h = build_board_layout(full_path, tile_paths)
    n_expected = cols * rows

    print("=" * 60)
    print(f"드론 쇼 동기 시뮬레이터")
    print(f"  디렉터리   : {directory}")
    print(f"  보드 크기  : {board_w} x {board_h} px")
    print(f"  드론 격자  : {cols} cols x {rows} rows = {n_expected} 드론(타일)")
    print(f"  발견 타일  : {len(tile_paths)} 개")
    print(f"  재생 FPS   : {fps}")

    drones: List[Drone] = []
    for i, p in enumerate(sorted(tile_paths, key=_natural_key)):
        # 파일명 tile_XX 의 번호를 신뢰(누락/순서뒤섞임 방지)
        m = re.search(r'tile_(\d+)', os.path.basename(p))
        tid = int(m.group(1)) if m else i
        drones.append(Drone(tid, p, cols))

    # --- 동기 가능성 사전 점검: 프레임 수가 다른 드론은 반드시 어긋난다 ---
    counts = {}
    for d in drones:
        counts.setdefault(d.count, []).append(d.id)
    majority = max(counts, key=lambda k: len(counts[k]))
    desync_by_count = {tid for cnt, ids in counts.items() if cnt != majority for tid in ids}

    print("-" * 60)
    if len(counts) == 1:
        print(f"  [OK] 모든 드론 프레임 수 동일 = {majority} → 구조적 동기 가능")
    else:
        print(f"  [경고] 드론별 프레임 수 불일치 → 루프 시 필연적 desync 발생")
        for cnt, ids in sorted(counts.items()):
            print(f"         frames={cnt}: tiles {ids}")
        print(f"         (다수={majority}, 어긋나는 드론={sorted(desync_by_count)})")
    print("-" * 60)
    print("조작: q 종료 · space 일시정지 · g 격자 · r 재동기 · d desync 토글")

    # --- desync 주입(시작 오프셋) ---
    # 결정적 재현을 위해 고정 시드 사용(Math.random 류 불필요)
    rng = random.Random(20240604)
    if offset_max > 0:
        for d in drones:
            d.offset = rng.randint(0, offset_max)

    win = 'Drone Sync Tester'
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, board_w * scale, board_h * scale)

    frame_period = 1.0 / fps
    start = time.perf_counter()
    paused = False
    demo_desync = jitter > 0.0
    master = 0
    pause_started = 0.0
    paused_total = 0.0
    last_render = -1

    while True:
        now = time.perf_counter()
        if not paused:
            elapsed = now - start - paused_total
            master = int(elapsed * fps)

        # 재생 종료 판정(루프 아님 + 다수 프레임 다 지남)
        if not loop and master >= majority:
            print("재생 종료")
            break

        # --- desync 시뮬레이션: 각 드론 클럭 드리프트 갱신 ---
        if demo_desync and not paused:
            for d in drones:
                # 드론마다 독립적으로 가끔 1프레임 밀리거나 당겨짐(프레임 드롭/지터)
                if rng.random() < jitter * 0.1:
                    d.drift += rng.choice((-1, 1))

        # --- 보드 재조립 ---
        board = np.zeros((board_h, board_w, 3), dtype=np.uint8)
        for d in drones:
            tile = d.frame_at(master)
            board[d.y0:d.y0 + TILE, d.x0:d.x0 + TILE] = tile

        # RGB → BGR, 확대(최근접)
        bgr = cv2.cvtColor(board, cv2.COLOR_RGB2BGR)
        big = cv2.resize(bgr, (board_w * scale, board_h * scale),
                         interpolation=cv2.INTER_NEAREST)

        # 어긋나는 드론 강조: 프레임 수 불일치 + 드리프트가 0이 아닌 드론
        warn = set(desync_by_count)
        if demo_desync:
            warn |= {d.id for d in drones if int(d.drift) != 0}
        if show_grid:
            big = draw_grid(big, scale, cols, rows, warn)

        status = f"f={master%majority if majority else 0}/{majority}  fps={fps}"
        if demo_desync:
            status += f"  DESYNC-DEMO(jitter={jitter})"
        if paused:
            status += "  [PAUSED]"
        cv2.putText(big, status, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0), 1, cv2.LINE_AA)
        cv2.imshow(win, big)

        # 30FPS 페이싱: 다음 틱까지 남은 시간만큼 대기
        target = start + paused_total + (master + 1) * frame_period
        wait_ms = max(1, int((target - time.perf_counter()) * 1000))
        key = cv2.waitKey(wait_ms if not paused else 30) & 0xFF

        if key in (ord('q'), 27):
            break
        elif key == ord(' '):
            paused = not paused
            if paused:
                pause_started = time.perf_counter()
            else:
                paused_total += time.perf_counter() - pause_started
        elif key == ord('g'):
            show_grid = not show_grid
        elif key == ord('r'):
            # 전체 재동기: 모든 드론 오프셋/드리프트 초기화 + 시계 리셋
            for d in drones:
                d.offset = 0
                d.drift = 0.0
            start = time.perf_counter()
            paused_total = 0.0
            print("재동기(리셋) 완료")
        elif key == ord('d'):
            demo_desync = not demo_desync
            if not demo_desync:
                for d in drones:
                    d.drift = 0.0
            print(f"desync 데모 {'ON' if demo_desync else 'OFF'}")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="여러 드론(4x4 타일)을 독립 재생해 30FPS에서 동기 어긋남을 눈으로 검사")
    ap.add_argument('directory', nargs='?', default='./output/alphawave',
                    help='타일 .bin 들이 있는 디렉터리 (기본: ./output/alphawave)')
    ap.add_argument('--fps', type=int, default=30, help='재생 프레임레이트 (기본: 30)')
    ap.add_argument('--scale', type=int, default=24, help='픽셀 확대 배율 (기본: 24)')
    ap.add_argument('--jitter', type=float, default=0.0,
                    help='드론별 클럭 지터 강도 0~1 (>0 이면 desync 시연 모드)')
    ap.add_argument('--offset', type=int, default=0, dest='offset_max',
                    help='드론별 무작위 시작 오프셋 최대 프레임 (desync 시연)')
    ap.add_argument('--no-grid', action='store_true', help='타일 격자선 끄기')
    ap.add_argument('--no-loop', action='store_true', help='반복 재생 끄기')
    args = ap.parse_args()

    if not os.path.isdir(args.directory):
        print(f"디렉터리가 아닙니다: {args.directory}")
        sys.exit(1)

    run(args.directory, fps=args.fps, scale=args.scale, jitter=args.jitter,
        offset_max=args.offset_max, show_grid=not args.no_grid,
        loop=not args.no_loop)
