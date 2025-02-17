hm_total_hash1 = pd.read_csv('hm_total_hash1.csv', '|', names=['hash'], header=None)
hm_total_hash2 = pd.read_csv('hm_total_hash2.csv', '|', names=['hash'], header=None)
hm_total_hash = pd.concat([hm_total_hash1, hm_total_hash2], axis=0)
hm_total_hash.reset_index(drop=True, inplace=True)

# apply
def apply_hash_column(df):
    return df['hash'].apply(lambda x: x.split(',')[0])

hm_total_hash['hash'] = apply_hash_column(hm_total_hash)

hm_total_hash.to_csv('hm_total_hash.csv', index=False)

# sorting
KISA_df[KISA_df['malicious_count'] > 0].iloc[:,:5].sort_values(by='malicious_count', ascending=False)

# concat with reset_index
def concat_df(df1, df2, ax=0):
    df = pd.concat([df1, df2], axis=ax).reset_index(drop=True)
    return df

# drop duplicate 중복 제거
temp_df = temp_df.drop_duplicates(['md5'])
