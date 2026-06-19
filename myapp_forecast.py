import streamlit as st
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime


API_KEY = "7b9a62af92d044ce8e655941262205"

st.set_page_config(
    page_title="天気予報アプリ",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Weather Dashboard")

city = st.text_input(
    "都市名を入力してください",
    key="city_input"
)

if st.button("取得"):

    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=3&aqi=yes&lang=ja"

    response = requests.get(url)
    data = response.json()

    if "error" in data:
        st.error("都市が見つかりません")

    else:

        current = data["current"]
        forecast = data["forecast"]["forecastday"]

        weather = current["condition"]["text"]
        temp = current["temp_c"]

        # ==================
        # ⑦ 背景色変更
        # ==================

        bg = "#FFFFFF"

        if "晴" in weather:
            bg = "#87CEEB"

        elif "雨" in weather:
            bg = "#808080"

        elif "曇" in weather:
            bg = "#D3D3D3"

        st.markdown(f"""
        <style>
        .stApp {{
            background-color:{bg};
        }}
        </style>
        """, unsafe_allow_html=True)

        # ==================
        # ⑭ タブUI
        # ==================

        tab1, tab2, tab3, tab4= st.tabs([
            "🌤️ 現在天気",
            "📅 予報",
            "📈 時間別",
            "🌡️ 過去7日 気温ヒートマップ"
        ])

        # -------------------
        # 現在天気
        # -------------------

        with tab1:

            icon = current["condition"]["icon"]

            st.image(
                "https:" + icon,
                width=120
            )

            st.subheader(weather)

            c1,c2,c3 = st.columns(3)

            c1.metric("🌡️ 気温",f"{temp}℃")

            c2.metric(
                "💧 湿度",
                f"{current['humidity']}%"
            )

            c3.metric(
                "🍃 風速",
                f"{current['wind_kph']} km/h"
            )

        # -------------------
        # 予報
        # -------------------

        with tab2:

            cols = st.columns(3)

            for i,day in enumerate(forecast):

                with cols[i]:

                    st.write(day["date"])

                    st.image(
                        "https:" +
                        day["day"]["condition"]["icon"]
                    )

                    st.write(
                        day["day"]["condition"]["text"]
                    )

                    st.write(
                        f"⬆️ {day['day']['maxtemp_c']}℃"
                    )

                    st.write(
                        f"⬇️ {day['day']['mintemp_c']}℃"
                    )

        # -------------------
        # 時間別＋②傘通知
        # -------------------

        with tab3:

            hour_data = forecast[0]["hour"]

            temps = []

            times = []

            st.subheader("☔ 傘通知")

            rain_found = False

            for hour in hour_data:

                chance = hour["chance_of_rain"]

                if chance >= 70:

                    rain_found = True

                    st.warning(
                        f"{hour['time'][11:16]} "
                        f"雨確率 {chance}% "
                        "→ 傘推奨"
                    )

                temps.append(hour["temp_c"])

                times.append(
                    hour["time"][11:16]
                )

            if not rain_found:
                st.success("今日は大きな降雨予報なし")

            df = pd.DataFrame({
                "時間":times,
                "気温":temps
            })

            st.line_chart(
                df.set_index("時間")
            )
        with tab4:

            st.subheader("🌡️ 過去7日 気温ヒートマップ")

            today = datetime.date.today()

            all_data = []

            for i in range(7):

                date = today - datetime.timedelta(days=i)

                history_url = (
                    f"http://api.weatherapi.com/v1/history.json"
                 f"?key={API_KEY}"
                    f"&q={city}"
                    f"&dt={date}"
                )

                history_response = requests.get(history_url)

                history_data = history_response.json()

                # デバッグ確認
                st.write(f"取得日: {date}")

                if "error" in history_data:

                    st.error(history_data["error"]["message"])

                    continue

                hours = history_data["forecast"]["forecastday"][0]["hour"]

                row = {}

                row["日付"] = str(date)

                for h in hours:

                    hour = h["time"][11:13]

                    row[hour+"時"] = h["temp_c"]

                all_data.append(row)

            # デバッグ
            st.write(all_data)

            if len(all_data)==0:

                st.error("過去データ取得失敗")

                st.stop()

            df = pd.DataFrame(all_data)

            st.write(df.columns)

            df = df.set_index("日付")

            fig, ax = plt.subplots(figsize=(14,5))

            sns.heatmap(
                df,
                annot=True,
                cmap="coolwarm",
                ax=ax
            )

            st.pyplot(fig)