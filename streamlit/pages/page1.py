import streamlit as st
import numpy as np
import joblib
from tensorflow.keras.models import load_model
import pandas as pd
import os

# 스케일러와 모델 로드하기
scaler = joblib.load("../pkl/20260529_sales_scaler.pkl")
model = load_model("../pkl/20260529_sales_model.keras")

st.title("광고 판매량 예측")

st.write("TV, 라디오, 신문광고비를 입력하면 예상 판매량을 예측합니다.")

# 입력항목
tv = st.number_input("TV 광고비", min_value=0.0, value=100.0)
radio = st.number_input("라디오 광고비", min_value=0.0, value=20.0)
newspaper = st.number_input("신문 광고비", min_value=0.0, value=10.0)


if st.button("예측하기"):

    # 1. sample 만들기(n, 3)
    sample = np.array([[tv, radio, newspaper]])

    # 2. 스케일링
    sample = scaler.transform(sample)

    # 3. 예측
    pred = model.predict(sample)

    # 4. 결과 출력
    st.success(f"예측 결과: {pred[0][0]:.2f}")
