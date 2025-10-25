import streamlit as st
from openai import OpenAI
import json

# ✅ Streamlit Secrets에서 API 키 불러오기
client = OpenAI(api_key=st.secrets["openai_api_key"])

st.title("🏫 학교 방문 일지 자동요약기")
st.write("학교 방문 일지(JSON 파일)을 업로드하면 자동으로 요약해줍니다.")

uploaded_file = st.file_uploader("JSON 파일 업로드 (.json)", type=["json"])

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        st.subheader("📄 업로드된 원본 내용")
        st.json(data)

        # JSON을 문자열로 변환해서 프롬프트에 넣기
        content_str = json.dumps(data, ensure_ascii=False, indent=2)

        st.subheader("🧠 요약 생성 중...")
        with st.spinner("요약 중입니다..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 학교 방문일지를 요약하는 교사 비서야."},
                    {
                        "role": "user",
                        "content": f"다음은 학교 방문 기록이야. 핵심 내용만 간결하게 요약해줘:\n\n{content_str}"
                    }
                ],
                temperature=0.4,
            )

            summary = response.choices[0].message.content.strip()
            st.success("✅ 요약 완료!")
            st.subheader("📝 요약 결과")
            st.write(summary)

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
