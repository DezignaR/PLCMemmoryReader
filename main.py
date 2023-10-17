import pandas as pd
import numpy as np

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

df = pd.DataFrame()
arr_gen = ()
path = ""
window_close = True


# Выгрузка CSV в DataFrame
def parse_csv_to_df():
    global df
    df = pd.read_csv(path, delimiter=',', encoding="ISO-8859-1")


# Преобразование DataFrame
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


# Создание массива с нулевыми значениями
def create_arr():
    global arr_gen
    arr_gen = np.empty((262144, 8))
    return arr_gen


# Заполнение массива
def arr_proces(data_frame):
    global arr_gen
    for index in range(0, len(data_frame.index)):
        tag = data_frame['tag'].values[index]
        adr = data_frame['adr_mx'].values[index]
        delt = data_frame['adr_delt'].values[index]

        if tag != '%MX':
            for j in range(adr // 8, adr // 8 + delt // 8):
                for i in range(0, 8):
                    arr_gen[j][i] = delt
        else:
            arr_gen[adr // 8][adr % 8] = delt + 10


def file_dialog_window():
    def on_close():
        global window_close
        window_close = False
        dialog_window.destroy()

    def procces():
        dialog_window.destroy()
        table_window()

    def open_file():
        global path
        path = filedialog.Open(dialog_window).show()
        entry.insert(1, path)
        if path != '':
            parse_csv_to_df()

    dialog_window = Tk()
    dialog_window.geometry("300x100")
    dialog_window.title("Выберите файл CSV")
    entry = Entry(dialog_window)

    entry.pack(fill=X)

    button = Button(dialog_window, text='Выбрать файл', command=open_file)

    button.pack(anchor='e')
    button_apply = Button(dialog_window, text='Выполнить', command=procces)
    button_apply.pack(side=BOTTOM)
    dialog_window.protocol("WM_DELETE_WINDOW", on_close)
    dialog_window.mainloop()


def table_window():
    data_frame = get_adr_df()
    data_frame = data_frame.sort_values(by=['adr_mx'])
    create_arr()
    arr_proces(data_frame)

    def open_dialog():
        table_window.destroy()

    def add_to_table():
        end_ = len(arr_gen)
        count = 0
        table.tag_configure('10', background='#FF0000')
        table.tag_configure('32', background='#2E8B57')
        table.tag_configure('16', background='#4682B4')
        table.tag_configure('8', background='#D8BFD8')
        table.tag_configure('0', background='#FFFFFF')

        for index in range(0, end_):
            el0 = []
            flag = 0
            for jndex in range(0, 8):
                if arr_gen[index][jndex] == 10:
                    flag = 10
                elif arr_gen[index][jndex] == 16:
                    flag = 16
                elif arr_gen[index][jndex] == 32:
                    flag = 32
                elif arr_gen[index][jndex] == 8:
                    flag = 8
                el0.append(str(int(arr_gen[index][jndex])))

            if flag == 0:
                table.insert(parent='', index='end', iid=count, text='',
                             values=(str(index + 1), el0[7], el0[6], el0[5], el0[4], el0[3], el0[2], el0[1], el0[0]),
                             tags=('0',))
            elif flag == 8:
                table.insert(parent='', index='end', iid=count, text='',
                             values=(str(index + 1), el0[7], el0[6], el0[5], el0[4], el0[3], el0[2], el0[1], el0[0]),
                             tags=('8',))
            elif flag == 16:
                table.insert(parent='', index='end', iid=count, text='',
                             values=(str(index + 1), el0[7], el0[6], el0[5], el0[4], el0[3], el0[2], el0[1], el0[0]),
                             tags=('16',))
            elif flag == 32:
                table.insert(parent='', index='end', iid=count, text='',
                             values=(str(index + 1), el0[7], el0[6], el0[5], el0[4], el0[3], el0[2], el0[1], el0[0]),
                             tags=('32',))
            elif flag == 10:
                table.insert(parent='', index='end', iid=count, text='',
                             values=(str(index + 1), el0[7], el0[6], el0[5], el0[4], el0[3], el0[2], el0[1], el0[0]),
                             tags=('10',))
            count += 1

    table_window = Tk()
    table_window.title("PLC Memmory Reader")
    table_window.geometry("500x500")
    table_window.resizable(False, False)

    table = ttk.Treeview(table_window)
    table['height'] = 500
    table['columns'] = ('indx', '7', '6', '5', '4', '3', '2', '1', '0')
    scrollbar = ttk.Scrollbar(orient='vertical', command=table.yview)

    style = ttk.Style()
    style.configure(table, background='silver')

    table.column("#0", width=0)
    table.column('indx', width=80, anchor=CENTER)
    table.column('7', width=50, anchor=CENTER)
    table.column('6', width=50, anchor=CENTER)
    table.column('5', width=50, anchor=CENTER)
    table.column('4', width=50, anchor=CENTER)
    table.column('3', width=50, anchor=CENTER)
    table.column('2', width=50, anchor=CENTER)
    table.column('1', width=50, anchor=CENTER)
    table.column('0', width=50, anchor=CENTER)

    table.heading("#0", text="", anchor=CENTER)
    table.heading("indx", text="", anchor=CENTER)
    table.heading("7", text="7", anchor=CENTER)
    table.heading("6", text="6", anchor=CENTER)
    table.heading("5", text="5", anchor=CENTER)
    table.heading("4", text="4", anchor=CENTER)
    table.heading("3", text="3", anchor=CENTER)
    table.heading("2", text="2", anchor=CENTER)
    table.heading("1", text="1", anchor=CENTER)
    table.heading("0", text="0", anchor=CENTER)

    add_to_table()
    table.pack(side=LEFT, fill=X)
    scrollbar.pack(side=RIGHT, fill=Y)
    table["yscrollcommand"] = scrollbar.set
    button = Button(table_window, text='Выбрать файл', command=open_dialog)
    button.pack(side=BOTTOM)
    table_window.mainloop()


def main():
    while window_close:
        file_dialog_window()


if __name__ == '__main__':
    main()
