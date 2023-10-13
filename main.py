import pandas as pd
import numpy as np
import matplotlib as plt

df = pd.DataFrame()
arr_gen = ()

#Выгрузка CSV в DataFrame
def parse_csv_to_df():
    global df
    df = pd.read_csv('NewPLC_Global_Variable.csv', delimiter=',', encoding="ISO-8859-1")

#Преобразование DataFrame
def get_adr_df():
    ddf = df[df.Address.str.contains('%M', na=False)].Address

    tag_str = []
    adr_str = []
    adr_mx = []
    adr_delt = []

    for index in range(0, len(ddf.index)):
        str_ = str(ddf.iloc[index])
        adr_mem = int(str_[3::1])
        tag_mem = str_[:3:1]
        adr_mx_, adr_delt_ = parse_to_mx(tag=tag_mem, adr=adr_mem)
        tag_str.append(tag_mem)
        adr_str.append(adr_mem)
        adr_mx.append(adr_mx_)
        adr_delt.append(adr_delt_)

    dict_ = {'tag': tag_str, 'adr': adr_str, 'adr_mx': adr_mx, 'adr_delt': adr_delt}
    ddf = pd.DataFrame.from_dict(dict_, orient='columns')

    return ddf

# Перевод адреса в %MX
def parse_to_mx(tag, adr):
    if tag == '%MD':
        return adr * 2 ** 5, 2 ** 5
    elif tag == '%MW':
        return adr * 2 ** 4, 2 ** 4
    elif tag == '%MB':
        return adr * 2 ** 3, 2 ** 3
    elif tag == '%MX':
        return adr, 0

#Создание массива с нулевыми значениями
def create_arr():
    global arr_gen
    arr_gen = np.zeros((262144, 8))
    print(arr_gen)
    return arr_gen

# Заполнение массива
def arr_proces():
    global arr_gen





def main():

    parse_csv_to_df()
    data_frame = get_adr_df()
    data_frame = data_frame.sort_values(by=['adr_mx'])
    create_arr()


    print(data_frame)


if __name__ == '__main__':
    main()
