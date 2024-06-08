# Most of the code here has been modified from:
# https://github.com/bigscience-workshop/data-preparation
# --------------------------------------------------------

from ..base_op import OPERATORS, Mapper
from ..common.special_characters import VARIOUS_WHITESPACES


@OPERATORS.register_module('text_concat_mapper')
class TextConcatMapper(Mapper):
    def __init__(self, *args, **kwargs):
        """
        Initialization method.

        :param args: extra args
        :param kwargs: extra args
        """
        super().__init__(*args, **kwargs)

    def process(self, sample):
        if isinstance(sample[self.text_key], list):
            sample[self.text_key] = '\n'.join(sample[self.text_key])
        
        return sample
