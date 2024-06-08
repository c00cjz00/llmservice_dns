import regex as re

from ..base_op import OPERATORS, Mapper


@OPERATORS.register_module('ptt_mark_mapper')
class PttMarkMapper(Mapper):
    """Mapper to process ptt footnote and cite in text samples."""

    def __init__(self, *args, **kwargs):
        """
        Initialization method.

        :param pattern: regular expression pattern to search for within text.
        :param args: extra args
        :param kwargs: extra args
        """
        super().__init__(*args, **kwargs)
        self.bos_pattern = [ '--', '※ ', ': ', ' Sent from ', 'sent from ']
        
    def process(self, sample):
        for pat in self.bos_pattern:
            text = sample[self.text_key].split('\n')
            text = filter(lambda x: not x.strip().startswith(pat), text)
            sample[self.text_key] = '\n'.join(text)
                
        return sample
