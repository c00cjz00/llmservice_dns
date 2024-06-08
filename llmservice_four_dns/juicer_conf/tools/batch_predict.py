from fire import Fire
from glob import glob
from tqdm import tqdm
import datasets

import shutil
import os
from tools.quality_classifier.qc_utils import (export_result, init_spark,
                                               load_dataset, predict,
                                               prepare_model)


def batch_predict(dataset_path, result_path, model='gpt3', tokenizer=None, keep_method='gpt3', text_key='text', overall_stats=False, num_proc=32):
    
    # set default tokenizers for default models
    if model == 'chinese':
        tokenizer = 'zh.sp.model'
        keep_method = 'label'
    if model == 'code':
        tokenizer = 'code.sp.model'
        keep_method = 'label'
    if model == 'gpt3':
        tokenizer = None
        keep_method = 'gpt3'

    # initialize a spark session
    if '_JAVA_OPTIONS' in os.environ and \
            '-Djava.net.preferIPv6Addresses=true' \
            in os.environ['_JAVA_OPTIONS']:
        os.environ['_JAVA_OPTIONS'] = os.environ['_JAVA_OPTIONS'].replace(
            '-Djava.net.preferIPv6Addresses=true',
            '-Djava.net.preferIPv6Addresses=false')
    spark = init_spark()
    model = prepare_model(model_name=model)
    
    jsons = glob(f"{dataset_path}/*.jsonl")
    datasets.disable_caching()
    for json in tqdm(jsons):
        tmp_path = json.replace(dataset_path, result_path + '/tmp.')
        output_path = json.replace(dataset_path, result_path + '/')
        
        print("tmp_path", tmp_path)
        print("output_path", output_path)
        
        try:
            ds = load_dataset(spark, json, text_key=text_key)
            pred = predict(model, ds, tokenizer=tokenizer, keep_method=keep_method)
            export_result(pred, tmp_path)
        
            ds = datasets.load_dataset('json',
                            data_files=glob(f'{tmp_path}/*.json'),
                            num_proc=num_proc)['train']
            ds.to_json(output_path, lines=True, force_ascii=False)
            shutil.rmtree(tmp_path, ignore_errors=True)
        except Exception as e:
            print(e)
            print(f"Failed to process {json}")
            shutil.rmtree(tmp_path, ignore_errors=True)
            continue

if __name__ == "__main__":
    Fire(batch_predict)
