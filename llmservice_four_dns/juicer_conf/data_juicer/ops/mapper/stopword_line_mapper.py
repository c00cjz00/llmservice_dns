import regex
import re
from ..base_op import OPERATORS, Mapper


@OPERATORS.register_module('stopword_line_mapper')
class StopwordLineMapper(Mapper):
    """normalize zhtw punctuations"""

    def __init__(self, on_last_k_lines: int | float=8, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stopords = [
            "瀏覽人次",
            "瀏覽次數",
            "瀏覽人數",
            "瀏覽器",
            "第一頁",
            "另開新視窗",
            "無障礙網頁",
            "qrCode",
            "發布日期",
            "更新日期",
            "如何聯絡",
            '瀏覽者',
            "版權所有",
            "電話",
            "最佳解析度",
            "瀏覽解析"
            "傳真",
            "著作權",
            "copyright",
            "另開新視窗",
            "地址",
            "到訪人次",
            "隱私權",
            "上版日期",
            "web3",
            'rights reserved'
        ]
        self.on_last_k_lines = on_last_k_lines
        
    def process(self, sample):
        lines = sample[self.text_key].split('\n')
        
        on_last_k_lines = self.on_last_k_lines if isinstance(self.on_last_k_lines, int) else int(self.on_last_k_lines * len(lines))
        
        lines = list(filter(lambda x: x.strip(), lines))
        result: list[str] = lines[:-on_last_k_lines]
        
        for line in lines[-on_last_k_lines:]:
            line = line.strip()
            fl = any([stopword in line.lower() for stopword in self.stopords])
            if not fl:
                result.append(line)
        sample[self.text_key] = '\n'.join(result)
        return sample
