from typing import List, Tuple, Union

from ..base_op import OPERATORS, Filter


@OPERATORS.register_module('non_text_filter')
class NonTextFilter(Filter):
    """
    Filter non text_textkey columns
    """

    def __init__(self,
                 *args,
                 **kwargs):
        """
        Initialization method.

        :param field_key: Filter based on the specified value
            corresponding to the target key. The target key
            corresponding to multi-level field information need to be
            separated by '.'.
        :param target_value: The range of specified field information
            corresponding to the samples that need to be retained.
        :param args: extra args
        :param kwargs: extra args
        """
        super().__init__(*args, **kwargs)
    def compute_stats(self, sample):
        return sample

    def process(self, sample):
        if not isinstance(sample['text'], str):
            return False
        return True
