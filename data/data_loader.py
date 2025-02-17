import os
import pandas as pd


def set_default_path(default_root_path=None):
    if default_root_path == None:
        default_root_path = "/"

    os.chdir(default_root_path)
    return default_root_path


def get_full_path(name, default_root_path=None):
    try:
        if default_root_path is None:
            default_root_path = "/"

        file_list = list()
        dir_list = list()
        for root, dirs, files in os.walk(default_root_path):
            for f in files:
                if name in f:
                    file_full_path = os.path.join(root, f)
                    file_list.append(file_full_path)

            for d in dirs:
                if name in d:
                    dir_full_path = os.path.join(root, d)
                    dir_list.append(dir_full_path)
        
        if not file_list:
            #print("dir list: {}\n".format(dir_list))
            return dir_list

        if not dir_list:
            #print("file list: {}\n".format(file_list))
            return file_list
    
        full_list = file_list + dir_list
        #print("full list: {}\n".format(file_list))
        return full_list

    except Exception as e:
        print("Can't get full path error :", e)


def load_dataset(dataset_path):
    possible_separators = [',', ';', '\t', '|', ':', ' ']
    for separator in possible_separators:
        try:
            df = pd.read_csv(dataset_path, sep=separator)
            return df
        except pd.errors.ParserError:
            continue

    raise ValueError("Unable to determine the separator for the CSV file")


