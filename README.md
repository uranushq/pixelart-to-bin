# Pixelart to Binary Converter# Pixelart to Binary Converter# 데이터 폴더 구조

픽셀아트 이미지를 바이너리 파일로 변환하고 4x4 타일로 분할하여 저장하는 도구입니다.픽셀아트 이미지를 바이너리 파일로 변환하고 4x4 타일로 분할하여 저장하는 도구입니다.```

## 주요 기능pixelart/

- 픽셀아트 이미지를 바이너리 시퀀스로 변환## 주요 기능 S#\*/

- 전체 보드와 4x4 타일 단위로 분할 저장

- 자동 차원 검증 (가로/세로가 4의 배수여야 함) \*.png

- 클러스터 시각화 생성

- **스캐터링 애니메이션 모드** (새 기능!)- 픽셀아트 이미지를 바이너리 시퀀스로 변환 config.json

## 타일 분할 규칙- 전체 보드와 4x4 타일 단위로 분할 저장text/

모든 이미지는 **4x4 픽셀 단위로 분할**됩니다.- 자동 차원 검증 (가로/세로가 4의 배수여야 함) S#\*/

### 타일 넘버링 (0-15)- 클러스터 시각화 생성 \*.png

타일은 **상에서 하로, 좌에서 우로** 읽으며 0부터 번호가 매겨집니다: config.json

```## 타일 분할 규칙mixed/

0   1   2   3

4   5   6   7    pixelart/

8   9  10  11

12  13  14  15모든 이미지는 **4x4 픽셀 단위로 분할**됩니다. S#\*/

```

        *.png

예: 16x16 이미지는 4x4 레이아웃으로 총 16개의 타일로 분할됩니다.

### 타일 넘버링 (0-15) config.json

### 차원 요구사항

    text/

- **가로 크기**: 4의 배수여야 함

- **세로 크기**: 4의 배수여야 함타일은 **상에서 하로, 좌에서 우로** 읽으며 0부터 번호가 매겨집니다: S#\*/

- 조건을 만족하지 않으면 오류 발생

        *.png

## 설치

`````config.json

```bash

pip install -r requirements.txt0   1   2   3```

```

4   5   6   7

## 사용법

8   9  10  11# 알고리즘 아키텍처

### 일반 모드 (애니메이션 시퀀스)

12  13  14  15

```bash

python ./src/main.py <directory>```![PIXELTOBIN 아키](./image/PIXELTOBIN.png)

```



예시:예: 16x16 이미지는 4x4 레이아웃으로 총 16개의 타일로 분할됩니다.

```bash

python ./src/main.py ./data/watermelon### 차원 요구사항

```

- **가로 크기**: 4의 배수여야 함

### 스캐터링 애니메이션 모드- **세로 크기**: 4의 배수여야 함

- 조건을 만족하지 않으면 오류 발생

```bash

python ./src/main.py <directory> --scattering [옵션]## 설치

```

```bash

**옵션:**pip install -r requirements.txt

- `--scattering`: 스캐터링 애니메이션 모드 활성화````

- `--duration <초>`: 이미지 유지 시간 (기본값: 5초)

- `--transition <초>`: 나타나기/사라지기 전환 시간 (기본값: 0.5초)## 사용법

- `--fps <숫자>`: 프레임 레이트 (기본값: 15fps)

```bash

예시:python ./src/main.py <directory>

```bash```

python ./src/main.py ./data/alpha --scattering --duration 5 --transition 0.5 --fps 15

```예시:



### 스캐터링 애니메이션 효과```bash

python ./src/main.py ./data/watermelon

스캐터링 모드는 픽셀이 랜덤하게 깜빡이면서 나타나고 사라지는 효과를 만듭니다:```



1. **검은 프레임** (1초)## 출력 파일

2. **나타나기**: 각 픽셀이 랜덤하게 0% → 20% → 40% → 60% → 80% → 100% 밝기로 깜빡임

3. **유지**: 설정한 시간만큼 이미지 유지프로그램은 다음 파일들을 생성합니다:

4. **사라지기**: 100% → 0%로 랜덤하게 깜빡이며 사라짐

5. **검은 프레임** (1초)1. **{name}\_sequence_full.bin** - 전체 보드 바이너리 파일

2. **{name}\_sequence_tile_00.bin** ~ **tile_XX.bin** - 개별 4x4 타일 바이너리 파일

**여러 이미지 처리:**3. **{name}\_cluster_visualization.png** - 클러스터 시각화 이미지

- 폴더에 여러 이미지가 있으면 각 이미지를 순차적으로 스캐터링 애니메이션으로 표현

- 각 이미지 사이에 검은 프레임이 자동 삽입됨### 파일 예시 (12x12 이미지)



## 출력 파일```

watermelon_sequence_full.bin      (전체 12x12 보드)

프로그램은 다음 파일들을 생성합니다:watermelon_sequence_tile_00.bin   (타일 0: 좌상단 4x4)

watermelon_sequence_tile_01.bin   (타일 1: 상단 중앙 4x4)

### 일반 모드watermelon_sequence_tile_02.bin   (타일 2: 우상단 4x4)

1. **{name}_sequence_full.bin** - 전체 보드 바이너리 파일watermelon_sequence_tile_03.bin   (타일 3: 좌측 중앙 4x4)

2. **{name}_sequence_tile_00.bin** ~ **tile_XX.bin** - 개별 4x4 타일 바이너리 파일watermelon_sequence_tile_04.bin   (타일 4: 정중앙 4x4)

3. **{name}_cluster_visualization.png** - 클러스터 시각화 이미지watermelon_sequence_tile_05.bin   (타일 5: 우측 중앙 4x4)

watermelon_sequence_tile_06.bin   (타일 6: 좌하단 4x4)

### 스캐터링 모드watermelon_sequence_tile_07.bin   (타일 7: 하단 중앙 4x4)

1. **{name}_sequence_full.bin** - 스캐터링 애니메이션 전체 보드watermelon_sequence_tile_08.bin   (타일 8: 우하단 4x4)

2. **{name}_sequence_tile_00.bin** ~ **tile_XX.bin** - 개별 4x4 타일 애니메이션```



### 파일 예시 (12x12 이미지)# 데이터 폴더 구조



`````

watermelon_sequence_full.bin (전체 12x12 보드)pixelart/

watermelon_sequence_tile_00.bin (타일 0: 좌상단 4x4) S#\*/

watermelon_sequence_tile_01.bin (타일 1: 상단 중앙 4x4) \*.png

watermelon_sequence_tile_02.bin (타일 2: 우상단 4x4) config.json

watermelon_sequence_tile_03.bin (타일 3: 좌측 중앙 4x4)text/

watermelon_sequence_tile_04.bin (타일 4: 정중앙 4x4) S#\*/

watermelon_sequence_tile_05.bin (타일 5: 우측 중앙 4x4) \*.png

watermelon_sequence_tile_06.bin (타일 6: 좌하단 4x4) config.json

watermelon_sequence_tile_07.bin (타일 7: 하단 중앙 4x4)mixed/

watermelon_sequence_tile_08.bin (타일 8: 우하단 4x4) pixelart/

````S#*/

        *.png

## 데이터 폴더 구조        config.json

    text/

```        S#*/

data/        *.png

  pixelart/        config.json

    S#*/```

      *.png

      config.json# 알고리즘 아키텍처

  text/

    S#*/![PIXELTOBIN 아키](./image/PIXELTOBIN.png)

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
````

## 알고리즘 아키텍처

![PIXELTOBIN 아키](./image/PIXELTOBIN.png)
