from datasets import load_dataset, config
from glob import glob
from fire import Fire
import numpy as np
from urllib.parse import urlparse
import ftfy
import datasets
import json
import os
import codecs
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import orjson


config.IN_MEMORY_MAX_SIZE = 122122547200  # 300GB
config.DEFAULT_MAX_BATCH_SIZE = 1_000_00


def filter_text(x):
    try:
        return len(x['text'].strip()) > 10
    except:
        return False


def try_load_different_encode_json(path):
    result = []

    with codecs.open(path, 'r', encoding='utf-8', errors='ignore') as f:
        err_cnt = 0
        for line in tqdm(f):
            try:
                result.append(orjson.loads(line))
            except:
                err_cnt += 1
    print(f'Error count: {err_cnt}')
    return datasets.Dataset.from_list(result)


def proc_one_file(path, output_dir, req_cols=['text', 'source', 'url', 'keywords', 'title', 'MainTextMD5', 'create_time', 'crawl_date']):
    file = path.split('/')[-2] + path.split('/')[-1]
    to_file = os.path.join(output_dir, file)

    if os.path.exists(to_file):
        print(f'{to_file} exists, skip')
        return

    ds = try_load_different_encode_json(path)

    col_to_remove = [k for k in ds.column_names if k not in req_cols]
    ds = ds.map(proc_item, num_proc=1, remove_columns=col_to_remove)
    ds = ds.filter(lambda x: len(x['text']) > 10, num_proc=1)

    if len(ds) > 0:
        ds.to_json(to_file, lines=True, force_ascii=False)

    return


def proc_item(dct: dict):
    try:
        text = dct['body'].strip()
        if text and len(text) < 10:
            desc = dct['description'].strip()
            text = desc if desc and len(desc) > 10 else ''

    except Exception as e:
        try:
            text = ftfy.fix_text(dct['text'])
        except Exception as e:
            text = ''

    try:
        url = dct['url']
        url = urlparse(url).netloc
    except:
        url = ''
        dct['url'] = ""

    if '.gov' in url:
        domain = 'gov'
    elif '.edu' in url:
        domain = 'edu'
    elif '.org' in url:
        domain = 'org'
    else:
        domain = 'com'

    try:
        dct.pop('body')
        dct.pop('description')
    except:
        pass
    # for k, v in dct.items():
    #     try:
    #         if ftfy.is_bad(v):
    #             dct[k] = ftfy.fix_text(v)
    #     except:
    #         pass

    return {'text': text, 'domain': domain}


def to_jsonl(ds, num_shards, dst_path, i):
    ds_shard = ds.shard(
        num_shards, i, keep_in_memory=True, contiguous=True)
    
    ds_shard.to_json(
        f"{dst_path}/unique_md5/shard_{i}.jsonl", lines=True, force_ascii=False)


def main(
    src_path: str,
    dst_path: str,
    num_shards: int = 20,
    num_proc: int = 4,
):
    jsons = glob(f"{src_path}/*.json*")
    jsons += glob(f"{src_path}/**/*.json*", recursive=True)
    jsons = list(set(jsons))
    print('\n'.join(jsons))

    # ds = ds.select(unique_indices.tolist())

    with ProcessPoolExecutor(num_proc) as executor:
        list(executor.map(proc_one_file, jsons, [dst_path]*len(jsons)))

    # ds = datasets.concatenate_datasets(dss)
    jsonls = glob(f"{dst_path}/**/*.json", recursive=True)
    jsonls += glob(f"{dst_path}/*.json")
    jsonls = list(set(jsonls))
    print(jsonls)

    ds = load_dataset('json', data_files=jsonls, num_proc=num_proc)['train']

    print(f'Before filter: {len(ds)} records')

    _, unique_indices = np.unique(ds['MainTextMD5'], return_index=True, axis=0)
    fl_table = np.zeros(len(ds), dtype=bool)
    fl_table[unique_indices] = True
    print(f'Unique records: {len(unique_indices)}')
    ds = ds.filter(lambda x, i: fl_table[i],
                   with_indices=True, num_proc=32)
    # ds = ds.flatten_indices(keep_in_memory=True)
    with ProcessPoolExecutor(num_proc) as executor:
        procs = [executor.submit(to_jsonl, ds, num_shards, dst_path, i) for i in range(num_shards)]
        for p in tqdm(procs, desc='Writing shards'):
            p.result()
    # for i in range(num_shards):
    #     ds_shard = ds.shard(
    #         num_shards, i, keep_in_memory=True, contiguous=True)
    #     ds_shard.to_json(
    #         f"{dst_path}/unique_md5/shard_{i}.jsonl", lines=True, force_ascii=False)
        # ds_shard.to_parquet(f"{dst_path}/unique_md5/shard_{i}.parquet", )


if __name__ == "__main__":
    Fire(main)
