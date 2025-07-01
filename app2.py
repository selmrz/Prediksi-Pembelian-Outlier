import streamlit as st
from dashboard import dashboard
from logic import logic

st.sidebar.title("Pengaturan Aplikasi")
menu = st.sidebar.radio("Pilih Menu", ["Dashboard", "Prediksi Outlier"])

if menu == "Dashboard":
    dashboard()
elif menu == "Prediksi Outlier":
    logic()
