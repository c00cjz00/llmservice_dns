# FastText Quality Classifier

以 FastText 的模型，將文章分類為高品質或低品質。

## Requirements
根據 repo 安裝 fasttext: https://github.com/facebookresearch/fastText


## Usage

### 準備訓練資料
```bash
 python tools/fasttext/prepare_cls_dataset.py <positive jsonl dir> <negeditive jsonl dir> $output_dir
```

### 訓練模型
```bash
python tools/fasttext/train_quality_cls.py $output_dir/train.txt $output_dir/test.txt $ckpt_output_dir
```

### 區分資料

* 高品質資料會在: `$output_dir/pos.jsonl`
* 低品質資料會在: `$output_dir/neg.jsonl`

```bash
 python tools/fasttext/predict.py <dir containing .jsonl to predict> $ckpt_output_dir
```
