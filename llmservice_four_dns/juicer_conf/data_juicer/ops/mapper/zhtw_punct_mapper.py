import regex
import re
from ..base_op import OPERATORS, Mapper

halfwidth_to_fullwidth_punctuation = {
    r'(?<=\p{Han})!|!(?=\p{Han})': '！',
    r'(?<=\p{Han}),|,(?=\p{Han})': '，',
    r'(?<=\p{Han}):|:(?=\p{Han})': '：',
    r'(?<=\p{Han});|;(?=\p{Han})': '；',
    r'(?<=\p{Han})\?|\?(?=\p{Han})': '？',
    # r'(?<=\p{Han}).|.(?=\p{Han})': '。',
}

@OPERATORS.register_module('zhtw_punct_mapper')
class ZhtwPunctMapper(Mapper):
    """normalize zhtw punctuations"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # chinese characters
        
        self.patterns = halfwidth_to_fullwidth_punctuation
        
    def process(self, sample):
        for pat, rep in self.patterns.items():
            sample[self.text_key] = regex.sub(pat, rep, sample[self.text_key])
        
        return sample
