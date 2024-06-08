from fire import Fire
import os
from glob import glob
from datasets import Dataset, disable_caching
import codecs
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
SAVE_COLS = ['url', 'body', 'title']


def one_rdb_file(
    rdb_file: str,
    jsonl_file: str,
):
    item = {}
    last_col = ''
    result = []
    disable_caching()
    f = codecs.open(rdb_file, 'r', 'utf-8', errors='ignore')

    for line in tqdm(f):
        line = line.strip()
        if line.startswith("@Gais_REC:"):
            if all([x in item for x in SAVE_COLS]):
                result.append(item)
            item = {}
        elif line.startswith('@'):
            try:
                col_name, text = line.split(':', 1)
                col_name = col_name.strip()[1:]
                if col_name in SAVE_COLS:
                    item[col_name] = text.strip()
                last_col = col_name
            except ValueError:
                if last_col in item:
                    item[last_col] += '\n' + line
        else:
            if last_col in item:
                item[last_col] += '\n' + line
    f.close()
    
    ds = Dataset.from_list(result).rename_column('body', 'text')
    ds.to_json(jsonl_file,
               orient='records',
               lines=True,
               force_ascii=False)
    
    print('Done', rdb_file, 'to', jsonl_file)


def main(data_path: str,
         output_dir: str,
         num_proc: int = 4
         ):
    rdb_files = glob(os.path.join(data_path, 'rdb*'))
    rdb_files = list(filter(os.path.isfile, rdb_files))
    print(rdb_files)
    with ProcessPoolExecutor(num_proc) as executor:
        for rdb_file in rdb_files:
            jsonl_file = os.path.join(output_dir,
                                      os.path.basename(rdb_file) + '.jsonl')
            
            executor.submit(one_rdb_file,
                            rdb_file,
                            jsonl_file)
    
    

if __name__ == '__main__':
    Fire(main)
