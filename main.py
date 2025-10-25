import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import face_recognition
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="학교 방문자 사전예약 시스템", page_icon="🏫", layout="wide")

# -----------------------------
# Google Sheets 연결
# -----------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open("방문자예약시트").sheet1  # 시트명 변경 가능

# -----------------------------
# Streamlit 메뉴 구성
# -----------------------------
menu = st.sidebar.radio("메뉴 선택", ["📝 사전 방문 예약", "✅ 출입 인증"])

# -----------------------------
# 1️⃣ 사전 방문 예약 페이지
# -----------------------------
if menu == "📝 사전 방문 예약":
    st.header("📝 학교 방문자 사전 예약")
    st.write("방문 전 반드시 아래 정보를 입력해 주세요.")
    
    with st.form("visitor_form"):
        name = st.text_input("이름")
        ssn = st.text_input("주민번호 앞 6자리", max_chars=6)
        purpose = st.text_input("방문 목적")
        car_num = st.text_input("차량번호 (선택)")
        photo = st.file_uploader("얼굴 사진 업로드", type=["jpg", "jpeg", "png"])
        submitted = st.form_submit_button("제출하기")
        
        if submitted:
            if not (name and ssn and purpose and photo):
                st.error("이름, 주민번호, 방문목적, 사진은 필수 입력입니다.")
            else:
                image = Image.open(photo)
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="PNG")
                img_base64 = img_bytes.getvalue()
                
                # 시트에 데이터 추가
                sheet.append_row([name, ssn, purpose, car_num, str(list(img_base64))])
                st.success("✅ 사전 예약이 완료되었습니다!")

# -----------------------------
# 2️⃣ 출입 인증 페이지
# -----------------------------
elif menu == "✅ 출입 인증":
    st.header("✅ 방문자 출입 인증")
    st.write("등록된 얼굴 사진과 일치하는지 확인합니다.")
    
    visitor_name = st.text_input("방문자 이름 입력")
    capture = st.camera_input("얼굴을 카메라로 촬영하세요")
    
    if capture and visitor_name:
        # DB에서 해당 이름의 사진 데이터 가져오기
        records = sheet.get_all_records()
        matched_row = next((r for r in records if r["이름"] == visitor_name), None)
        
        if not matched_row:
            st.error("해당 이름으로 예약된 방문자가 없습니다.")
        else:
            try:
                stored_img_data = eval(matched_row["얼굴사진"])  # 문자열 → 바이트 배열
                stored_img = Image.open(io.BytesIO(bytearray(stored_img_data)))
                
                # 얼굴 인코딩
                known_encoding = face_recognition.face_encodings(np.array(stored_img))[0]
                uploaded_img = Image.open(capture)
                uploaded_encoding = face_recognition.face_encodings(np.array(uploaded_img))[0]
                
                result = face_recognition.compare_faces([known_encoding], uploaded_encoding)[0]
                
                if result:
                    st.success("✅ 얼굴 인식 성공! 출입이 허용되었습니다.")
                else:
                    st.error("❌ 얼굴이 일치하지 않습니다. 출입 불가.")
            except Exception as e:
                st.error(f"얼굴 인식 중 오류 발생: {e}")
