import pandas as pd
import requests
import json
import pickle
import os
from itertools import chain
from collections import defaultdict
from time import localtime, strftime, time, sleep

def VT_get_a_file_report(file_hash):
    url = "https://www.virustotal.com/api/v3/files/" + "/" + file_hash
    API = "1eb48a654f6743bbb6f3b3ccea45760c87ae72f9e387567394ac50da543b6c3c"
    
    headers = {
        "accept": "application/json",
        "x-apikey": API
    }

    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        print("requests get Error : ", e)
        return    

    return response.text


def VT_get_report_list_with_hash(hash_list, time_sleep=True):
    report_list = []
    i = 0
    for h in hash_list:
        report = VT_get_a_file_report(h)
        print("{} get a file report from hash : {}".format(i, h))
        i += 1
 
        if 'error' in list(json.loads(report).keys()):
            print(json.loads(report))

        if time_sleep == True:
            sleep(15)
        
        if report == None:
            continue

        report_list.append(report)
    
    return report_list


# get only data report except error report
def VT_convert_report_to_json_list(report_list):
    err_cnt = 0
    data_cnt = 0

    error_list = []
    data_list = []
    for i, rep in enumerate(report_list):
        if 'error' in list(json.loads(rep).keys()):
            err_cnt += 1
            error_list.append(json.loads(rep))

        elif 'data' in list(json.loads(rep).keys()):
            data_cnt += 1
            data_list.append(json.loads(rep))

        else:
            print("index \"{}\" extra case!!", i)
            print(json.loads(rep))
    
    print("error count : {}\ndata count: {}\n".format(err_cnt, data_cnt))
    
    return data_list, error_list


"""
    function VT_get_stats_count "key" parameter can get bottom keywords
    'malicious', 'suspicious', 'undetected', 'harmless', 'timeout', 'confirmed-timeout', 'failure', 'type-unsupported'
"""
def VT_get_stats_count(response_json, category:str):
    last_analysis_stats = response_json['data']['attributes']['last_analysis_stats']
    count = last_analysis_stats[category]
    return count


def show_stats_count(data_list):
    total_malware = 0
    total_suspicious = 0
    total_undetected = 0
    total_harmless = 0
    total_timeout = 0
    total_confirmed_timeout = 0
    total_failure = 0
    total_type_unsupported =0

    for data in data_list:
        if VT_get_stats_count(data, 'malicious') > 0:
            total_malware += 1
            
        if VT_get_stats_count(data, 'suspicious') > 0:
            total_suspicious += 1
            
        if VT_get_stats_count(data, 'undetected') > 0:
            total_undetected += 1
            
        if VT_get_stats_count(data, 'harmless') > 0:
            total_harmless += 1
            
        if VT_get_stats_count(data, 'timeout') > 0:
            total_timeout += 1
            
        if VT_get_stats_count(data, 'confirmed-timeout') > 0:
            total_confirmed_timeout += 1
            
        if VT_get_stats_count(data, 'failure') > 0:
            total_failure += 1
            
        if VT_get_stats_count(data, 'type-unsupported') > 0:
            total_type_unsupported += 1

    print("malicious count:", total_malware)
    print("suspicious count:", total_suspicious)
    print("undetected count:", total_undetected)
    print("harmless count:", total_harmless)
    print("timeout count:", total_timeout)
    print("confirmed-timeout count:", total_confirmed_timeout)
    print("failure count:", total_failure)
    print("type-unsupported count:", total_type_unsupported)


def VT_vendor_analysis(response_json, category) -> dict:
    vendors_list = list(response_json['data']['attributes']['last_analysis_results'].keys())
    
    vendor_category_list = list()
    cat_vendor_list = list() 
    vendors_dict = dict()
    for vendor in vendors_list:
        vendor_category = response_json['data']['attributes']['last_analysis_results'][vendor]['category']
        if vendor_category == category:
            cat_vendor_list.append(vendor)
    
    vendors_dict[category+'_vendors'] = cat_vendor_list
    vendors_dict[category+'_count'] = VT_get_stats_count(response_json, category)
    
    return vendors_dict


# from itertools import chain
# from collections import defaultdict
# from time import localtime, strftime
def VT_make_analysis_df(data_list:list, category_list:list):
    df_dict = dict()
    for data in data_list:
        id_ = data['data']['id']
        
        cat_vendor_dict_list = list()
        for category in category_list:
            cat_vendor_dict_list.append(VT_vendor_analysis(data, category).items())
                
        default_dict = defaultdict(list)
        default_dict['names'] = data['data']['attributes']['names']
        default_dict['creation_date'] = VT_get_creation_date(data)
        default_dict['md5'] = data['data']['attributes']['md5']
        for k, v  in chain(*cat_vendor_dict_list):
            if v == []:
                default_dict[k]
            else:
                default_dict[k] = v
        
        df_dict[id_] = default_dict
    
    df = pd.DataFrame.from_dict(df_dict, orient='index')
    return df

def VT_get_creation_date(json_data):
    try:
        creation_date = json_data['data']['attributes']['creation_date']
        tm = localtime(creation_date)
        return strftime("%Y-%m-%d", tm)
    except:
        return None

 
def VT_run_full_cycle(hash_list, time_sleep=True):
    data_list = list()
    error_list = list()
    df = pd.DataFrame()
    try:
        start_time = time()
        report_list = VT_get_report_list_with_hash(hash_list, time_sleep)
        end_time = time()
        print("elapsed time of getting report: {}\n".format(end_time - start_time))

        data_list, error_list = VT_convert_report_to_json_list(report_list)
        show_stats_count(data_list)

        category_list = ['malicious', 'undetected', 'suspicious', 'harmless', 'timeout', 'confirmed-timeout', 'failure', 'type-unsupported']
        df = VT_make_analysis_df(data_list, category_list)
    except Exception as e:
        print("Error in full cycle : ", e)
        pass
    finally :
        return data_list, error_list, df


def VT_process_one_day_quota(md5_list, fname):
    data_list = []
    error_list = []
    new_df = pd.DataFrame()
    old_df = pd.DataFrame()
    if os.path.exists(fname):
        old_df = pd.read_csv(fname)
    else:
        new_df.to_csv(fname, index=False)
    

    step = 0
    while True:
        print(f"#step : {step}")
        step += 1
        
        if step > 1:
            old_df = pd.read_csv(fname)

        if len(md5_list) < 500:
            data, error, normal_df = VT_run_full_cycle(md5_list)
        else:
            data, error, normal_df = VT_run_full_cycle(md5_list[:500])

        data_list.extend(data)
        error_list.extend(error)
        new_df = pd.concat([old_df, normal_df], axis=0)
        new_df.to_csv(fname, index=False)

        print(new_df.info())

        if len(md5_list) < 500:
                break

        md5_list = md5_list[500:]
        sleep(86400) # wait one day

    return new_df, data_list, error_list

def pkl_save(file_name, data):
    with open(file_name, 'wb') as handle:
        pickle.dump(data, handle)
        
def pkl_load(file_name):
    with open(file_name, 'rb') as handle:
        data = pickle.load(handle)
    return data


"""

    visualization

"""

import seaborn as sns
import matplotlib.pyplot as plt

def plot_vendors(df, column:str):
    vendor_counts = df[column].explode().value_counts()

    vendor_counts.plot(kind='bar')
    plt.title('Vendor Occurrences')
    plt.xlabel('Vendor')
    plt.ylabel('Occurrences')
    plt.xticks(rotation=45)
    plt.show()


def hist_malicious_count(df, column:str):
    plt.hist(df[column], bins=range(1, df['malicious_count'].max() + 2), align='left', rwidth=0.8)
    plt.title('Malicious count')
    plt.xlabel('Vendors count')
    plt.ylabel('Frequency')
    plt.xticks(range(1, df[column].max() + 1))
    plt.show()
