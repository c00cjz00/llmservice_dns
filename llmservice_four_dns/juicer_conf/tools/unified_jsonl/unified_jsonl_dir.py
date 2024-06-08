import datasets
import json
import os
import glob
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List
import random
from collections import Counter


def convert_col_to_text(dct: Dict[str, str]):
    keys = [k for k in dct.keys() if 'text' in k]
    if len(keys) == 0:
        return {"text": ""}
    random.shuffle(keys)
    text = random.choice(['\n', '\n\n', '\t', ' ']).join(
        [dct[k] for k in keys if isinstance(dct[k], str)])
    
    return {'text': text}


def extract_domain(src_path):
    "./xxx/yyy/train.jsonl -> yyy"
    source = src_path.strip().split('/')[-2]
    return source


def proc_one_file(path, output_dir, req_cols=['text', 'source']):
    file = path.split('/')[-1]
    source = extract_domain(path)
    to_file = os.path.join(output_dir, source, file)
    
    if os.path.exists(to_file):
        print(to_file, "exists")
        return []
    
    try:
        try:
            ds = datasets.load_dataset(
                "json", data_files=path, keep_in_memory=True)['train']
            ds = ds.remove_columns(list(set(ds.column_names) - {'text'}))
        except Exception as e:
            result = []
            with open(path) as f:
                for line in f.readlines():
                    try:
                        d = json.loads(line)
                        result.append({"text": d})
                    except Exception as e:
                        try:
                            result.append({"text": eval(line)})
                        except Exception as e:
                            pass
            ds = datasets.Dataset.from_list(result)

        col_to_remove = [k for k in ds.column_names if k not in req_cols]
        ds = ds.remove_columns(col_to_remove,)
        # convert col to text
        ds = ds.map(convert_col_to_text, num_proc=1)
        ds = ds.map(lambda x: {'source': source, 'path': path}, num_proc=1)
        # ds = ds.filter(lambda x: len(x['text']) > 10)
        
        if len(ds) > 0:
            ds.to_json(to_file, lines=True, force_ascii=False)

        # return ds

    except Exception as e:
        print(f"Error loading {path}: {e}")
        # return []
    

def main(data_path: str,
         output_dir: str,
         num_proc: int = 8,
         requrired_cols: list = ['text', 'source', 'path'],
         except_domains: list = [],
         ):
    datasets.disable_caching()
    jsonls = []
    jsonls = glob.glob(os.path.join(data_path, '**/*.json*'), recursive=True,)

    print(jsonls)

    jsonls = [j for j in jsonls if j.split('/')[-2] not in except_domains]

    with ProcessPoolExecutor(num_proc) as executor:
        dss = executor.map(proc_one_file, jsonls, [output_dir] * len(jsonls), [
                           requrired_cols] * len(jsonls))



if __name__ == '__main__':
    import fire
    fire.Fire(main)
