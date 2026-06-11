import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
import random
from itertools import islice
import pandas as pd
import os
import sys
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense
from tensorflow.keras.models import Sequential

# Get the base directory of your Conda environment
conda_base_dir = sys.exec_prefix

# Point XLA to the parent environment directory instead of \Library\bin
os.environ["XLA_FLAGS"] = f"--xla_gpu_cuda_data_dir={conda_base_dir}"

print("New XLA Pointer:", os.environ["XLA_FLAGS"])


train = pd.read_csv("http://114.207.245.181:13000/txt/ratings_train.txt", sep="\t")
test = pd.read_csv("http://114.207.245.181:13000/txt/ratings_test.txt", sep="\t")

# na인것은 삭제
train_clean = train.dropna()
test_clean = test.dropna()

train_texts = train_clean["document"].to_list()
test_texts = test_clean["document"].to_list()

train_labels = train_clean["label"].to_list()
test_labels = test_clean["label"].to_list()

s = random.randint(0, len(train_texts) - 10)
for t, l in islice(zip(train_texts, train_labels), s, s + 10):
    print(f"긍정:{l}" if l == 1 else f"부정:{l}", t)

voca_size = 20000
tokenizer = Tokenizer(num_words=voca_size, oov_token="<UNK>")
tokenizer.fit_on_texts(train_texts)


print(voca_size)
x_train = tokenizer.texts_to_sequences(train_texts)
x_test = tokenizer.texts_to_sequences(test_texts)

print(x_train[:3])

x_train_pad1 = pad_sequences(x_train, maxlen=100, padding="post")
x_test_pad1 = pad_sequences(x_test, maxlen=100, padding="post")

x_train_pad = np.array(x_train_pad1)
x_test_pad = np.array(x_test_pad1)

x_train_pad.shape, x_test_pad.shape


y_train = np.array(train_labels)
y_test = np.array(test_labels)

model = Sequential(
    [
        Input(shape=(100,)),
        # mask_zero=True => 0의 값은 패딩으로처리
        Embedding(input_dim=voca_size, output_dim=128, mask_zero=True),
        LSTM(units=64, activation="tanh"),
        Dense(units=32, activation="relu"),
        Dense(units=1, activation="sigmoid"),
    ]
)

model.summary()

model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

model.fit(
    x_train_pad, y_train, validation_data=(x_test_pad, y_test), epochs=1, verbose=2
)

sample = "이 영화 진짜 재밌다"
seq = tokenizer.texts_to_sequences([sample])
padded = pad_sequences(seq, maxlen=100, padding="post")

# 0 ~ 1
model.predect(padded)
