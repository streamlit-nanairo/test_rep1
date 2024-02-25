from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

# CSVファイルの読み込み、必要な列を指定
df = pd.read_csv(
    "./注文履歴.csv",
    header=0,
    usecols=["No.", "購入日", "部署", "品名", "単価", "数量", "金額"],  # ここを修正
    parse_dates=["購入日"]  # 購入日を日付型で読み込む
)
df = df.dropna()  # 空白データがある行を除外
df[["単価", "数量", "金額"]] = df[["単価", "数量", "金額"]].astype(int)  # 金額や数量を整数型に変換
df["月"] = df["購入日"].dt.month.astype(str)  # "月"の列を追加
df["購入日|部署"] = df["購入日"].astype(str).str.cat(df["部署"], sep="|")  # "購入日|部署" 列を追加

view_columns = ['購入日', '部署', '品名', '単価', '数量', '金額']

# Streamlitのページ設定
st.set_page_config(
   page_title="備品購入ダッシュボード",
   layout="wide",
)

# 現在の年月を取得（サンプルデータの年月を使用する場合は下の2行をコメントアウト）
# today = date.today()
# this_year, this_month = today.year, today.month
this_year = 2022  # サンプルCSVをそのまま使用する場合はこの行のコメントを解除してください
this_month = 9  # サンプルCSVをそのまま使用する場合はこの行のコメントを解除してください

st.title(f"{this_year}年{this_month}月")

# 4カラム表示
col1, col2, col3, col4 = st.columns(4)
# 今年の購入回数
this_year_counts = df.loc[df["購入日"].dt.year == this_year, "購入日|部署"].nunique()
col1.metric("📝今年の購入回数", f"{this_year_counts}回")
# 今年の購入額
this_year_purchase = df.loc[df["購入日"].dt.year == this_year, "金額"].sum()
col2.metric("💰今年の購入額", f"{this_year_purchase}円")
# 今月の購入回数
this_month_counts = df.loc[df["購入日"].dt.month == this_month, "購入日|部署"].nunique()
col3.metric("📝今月の購入回数", f"{this_month_counts}回")
# 今月の購入額
this_month_purchase = df.loc[df["購入日"].dt.month == this_month, "金額"].sum()
col4.metric("💰今月の購入額", f"{this_month_purchase}円")


# 3カラム表示 (1:2:2)
col1, col2, col3 = st.columns([1, 2, 2])

# 購入数TOP10
# many_df = df.groupby(by="品名").sum().sort_values(by="数量", ascending=False).reset_index()
many_df = df.groupby("品名", as_index=False)[["単価", "数量", "金額"]].sum().sort_values(by="数量", ascending=False)
col1.subheader("購入数TOP10")
col1.table(many_df[["品名", "単価", "数量", "金額"]].iloc[:10])

# 部署別購入金額
# department_group_df = df.groupby(["部署", "月"]).sum()
department_group_df = df.groupby(["部署", "月"])[["単価", "数量", "金額"]].sum()
fig = px.bar(department_group_df.reset_index(), x="金額", y="部署", color="月", orientation="h")
col2.subheader("部署別購入金額")
col2.plotly_chart(fig, use_container_width=True)

# 直近3件の購入
recent_df = df[df["購入日|部署"].isin(sorted(df["購入日|部署"].unique())[-3:])]
recent_df["購入日"] = recent_df["購入日"].dt.strftime("%Y-%m-%d")
col3.subheader("直近3件の購入")
col3.table(recent_df[view_columns])

# 月ごとの購入金額推移
# month_group_df = df.groupby(["月", "部署"]).sum()
month_group_df = df.groupby(["月", "部署"])[["単価", "数量", "金額"]].sum()
fig = px.bar(month_group_df.reset_index(), x="月", y="金額", color="部署", title="月別購入金額")
st.plotly_chart(fig, use_container_width=True)


# 詳細表示
with st.expander("詳細データ"):
   # 表示する期間の入力
   min_date = df["購入日"].min().date()
   max_date = df["購入日"].max().date()
   start_date, end_date = st.slider(
      "表示する期間を入力",
      min_value=min_date,
      max_value=max_date,
      value=(min_date, max_date),
      format="YYYY/MM/DD")

   col1, col2 = st.columns(2)

   # 表示する部署の選択
   departments = df["部署"].unique()
   select_departments = col1.multiselect("表示部署", options=departments, default=departments)

   df["購入日"] = df["購入日"].apply(lambda x: x.date())
   detail_df = df[(start_date <= df["購入日"]) & (df["購入日"] <= end_date) & (df["部署"].isin(select_departments))]

   # productname_group_df = detail_df.groupby(["品名", "部署"]).sum()
   productname_group_df = detail_df.groupby(["品名", "部署"])[["単価", "数量", "金額"]].sum()

   view_h = len(productname_group_df)*15
   fig = px.bar(productname_group_df.reset_index(), x="金額", y="品名", color="部署", orientation="h", title="購入品別購入金額", height=view_h+300, width=600)
   fig.update_layout(yaxis={'categoryorder':'total ascending'})
   col1.plotly_chart(fig, use_container_width=True)

   col2.subheader("購入一覧")
   col2.dataframe(detail_df[view_columns], height=view_h+200)
