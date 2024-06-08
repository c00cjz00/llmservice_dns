# Some code here has been modified from:
# https://huggingface.co/spaces/huggingface/text-data-filtering
# --------------------------------------------------------

from jsonargparse.typing import ClosedUnitInterval, List
import json

from data_juicer.utils.asset_utils import ASSET_DIR, load_words_asset
from data_juicer.utils.availability_utils import AvailabilityChecking
from data_juicer.utils.constant import Fields, InterVars, StatsKeys
from data_juicer.utils.model_utils import get_model, prepare_model

from ..base_op import OPERATORS, Filter
from ..common import (SPECIAL_CHARACTERS, get_words_from_document,
                      words_refinement)
from ..op_fusion import INTER_WORDS

OP_NAME = 'stopwords_filter_cn'

with AvailabilityChecking(['sentencepiece'], OP_NAME):
    import sentencepiece  # noqa: F401


@OPERATORS.register_module(OP_NAME)
@INTER_WORDS.register_module(OP_NAME)
class StopWordsFilterCn(Filter):
    """Filter to keep samples with stopword ratio larger than a specific min
    value."""

    def __init__(self,
                 lang: str = 'all',
                 tokenization: bool = False,
                 min_ratio: ClosedUnitInterval = 0.3,
                 min_cnt: int = 1,
                 stopwords_dir: str = ASSET_DIR,
                 use_words_aug: bool = False,
                 words_aug_group_sizes: List = [2],
                 words_aug_join_char: str = '',
                 *args,
                 **kwargs):
        """
        Initialization method.

        :param lang: Consider stopwords in what language. If lang ==
            "all", we will adopt the one merged from all the available
            languages
        :param tokenization: whether to use model to tokenize documents
        :param min_ratio: The min filter ratio in this op.
        :param stopwords_dir: The directory storing the stopwords
            file(s) whose name includes "stopwords" and in json format
        :param use_words_aug: Whether to augment words, especially for
            Chinese and Vietnamese
        :param words_aug_group_sizes: The group size of words to augment
        :param words_aug_join_char: The join char between words to
            augment
        :param args: extra args
        :param kwargs: extra args
        """
        super().__init__(*args, **kwargs)
        self.lang = lang
        self.min_ratio = min_ratio
        self.min_cnt = min_cnt
        self.use_words_aug = use_words_aug
        self.words_aug_group_sizes = words_aug_group_sizes
        self.words_aug_join_char = words_aug_join_char
        self.model_key = None
        self.lang = lang
        self.STOPWORDS = json.load(open('assets/stopwords_cn.json', 'r'))
        # self.STOPWORDS = load_words_asset(words_dir=stopwords_dir,
        #                                   words_type='stopwords')
        if 'all' not in self.STOPWORDS:
            self.STOPWORDS['all'] = [
                val for vals in self.STOPWORDS.values() for val in vals
            ]
            self.STOPWORDS['all'] = [w for w in self.STOPWORDS['all'] if w.strip() != '']
        if tokenization:
            self.model_key = prepare_model(lang=lang,
                                           model_type='sentencepiece')

    def compute_stats(self, sample, context=False):
        sample[Fields.stats]['stopwords_cnt'] = 0
        for stopword in self.STOPWORDS['all']:
            sample[Fields.stats]['stopwords_cnt'] += sample['text'].count(stopword)
            
        # sample[Fields.stats]['stopwords_cnt'] = stopwords_cnt
        # sample[Fields.stats][StatsKeys.stopwords_ratio] = stopwords_ratio
        return sample

    def process(self, sample):
        return sample[Fields.stats]['stopwords_cnt'] < self.min_cnt
    
        # return sample[Fields.stats][
        #     StatsKeys.stopwords_ratio] <= self.min_ratio and \
        #        sample[Fields.stats]['stopwords_cnt'] < self.min_cnt
