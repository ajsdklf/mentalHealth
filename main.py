import streamlit as st
from openai import OpenAI
import json

client = OpenAI()

st.set_page_config(page_title="정신 건강 챗봇", page_icon="🤖💚", layout="wide")

st.title("정신 건강 챗봇 🤖💚")

st.write("정신 건강 챗봇에 오신 것을 환영합니다. 정신 건강에 대한 고민이 있다면 물어보세요. 최선을 다해 도와드리겠습니다. 😊")

st.write("먼저, 당신에 대한 정보를 알려주세요. 📝")

if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'initial_summary' not in st.session_state:
    st.session_state.initial_summary = ""

col1, col2 = st.columns(2)

with col1:
    st.session_state.user_data['age'] = st.slider("나이 🎂", 18, 100, 25)

with col2:
    st.session_state.user_data['gender'] = st.selectbox("성별 🧑‍🤝‍🧑", ["남성", "여성", "기타", "말하고 싶지 않음"])

if st.session_state.user_data['age'] and st.session_state.user_data['gender']:
    st.session_state.user_data['emotional_state'] = st.text_input("현재 당신의 감정 상태는 어떠신가요? 😊😔😡")

    if st.session_state.user_data['emotional_state']:
        st.success("공유해 주셔서 감사합니다. 계속 진행하겠습니다. 👍")
        st.session_state.user_data['main_concern'] = st.text_area("주요 고민거리는 무엇인가요? 🤔", height=100)

        if st.session_state.user_data['main_concern']:
            st.info("이해했습니다. 더 자세히 알아보겠습니다. 🧐")
            st.session_state.user_data['stress_management'] = st.text_area("스트레스 관리 방법은 무엇인가요? 🧘‍♀️", height=100)

            if st.session_state.user_data['stress_management']:
                st.success("좋은 방법이네요! 마지막 질문입니다. 😴")
                st.session_state.user_data['sleep_quality'] = st.text_input("수면의 질은 어떠신가요? 💤")

                if st.session_state.user_data['sleep_quality']:
                    st.success("모든 정보를 제공해 주셔서 감사합니다. 이제 당신의 상태를 분석해 보겠습니다. 🗨️")

                    with st.spinner("분석 중..."):
                        # OpenAI API 호출
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "당신은 공감적이고 전문적인 정신 건강 전문가입니다. 제공된 정보를 바탕으로 사용자의 현재 상태를 요약하고, 적절한 조언을 제공해주세요. 응답은 '현재 상태 요약'과 '조언'으로 구분하여 작성해 주세요. 응답은 간결하면서도 통찰력 있게 작성해 주세요."},
                                {"role": "user", "content": json.dumps(st.session_state.user_data, ensure_ascii=False)}
                            ]
                        )

                    # API 응답 처리 및 표시
                    if response.choices:
                        st.session_state.initial_summary = response.choices[0].message.content
                        st.subheader("🧠 당신의 현재 상태 분석")
                        st.info(st.session_state.initial_summary)

                        # 사용자 데이터 JSON 형태로 표시
                        with st.expander("📊 입력하신 정보 (상세)"):
                            st.json(st.session_state.user_data)

                        # 정신 건강 상담 챗봇 기능 추가
                        st.subheader("💬 정신 건강 상담 챗봇")
                        st.write("정신 건강에 대해 더 자세히 상담하고 싶으신 점이 있다면 아래에 입력해주세요.")

                        # 채팅 기록 표시
                        for message in st.session_state.chat_history:
                            with st.chat_message(message["role"]):
                                st.markdown(message["content"])

                        # 사용자 메시지 입력란
                        user_message = st.chat_input("상담 내용을 입력하세요:")

                        if user_message:
                            # 사용자 메시지를 채팅 기록에 추가
                            st.session_state.chat_history.append({"role": "user", "content": user_message})

                            # 사용자 메시지 표시
                            with st.chat_message("user"):
                                st.markdown(user_message)

                            # 챗봇 응답 생성
                            with st.spinner("응답 생성 중..."):
                                chat_response = client.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "당신은 공감적이고 전문적인 정신 건강 상담사입니다. 사용자의 정보와 질문을 바탕으로 적절한 조언을 제공해주세요. 응답은 전문적이면서도 따뜻하고 이해하기 쉬운 말투로 작성해 주세요. 이전 대화 내용을 참고하여 일관성 있는 답변을 제공하세요."},
                                        {"role": "assistant", "content": f"사용자 정보 요약: {st.session_state.initial_summary}"},
                                        *[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history],
                                        {"role": "user", "content": user_message}
                                    ]
                                )

                            if chat_response.choices:
                                bot_response = chat_response.choices[0].message.content
                                # 챗봇 응답을 채팅 기록에 추가
                                st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
                                
                                # 챗봇 응답 표시
                                with st.chat_message("assistant"):
                                    st.markdown(bot_response)
                            else:
                                st.error("죄송합니다. 응답 생성 중 오류가 발생했습니다. 다시 시도해 주세요.")
                    else:
                        st.error("죄송합니다. 상태 분석 중 오류가 발생했습니다. 다시 시도해 주세요.")
