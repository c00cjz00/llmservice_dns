# 將 *.rdb 轉換成 jsonl

* GaisDB .rdb 轉換成 jsonl

## How to use

```bash
python tools/rdb/rdb2jsonl.py <data dir to rdb file> <dest dir> <num process>
```

for example:

```bash
python tools/rdb/rdb2jsonl.py ~/data/raw_data/gov/rdb ~/data/raw_data/gov/jsonl 4 
```