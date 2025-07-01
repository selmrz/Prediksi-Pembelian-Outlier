import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import joblib

# Load model
try:
    model = joblib.load('logistic_regression_model.pkl')
except FileNotFoundError:
    raise FileNotFoundError("❌ Model file tidak ditemukan.")

# Koneksi ke database
def create_connection():
    return mysql.connector.connect(
        host='localhost', 
        user='root', 
        password='', 
        database='outlier_data')

    
def predict_purchase(data: dict):
    # Encode country dan productname jika diperlukan
    input_df = pd.DataFrame([{
        'Country': data['country_encoded'],         # hasil encoding
        'ProductName': data['product_encoded'],     # hasil encoding
        'Quantity': data['quantity'],
        'Price': data['price']                      
    }])

    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]

    return prediction, probability, input_df


def save_to_database(data: dict):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (
            country, productname, quantity
        ) VALUES (%s, %s, %s)
    """, (
        data['country'],
        data['productname'],
        data['quantity']
    ))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_all_predictions():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM predictions ORDER BY customerid DESC")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows)
    cursor.close()
    conn.close()
    return pd.DataFrame(rows)

def logic():
    df = pd.read_csv('outlier_data.csv')

    produk_list = df['ProductName'].dropna().unique().tolist()
    produk_list.insert(0, 'Pilih produk...')

    produk_dict = df.dropna(subset=['ProductName', 'Price']) \
                    .drop_duplicates(subset=['ProductName']) \
                    .set_index('ProductName')['Price'].to_dict()

    negara_list = sorted(df['Country'].dropna().unique().tolist())
    negara_list.insert(0, 'Pilih negara...')

    st.title('📦 Prediksi Outlier Pembelian Produk')
    st.write("Masukkan data transaksi untuk memprediksi apakah transaksi termasuk outlier.")

    selected_country = st.selectbox('Negara', negara_list)
    selected_product = st.selectbox('Nama Produk', produk_list)

    harga_produk = produk_dict.get(selected_product, 0)
    if selected_product != 'Pilih produk...':
        st.write(f"💰 Harga per item: **${harga_produk:,.0f}**")

    quantity = st.number_input('Jumlah Produk', min_value=0)
    total_harga = harga_produk * quantity 
    st.write(f"🧾 Total harga: **${total_harga:,.0f}**")

    if st.button('Prediksi Transaksi'):
        if selected_country == 'Pilih negara...':
            st.warning("⚠️ Silakan pilih negara terlebih dahulu.")
        elif selected_product == 'Pilih produk...':
            st.warning("⚠️ Silakan pilih produk terlebih dahulu.")
        else:
            try:
                country_encoded = hash(selected_country) % 1000
                product_encoded = hash(selected_product) % 1000

                input_data = {
                    'country': selected_country,
                    'productname': selected_product,
                    'quantity': quantity,
                    'country_encoded': country_encoded,
                    'product_encoded': product_encoded,
                    'price': harga_produk
                }

                prediction, probability, _ = predict_purchase(input_data)

                st.header('📈 Hasil Prediksi')
                if prediction == 1:
                    st.success('✅ Transaksi DIPREDIKSI NORMAL')
                else:
                    st.error('⚠️ Transaksi DIPREDIKSI OUTLIER')

                st.write(f"🎯 Probabilitas termasuk data normal: {probability:.2f}")

                if prediction == 1:
                    save_to_database(input_data)
                    st.info("✅ Data transaksi disimpan ke database.")
                else:
                    st.warning("❌ Data tidak disimpan karena termasuk outlier.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

    st.markdown("---")
    st.subheader("📋 Riwayat Transaksi Tersimpan")
    if st.button("Tampilkan Data dari Database"):
        try:
            df_show = fetch_all_predictions()
            if df_show.empty:
                st.info("📭 Belum ada data.")
            else:
                st.dataframe(df_show)
        except Exception as e:
            st.error(f"Gagal menampilkan data: {e}")