import random
from ..base_op import OPERATORS, Mapper

OP_NAME = 'html_tag_mapper'
DEFAULT_TAGS_MAP = {
    "<h1>": "# ",
    "</h1>": "",
    "<h2>": "## ",
    "</h2>": "",
    "<h3>": "### ",
    "</h3>": "",
    "<h4>": "#### ",
    "</h4>": "",
    "<h5>": "##### ",
    "</h5>": "",
    "<li>": ["* ", "+ ", "- "],
    "</li>": "",
    "<ul>": "",
    "</ul>": "",
    "<ol>": "",
    "</ol>": "",
    "<b>": "**",
    "</b>": "**",
    "<strong>": "**",
    "</strong>": "**",
    "<i>": "*",
    "</i>": "*",
}


@OPERATORS.register_module(OP_NAME)
class HtmlTagMapper(Mapper):
    def __init__(self, tags_map: dict = DEFAULT_TAGS_MAP, prob: float = 0.7, *args, **kwargs):
        """
        :param args: extra args
        :param kwargs: extra args
        """
        super().__init__(*args, **kwargs)
        self.tags_map = tags_map
        self.prob = prob

    def process(self, sample):
        for tag, replacement in self.tags_map.items():
            if isinstance(replacement, list):
                replacement = random.choice(replacement)

            sample[self.text_key] = sample[self.text_key].replace(
                tag, replacement)

        return sample
