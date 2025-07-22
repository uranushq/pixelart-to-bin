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

def process_pixelart(bin_path: str, image_paths: List[str], config: Dict) -> PixelArtInput:
    """픽셀아트 모드의 입력을 처리하는 함수"""
    # 이미지를 배열로 변환
    image_arrays = load_images_and_convert(image_paths, bin_path)
    
    # 클러스터 정보 가져오기
    cluster = config.get('cluster', {})
    loop = config.get('loop', infinity)
    loop_delay = config.get('loopDelay', 0)
    
    return PixelArtInput(
        image_arrays=image_arrays, 
        cluster=cluster,
        loop=loop,
        loopDelay=loop_delay
    )

def process_text(bin_path: str, text_paths: List[str], config: Dict) -> TextInput:
    """텍스트 모드의 입력을 처리하는 함수"""
    # 텍스트 이미지를 배열로 변환
    text_arrays = load_images_and_convert(text_paths, bin_path)
    
    # 설정 가져오기
    loop = config.get('loop', infinity)
    duration = config.get('duration', [1000] * len(text_arrays))
    action = config.get('action', ['stay'] * len(text_arrays))
    
    return TextInput(
        text_arrays=text_arrays,
        loop=loop,
        duration=duration,
        action=action
    )

def process_mixed(bin_path: str, image_paths: List[str], text_paths: List[str], config: Dict) -> MixedInput:
    """혼합 모드의 입력을 처리하는 함수"""
    # 이미지와 텍스트 이미지를 배열로 변환
    image_arrays = load_images_and_convert(image_paths, bin_path)
    text_arrays = load_images_and_convert(text_paths, bin_path) if text_paths else None
    
    # 설정 가져오기
    cluster = config.get('cluster', {})
    loop = config.get('loop', infinity)
    loop_delay = config.get('loopDelay', 0)
    
    duration = None
    action = None
    if text_arrays:
        duration = config.get('duration', [1000] * len(text_arrays))
        action = config.get('action', ['stay'] * len(text_arrays))
    
    return MixedInput(
        image_arrays=image_arrays,
        cluster=cluster,
        loop=loop,
        loopDelay=loop_delay,
        text_arrays=text_arrays,
        duration=duration,
        action=action
    )

def add_header(data_arrays: List[Any], mode: str, metadata: Dict = None) -> bytes:
    """배열 데이터에 bin 파일 헤더 추가"""
    # 헤더 형식은 실제 요구사항에 맞게 구현해야 함
    header = bytearray()
    
    # 모드 정보 추가
    header.extend(mode.encode('utf-8'))
    
    # 메타데이터 추가 (클러스터, 루프 등)
    if metadata:
        metadata_bytes = json.dumps(metadata).encode('utf-8')
        header.extend(len(metadata_bytes).to_bytes(4, byteorder='little'))
        header.extend(metadata_bytes)
    else:
        header.extend((0).to_bytes(4, byteorder='little'))
    
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

def generate_bin_file(input_data, output_path: str):
    """입력 데이터를 기반으로 bin 파일을 생성하는 함수"""
    try:
        if isinstance(input_data, PixelArtInput):
            print("픽셀아트 모드로 bin 파일 생성")
            
            # 메타데이터 구성
            metadata = {
                'cluster': input_data.cluster,
                'loop': input_data.loop if input_data.loop != infinity else -1,
                'loopDelay': input_data.loopDelay
            }
            
            # 헤더 추가
            bin_content = add_header(input_data.image_arrays, 'pixelart', metadata)
            
            # 배열 데이터 추가
            bin_content += array_to_bin_data(input_data.image_arrays)
            
        elif isinstance(input_data, TextInput):
            print("텍스트 모드로 bin 파일 생성")
            
            # 메타데이터 구성
            metadata = {
                'loop': input_data.loop if input_data.loop != infinity else -1,
                'duration': input_data.duration,
                'action': input_data.action
            }
            
            # 헤더 추가
            bin_content = add_header(input_data.text_arrays, 'text', metadata)
            
            # 배열 데이터 추가
            bin_content += array_to_bin_data(input_data.text_arrays)
            
        elif isinstance(input_data, MixedInput):
            print("혼합 모드로 bin 파일 생성")
            
            # 메타데이터 구성
            metadata = {
                'cluster': input_data.cluster,
                'loop': input_data.loop if input_data.loop != infinity else -1,
                'loopDelay': input_data.loopDelay
            }
            
            if input_data.text_arrays:
                metadata.update({
                    'duration': input_data.duration,
                    'action': input_data.action
                })
            
            # 모든 배열 합치기
            all_arrays = input_data.image_arrays.copy()
            if input_data.text_arrays:
                all_arrays.extend(input_data.text_arrays)
            
            # 헤더 추가
            bin_content = add_header(all_arrays, 'mixed', metadata)
            
            # 배열 데이터 추가
            bin_content += array_to_bin_data(all_arrays)
            
        else:
            raise ValueError("지원하지 않는 입력 타입입니다.")
        
        # 테일링 추가
        bin_content = add_tailing(bin_content)
        
        # bin 파일로 저장
        with open(output_path, 'wb') as f:
            f.write(bin_content)
        
        print(f"bin 파일 생성 완료: {output_path}")
        return True
        
    except Exception as e:
        print(f"bin 파일 생성 실패: {str(e)}")
        return False

def get_file_paths(directory: str) -> Tuple[List[str], List[str], Dict]:
    """디렉토리에서 이미지 파일과 텍스트 파일 경로, 설정 가져오기"""
    # 이 함수는 추상적인 설계를 위한 것으로, 실제 구현은 달라질 수 있음
    image_paths = []  # 일반 이미지 파일 경로 목록
    text_paths = []   # 텍스트 이미지 파일 경로 목록
    config = {}       # 설정 정보
    
    # 실제 구현에서는 파일 시스템에서 파일을 찾고 분류하는 코드가 필요
    
    return image_paths, text_paths, config

def TotalFunction(mode: Literal['pixelart', 'text', 'mixed'], directory: str):
    """주어진 디렉토리의 모든 bin 폴더에 대해 bin 파일을 생성하는 메인 함수"""
    # 디렉토리 내의 모든 bin 폴더와 출력 경로 목록 가져오기
    bin_folders = []  # 실제 구현에서는 디렉토리에서 bin 폴더 목록을 가져옴
    
    for bin_path in bin_folders:
        output_path = f"{bin_path}.bin"  # bin 파일 출력 경로
        
        try:
            # 파일 경로와 설정 가져오기
            image_paths, text_paths, config = get_file_paths(bin_path)
            
            # 모드에 따라 적절한 처리 함수 호출
            if mode == 'pixelart':
                input_data = process_pixelart(bin_path, image_paths, config)
            elif mode == 'text':
                input_data = process_text(bin_path, text_paths, config)
            elif mode == 'mixed':
                input_data = process_mixed(bin_path, image_paths, text_paths, config)
            else:
                raise ValueError(f"지원하지 않는 모드입니다: {mode}")
            
            # bin 파일 생성
            generate_bin_file(input_data, output_path)
            print(f"성공적으로 처리됨: {bin_path}")
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    # 예시 사용법
    input_data = TotalFunctionInput(mode='pixelart', directory='bins_directory')
    TotalFunction(input_data.mode, input_data.directory)