import regex as re

from ..base_op import OPERATORS, Mapper


@OPERATORS.register_module('ptt_newline_mapper')
class PttNewlineMapper(Mapper):
    """Mapper to process ptt newline in text samples."""

    def __init__(self, repl: str = '', *args, **kwargs):
        """
        Initialization method.

        :param pattern: regular expression pattern to search for within text.
        :param repl: replacement string, default is empty string.
        :param args: extra args
        :param kwargs: extra args
        """
        super().__init__(*args, **kwargs)
        self.pattern = re.compile(r'(?<=\p{Han})\n+(?=\p{Han})')
        
        self.repl = repl
        
    def process(self, sample):
        sample[self.text_key] = self.pattern.sub(self.repl, sample[self.text_key])
        return sample
