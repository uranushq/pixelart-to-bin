from dataclasses import dataclass
from typing import List, Dict, Union, Literal, Any, Tuple
from math import inf

@dataclass
class PixelArtInput:
    image_arrays: List[Any]
    cluster: Dict[int, List[int]]
    loop: Union[int, float] = inf
    loopDelay: int = 0

@dataclass
class TextInput:
    text_arrays: List[Any]
    loop: Union[int, float] = inf
    duration: List[int]
    action: List[Literal['left', 'right', 'up', 'down', 'stay']]
    loopDelay: int = 0

@dataclass
class MixedInput:
    image_arrays: List[Any]
    cluster: Dict[int, List[int]]
    loop: Union[int, float] = inf
    loopDelay: int = 0
    text_arrays: List[Any] = None
    duration: List[int] = None
    action: List[Literal['left', 'right', 'up', 'down', 'stay']] = None

@dataclass
class TotalFunctionInput:
    mode: Literal['pixelart', 'text', 'mixed']
    directory: str