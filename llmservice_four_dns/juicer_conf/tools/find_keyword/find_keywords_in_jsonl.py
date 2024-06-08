from datasets import load_dataset, disable_caching
from fire import Fire
import os
from concurrent.futures import ProcessPoolExecutor
from glob import glob

disable_caching()

# def has_keyword(dct: dict, keywords: set[str]):
#     text_kws = set(dct['text'])
#     return len(text_kws & keywords) >= 5


def has_keyword(dct: dict, keywords: set[str]):
    cnt = 0
    for kw in keywords:
        cnt += bool(dct['keywords'].count(kw))
    return cnt >= 2

def process_one_file(
    file_path: str,
    keyword_set: set[str],
    output_path: str,
    num_proc=4
):
    ds = load_dataset('json', data_files=file_path)['train']
    ds = ds.filter(has_keyword, fn_kwargs={'keywords': keyword_set}, num_proc=num_proc)
    output_path = os.path.join(output_path, os.path.basename(file_path))
    ds.to_json(
        output_path,
        orient='records',
        lines=True,
        force_ascii=False,
    )

def main(
    data_path: str,
    output_path: str=None,
    keyword_file: str='keywords.txt',
):
    keywords = set()
    
    with open(keyword_file, 'r') as f:
        for line in f:
            keywords.add(line.strip())
    if data_path.endswith('.jsonl'):
        jsonls = [data_path]
    else:
        jsonls = glob(os.path.join(data_path, '*.jsonl'))
        jsonls += glob(os.path.join(data_path, '*.json'))
        jsonls = list(set(jsonls))
    
    with ProcessPoolExecutor(4) as executor:
        executor.map(
            process_one_file,
            jsonls,
            [keywords] * len(jsonls),
            [output_path] * len(jsonls),
        )


if __name__ == '__main__':
    Fire(main)
