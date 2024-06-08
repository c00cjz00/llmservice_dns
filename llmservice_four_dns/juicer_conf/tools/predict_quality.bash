#!/bin/bash
SRC_PATH=$1
TGT_DIR=$2

python tools/quality_classifier/batch_predict.py  $1 ~/.cache/qtmp_quality/  --model ckpt/regression_quality/q2 --tokenizer TLLM/llama-tokenizer-120k

python tools/fasttext/predict.py ~/.cache/qtmp_quality/ $2 ckpt/fasttext_quality_cls/model_v2.ckpt

rm -rf ~/.cache/qtmp_quality/ 