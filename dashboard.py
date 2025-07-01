import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import calendar
import plotly.express as px

def dashboard():
    st.title("📊 Dashboard Analisis Outlier Penjualan")
    st.markdown("Visualisasi berdasarkan data penjualan dan cancel.")

    # Load data
    outlier_data = pd.read_csv('outlier_data.csv')
    outlier_data['Date'] = pd.to_datetime(outlier_data['Date'])
    outlier_data['Day'] = outlier_data['Date'].dt.strftime('%A')
    outlier_data['Month'] = outlier_data['Date'].dt.month
    outlier_data['DayOfMonth'] = outlier_data['Date'].dt.day

# Grafik per bulan (12 subplot)
    sales_by_day = outlier_data.groupby(['Month', 'DayOfMonth'])['SalesTotal'].sum().reset_index()
    fig_months = make_subplots(rows=6, cols=2, subplot_titles=[calendar.month_name[i] for i in range(1, 13)])

    for i, month in enumerate(range(1, 13)):
        month_data = sales_by_day[sales_by_day['Month'] == month]
        row = (i % 6) + 1
        col = (i // 6) + 1
        fig_months.add_trace(go.Scatter(
            x=month_data['DayOfMonth'],
            y=month_data['SalesTotal'],
            mode='lines',
            name=calendar.month_name[month],
            hovertemplate='<b>Tanggal:</b> %{x}<br><b>Sales Total:</b> %{y:,.0f}'
        ), row=row, col=col)
        fig_months.update_xaxes(range=[0, 32], row=row, col=col)

    fig_months.update_layout(height=1200, width=1000, title='Monthly Sales Analysis', showlegend=False)
    st.subheader("📉 Grafik Penjualan Harian per Bulan")
    st.plotly_chart(fig_months)


# Grafik transaksi vs pembatalan per bulan
    trans = outlier_data[outlier_data['SalesTotal'] >= 0].groupby('Month')['SalesTotal'].sum()
    cancl = outlier_data[outlier_data['SalesTotal'] <= 0].groupby('Month')['SalesTotal'].sum()
    months = np.arange(1, 13)
    width = 0.5

    fig_compare = go.Figure()
    fig_compare.add_trace(go.Scatter(x=months - width/2, y=trans, name='Transaksi', mode='lines+markers', marker_color='blue'))
    fig_compare.add_trace(go.Scatter(x=months + width/2, y=cancl.abs(), name='Pembatalan', mode='lines+markers', marker_color='red'))

    fig_compare.update_layout(
        xaxis=dict(tickmode='array', tickvals=months, ticktext=[calendar.month_name[m] for m in months]),
        xaxis_title='Bulan',
        yaxis_title='Total Penjualan',
        showlegend=True
    )
    st.subheader("📈 Perbandingan Transaksi vs Pembatalan per Bulan")
    st.plotly_chart(fig_compare)


# Tabel Desember Positif
    st.subheader("📄 Transaksi Positif Bulan Desember")
    outlier_december_positive = outlier_data[(outlier_data['Month'] == 12) & (outlier_data['SalesTotal'] > 0)]
    st.dataframe(outlier_december_positive.head(10))

# Grafik per hari dalam seminggu 
    filtered_data = outlier_data[outlier_data['SalesTotal'] >= 0].copy()
    filtered_data2 = outlier_data[outlier_data['SalesTotal'] <= 0].copy()
    filtered_data2['SalesTotal'] = np.abs(filtered_data2['SalesTotal'])

    daily_sales = filtered_data.groupby('Day')['SalesTotal'].sum().reset_index()
    daily_cancel = filtered_data2.groupby('Day')['SalesTotal'].sum().reset_index()

    # Urutkan hari
    order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_sales['Day'] = pd.Categorical(daily_sales['Day'], categories=order, ordered=True)
    daily_cancel['Day'] = pd.Categorical(daily_cancel['Day'], categories=order, ordered=True)
    daily_sales = daily_sales.sort_values('Day')
    daily_cancel = daily_cancel.sort_values('Day')

    fig_week = go.Figure()
    fig_week.add_trace(go.Bar(x=daily_sales['Day'], y=daily_sales['SalesTotal'], name='Transaksi', marker_color='blue'))
    fig_week.add_trace(go.Bar(x=daily_cancel['Day'], y=daily_cancel['SalesTotal'], name='Pembatalan', marker_color='red'))

    fig_week.update_layout(
        xaxis_title='Hari',
        yaxis_title='Total Penjualan',
        barmode='group',
        showlegend=True
    )
    st.subheader("🪙 Total Penjualan Berdasarkan Hari")
    st.plotly_chart(fig_week)



# Tabel data outlier positif pada hari Rabu
    outlier_rabu_positive = outlier_data[(outlier_data['Day'] == 'Wednesday') & (outlier_data['SalesTotal'] > 0)]

    st.subheader("📅 Data Outlier Positif pada Hari Rabu")
    st.write(f"Jumlah data: {outlier_rabu_positive.shape[0]}")
    st.dataframe(outlier_rabu_positive.head(10))


    canceled_data = outlier_data[outlier_data['SalesTotal'] <= 0].copy()
    canceled_data['SalesTotal'] = np.abs(canceled_data['SalesTotal'])
    positive_data = outlier_data[outlier_data['SalesTotal'] >= 0].copy()
    combined_outlier_data = pd.concat([canceled_data, positive_data])

    top_products = combined_outlier_data.groupby('ProductName')['SalesTotal'].sum().reset_index()
    top_products = top_products.sort_values(by='SalesTotal', ascending=False).head(10)

# Diagram data outlier berdasarkan total penjualan
    st.subheader("🏆 Top Produk Outlier berdasarkan Total Sales")

    fig_top_products = px.bar(top_products, x='SalesTotal', y='ProductName', orientation='h',
                            color='ProductName')
    fig_top_products.update_traces(hovertemplate='%{x:,.0f} Pound Sterling')
    st.plotly_chart(fig_top_products)

    product_name = "Medium Ceramic Top Storage Jar"
    outlier_product_data = outlier_data[outlier_data['ProductName'] == product_name]

# Table data outlier untuk produk tertentu
    st.subheader(f"📦 Data Outlier untuk Produk: {product_name}")
    st.write(f"Jumlah data: {outlier_product_data.shape[0]}")
    st.dataframe(outlier_product_data.head(10))


    combined_outlier_data2 = pd.concat([canceled_data, positive_data])
    top_customers = combined_outlier_data2.groupby('CustomerNo')['SalesTotal'].sum().reset_index()
    top_customers = top_customers.sort_values(by='SalesTotal', ascending=False).head(10)

    top_customers['CustomerNo'] = top_customers['CustomerNo'].astype(str)
    top_customers['CustomerNo'] = pd.Categorical(top_customers['CustomerNo'], categories=top_customers['CustomerNo'], ordered=True)

# Diagram data outlier berdasarkan total penjualan per customer
    st.subheader("👥 Top Outlier Customers by Total Sales")
    fig_top_customers = px.bar(top_customers, x='SalesTotal', y='CustomerNo', orientation='h',
                            color='CustomerNo')
    fig_top_customers.update_traces(hovertemplate='%{x:,.0f} Pound Sterling')
    st.plotly_chart(fig_top_customers)

# Tabel data outlier untuk 2 customer teratas 
    st.subheader("📄 Data Outlier untuk CustomerNo 12346.0")
    out_12346 = outlier_data[outlier_data['CustomerNo'] == 12346.0]
    st.write(f"Jumlah data: {out_12346.shape[0]}")
    st.dataframe(out_12346.head(10))

    st.subheader("📄 Data Outlier untuk CustomerNo 16446.0")
    out_16446 = outlier_data[outlier_data['CustomerNo'] == 16446.0]
    st.write(f"Jumlah data: {out_16446.shape[0]}")
    st.dataframe(out_16446.head(10))

# Kelompokkan berdasarkan Country
    st.subheader("🗺️ Persebaran Total Sales Outlier Berdasarkan Negara")

    city_sales_outlier = outlier_data.groupby('Country')['SalesTotal'].sum().reset_index()

    # Peta global dengan semua negara
    fig_map_all = px.choropleth(
        city_sales_outlier,
        locations='Country',
        locationmode='country names',
        color='SalesTotal',
        hover_name='Country',
        hover_data={'SalesTotal': ':,.0f'},
        title='🌍 Persebaran Total Sales Outlier Berdasarkan Negara (Semua Negara)',
        color_continuous_scale='Viridis',
        projection='natural earth'
    )
    st.plotly_chart(fig_map_all)


    # Hapus United Kingdom untuk analisis tanpa dominasi data
    city_sales_outlier_no_uk = city_sales_outlier[city_sales_outlier['Country'] != 'United Kingdom']

    fig_map_ex_uk = px.choropleth(
        city_sales_outlier_no_uk,
        locations='Country',
        locationmode='country names',
        color='SalesTotal',
        hover_name='Country',
        hover_data={'SalesTotal': ':,.0f'},
        title='🌐 Persebaran Total Sales Outlier (Tanpa United Kingdom)',
        color_continuous_scale='Viridis',
        projection='natural earth'
    )
    st.plotly_chart(fig_map_ex_uk)
