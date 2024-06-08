from datasets import load_dataset
from fire import Fire
import numpy as np
from glob import glob
import os
from concurrent.futures import ProcessPoolExecutor

def extract_result(
    jsonl: str,
    result_path: str = None,
    score_threshold: float = 0.3,
):
    print('Processing', jsonl)
    ds = load_dataset("json", data_files=jsonl, keep_in_memory=True)['train']
    
    ds = ds.filter(lambda x: x["doc_score"] > score_threshold, num_proc=2, )
    ds = ds.remove_columns(["doc_score", "should_keep", "MainTextMD5"])
    output_path = os.path.join(result_path, os.path.basename(jsonl))
    # if len(ds) > 0:
    ds.to_json(output_path, lines=True, force_ascii=False, batch_size=10000)
    print('Done', output_path)
    
def main(
    data_path: str,
    result_path: str = None,
    score_threshold: float = 0.3,
    num_proc: int = 16,
):
    jsonls = glob(f"{data_path}/*.jsonl")
    if result_path is None:
        dataset = load_dataset("json", data_files=jsonls, num_proc=32)['train']
        percent = np.arange(0, 101, 10)
        print(percent)
        print(np.percentile(dataset['doc_score'], percent))
    else:
        # for jsonl in jsonls:
            # extract_result(jsonl, result_path, score_threshold)
        with ProcessPoolExecutor(max_workers=num_proc) as executor:
            procs = []
            for jsonl in jsonls:
                procs.append(executor.submit(extract_result, jsonl, result_path, score_threshold))
            for proc in procs:
                proc.result()


if __name__ == '__main__':
    Fire(main)
