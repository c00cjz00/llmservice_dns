import fasttext


def train(
    train_path: str,
    test_path: str,
    ckpt_path: str,
):
    # loss='hs', dim=50,
    model = fasttext.train_supervised(input=train_path,
                                      lr=1.0,
                                      epoch=10,
                                      wordNgrams=3,
                                      bucket=100000,
                                      dim=100,
                                      loss='hs')
    print('-' * 20, 'Test', '-'*20)
    print(model.test(test_path))
    model.save_model(ckpt_path)


if __name__ == "__main__":
    from fire import Fire
    Fire(train)
