from datasets import load_dataset, concatenate_datasets, Dataset
from glob import glob
import os
import json
from concurrent.futures import ProcessPoolExecutor
from transformers import AutoTokenizer
from itertools import chain
from tqdm import tqdm


def load_jsonl(
    path: str,
):
    with open(path, 'r') as f:
        data = [{'text': json.loads(line)['text'].replace(
            '\n', '<n>')} for line in tqdm(f)]
    return data


def tokenize(
    dct: dict,
    tokenizer: AutoTokenizer
):
    dct['text'] = ' '.join(tokenizer.tokenize(dct['text']))
    return dct


def prepaare(
    pos_data_path: str,
    neg_data_path: str,
    output_path: str,
):
    if pos_data_path.endswith('.jsonl'):
        pos_data_path = [pos_data_path]
        neg_data_path = [neg_data_path]
    else:
        pos_data_path = glob(os.path.join(pos_data_path, '*.jsonl'))
        neg_data_path = glob(os.path.join(neg_data_path, '*.jsonl'))

    with ProcessPoolExecutor(4) as executor:
        ds_pos = executor.map(load_jsonl, pos_data_path)
        ds_pos = sum(ds_pos, [])
        ds_pos = Dataset.from_list(ds_pos)
        ds_neg = executor.map(load_jsonl, neg_data_path)
        ds_neg = sum(ds_neg, [])
        ds_neg = Dataset.from_list(ds_neg)

    ds_pos = ds_pos.add_column('label', ['__label__1'] * len(ds_pos))
    ds_neg = ds_neg.add_column('label', ['__label__0'] * len(ds_neg))

    ds = concatenate_datasets([ds_pos, ds_neg])
    ds = ds.map(tokenize, num_proc=32, fn_kwargs={
                'tokenizer': AutoTokenizer.from_pretrained('TLLM/llama-tokenizer-120k')})

    ds = ds.shuffle(seed=52)
    ds = ds.train_test_split(test_size=0.1, seed=42, shuffle=True)

    # ds['train'].to_csv(output_path + '/train.csv', header=None, index=False, escapechar='\\', quoting=1,)
    # ds['test'].to_csv(output_path + '/test.csv', header=None, index=False, escapechar='\\', quoting=1, )

    with open(output_path + '/train.txt', 'w') as f:
        for d in ds['train']:
            f.write(str(d['label']) + ' ' + d['text'] + '\n')
    with open(output_path + '/test.txt', 'w') as f:
        for d in ds['test']:
            f.write(str(d['label']) + ' ' + d['text'] + '\n')


if __name__ == "__main__":
    from fire import Fire
    Fire(prepaare)
