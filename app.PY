import streamlit as st
import pandas as pd
from io import BytesIO

def process_file(file, min_average):
    # قراءة ملف الاكسل
    df = pd.read_excel(file)

    # التحقق من الشروط (إذا كانت إحدى القيم تساوي صفرًا بينما القيمتين الأخريين أو أحدهما أكبر من صفر)
    anomaly = df[
        ((df['A1'] == 0) & ((df['A2'] > 0) | (df['A3'] > 0))) |
        ((df['A2'] == 0) & ((df['A1'] > 0) | (df['A3'] > 0))) |
        ((df['A3'] == 0) & ((df['A1'] > 0) | (df['A2'] > 0)))
    ]

    # حساب متوسط القيم A1, A2, A3
    anomaly['متوسط'] = anomaly[['A1', 'A2', 'A3']].mean(axis=1)

    # تطبيق الفلتر: عرض الحالات التي يكون فيها المتوسط أعلى من الحد الأدنى المحدد
    anomaly = anomaly[anomaly['متوسط'] >= min_average]

    # ترتيب الحالات بناءً على قيمة المتوسط من الأكبر إلى الأصغر
    anomaly = anomaly.sort_values(by='متوسط', ascending=False)

    # حساب عدد الحالات المكتشفة
    num_cases = len(anomaly)

    return anomaly, num_cases

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

st.title("تحليل أحمال العدادات لاكتشاف حالات الفاقد")

uploaded_file = st.file_uploader("ارفع ملف الاكسل الخاص بالعدادات")
min_avg = st.number_input("حدد الحد الأدنى لقيمة المتوسط", value=0)

if uploaded_file is not None:
    df, num_cases = process_file(uploaded_file, min_avg)
    st.write(f"عدد الحالات المكتشفة: {num_cases}")
    st.write(df)

    # تحويل البيانات إلى ملف Excel وتنزيله
    excel_data = to_excel(df)
    st.download_button(label="تحميل النتائج كملف Excel", data=excel_data, file_name='anomalies_filtered.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
