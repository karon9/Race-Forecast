#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd

# 最大表示列数の指定（ここでは50列を指定）
pd.set_option('display.max_columns', 50)



race_df = pd.read_csv("./csv/race-2008.csv", sep=",")
horse_df = pd.read_csv("./csv/horse-2008.csv", sep=",")
for year in range(2009, 2020):
    race_tmp_df = pd.read_csv("./csv/race-" + str(year) + ".csv", sep=",")
    horse_tmp_df = pd.read_csv("./csv/horse-" + str(year) + ".csv", sep=",")
    race_df = pd.concat([race_df, race_tmp_df], axis=0)
    horse_df = pd.concat([horse_df, horse_tmp_df], axis=0)

# ## 元データの確認



# race_id単位で重複したデータが存在しないか確認
print(len(race_df) == len(race_df['race_id'].unique()))
print(race_df.shape)
race_df.tail(2)



# 出走馬数の確認
race_df["total_horse_number"].value_counts()



print(horse_df.shape)
horse_df.head(2)

# ## raceデータの整形



race_df.head(1)

# ### race_id
# そのままでOK



# 一応確認
race_df["race_id"].dtypes

# ### race_round
# 余分な空白とRを取り除く



race_df["race_round"].dtypes


race_df['race_round'].unique()



race_df['race_round'] = race_df['race_round'].str.strip('R \n')



race_df['race_round'].unique()



race_df['race_round'] = race_df['race_round'].astype(int)
race_df["race_round"].dtypes

# ### race_title
# いらないので削除



# もともとのカラムは不要なので削除
race_df.drop(['race_title'], axis=1, inplace=True)

# ### race_course
# 「ダ右1200m」などであれば、ダート・右回り・1200に分割して、それぞれ別のカラムにする。
# 
# 新たに4つのカラムを追加
# - 障害コースか？
# - 地面のタイプは何か？
# - 右回り・左回り・直線か？
# - 距離は？



race_df["race_course"].unique()



# 正規表現で取得

# 障害か、地面のタイプは何か、左か、右か、直線か、
obstacle = race_df["race_course"].str.extract('(障)', expand=True)
ground_type = race_df["race_course"].str.extract('(ダ|芝)', expand=True)
is_left_right_straight = race_df["race_course"].str.extract('(左|右|直線)', expand=True)
distance = race_df["race_course"].str.extract('(\d+)m', expand=True)

obstacle.columns = {"is_obstacle"}
ground_type.columns = {"ground_type"}
is_left_right_straight.columns = {"is_left_right_straight"}
distance.columns = {"distance"}

race_df = pd.concat([race_df, obstacle], axis=1)
race_df = pd.concat([race_df, ground_type], axis=1)
race_df = pd.concat([race_df, is_left_right_straight], axis=1)
race_df = pd.concat([race_df, distance], axis=1)



# 'is_obstacle' 列の '障芝' を1に置き換え、Nanに0埋め
race_df['is_obstacle'] = race_df['is_obstacle'].replace('障', 1)
race_df.fillna(value={'is_obstacle': 0}, inplace=True)



print("is_obstacle:", race_df["is_obstacle"].unique())
print("ground_type:", race_df["ground_type"].unique())
print("is_left_right_straight:", race_df["is_left_right_straight"].unique())
print("distance isnull sum:", race_df["distance"].isnull().sum())



# もともとのカラムは不要なので削除
race_df.drop(['race_course'], axis=1, inplace=True)



race_df["distance"] = race_df["distance"].astype(int)

# ### weather
# そのままone_hotエンコーディングしてデータを食わせても良さそうだが...
# 
# 余分な文字列を取り除く。
# 
# また、少雨よりも雨が強いはず、小雪よりも雪が強いはず。これらの単純な雨量は別のデータを取ってこないと分からないが、大小関係は情報として入れられるはず。



race_df["weather"].unique()



race_df['weather'] = race_df['weather'].str.strip('天候 :')



race_df["weather"].unique()



weather_rain = race_df["weather"].str.extract('(小雨|雨)', expand=True)
weather_snow = race_df["weather"].str.extract('(小雪|雪)', expand=True)
weather_rain.columns = {"weather_rain"}
weather_snow.columns = {"weather_snow"}
race_df = pd.concat([race_df, weather_rain], axis=1)
race_df = pd.concat([race_df, weather_snow], axis=1)

race_df.fillna(value={'weather_rain': 0}, inplace=True)
race_df['weather_rain'] = race_df['weather_rain'].replace('小雨', 1)
race_df['weather_rain'] = race_df['weather_rain'].replace('雨', 2)
race_df.fillna(value={'weather_snow': 0}, inplace=True)
race_df['weather_snow'] = race_df['weather_snow'].replace('小雪', 1)
race_df['weather_snow'] = race_df['weather_snow'].replace('雪', 2)



print("weather_rain:", race_df["weather_rain"].value_counts())
print("weather_snow:", race_df["weather_snow"].value_counts())



# ### ground_status
# 芝かダートかは既に別カラムにあるので、状態を見る。
# 大小関係があるので数値として。



race_df["ground_status"].unique()



race_df['ground_status'] = race_df['ground_status'].replace('.*(稍重).*', 4, regex=True)
race_df['ground_status'] = race_df['ground_status'].replace('.*(重).*', 3, regex=True)
race_df['ground_status'] = race_df['ground_status'].replace('.*(不良).*', 2, regex=True)
race_df['ground_status'] = race_df['ground_status'].replace('.*(良).*', 1, regex=True)



print("ground_status:", race_df["ground_status"].value_counts())

# ### time と dateをあわせてdatetimeに



race_df["time"] = race_df["time"].str.replace('発走 : (\d\d):(\d\d)(.|\n)*', r'\1時\2分')



race_df["date"] = race_df["date"] + race_df["time"]



race_df["date"] = pd.to_datetime(race_df['date'], format='%Y年%m月%d日%H時%M分')



# もともとのtimeは不要なので削除
race_df.drop(['time'], axis=1, inplace=True)



print(race_df["date"].dtype)
print("date isnull sum:", race_df["date"].isnull().sum())

# ### where_racecourse
# 例:1回小倉3日目 の中から小倉を取り出す



race_df["where_racecourse"] = race_df["where_racecourse"].str.replace('\d*回(..)\d*日目', r'\1')



# 確認
race_df["where_racecourse"].unique()

# ###  馬の数や順位
# - total_horse_number                 int64
# - frame_number_first                 int64
# - horse_number_first                 int64
# - frame_number_second                int64
# - horse_number_second                int64
# - frame_number_third                 int64
# - horse_number_third                 int64
# 
# これらはそのままでOK

# ### オッズから余分な「,」を除く
# - tansyo                            object
# - hukuren_first                     object
# - hukuren_second                    object
# - hukuren_third                     object
# - renhuku3                          object
# - rentan3                           object
# 
# 数値と文字列が混在しているので面倒
# ```
# race_df['tansyo'] = race_df['tansyo'].str.strip(',')
# ```
# などとしてもだめ

# In[35]:


race_df.columns



race_df['tansyo'] = race_df['tansyo'].apply(lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['hukusyo_first'] = race_df['hukusyo_first'].apply(
    lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['hukusyo_second'] = race_df['hukusyo_second'].apply(
    lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['hukusyo_third'] = race_df['hukusyo_third'].apply(
    lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['wakuren'] = race_df['wakuren'].apply(lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['umaren'] = race_df['umaren'].apply(lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['wide_1_2'] = race_df['wide_1_2'].apply(lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['wide_1_3'] = race_df['wide_1_3'].apply(lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['wide_2_3'] = race_df['wide_2_3'].apply(lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['umatan'] = race_df['umatan'].apply(lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['renhuku3'] = race_df['renhuku3'].apply(lambda x: int(x.replace(",", "")) if type(x) is str else int(x))
race_df['rentan3'] = race_df['rentan3'].apply(lambda x: int(x.replace(",", "")) if type(x) is str else int(x))



race_df[race_df['race_id'] == 200808010709]



# 確認
race_df['race_id'] = race_df['race_id'].astype(str)
# race_df['race_title'] = race_df['race_title'].astype(str)
print('dataframeの各列のデータ型を確認==>\n', race_df.dtypes)

race_df.head(1)

# ### race dataの保存



race_df.to_csv("csv/cleaned_race_data.csv", index=False)

# ## horse data の整形



print(horse_df.shape)
print(horse_df.dtypes)
horse_df['race_id'] = horse_df['race_id'].astype(str)
horse_df['horse_id'] = horse_df['horse_id'].astype(str)
horse_df['tamer_id'] = horse_df['tamer_id'].astype(str)
horse_df['owner_id'] = horse_df['owner_id'].astype(str)
horse_df['rider_id'] = horse_df['rider_id'].astype(str)

horse_df.head(2)





# 何かとデータ分析で便利なので、レース日時情報をmerge
race_tmp_df = race_df[["race_id", "date"]]
horse_df = pd.merge(horse_df, race_tmp_df, on='race_id')
horse_df.head()

# ### 使わなさそうな情報を削除
# - time_value, tame_time(プレミアム会員向けの情報)
# - goal_time_dif(自分で作成する)



horse_df.drop(['time_value'], axis=1, inplace=True)
horse_df.drop(['goal_time_dif'], axis=1, inplace=True)
horse_df.drop(['tame_time'], axis=1, inplace=True)

# ### race_id
# そのままでOK

# ### rank
# > - 降着・・・	「その走行妨害がなければ被害馬が加害馬に先着していた」と判断した場合、加害馬は被害馬の後ろに降着となります。
# > - 失格・・・	「極めて悪質で他の騎手や馬に対する危険な行為によって、競走に重大な支障を生じさせた」と判断した場合、加害馬は失格となります。
# 
# > 注記：被害馬が落馬や疾病発症等により競走を中止した場合には、上記の「失格」に該当しない限り着順は到達順位のとおり確定します。
# 

# - 降格は降格フラグに分割、順位そのまま入れておく
# - 取・除はそもそも参加していないので削除
# - 失は順位が全く当てにならないので情報を削除
# - 中は最後まで到達していないが参加はしている。ひとまず20位にしておく。goal_timeが無いので、大きめに取る必要がある。
# - 12(再)は12で最後の模様。そのまま12にする



# 確認
horse_df[horse_df['rank'] == '中'].sort_values('date').head(2)
horse_df[horse_df['rank'] == '取'].sort_values('date').head(2)
horse_df[horse_df['rank'] == '除'].sort_values('date').head(2)
horse_df[horse_df['rank'] == '16(降)'].sort_values('date').head(2)
horse_df[horse_df['rank'] == '12(再)'].sort_values('date').head(2)



# 降格を別へ
is_down = horse_df["rank"].str.extract('(\(降\))', expand=True)
is_down.columns = {"is_down"}
horse_df = pd.concat([horse_df, is_down], axis=1)

horse_df.fillna(value={'is_down': 0}, inplace=True)
horse_df['is_down'] = horse_df['is_down'].replace('(降)', 1)

## 余分な文字を削除
horse_df['rank'] = horse_df['rank'].apply(lambda x: x.replace("(降)", ""))
horse_df['rank'] = horse_df['rank'].apply(lambda x: x.replace("(再)", ""))



"""- 取・除はそもそも参加していないので削除
- 失は順位が全く当てにならないので情報を削除
- 中は最後まで到達していないが参加はしている。ひとまず20位にしておく"""

horse_df = horse_df[(horse_df['rank'] != "取") & (horse_df['rank'] != "除") & (horse_df['rank'] != "失")]
horse_df['rank'] = pd.DataFrame(horse_df['rank'].mask(horse_df['rank'] == "中", 20))



# 確認
horse_df["rank"].value_counts()

# ### 姓と年齢をsplit



horse_df['sex_and_age'].unique()



# 性別を別へ

is_senba = horse_df["sex_and_age"].str.extract('(セ)', expand=True)
is_senba.columns = {"is_senba"}
horse_df = pd.concat([horse_df, is_senba], axis=1)

is_mesu = horse_df["sex_and_age"].str.extract('(牝)', expand=True)
is_mesu.columns = {"is_mesu"}
horse_df = pd.concat([horse_df, is_mesu], axis=1)

is_osu = horse_df["sex_and_age"].str.extract('(牡)', expand=True)
is_osu.columns = {"is_osu"}
horse_df = pd.concat([horse_df, is_osu], axis=1)



horse_df.fillna(value={'is_osu': 0}, inplace=True)
horse_df['is_osu'] = horse_df['is_osu'].replace('牡', 1)
horse_df.fillna(value={'is_mesu': 0}, inplace=True)
horse_df['is_mesu'] = horse_df['is_mesu'].replace('牝', 1)
horse_df.fillna(value={'is_senba': 0}, inplace=True)
horse_df['is_senba'] = horse_df['is_senba'].replace('セ', 1)
## 余分な文字を削除
horse_df['sex_and_age'] = horse_df['sex_and_age'].str.strip("牝牡セ")
horse_df['sex_and_age'] = horse_df['sex_and_age'].astype(int)



horse_df = horse_df.rename(columns={'sex_and_age': 'age'})

# ## goal_timeをtimedelta型にしてから秒に(last_timeも)



# nullになるのは、レースで「中」になった馬
print(horse_df['goal_time'].isnull().sum())
print(horse_df['last_time'].isnull().sum())



horse_df['goal_time'] = pd.to_datetime(horse_df['goal_time'], format='%M:%S.%f') - pd.to_datetime('00:00.0',
                                                                                                  format='%M:%S.%f')
horse_df['goal_time'] = horse_df['goal_time'].dt.total_seconds()



# 欠損値を最大値で埋める
horse_df.fillna(value={'goal_time': horse_df['goal_time'].max()}, inplace=True)
horse_df.fillna(value={'last_time': horse_df['last_time'].max()}, inplace=True)



horse_df.dtypes

# ### goal_timeとレース距離から、平均速度を求める



# レース距離情報をmerge
race_tmp_df = race_df[["race_id", "distance"]]
horse_df = pd.merge(horse_df, race_tmp_df, on='race_id')



horse_df["distance"] = horse_df["distance"].astype(int)
horse_df["avg_velocity"] = horse_df["distance"] / horse_df["goal_time"]



# ### half_way_rank
# splitして平均値を保持する（レースによってまちまちなので）



from statistics import mean

horse_df["half_way_rank"] = horse_df["half_way_rank"].apply(
    lambda x: mean([float(n) for n in (x.split("-"))]) if type(x) is str else float(x))



horse_df[horse_df["rank"] == 20] = horse_df[horse_df["rank"] == 20].fillna({'half_way_rank': 20})
horse_df["half_way_rank"] = horse_df["half_way_rank"].fillna(horse_df['half_way_rank'].mean())
horse_df["half_way_rank"].isnull().sum()



horse_df["half_way_rank"] = horse_df["half_way_rank"].astype(float)

# ### horse_weight と diff の分離
# 「計不」は平均で穴埋め



horse_weight_dif = horse_df["horse_weight"].str.extract('\(([-|+]?\d*)\)', expand=True)
horse_weight_dif.columns = {"horse_weight_dif"}

horse_df = pd.concat([horse_df, horse_weight_dif], axis=1)

horse_df['horse_weight'] = horse_df['horse_weight'].replace('\(([-|+]?\d*)\)', '', regex=True)



horse_df['horse_weight'] = horse_df['horse_weight'].replace('計不', np.nan)
horse_df['horse_weight'] = horse_df['horse_weight'].astype(float)
horse_df['horse_weight_dif'] = horse_df['horse_weight_dif'].astype(float)



# 計不 の horse_idを探し、馬ごとの平均値で穴埋め
no_records = horse_df[horse_df['horse_weight'].isnull()]['horse_id']
for no_record_id in no_records:
    horse_df.loc[(horse_df['horse_id'] == no_record_id) & (horse_df['horse_weight'].isnull()), 'horse_weight'] = \
        horse_df[horse_df['horse_id'] == no_record_id]['horse_weight'].mean()
    horse_df.loc[
        (horse_df['horse_id'] == no_record_id) & (horse_df['horse_weight_dif'].isnull()), 'horse_weight_dif'] = 0


horse_df.dtypes

# ### burden_weight, horse_weight の比率を追加



horse_df['burden_weight_rate'] = horse_df['burden_weight'] / horse_df['horse_weight']

# ### last_time
# とりあえず放置するが、外れ値の扱いを考えたほうが良さそう。



horse_df.plot(kind='hist', y='last_time', bins=50, figsize=(16, 4), alpha=0.5)



horse_df[horse_df['last_time'] < 20]['race_id'].unique()



race_df[(race_df['race_id'] == '200808010804') | (race_df['race_id'] == '200806010208') | (
        race_df['race_id'] == '200806010304')]

# ### odds



horse_df['odds'] = horse_df['odds'].astype(float)



# ### horse dataの保存



print(horse_df.dtypes)
horse_df.head(3)



horse_df.to_csv("csv/cleaned_horse_data.csv", index=False)

