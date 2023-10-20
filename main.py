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
    arr_gen = np.empty((32 * 1024, 8))
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


def mx_to_hmi(mx_adr=0, hmi_adr=0):
    if mx_adr != 0:
        mx_int = mx_adr // 16
        mx_fl = mx_adr - (mx_int * 16)
        if mx_fl < 10:
            mx_fl = "0" + str(mx_fl)
        return str(mx_int) + str(mx_fl)
    elif hmi_adr != 0:
        hmi_int = int(str(hmi_adr)[:-2])
        hmi_fl = int(str(hmi_adr)[-2:])
        return str(hmi_int * 16 + hmi_fl)


def file_dialog_window():
    def on_close():
        global window_close
        window_close = False
        dialog_window.destroy()

    def procces():
        # dialog_window.destroy()
        table_window()

    def open_file():
        global path
        path = filedialog.Open(dialog_window).show()
        entry.insert(0, path)
        if path != '':
            parse_csv_to_df()

    def set_flag_true(event):
        nonlocal flag
        flag = True

    def set_flag_false(event):
        nonlocal flag
        flag = False

    def calc_btn(event):
        if flag:
            calc_mx()
        else:
            calc_hmi()

    def calc_mx():
        mx_adr = mx_entry.get()
        hmi_entry.delete(0, END)
        hmi_entry.insert(0, str(mx_to_hmi(int(mx_adr), 0)))

    def calc_hmi():
        hmi_adr = hmi_entry.get()
        mx_entry.delete(0, END)
        mx_entry.insert(0, str(mx_to_hmi(0, int(hmi_adr))))

    dialog_window = Tk()
    dialog_window.geometry("300x250")
    dialog_window.title("PLC Memmory Reader")
    dialog_window.resizable(False, False)
    entry = Entry(dialog_window, width=40)

    flag = True

    mx_entry = Entry(dialog_window)
    hmi_entry = Entry(dialog_window)
    btn_calc = Button(dialog_window, text='Расчитать')
    mx_lb = Label(dialog_window, text='%MX')
    hmi_lb = Label(dialog_window, text='HMI')

    mx_entry.bind("<Return>", calc_btn)
    mx_entry.bind("<Button-1>", set_flag_true)
    hmi_entry.bind("<Return>", calc_btn)
    hmi_entry.bind("<Button-1>", set_flag_false)

    title_label_calc = Label(dialog_window,text="Калькулятор адреса памяти").grid(row=1, column=1, columnspan=2)
    mx_lb.grid(row=2, column=1)
    hmi_lb.grid(row=2, column=2)
    mx_entry.grid(row=3, column=1)
    hmi_entry.grid(row=3, column=2)
    btn_calc.grid(row=4, column=2, sticky='e')
    btn_calc.bind("<Button-1>",calc_btn)

    zero_lab1 = Label(dialog_window).grid(row=5, column=1, columnspan=2)
    title_label_table= Label(dialog_window, text="Выгрузить таблицу адресов из CSV").grid(row=6, column=1, columnspan=2)
    entry.grid(row=7, column=1, columnspan=2)
    button = Button(dialog_window, text='Выбрать файл', command=open_file)

    button.grid(row=8, column=2, sticky='e')
    zero_lab = Label(dialog_window).grid(row=9, column=1, columnspan=2)
    button_apply = Button(dialog_window, text='Выполнить', command=procces)
    button_apply.grid(row=10, column=2, sticky='e')
    dialog_window.protocol("WM_DELETE_WINDOW", on_close)
    dialog_window.mainloop()


def table_window():
    data_frame = get_adr_df()
    data_frame = data_frame.sort_values(by=['adr_mx'])
    create_arr()
    arr_proces(data_frame)

    def on_close():
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
                for i in range(0, len(el0)):
                    if el0[i] != '0': el0[i] = 'MB'

                table.insert(parent='', index='end', iid=count, text='',
                             values=(str(index + 1), el0[7], el0[6], el0[5], el0[4], el0[3], el0[2], el0[1], el0[0]),
                             tags=('8',))
            elif flag == 16:
                for i in range(0, len(el0)):
                    if el0[i] != '0': el0[i] = 'MW'
                table.insert(parent='', index='end', iid=count, text='',
                             values=(str(index + 1), el0[7], el0[6], el0[5], el0[4], el0[3], el0[2], el0[1], el0[0]),
                             tags=('16',))
            elif flag == 32:
                for i in range(0, len(el0)):
                    if el0[i] != '0': el0[i] = 'MD'
                table.insert(parent='', index='end', iid=count, text='',
                             values=(str(index + 1), el0[7], el0[6], el0[5], el0[4], el0[3], el0[2], el0[1], el0[0]),
                             tags=('32',))
            elif flag == 10:
                for i in range(0, len(el0)):
                    if el0[i] != '0': el0[i] = 'MX'
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
    scrollbar = ttk.Scrollbar(table_window, orient='vertical', command=table.yview)

    style = ttk.Style()
    style.configure(table, background='silver')

    table.column("#0", width=1, stretch=NO)
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
    table.heading("indx", text="#Byte", anchor=CENTER)
    table.heading("7", text="7", anchor=CENTER)
    table.heading("6", text="6", anchor=CENTER)
    table.heading("5", text="5", anchor=CENTER)
    table.heading("4", text="4", anchor=CENTER)
    table.heading("3", text="3", anchor=CENTER)
    table.heading("2", text="2", anchor=CENTER)
    table.heading("1", text="1", anchor=CENTER)
    table.heading("0", text="0", anchor=CENTER)

    add_to_table()
    table.pack(side=LEFT, fill=BOTH)
    scrollbar.pack(side=RIGHT, fill=Y)
    table["yscrollcommand"] = scrollbar.set
    # button = Button(table_window, text='Выбрать файл', command=open_dialog)
    # button.pack(side=BOTTOM)

    table_window.protocol("WM_DELETE_WINDOW", on_close)

    table_window.mainloop()


def calc_mem_window():
    calc_window = Tk()

    calc_window.mainloop()


def main():
    while window_close:
        file_dialog_window()


if __name__ == '__main__':
    main()
