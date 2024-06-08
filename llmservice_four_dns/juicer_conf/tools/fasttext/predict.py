import fasttext
from datasets import load_dataset, disable_caching
from transformers import AutoTokenizer
from glob import glob
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import os


def predict(
    data_path: str,
    output_path: str,
    ckpt_path: str,
):
    disable_caching()

    def predict_score(
        dct: dict,
    ):
        text = ' '.join(TOK.tokenize(dct['text'].replace('\n', '<n>')))
        pred = MODEL.predict(text, k=1)
        label = pred[0][0].replace('__label__', '')
        score = pred[1][0] if label == '1' else 1 - pred[1][0]
        return {'__fasttext_score': round(score, 2)}
    output_path = os.path.join(output_path, os.path.basename(
        data_path))
    print('ouput_path', output_path)
    TOK = AutoTokenizer.from_pretrained('TLLM/llama-tokenizer-120k')
    MODEL = fasttext.FastText.load_model(ckpt_path)
    print(MODEL.predict('hello world', k=1))
    ds = load_dataset('json', data_files=data_path, num_proc=1)['train']
    ds = ds.map(predict_score, num_proc=1)
    ds.to_json(output_path, lines=True, force_ascii=False)


def main(
    data_path: str,
    output_path: str,
    ckpt_path: str,
    num_proc: int = 8,
):
    jsonls = glob(f"{data_path}/*.jsonl")
    jsonls += glob(f"{data_path}/*.json")
    print(jsonls)
    os.makedirs(output_path, exist_ok=True)
    with ProcessPoolExecutor(max_workers=num_proc) as executor:
        for jsonl in tqdm(jsonls):
            executor.submit(predict, jsonl, output_path, ckpt_path)


if __name__ == "__main__":
    from fire import Fire
    Fire(main)
