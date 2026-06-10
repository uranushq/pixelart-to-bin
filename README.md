# Pixelart to Binary Converter

픽셀아트 이미지를 바이너리(`.bin`) 시퀀스로 변환하고, 4x4 타일 단위로 분할하여 저장하는 도구입니다.

## 주요 기능

- 픽셀아트 이미지를 바이너리 애니메이션 시퀀스로 변환
- 전체 보드와 4x4 타일 단위로 분할 저장
- 자동 차원 검증 (가로/세로가 4의 배수여야 함)
- 클러스터 시각화 이미지 생성
- 스캐터링 애니메이션 모드

---

## 바이너리(.bin) 파일 구조

> 이 절만 보고도 다른 언어/코드에서 동일한 `.bin` 파일을 생성하거나 파싱할 수 있도록 작성되었습니다.
> 정의 코드: [add_metadata.py](src/utils/add_metadata.py) / 파서 코드: [test_bin.py](src/test/test_bin.py)

### 전체 레이아웃

파일은 **헤더 → 프레임 데이터 → 트레일러** 순서로 이어진 단일 연속 바이트 스트림입니다.

```
┌──────────────┬───────────────────────────────┬──────────────┐
│   HEADER     │        FRAME DATA             │   TRAILER    │
│   16 bytes   │   total_frames × H × W × 3    │   16 bytes   │
└──────────────┴───────────────────────────────┴──────────────┘
```

- **바이트 순서(엔디안):** 모든 정수 필드는 **리틀 엔디안(little-endian)**
- **정렬(alignment):** 패딩 없음. 모든 필드가 빈틈없이 연속 배치됨
- **전체 파일 크기:** `16 + (total_frames × height × width × 3) + 16` 바이트

### 1. 헤더 (16 bytes)

오프셋 0에서 시작. C 구조체 기준 `struct.pack('<IIII', ...)`.

| 오프셋 | 크기 | 타입      | 필드           | 설명                       |
| ------ | ---- | --------- | -------------- | -------------------------- |
| 0      | 4    | uint32 LE | `total_frames` | 총 프레임 수               |
| 4      | 4    | uint32 LE | `height`       | 프레임 세로 픽셀 수        |
| 8      | 4    | uint32 LE | `width`        | 프레임 가로 픽셀 수        |
| 12     | 4    | uint32 LE | `fps`          | 초당 프레임 수 (재생 속도) |

### 2. 프레임 데이터 (가변 길이)

오프셋 16에서 시작. `total_frames`개의 프레임이 순서대로 연속 저장됩니다.

- **프레임 1개 크기:** `height × width × 3` 바이트
- **픽셀 순서:** 행 우선(row-major) — 위에서 아래(y: 0 → height-1), 각 행 안에서 왼쪽에서 오른쪽(x: 0 → width-1)
- **픽셀 1개:** `R`, `G`, `B` 각각 1바이트(uint8, 0–255), **RGB 순서** (BGR/RGBA 아님, 알파 채널 없음)

픽셀 1개(3바이트) 내부의 바이트 위치 — 픽셀 시작 오프셋 `pixel_start` 기준:

| 픽셀 내 오프셋 | 크기 | 타입  | 채널     | 범위  |
| -------------- | ---- | ----- | -------- | ----- |
| +0             | 1    | uint8 | R (빨강) | 0–255 |
| +1             | 1    | uint8 | G (초록) | 0–255 |
| +2             | 1    | uint8 | B (파랑) | 0–255 |

한 프레임의 바이트 나열 순서:

```
(y=0,x=0)R G B  (y=0,x=1)R G B  ...  (y=0,x=W-1)R G B
(y=1,x=0)R G B  (y=1,x=1)R G B  ...  (y=1,x=W-1)R G B
...
(y=H-1,x=0)R G B  ...             (y=H-1,x=W-1)R G B
```

특정 프레임/픽셀의 바이트 오프셋 계산:

```
frame_size  = height × width × 3
frame_start = 16 + frame_index × frame_size
pixel_start = frame_start + (y × width + x) × 3
R = byte[pixel_start + 0]
G = byte[pixel_start + 1]
B = byte[pixel_start + 2]
```

### 3. 트레일러 (16 bytes)

프레임 데이터 바로 뒤에서 시작 (오프셋 `16 + total_frames × height × width × 3`). `struct.pack('<IQI', ...)`.

| 오프셋(트레일러 기준) | 크기 | 타입      | 필드           | 설명                                          |
| --------------------- | ---- | --------- | -------------- | --------------------------------------------- |
| 0                     | 4    | uint32 LE | `total_frames` | 헤더의 값과 동일 (무결성 검증용)              |
| 4                     | 8    | uint64 LE | `save_time`    | 저장 시각, Unix epoch 초 (`time.time()` 정수) |
| 12                    | 4    | uint32 LE | `end_marker`   | 고정 종료 마커 `0xDEADBEEF`                   |

> **참고:** 트레일러 시작이 8바이트 필드(`save_time`)를 포함하지만 자연 정렬을 위한 패딩은 없습니다. `uint32` + `uint64` + `uint32` = 16바이트가 그대로 이어집니다.

### 검증 규칙

올바른 파일은 다음을 모두 만족합니다.

1. 파일 크기 == `16 + total_frames × height × width × 3 + 16`
2. 헤더의 `total_frames` == 트레일러의 `total_frames`
3. 트레일러의 `end_marker` == `0xDEADBEEF`

### 실제 예시 (4x4 타일, 97프레임, 15fps)

[output/alphawave/alphawave_sequence_tile_00.bin](output/alphawave/alphawave_sequence_tile_00.bin) 기준:

```
파일 크기 : 4688 bytes
헤더      : total_frames=97, height=4, width=4, fps=15
프레임    : 97 × (4 × 4 × 3) = 97 × 48 = 4656 bytes
트레일러  : total_frames=97, save_time=1762322151, end_marker=0xDEADBEEF
검증      : 16 + 4656 + 16 = 4688  ✓
```

### 참조 구현 (Python)

쓰기:

```python
import struct, time

def write_bin(path, frames, fps):
    # frames: List[ frame[height][width][r,g,b] ]
    total = len(frames)
    height = len(frames[0])
    width  = len(frames[0][0])

    header = struct.pack('<IIII', total, height, width, fps)
    body = b''.join(
        bytes(v for row in frame for px in row for v in px)  # row-major, RGB
        for frame in frames
    )
    trailer = struct.pack('<IQI', total, int(time.time()), 0xDEADBEEF)

    with open(path, 'wb') as f:
        f.write(header + body + trailer)
```

읽기:

```python
import struct

def read_bin(path):
    with open(path, 'rb') as f:
        total, height, width, fps = struct.unpack('<IIII', f.read(16))
        frame_size = height * width * 3
        frames = []
        for _ in range(total):
            data = f.read(frame_size)
            frame = [
                [list(data[(y*width + x)*3 : (y*width + x)*3 + 3]) for x in range(width)]
                for y in range(height)
            ]
            frames.append(frame)
        tf, save_time, end_marker = struct.unpack('<IQI', f.read(16))
        assert tf == total and end_marker == 0xDEADBEEF
    return frames, height, width, fps
```

---

## 타일 분할 규칙

모든 이미지는 **4x4 픽셀 단위 타일**로 분할됩니다.

### 차원 요구사항

- 가로 크기: 4의 배수
- 세로 크기: 4의 배수
- 조건을 만족하지 않으면 오류 발생

### 타일 넘버링

타일은 **위에서 아래로, 왼쪽에서 오른쪽으로** 읽으며 0부터 번호가 매겨집니다.
예를 들어 16x16 이미지(4x4 레이아웃, 총 16개 타일):

```
 0   1   2   3
 4   5   6   7
 8   9  10  11
12  13  14  15
```

각 타일은 자체 헤더/트레일러를 가진 독립적인 `.bin` 파일로 저장되며, 위에 정의된 파일 구조를 동일하게 따릅니다(`height = width = 4`).

---

## 출력 파일

| 파일명                                        | 설명                   |
| --------------------------------------------- | ---------------------- |
| `{name}_sequence_full.bin`                    | 전체 보드 바이너리     |
| `{name}_sequence_tile_00.bin` ~ `tile_XX.bin` | 개별 4x4 타일 바이너리 |
| `{name}_cluster_visualization.png`            | 클러스터 시각화 이미지 |

### 예시 (12x12 이미지 → 3x3 = 9개 타일)

```
watermelon_sequence_full.bin       (전체 12x12 보드)
watermelon_sequence_tile_00.bin    (타일 0: 좌상단 4x4)
watermelon_sequence_tile_01.bin    (타일 1: 상단 중앙 4x4)
watermelon_sequence_tile_02.bin    (타일 2: 우상단 4x4)
watermelon_sequence_tile_03.bin    (타일 3: 좌측 중앙 4x4)
watermelon_sequence_tile_04.bin    (타일 4: 정중앙 4x4)
watermelon_sequence_tile_05.bin    (타일 5: 우측 중앙 4x4)
watermelon_sequence_tile_06.bin    (타일 6: 좌하단 4x4)
watermelon_sequence_tile_07.bin    (타일 7: 하단 중앙 4x4)
watermelon_sequence_tile_08.bin    (타일 8: 우하단 4x4)
```

---

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 일반 모드 (애니메이션 시퀀스)

```bash
python ./src/main.py <directory>
```

예시:

```bash
python ./src/main.py ./data/watermelon
```

### 스캐터링 애니메이션 모드

```bash
python ./src/main.py <directory> --scattering [옵션]
```

옵션:

| 옵션                | 설명                            | 기본값 |
| ------------------- | ------------------------------- | ------ |
| `--scattering`      | 스캐터링 애니메이션 모드 활성화 | -      |
| `--duration <초>`   | 이미지 유지 시간                | 5초    |
| `--transition <초>` | 나타나기/사라지기 전환 시간     | 0.5초  |
| `--fps <숫자>`      | 프레임 레이트                   | 15fps  |

예시:

```bash
python ./src/main.py ./data/alpha --scattering --duration 5 --transition 0.5 --fps 15
```

스캐터링 효과 진행:

1. 검은 프레임 (1초)
2. 나타나기: 각 픽셀이 랜덤하게 0% → 20% → 40% → 60% → 80% → 100% 밝기로 깜빡임
3. 유지: 설정한 시간만큼 이미지 유지
4. 사라지기: 100% → 0%로 랜덤하게 깜빡이며 사라짐
5. 검은 프레임 (1초)

폴더에 여러 이미지가 있으면 각 이미지를 순차적으로 스캐터링 애니메이션으로 표현하며, 각 이미지 사이에 검은 프레임이 자동 삽입됩니다.

---

## 드론 쇼 동기 테스트 (30FPS)

여러 4x4 타일(`tile_XX.bin`)을 각각 **독립된 드론 1대**처럼 재생하고, 매 틱마다 전체 보드로 재조립해 30FPS로 보여 줍니다. 드론 간 **동기 어긋남(desync)** 으로 사람 눈에 화면이 찢어져(tearing) 보이는지 실시간으로 확인하는 도구입니다.

코드: 재생기 [test_drone_sync.py](src/test/test_drone_sync.py) · 테스트 패턴 생성기 [make_rising_line_bin.py](src/generate/make_rising_line_bin.py)

### 권장 테스트 패턴: 드론별 4줄 순환 (10회 반복)

전체 보드를 한 번 훑는 게 아니라, **각 드론(4x4)이 자기 4개 행 안에서** 가로줄을 아래→위로 순환시키고 이를 10번 반복합니다. 모든 드론이 동시에 같은 로컬 행을 켜야 하므로, 동기가 맞으면 보드 전체에 4px 간격의 가로줄들이 **일제히 같은 박자로** 오르내립니다. 드론 하나라도 어긋나면 그 4x4 칸만 줄 높이가 달라져 한눈에 보입니다.

```bash
# 1) 테스트 패턴 bin 생성 (output/rising_line/ 에 full + 타일 60개)
#    기본: 4줄 × 10회 × 줄당 10프레임 = 400프레임 @ 30fps ≈ 13.3초
python ./src/generate/make_rising_line_bin.py

# 2) 동기 재생 — 모든 드론의 줄이 같은 박자로 오르내림(끊김 없음)
python ./src/test/test_drone_sync.py ./output/rising_line

# 3) desync 시연 — 드론마다 시작 오프셋/지터 → 4x4 칸별로 줄 높이가 어긋나 보임
python ./src/test/test_drone_sync.py ./output/rising_line --offset 7
python ./src/test/test_drone_sync.py ./output/rising_line --jitter 0.5
```

생성기 옵션: `--width`(기본 40) `--height`(기본 24) `--cycles`(드론별 4줄 순환 횟수, 기본 10) `--frames-per-row`(한 줄 유지 프레임=속도, 기본 10) `--fps`(기본 30) — 가로/세로는 4의 배수.

### 임의 시퀀스에 적용

```bash
# 기존 시퀀스의 타일들을 30FPS로 동기 재생
python ./src/test/test_drone_sync.py ./output/alphawave

# desync 시연
python ./src/test/test_drone_sync.py ./output/alphawave --jitter 0.4
python ./src/test/test_drone_sync.py ./output/alphawave --offset 3
```

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--fps <n>` | 재생 프레임레이트 | 30 |
| `--scale <n>` | 픽셀 확대 배율 | 24 |
| `--jitter <0~1>` | 드론별 클럭 지터(>0이면 desync 시연 모드) | 0 |
| `--offset <n>` | 드론별 무작위 시작 오프셋 최대 프레임 | 0 |
| `--no-grid` | 타일 격자선 끄기 | - |
| `--no-loop` | 반복 재생 끄기 | - |

조작키: `q`/`ESC` 종료 · `space` 일시정지 · `g` 격자 토글 · `r` 전체 재동기 · `d` desync 데모 토글

동작 방식:
- 보드 배치는 `full.bin` 헤더의 `(width, height)`에서 `cols = width/4`, `rows = height/4` 그리드로 계산하고, 타일 번호는 행 우선(좌→우, 상→하)으로 배치합니다([tile_splitter.py](src/utils/tile_splitter.py) 규칙과 동일).
- 기본 모드는 모든 드론이 같은 벽시계를 참조하므로 구조적으로 동기가 맞습니다.
- 드론별 **프레임 수가 다르면** 루프 시점이 어긋나 필연적으로 desync가 발생하며, 시작 시 콘솔에 경고하고 재생 중 해당 타일을 빨간 테두리로 강조합니다.

---

## 데이터 폴더 구조

```
data/
  pixelart/
    S#*/
      *.png
      config.json
  text/
    S#*/
      *.png
      config.json
  mixed/
    pixelart/
      S#*/
        *.png
        config.json
    text/
      S#*/
        *.png
        config.json
```

---

## 알고리즘 아키텍처

![PIXELTOBIN 아키텍처](./image/PIXELTOBIN.png)
