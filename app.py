import streamlit as st 
import pandas as pd 
import joblib 
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder 
from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split 
from sklearn.metrics import confusion_matrix 
from sklearn.metrics import classification_report 
from sklearn.metrics import accuracy_score 


df = pd.read_csv('Sales Transaction v.4a.csv')

produk_list = df['ProductName'].dropna().unique().tolist()  
produk_list.insert(0, 'Pilih produk...')

produk_dict = df.dropna(subset=['ProductName', 'Price']) \
                .drop_duplicates(subset=['ProductName']) \
                .set_index('ProductName')['Price'].to_dict()

negara_list =  sorted (df['Country'].dropna().unique().tolist())
negara_list.insert(0, 'Pilih negara...')

# Load the pre-trained model
try: 
    model = joblib.load('logistic_regression_model (1).pkl') 
except FileNotFoundError: 
    st.error("Model file not found. Please make sure 'logistic_regression_model (1).pkl' is in the same directory.") 
    st.stop() 

# Judul aplikasi Streamlit 
st.title('📊 Aplikasi Prediksi Persetujuan Pembelian') 
st.write(""" Aplikasi ini memprediksi apakah pembelian tergolong normal atau outlier berdasarkan jumlah produk, harga, dan lokasi pelanggan.
""") 
 
# Buat form input untuk data dummy 
st.header('📝 Masukkan Data Calon Pembeli') 
 
customer = st.text_input('No Customer', '') 
country = st.selectbox('area customer', negara_list) 
produk_name = st.selectbox('Nama Produk', produk_list) 
# Tampilkan harga produk
harga_produk = produk_dict.get(produk_name, 0)  
st.write(f"💰 Harga satuan produk: **${harga_produk:,.2f}**")

quantity = st.number_input('Jumlah Produk', min_value=0) 
# Hitung total harga
total_harga = harga_produk * quantity if isinstance(harga_produk, (int, float)) else 0
st.write(f"🧾 Total harga: **${total_harga:,.2f}**")


# Tombol untuk memprediksi 
prediksi_clicked = st.button('Prediksi Persetujuan Pembelian')
if produk_name == 'Pilih produk...':
    st.warning("⚠️ Silakan pilih produk terlebih dahulu.")
elif quantity == 0:
    st.warning("⚠️ Silakan masukkan jumlah produk lebih dari 0.")
elif country == 'Pilih negara...':
    st.warning("⚠️ Silakan pilih negara terlebih dahulu.")
elif prediksi_clicked:

# Load encoder (jika disimpan saat training, lebih aman)
# Tapi kalau belum disimpan, encode langsung di sini:
    le_produk = LabelEncoder()
    le_produk.fit(df['ProductName'])

    le_negara = LabelEncoder()
    le_negara.fit(df['Country'])

    # Encode input user
    produk_encoded = le_produk.transform([produk_name])[0]
    negara_encoded = le_negara.transform([country])[0]
    # Encode input pengguna 
    input_data = {
        'ProductName': [produk_encoded],
        'Country': [negara_encoded],
        'Price': [harga_produk],
        'Quantity': [quantity],
    }
    
    # Buat DataFrame dari input pengguna 
    input_df = pd.DataFrame(input_data)

    # Pastikan kolom sesuai dengan model
    if 'ProductName' not in input_df.columns or 'Country' not in input_df.columns:
        st.error("Kolom yang diperlukan tidak ada dalam input.")
        st.stop()


    # Lakukan prediksi 
    prediction = model.predict(input_df) 
    prediction_proba = model.predict_proba(input_df)[:, 1] 

    # Tampilkan hasil prediksi 
    st.header('📈 Hasil Prediksi')
    st.write(f"👤 Customer: **{customer}**")
    st.write(f"📦 Produk: **{produk_name}**")
    st.write(f"📍 Area: **{country}**")
    st.write(f"🔢 Quantity: **{quantity}**")
    st.write(f"💵 Total Harga: **${total_harga:,.2f}**")

    if prediction[0] == 1:
        st.success("✅ Pinjaman DIPREDIKSI DISETUJUI (Data normal)")
    else:
        st.error("❌ Pinjaman DIPREDIKSI DITOLAK (Terdeteksi sebagai outlier oleh model)")

    st.write(f"🎯 Probabilitas termasuk data normal: **{prediction_proba[0]:.0f}**")
    st.write(f"🎯 Probabilitas termasuk data outlier: **{1 - prediction_proba[0]:.0f}**")