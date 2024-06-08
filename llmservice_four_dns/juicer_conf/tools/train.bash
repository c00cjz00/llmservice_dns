python train.py \
    /home/u3844240/data/train_data/quality_cls/gpt/pos.jsonl \
   /home/u3844240/data/train_data/quality_cls/gpt/neg.jsonl \
    --output_model_path ckpt/q2 \
    --train_test_split_ratio 0.95 \
    --tokenizer TLLM/llama-tokenizer-120k \
    --text_key text
