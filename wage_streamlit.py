import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px

st.title('日本の賃金データのダッシュボード')

# csvデータの読み込み
df_jp_ind = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_全国_全産業.csv', encoding='shift_jis')
df_jp_category = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_全国_大分類.csv', encoding='shift_jis')
df_pref_ind = pd.read_csv('./csv_data/雇用_医療福祉_一人当たり賃金_都道府県_全産業.csv', encoding='shift_jis')


#　----------------------------------------------
st.header('2019年:一人当たり平均賃金のヒートマップ')

# 都道府県の緯度経度情報を読み込みと列名の変更
jp_lat_lon = pd.read_csv('pref_lat_lon.csv')
jp_lat_lon = jp_lat_lon.rename(columns={'pref_name': '都道府県名'})

# 集計対象を抽出
df_pref_map = df_pref_ind[(df_pref_ind['年齢'] == '年齢計') & (df_pref_ind['集計年'] == 2019)]

# 緯度経度を元のデータにマージ
df_pref_map = pd.merge(df_pref_map, jp_lat_lon, on='都道府県名')

# 最大値１、最小値０の正規化
df_pref_map['一人当たり賃金（相対値）'] = ((df_pref_map['一人当たり賃金（万円）'] - df_pref_map['一人当たり賃金（万円）'].min()) / (df_pref_map['一人当たり賃金（万円）'].max() - df_pref_map['一人当たり賃金（万円）'].min()))

#　データフレーム「df_pref_map」を使った３Dマップの作成
view = pdk.ViewState(
    longitude=139.69,
    latitude=35.69,
    zoom=4,
    pitch=40.5
)

layer = pdk.Layer(
    'HeatmapLayer',
    data=df_pref_map,
    opacity=0.4,
    get_position=['lon','lat'],
    threshold=0.3,
    get_weight='一人当たり賃金（相対値）'
)

layer_map = pdk.Deck(
    layers=layer,
    initial_view_state=view
)

#3D map の表示
st.pydeck_chart(layer_map)

# チェックボックスでdataframeを表示
show_dataframe = st.checkbox('Show DataFrame')
if show_dataframe == True:
    st.write(df_pref_map)


#　----------------------------------------------
# 集計年別の一人当たり賃金（万円）の推移グラフの作成
st.header('集計年別の一人当たり賃金（万円）の推移')

# 集計対象の抽出と列名の変更
df_ts_mean = df_jp_ind[df_jp_ind['年齢'] == '年齢計']
df_ts_mean = df_ts_mean.rename(columns={'一人当たり賃金（万円）': '全国_一人当たり賃金（万円）'})

# 都道府県別の集計対象の選別
df_pref_mean = df_pref_ind[df_pref_ind['年齢'] == '年齢計']

#都道府県のセレクトボックスを作成
pref_list = df_pref_mean['都道府県名'].unique()
option_pref = st.selectbox(
    '都道府県',
    (pref_list)
)

# セレクトボックスで選択された都道府県をdf_pref_meanに入れ直す
df_pref_mean = df_pref_mean[df_pref_mean['都道府県名'] == option_pref]

# 二つのデータフレームを結合
df_mean_line = pd.merge(df_ts_mean, df_pref_mean, on='集計年')

# 必要列のみ抽出し、集計年をインデックスとする
df_mean_line = df_mean_line[['集計年', '全国_一人当たり賃金（万円）', '一人当たり賃金（万円）']]
df_mean_line = df_mean_line.set_index('集計年')

#折れ線グラフで表示
st.line_chart(df_mean_line)


#　----------------------------------------------
#必要なデータフレームを作成
st.header('年齢階層別の全国一人当たり平均賃金（万円）')
df_mean_bubble = df_jp_ind[df_jp_ind['年齢'] != '年齢計']

#バブルチャートを作成
fig = px.scatter(df_mean_bubble,
                 x='一人当たり賃金（万円）',
                 y='年間賞与その他特別給与額（万円）',
                 range_x=[150,700],
                 range_y=[0,150],
                 size='所定内給与額（万円）',
                 size_max=38,
                 color='年齢',
                 animation_frame='集計年',
                 animation_group='年齢'
                 )

#バブルチャートを表示
st.plotly_chart(fig)


#　----------------------------------------------
#産業別の賃金推移の棒グラフ作成
st.header('産業別の賃金推移')

#集計年と賃金の種類をセレクトボックスで準備
year_list = df_jp_category['集計年'].unique()
option_year = st.selectbox(
    '集計年',
    (year_list)
)

wage_list = ['一人当たり賃金（万円）', '所定内給与額（万円）', '年間賞与その他特別給与額（万円）']
option_wage = st.selectbox(
    '賃金の種類',
    (wage_list)
)

#条件抽出したデータフレームを準備
df_mean_categ = df_jp_category[df_jp_category['集計年'] == option_year]

#wage_listにて選択した対象の最大値に合わせて、軸の最大値を変更する
max_x = df_mean_categ[option_wage].max() + 50

#横棒グラフのチャート
fig = px.bar(
    df_mean_categ,
    x=option_wage,
    y='産業大分類名',
    color='産業大分類名',
    animation_frame='年齢',
    range_x=[0,max_x],
    orientation='h',
    width=800,
    height=500
)

#棒グラフチャートを表示
st.plotly_chart(fig)


#　----------------------------------------------
#出典元
st.text('出典：RESAS（地域経済分析システム）')
st.text('本結果は、RESAS（地域経済分析システム）を加工して作成')

