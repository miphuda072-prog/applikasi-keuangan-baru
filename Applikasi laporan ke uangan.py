import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Keuangan Real-Time", layout="wide")

# --- JUDUL APLIKASI ---
st.title("💰 Aplikasi Keuangan & Investasi")

# --- FUNGSI LOAD & SAVE DATA ---
# Kita simpan data dalam file CSV sederhana agar mudah dibaca
FILE_DATA = 'data_keuangan.csv'

def load_data():
    if os.path.exists(FILE_DATA):
        return pd.read_csv(FILE_DATA)
    else:
        # Membuat struktur jika file belum ada
        return pd.DataFrame(columns=["Tanggal", "Kategori", "Jenis", "Jumlah", "Keterangan", "Bulan", "Tahun"])

def save_data(df):
    df.to_csv(FILE_DATA, index=False)

# Load data saat aplikasi dibuka
df = load_data()

# --- SIDEBAR: INPUT DATA ---
st.sidebar.header("📝 Input Transaksi Baru")

with st.sidebar.form("form_transaksi", clear_on_submit=True):
    tgl = st.date_input("Tanggal", datetime.now())
    
    # Kategori sesuai permintaan
    jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
    
    kategori_opsi = []
    if jenis == "Pemasukan":
        kategori_opsi = ["Gaji", "Dividen", "Bonus", "Lainnya"]
    else:
        kategori_opsi = ["Operasional Bulanan", "Investasi", "Kebutuhan Pokok", "Hiburan", "Lainnya"]
        
    kategori = st.selectbox("Kategori Detail", kategori_opsi)
    jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
    ket = st.text_input("Keterangan Tambahan")
    
    submit = st.form_submit_button("Simpan Data")

    if submit:
        new_data = {
            "Tanggal": tgl,
            "Kategori": kategori,
            "Jenis": jenis,
            "Jumlah": jumlah,
            "Keterangan": ket,
            "Bulan": tgl.strftime("%B"), # Mengambil nama bulan
            "Tahun": tgl.year
        }
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        save_data(df)
        st.success("Data berhasil disimpan!")
        st.rerun() # Refresh halaman

# --- DASHBOARD UTAMA ---

# 1. Filter Data (Tahun)
tahun_list = df['Tahun'].unique().tolist()
if tahun_list:
    pilih_tahun = st.selectbox("Pilih Tahun Laporan", sorted(tahun_list, reverse=True))
    df_filtered = df[df['Tahun'] == pilih_tahun]
else:
    st.info("Belum ada data. Silakan input data di sidebar.")
    st.stop() # Berhenti jika tidak ada data

# --- REKAP & METRIK ---
col1, col2, col3, col4 = st.columns(4)

total_masuk = df_filtered[df_filtered['Jenis'] == 'Pemasukan']['Jumlah'].sum()
total_keluar = df_filtered[df_filtered['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
total_invest = df_filtered[df_filtered['Kategori'] == 'Investasi']['Jumlah'].sum()
saldo = total_masuk - total_keluar

col1.metric("Total Pemasukan", f"Rp {total_masuk:,.0f}")
col2.metric("Total Pengeluaran", f"Rp {total_keluar:,.0f}")
col3.metric("Total Investasi", f"Rp {total_invest:,.0f}")
col4.metric("Sisa Saldo", f"Rp {saldo:,.0f}")

st.markdown("---")

# --- GRAFIK (VISUALISASI) ---
col_grafik1, col_grafik2 = st.columns(2)

# Grafik 1: Tren Bulanan (Januari - Desember)
# Mengurutkan bulan agar rapi
order_bulan = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

# Grouping data per bulan
df_bulan = df_filtered.groupby(['Bulan', 'Jenis'])['Jumlah'].sum().reset_index()

with col_grafik1:
    st.subheader("Grafik Arus Kas Bulanan")
    if not df_bulan.empty:
        fig_bar = px.bar(df_bulan, x='Bulan', y='Jumlah', color='Jenis', 
                         barmode='group', category_orders={"Bulan": order_bulan},
                         color_discrete_map={"Pemasukan": "green", "Pengeluaran": "red"})
        st.plotly_chart(fig_bar, use_container_width=True)

# Grafik 2: Komposisi Pengeluaran (Pie Chart)
df_expense = df_filtered[df_filtered['Jenis'] == 'Pengeluaran']
with col_grafik2:
    st.subheader("Proporsi Pengeluaran & Investasi")
    if not df_expense.empty:
        fig_pie = px.pie(df_expense, values='Jumlah', names='Kategori', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TABEL DETAIL ---
st.subheader("📄 Laporan Detail Transaksi")
st.dataframe(df_filtered.sort_values(by="Tanggal", ascending=False), use_container_width=True)

# --- LAPORAN TAHUNAN (SUMMARY) ---
st.markdown("---")
st.subheader(f"Laporan Rekapitulasi Tahun {pilih_tahun}")
summary_table = df_filtered.groupby(['Bulan', 'Jenis'])['Jumlah'].sum().unstack().fillna(0)
# Mengurutkan index bulan
summary_table = summary_table.reindex(order_bulan).dropna(how='all')
st.table(summary_table.style.format("Rp {:,.0f}"))