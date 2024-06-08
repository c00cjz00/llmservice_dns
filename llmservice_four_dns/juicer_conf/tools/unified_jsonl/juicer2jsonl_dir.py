from datasets import load_dataset, Dataset
from fire import Fire
from glob import glob
from tqdm import tqdm
import os
from concurrent.futures import ProcessPoolExecutor

def group_by(d, col):
    """from: https://github.com/huggingface/datasets/issues/3644"""
    # Get the indices of each group
    groups = {key: [] for key in d.unique(col)}

    def create_groups_indices(key, i):
        groups[key].append(i)

    d.map(create_groups_indices, with_indices=True, input_columns=col)
    # Get one dataset object per group
    for k, v in groups.items():
        yield k, d.select(v)


def to_jsonl(f: str, output_dir: str, col: str):
    ds = load_dataset('json', data_files=f, split='train')
    grp_by_iter = group_by(ds, col)
    
    for src, d in grp_by_iter:
        out_file = os.path.join(output_dir, src, os.path.basename(f))
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        d.to_json(out_file, orient='records', lines=True, force_ascii=False)


def main(
    juicer_dir: str,
    output_dir: str,
    col_as_dir: str = 'source',
    num_workers: int = 32,
):
    files = glob(juicer_dir + '/*.jsonl')
    files = [f for f in files if 'stats.jsonl' not in f]
    
    procs  = []
    with ProcessPoolExecutor(num_workers) as executor:
        for f in tqdm(files):
            procs += [executor.submit(to_jsonl, f, output_dir, col_as_dir)]
        
        for p in tqdm(procs):
            p.result()
    # ds = load_dataset('json', data_files=juicer_dir)['train']

    # for src, d in group_by(ds, col_as_dir):
    #     print(src)
    #     to_jsonl(d, output_dir, src)


if __name__ == '__main__':
    Fire(main)
