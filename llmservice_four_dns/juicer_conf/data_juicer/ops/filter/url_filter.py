from jsonargparse.typing import ClosedUnitInterval, List

from data_juicer.utils.availability_utils import AvailabilityChecking
from data_juicer.utils.constant import Fields, InterVars, StatsKeys
from data_juicer.utils.model_utils import get_model, prepare_model
import json
from ...utils.asset_utils import ASSET_DIR, load_words_asset
from ..base_op import OPERATORS, Filter
from ..common import (SPECIAL_CHARACTERS, get_words_from_document,
                      words_refinement)
from ..op_fusion import INTER_WORDS

OP_NAME = 'url_filter'


@OPERATORS.register_module(OP_NAME)
@INTER_WORDS.register_module(OP_NAME)
class UrlFilter(Filter):

    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        with open('assets/banned_url.json') as f:
            self.banned_url = json.load(f)

    def compute_stats(self, sample, context=False):
        # check if it's computed already
        if 'is_banned_url' in sample[Fields.stats]:
            return sample
        
        # compute stats
        if sample['url'] is not None:
            for ban_dom in self.banned_url:
                # if ban_dom in sample['url']:
                if ban_dom in sample['url']:
                    sample[Fields.stats]['is_banned_url'] = True
                    return sample
            sample[Fields.stats]['is_banned_url'] = False
        else:
            sample[Fields.stats]['is_banned_url'] = False

        return sample

    def process(self, sample):
        return not sample[Fields.stats]['is_banned_url']
