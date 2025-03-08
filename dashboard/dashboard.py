import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import altair as alt

# ========== CONFIGURASI HALAMAN ==========
st.set_page_config(page_title="Dashboard E-Commerce Brasil", layout="wide")

# ========== STYLE CUSTOM ==========
st.markdown("""
    <style>
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Arial', sans-serif;
            font-weight: bold;
            color: #333333;
        }
        .stMetricLabel { font-size: 20px; }
        .stMetricValue { font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ========== HEADER ==========
st.title("📊 Analisis E-Commerce Brasil")

# ========== LOAD DATA ==========
# File Uploader untuk mengatasi FileNotFoundError
uploaded_file = st.file_uploader("Upload hasil_analisis.csv", type="csv")

if uploaded_file is not None:
    full_data = pd.read_csv(uploaded_file)
    st.write("✅ File berhasil dimuat!")
    st.write(full_data.head())  # Tampilkan data
else:
    st.error("❌ File tidak ditemukan! Silakan upload CSV.")
full_data['order_purchase_timestamp'] = pd.to_datetime(full_data['order_purchase_timestamp'])

# ========== SIDEBAR ==========
st.sidebar.title(" Pengaturan Dashboard")
selected_page = st.sidebar.radio("Pilih Halaman:", [" Gambaran Data", " Analisis Visualisasi"])

if selected_page == " Analisis Visualisasi":
    st.sidebar.title("📅 Filter Waktu")
    min_date = full_data['order_purchase_timestamp'].min().date()
    max_date = full_data['order_purchase_timestamp'].max().date()
    start_date, end_date = st.sidebar.date_input("Pilih Rentang Waktu:", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    mask = (full_data['order_purchase_timestamp'].dt.date >= start_date) & (full_data['order_purchase_timestamp'].dt.date <= end_date)
    filtered_data = full_data[mask]
    
    st.sidebar.title("🔍 Pilih Analisis")
    selected_options = st.sidebar.multiselect("Pilih visualisasi:", ["Top 10 Kategori Produk Terlaris", "Heatmap Penawaran", "Heatmap Permintaan", "Produk dengan Tren Peningkatan"], default=[])
else:
    filtered_data = full_data

# ========== GAMBARA DATA ==========
if selected_page == " Gambaran Data":
    st.header(" Gambaran Data E-Commerce")
    
    total_orders = full_data['order_id'].nunique()
    total_customers = full_data['customer_id'].nunique()
    total_revenue = full_data['price'].sum()
    total_sellers = full_data['seller_id'].nunique()
    avg_order_value = total_revenue / total_orders

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📦 Total Pesanan", f"{total_orders:,}")
    col2.metric("👥 Total Pelanggan", f"{total_customers:,}")
    col3.metric("💰 Total Pendapatan", f"Rp {total_revenue:,.0f}")
    col4.metric("🏬 Total Seller", f"{total_sellers:,}")
    col5.metric("📊 Rata-rata Order", f"Rp {avg_order_value:,.0f}")
    
    # Top 10 State & Kota Seller dalam dua kolom
    st.subheader(" Top 10 Negara Bagian & Kota dengan Seller Terbanyak")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("🏢 **Top 10 Negara bagian dengan Seller Terbanyak**")
        top_states = full_data.groupby("seller_state")["seller_id"].nunique().nlargest(10).reset_index()
        chart_state = alt.Chart(top_states).mark_bar().encode(
            x="seller_id:Q",
            y=alt.Y("seller_state:N", sort='-x'),
            color=alt.value("#87CEEB")
        ).properties(width=350, height=300)
        st.altair_chart(chart_state, use_container_width=True)
    
    with col2:
        st.write("🏙️ **Top 10 Kota dengan Seller Terbanyak**")
        top_cities = full_data.groupby("seller_city")["seller_id"].nunique().nlargest(10).reset_index()
        chart_city = alt.Chart(top_cities).mark_bar().encode(
            x="seller_id:Q",
            y=alt.Y("seller_city:N", sort='-x'),
            color=alt.value("#87CEEB")
        ).properties(width=350, height=300)
        st.altair_chart(chart_city, use_container_width=True)
 

    # Visualisasi Distribusi Skor Review dan Keterlambatan Pengiriman Bersebelahan
    st.subheader(" Distribusi Skor Review & Keterlambatan Pengiriman Produk")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("⭐ Distribusi Skor Review Produk")
        if "review_score" in full_data.columns:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.countplot(x=full_data['review_score'], palette='Blues', ax=ax)
            ax.set_title("Distribusi Skor Review Produk", fontsize=12)
            st.pyplot(fig)
        else:
            st.warning("Kolom 'review_score' tidak ditemukan dalam dataset.")
    
    with col2:
        st.write("⏳ Distribusi Keterlambatan Pengiriman Produk")
        full_data['order_delivered_customer_date'] = pd.to_datetime(full_data['order_delivered_customer_date'], errors='coerce')
        full_data['order_estimated_delivery_date'] = pd.to_datetime(full_data['order_estimated_delivery_date'], errors='coerce')
        full_data['delivery_delay'] = (full_data['order_delivered_customer_date'] - full_data['order_estimated_delivery_date']).dt.days
        delay = full_data['delivery_delay'].dropna()
        
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(delay, bins=50, kde=True, color='skyblue', ax=ax)
        ax.set_xlabel("Delay (Hari)", fontsize=12)
        ax.set_ylabel("Jumlah Pesanan", fontsize=12)
        ax.set_title("Distribusi Keterlambatan Pengiriman Produk", fontsize=12)
        ax.set_xlim(-50, 50)
        ax.set_xticks(range(-50, 51, 10))
        st.pyplot(fig)

# ========== ANALISIS VISUALISASI ==========
elif selected_page == " Analisis Visualisasi":
    st.header(" Hasil Analisis Visualisasi")
    if not selected_options:
        st.info("Silakan pilih minimal satu analisis di sidebar.")
    
    if "Top 10 Kategori Produk Terlaris" in selected_options:
        st.subheader("📦 Top 10 Kategori Produk Terlaris")
        top_categories = filtered_data['product_category_name'].value_counts().nlargest(10).reset_index()
        top_categories.columns = ["product_category_name", "count"]

        st.altair_chart(
            alt.Chart(top_categories)
            .mark_bar()
            .encode(x="count:Q", y=alt.Y("product_category_name:N", sort='-x'), color=alt.value("#87CEEB")),
            use_container_width=True
        )

    if "Heatmap Penawaran" in selected_options:
        st.subheader("🔥 Heatmap Penawaran (Supply)")
        filtered_sales = filtered_data.groupby(['seller_city', 'product_category_name'])['order_item_id'].count().reset_index()

        # Ambil Top 10 Seller Cities
        top_seller_cities = filtered_sales.groupby("seller_city")["order_item_id"].sum().nlargest(10).index
        filtered_sales = filtered_sales[filtered_sales["seller_city"].isin(top_seller_cities)]

        # Ambil Top 10 Product Categories
        top_categories = filtered_sales.groupby("product_category_name")["order_item_id"].sum().nlargest(10).index
        filtered_sales = filtered_sales[filtered_sales["product_category_name"].isin(top_categories)]

        # Pivot data untuk heatmap
        sales_pivot = filtered_sales.pivot(index="seller_city", columns="product_category_name", values="order_item_id").fillna(0)

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(sales_pivot, cmap="Blues", annot=True, fmt="g", linewidths=0.5, ax=ax)
        ax.set_title("🔥 Heatmap Penawaran (Supply)", fontsize=14)
        ax.set_xlabel("Product Category", fontsize=12)
        ax.set_ylabel("Seller City", fontsize=12)
        plt.xticks(rotation=45, ha="right")

        st.pyplot(fig)

    if "Heatmap Permintaan" in selected_options:
        st.subheader("🔥 Heatmap Permintaan (Demand)")
        filtered_demand = filtered_data.groupby(['customer_city', 'product_category_name'])['order_item_id'].count().reset_index()

        # Ambil Top 10 Customer Cities
        top_customer_cities = filtered_demand.groupby("customer_city")["order_item_id"].sum().nlargest(10).index
        filtered_demand = filtered_demand[filtered_demand["customer_city"].isin(top_customer_cities)]

        # Ambil Top 10 Product Categories
        top_categories = filtered_demand.groupby("product_category_name")["order_item_id"].sum().nlargest(10).index
        filtered_demand = filtered_demand[filtered_demand["product_category_name"].isin(top_categories)]

        # Pivot data untuk heatmap
        demand_pivot = filtered_demand.pivot(index="customer_city", columns="product_category_name", values="order_item_id").fillna(0)

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(demand_pivot, cmap="Blues", annot=True, fmt="g", linewidths=0.5, ax=ax)
        ax.set_title("🔥 Heatmap Permintaan (Demand)", fontsize=14)
        ax.set_xlabel("Product Category", fontsize=12)
        ax.set_ylabel("Customer City", fontsize=12)
        plt.xticks(rotation=45, ha="right")

        st.pyplot(fig)

    if "Produk dengan Tren Peningkatan" in selected_options:
        st.subheader("📈 Produk dengan Tren Peningkatan")

        if 'year_month' not in filtered_data:
            filtered_data['year_month'] = filtered_data['order_purchase_timestamp'].dt.strftime('%Y-%m')

        product_trend_monthly = filtered_data.groupby(['year_month', 'product_category_name'])['order_id'].count().reset_index()

        # Ambil 5 produk dengan penjualan tertinggi
        top_products = product_trend_monthly.groupby('product_category_name')['order_id'].sum().nlargest(5).index.tolist()
        trending_products = product_trend_monthly[product_trend_monthly['product_category_name'].isin(top_products)]

        if trending_products.empty:
            st.warning("Data kosong! Coba ubah filter waktu untuk melihat tren produk.")
        else:
            trending_products = trending_products.sort_values("year_month")

            chart_trend = alt.Chart(trending_products).mark_line(point=True).encode(
                x=alt.X("year_month:T", title="Bulan-Tahun", axis=alt.Axis(format="%Y-%m")),
                y=alt.Y("order_id:Q", title="Total Orders"),
                color=alt.Color("product_category_name:N", legend=alt.Legend(title="Kategori Produk")),
                tooltip=["year_month", "product_category_name", "order_id"]
            ).properties(width=800, height=400, title="Tren Penjualan Produk Populer Per Bulan")

            st.altair_chart(chart_trend, use_container_width=True)
