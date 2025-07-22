from dataclasses import dataclass
from typing import List, Dict, Union, Literal, Any, Tuple
from PIL import Image
import os
import json
from math import inf as infinity
import pickle

@dataclass
class PixelArtInput:
    image_arrays: List[Any]  # 이미지 배열 데이터
    cluster: Dict[int, List[int]]
    loop: Union[int, float] = infinity
    loopDelay: int = 0

@dataclass
class TextInput:
    text_arrays: List[Any]  # 텍스트 이미지 배열 데이터
    loop: Union[int, float] = infinity
    duration: List[int]
    action: List[Literal['left', 'right', 'up', 'down', 'stay']]

@dataclass
class MixedInput:
    image_arrays: List[Any]  # 이미지 배열 데이터
    cluster: Dict[int, List[int]]
    loop: Union[int, float] = infinity
    loopDelay: int = 0
    text_arrays: List[Any] = None  # 텍스트 이미지 배열 데이터
    duration: List[int] = None
    action: List[Literal['left', 'right', 'up', 'down', 'stay']] = None

@dataclass
class TotalFunctionInput:
    mode: Literal['pixelart', 'text', 'mixed']
    directory: str

def pixel_image_to_array(image: Image.Image, bin_path: str):
    """이미지 변환 처리"""
    # 가짜 함수, 실제 구현 필요
    return "이미지 배열 데이터"

def load_images_and_convert(image_paths: List[str], bin_path: str) -> List[Any]:
    """이미지 파일들을 로드하고 배열로 변환"""
    images = [Image.open(path) for path in image_paths]
    return [pixel_image_to_array(img, bin_path) for img in images]

def load_config(config_path: str) -> Dict:
    """설정 파일 로드"""
    if not os.path.exists(config_path):
        return {}
    
    with open(config_path, 'r') as f:
        return json.load(f)
    
def add_header(data_arrays: List[Any], mode: str) -> bytes:
    """배열 데이터에 bin 파일 헤더 추가"""
    # 헤더 형식은 실제 요구사항에 맞게 구현해야 함
    header = bytearray()
    
    # 모드 정보 추가
    header.extend(mode.encode('utf-8'))

    # TODO: 실제 헤더 정보 추가
    # 예: 버전, 크기, 타임스탬프 등
    
    # 데이터 배열 수 추가
    header.extend(len(data_arrays).to_bytes(4, byteorder='little'))
    
    return bytes(header)

def add_tailing(data: bytes) -> bytes:
    """bin 파일 테일링 추가"""
    # 테일링 정보 추가 (체크섬, 끝 표시 등)
    tailing = bytearray()
    
    # 예: 체크섬 추가
    checksum = sum(data) % 256
    tailing.extend(checksum.to_bytes(1, byteorder='little'))
    
    # 끝 표시 추가
    tailing.extend(b'END')
    
    return data + bytes(tailing)

def array_to_bin_data(arrays: List[Any]) -> bytes:
    """배열 데이터를 bin 데이터로 변환"""
    bin_data = bytearray()
    
    for array in arrays:
        # 각 배열의 크기 정보 추가
        # 실제 구현에서는 배열의 차원과 타입에 따라 달라질 수 있음
        array_bytes = pickle.dumps(array)  # 예시: pickle을 사용하여 직렬화
        bin_data.extend(len(array_bytes).to_bytes(4, byteorder='little'))
        bin_data.extend(array_bytes)
    
    return bytes(bin_data)

def process_pixelart(input_data: PixelArtInput, bin_path: str) -> str:
    """픽셀아트 모드의 입력을 처리하여 BIN 파일을 생성하는 함수"""
    # 헤더 추가
    header = add_header(input_data.image_arrays, 'pixelart')
    
    # 이미지 배열들을 bin 데이터로 변환
    bin_data = array_to_bin_data(input_data.image_arrays)
    
    # 클러스터 정보와 루프 정보를 bin 데이터에 추가
    cluster_data = pickle.dumps(input_data.cluster)
    loop_data = pickle.dumps({'loop': input_data.loop, 'loopDelay': input_data.loopDelay})
    
    # 전체 데이터 결합
    total_data = header + cluster_data + loop_data + bin_data
    
    # 테일링 추가
    final_data = add_tailing(total_data)
    
    # BIN 파일 작성
    with open(bin_path, 'wb') as f:
        f.write(final_data)
    
    return bin_path


def process_text(input_data: TextInput, bin_path: str) -> str:
    """텍스트 모드의 입력을 처리하여 BIN 파일을 생성하는 함수"""
    # 헤더 추가
    header = add_header(input_data.text_arrays, 'text')
    
    # 텍스트 이미지 배열들을 bin 데이터로 변환
    bin_data = array_to_bin_data(input_data.text_arrays)
    
    # 텍스트 설정 정보를 bin 데이터에 추가
    text_config = {
        'loop': input_data.loop,
        'duration': input_data.duration,
        'action': input_data.action
    }
    config_data = pickle.dumps(text_config)
    
    # 전체 데이터 결합
    total_data = header + config_data + bin_data
    
    # 테일링 추가
    final_data = add_tailing(total_data)
    
    # BIN 파일 작성
    with open(bin_path, 'wb') as f:
        f.write(final_data)
    
    return bin_path

def process_mixed(input_data: MixedInput, bin_path: str) -> str:
    """혼합 모드의 입력을 처리하여 BIN 파일을 생성하는 함수"""
    # 헤더 추가
    all_arrays = input_data.image_arrays + (input_data.text_arrays or [])
    header = add_header(all_arrays, 'mixed')
    
    # 이미지 배열들과 텍스트 배열들을 bin 데이터로 변환
    image_bin_data = array_to_bin_data(input_data.image_arrays)
    text_bin_data = array_to_bin_data(input_data.text_arrays) if input_data.text_arrays else b''
    
    # 혼합 설정 정보를 bin 데이터에 추가
    mixed_config = {
        'cluster': input_data.cluster,
        'loop': input_data.loop,
        'loopDelay': input_data.loopDelay,
        'duration': input_data.duration,
        'action': input_data.action
    }
    config_data = pickle.dumps(mixed_config)
    
    # 전체 데이터 결합
    total_data = header + config_data + image_bin_data + text_bin_data
    
    # 테일링 추가
    final_data = add_tailing(total_data)
    
    # BIN 파일 작성
    with open(bin_path, 'wb') as f:
        f.write(final_data)
    
    return bin_path