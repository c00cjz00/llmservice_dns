import regex as re

from ..base_op import OPERATORS, Mapper


def remove_short_lines(text: str, min_line_length=2, consecutive_lines=5):
    lines = text.split('\n')
    new_lines, tmp_line = [], []

    consecutive_count = 0
    for line in lines:
        line = line.strip()

        if len(line) < min_line_length:
            consecutive_count += 1
            if consecutive_count >= consecutive_lines:
                tmp_line = []
                consecutive_count = 0
        else:
            consecutive_count = 0
            for l in tmp_line:
                new_lines.append(l)
            tmp_line = []
            new_lines.append(line)

    return '\n'.join(new_lines)


CHINESE_PUNCS = """，。、：；「」（）【】？?!,！."""


def remove_no_puncs(text: str, consecutive_lines=5):

    lines = text.split('\n')
    new_lines, tmp_line = [], []

    consecutive_count = 0
    for line in lines:
        line = line.strip()

        if not any([c in line for c in CHINESE_PUNCS]):
            consecutive_count += 1
            if consecutive_count >= consecutive_lines:
                tmp_line = []
                consecutive_count = 0
        else:
            consecutive_count = 0
            for l in tmp_line:
                new_lines.append(l)
            tmp_line = []
            new_lines.append(line)

    return '\n'.join(new_lines)


@OPERATORS.register_module('consecutive_short_line_mapper')
class ConsecutiveShortLineMapper(Mapper):
    """Mapper to ConsecutiveShortLineMapper"""

    def __init__(self,
                 min_line_length: int = 10,
                 consecutive_lines: int = 5,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_line_length = min_line_length
        self.consecutive_lines = consecutive_lines

    def process(self, sample):
        sample[self.text_key] = remove_short_lines(
            sample[self.text_key], self.min_line_length, self.consecutive_lines)
        sample[self.text_key] = remove_no_puncs(
            sample[self.text_key], self.consecutive_lines)
        return sample
