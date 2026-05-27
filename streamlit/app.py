import streamlit as st
import requests

st.title("손글씨 예상")

uploaded_file = st.file_uploader(
    "이미지 파일을 업로드하세요", type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="업로드된 이미지", use_container_width=True)

    if st.button("예상"):
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        try:
            response = requests.post(
                "http://localhost:8000/api/predict/number", files=files
            )
            data = response.json()
            if data.get("status") == "ok":
                st.success(f"예상 번호는 {data['pred']} 입니다")
            else:
                st.error("서비스 불가")
        except Exception as e:
            st.error(f"요청 실패: {e}")
