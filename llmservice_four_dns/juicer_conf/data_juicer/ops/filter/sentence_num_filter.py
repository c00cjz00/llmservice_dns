# Some code here has been modified from:
# https://huggingface.co/spaces/huggingface/text-data-filtering
# --------------------------------------------------------

from jsonargparse.typing import ClosedUnitInterval, List
import regex

from data_juicer.utils.availability_utils import AvailabilityChecking
from data_juicer.utils.constant import Fields

from ..base_op import OPERATORS, Filter
from ..op_fusion import INTER_WORDS

OP_NAME = 'sentence_num_filter'


@OPERATORS.register_module(OP_NAME)
@INTER_WORDS.register_module(OP_NAME)
class SentenceNumilter(Filter):
    """Filter to keep samples with stopword ratio larger than a specific min
    value."""

    def __init__(self,
                 puncts: List[str] = None,
                 min_cnt: int = 5,
                 max_cnt: int = -1,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.min_cnt, self.max_cnt = min_cnt, max_cnt
        if puncts is None:
            # english and chinese punctuations
            self.pattern = regex.compile(r'[\p{P},?.]+')
        else:
            self.pattern = regex.compile(f'[{"".join(puncts)}]+')

    def compute_stats(self, sample):
        return sample

    def process(self, sample):
        num_sents = len([sent for sent in self.pattern.split(
            sample[self.text_key]) if len(sent) > 5])
        if self.min_cnt != -1 and num_sents < self.min_cnt:
            return False
        if self.max_cnt != -1 and num_sents > self.max_cnt:
            return False
        return True
