import time
from typing import Dict, List, Any
import re
import bs4
import json
import requests
from io import StringIO
from pathlib import Path

import pandas as pd
import jdatetime

TSE_dir = Path(__file__).resolve().parent


def all_symbols():
    symbol_file = open(f"{TSE_dir}/Data/symbols.json", "r", encoding="utf-8")
    symbols = json.load(symbol_file)
    symbol_file.close()
    return list(symbols.keys())


def to_arabic(string: str):
    return string.replace('ک', 'ك').replace('ی', 'ي').strip()


def to_farsi(string: str):
    return string.replace('ك', 'ک').replace('ي', 'ی').replace('\u200c', ' ').strip()


def _loop_(data):
    index = 0
    while index != 1:
        try:
            output = data
            index += 1
        except:
            print('خطا در برقراری ارتباط لطفا 5 ثانیه صبر کنید تا برطرف شود')
            x = jdatetime.datetime.now()
            y = x + jdatetime.timedelta(seconds=5)
            while jdatetime.datetime.now() < y:
                time.sleep(1)
    return output


def tse_split(data):
    data = data.split(";")
    result = []
    for i in range(len(data)):
        res_split = data[i].split(",")
        result_ = []
        for res_i in res_split:
            if '@' in res_i:
                result_.extend([res_i.split("@")])
            else:
                result_.append(res_i)
        result.append(result_)
    return result


def _adjust_data_frame(df, date: str):
    df[date] = pd.to_datetime(df[date], format="%Y%m%d")
    df['jdate'] = pd.to_datetime(df[date], format="%Y%m%d").apply(
        lambda gregorian: jdatetime.date.fromgregorian(date=gregorian))


def Ticker_To_InsCode(symbol_name) -> List:
    url = f"http://www.tsetmc.com/tsev2/data/search.aspx?skey={symbol_name}".encode('utf-8').strip()
    Response_InsCode = _loop_(requests.get(url, timeout=30).text.encode('utf-8').decode('utf-8'))

    symbol_full_info = Response_InsCode.split(';')[0].split(',')
    if to_arabic(symbol_name) == symbol_full_info[0].strip():
        ticker_index = symbol_full_info[2]  # symbol id

        url = f"http://tsetmc.com/Loader.aspx?ParTree=151311&i={ticker_index}"
        Response_Other = _loop_(requests.get(url, timeout=30).text)
        Group_Name = re.findall(r"LSecVal='([\D]*)',", Response_Other)[0]
        Id_Shareholders = re.findall(r"CIsin='([\w\d]*)|',$", Response_Other)[0]
        try:
            Title = re.findall(r"Title='([\D]*)',", Response_Other)[0].split(',')[0].split(' - ')[1]
        except:
            if 'انرژی3' == symbol_name:
                Title = 'بازار دوم بورس'
            elif 'انرژی2' == symbol_name:
                Title = 'بازار دوم بورس'
            elif 'انرژی1' == symbol_name:
                Title = 'بازار دوم بورس'
            elif 'وسیزد' == symbol_name:
                Title = 'بازار دوم بورس'
            elif 'فیروزه' == symbol_name:
                Title = 'صندوق شاخص30 شركت فيروزه'
            else:
                print(f'Ticker_To_InsCode None is data {symbol_name}')

        new_symbol = [
            ticker_index.strip(),
            to_farsi(symbol_full_info[1]),
            to_farsi(Title).replace("'", ''),
            to_farsi(Group_Name.strip()),
            Id_Shareholders.strip()
        ]
        return new_symbol


class Ticker:
    def __init__(self, Symbol: str, Full_Name: str, Group_Name: str,
                 ID_InsCode: str, ID_Shareholder: str, timeout: int = 30,
                 Lim_Date=None, Lim_Len=None):
        self.symbol = Symbol
        self.Full_Name = Full_Name
        self.Group_Name = Group_Name
        self.ID_InsCode = ID_InsCode
        self.ID_Shareholders = ID_Shareholder
        self.timeout = timeout
        self.Limitations_Date = Lim_Date
        self.Limitations_Len = Lim_Len

    @property
    def shareholders(self) -> Dict[str, Dict[str, Any]]:
        index = 0
        while index != 1:
            try:
                url = f"http://www.tsetmc.com/Loader.aspx?Partree=15131T&c={self.ID_Shareholders}"
                response = requests.get(url, timeout=self.timeout).content

                soup = bs4.BeautifulSoup(response, 'html.parser')
                table = to_farsi(str(soup.find("table")))
                shareholders_df = pd.read_html(table)[0]
                shareholders_df = shareholders_df.drop(shareholders_df.columns[[4]], axis=1)
                shareholders_df = pd.DataFrame(shareholders_df)
                shareholders_df.rename(columns={'سهامدار/دارنده': 'سهامداران عمده'})

                shareholder_sum = float(shareholders_df['درصد'].astype(float).sum())

                shareholder = {
                    "shareholder_sum": round(shareholder_sum, 2),
                    "floating": round(100.0 - shareholder_sum, 2),
                    "shareholders": shareholders_df.to_html().replace('<table border="1" class="dataframe">', '').replace(
                        '</table>', '')
                        .replace('<tbody>', '<tbody class="cart-item">').replace('<tr style="text-align: right;">', '<tr>'),
                }
                return shareholder
            except:
                print('خطا در برقراری ارتباط لطفا 5 ثانیه صبر کنید تا برطرف شود')
                x = jdatetime.datetime.now()
                y = x + jdatetime.timedelta(seconds=5)
                while jdatetime.datetime.now() < y:
                    time.sleep(1)

    @property
    def get_ticker(self) -> Dict[str, Dict[str, Any]]:
        url = f"http://www.tsetmc.com/tsev2/data/instinfofast.aspx?i={self.ID_InsCode}&c=57+"
        response = requests.get(url, timeout=self.timeout).text

        res = tse_split(response)

        if 'A' in res[0][1]:
            waz = 'مجاز'
        elif 'IS' in res[0][1]:  # مجاز-متوقف    مجاز-مسدود      مجاز-محفوظ
            waz = 'ممنوع-متوقف'
        elif 'I' in res[0][1]:
            waz = 'ممنوع'
        else:
            waz = ""

        date = jdatetime.datetime.strptime(f'{int(res[0][12])}', '%Y%m%d').date()
        jdate = jdatetime.GregorianToJalali(date.year, date.month, date.day)
        jdate = f'{jdate.jyear}/{jdate.jmonth}/{jdate.jday}'

        jtime = res[0][13]
        if not re.search('^1', jtime):
            jtime = f'0{int(res[0][13])}'
        jtime = jdatetime.datetime.strptime(f'{jtime}', '%H%M%S').time()

        data = {
            'Full_Name': self.Full_Name,
            'Group_Name': self.Group_Name,
            'Id_Shareholders': self.ID_Shareholders,
            'Update_hours': res[0][0],
            'High': '{:,}'.format(int(res[0][6])),
            'Close': '{:,}'.format(int(res[0][2])),
            'Open': '{:,}'.format(int(res[0][4])),
            'Low': '{:,}'.format(int(res[0][7])),
            'AdjClose': '{:,}'.format(int(res[0][3])),
            'Percent_Close': round((((int(res[0][2]) - int(res[0][5])) / int(res[0][5])) * 100), 2),
            'Percent_AdjClose': round((((int(res[0][3]) - int(res[0][5])) / int(res[0][5])) * 100), 2),
            'Yesterday_Close': '{:,}'.format(int(res[0][5])),
            'Count': '{:,}'.format(int(res[0][8])),
            'Value': '{:,}'.format(int(res[0][10])),
            'Volume': '{:,}'.format(int(res[0][9])),
            'Date_of_last': str(jdate),
            'Hour_of_last': str(jtime),
            'Condition': waz,
        }
        if res[2][0] != '':
            li_res_2 = []
            for i in range(len(res[2])):
                if res[2][i] != '':
                    li_res_2.append([])
                    for x in range(-len(res[2][i]) + 1, 1):
                        x = abs(x)
                        li_res_2[i].append('{:,}'.format(int(res[2][i][x])))
            data.update({
                'Table_BayAndSell': list(map(list, zip(*li_res_2)))
            })
        if res[4] != ['']:
            data.update({
                'Real_count_buy': '{:,}'.format(int(res[4][5])),
                'Real_count_sell': '{:,}'.format(int(res[4][8])),
                'Real_buy': '{:,}'.format(int(res[4][0])),
                'Real_sell': '{:,}'.format(int(res[4][3])),
                'Legal_count_buy': '{:,}'.format(int(res[4][6])),
                'Legal_count_sell': '{:,}'.format(int(res[4][9])),
                'Legal_buy': '{:,}'.format(int(res[4][1])),
                'Legal_sell': '{:,}'.format(int(res[4][4])),
            })

            url = f'http://www.tsetmc.com/tsev2/chart/data/IntraDayPrice.aspx?i={self.ID_InsCode}'
            chart = _loop_(requests.get(url, timeout=self.timeout).text)
            data.update({'chart_day': tse_split(chart)})
        return data

    @property
    def get_ticker_other(self) -> Dict[str, Dict[str, Any]]:
        url = f"http://tsetmc.com/Loader.aspx?ParTree=151311&i={self.ID_InsCode}"
        response = requests.get(url, timeout=self.timeout).text

        adj_close = float(self.get_ticker['AdjClose'].replace(',', ''))

        try:
            eps = round(float(re.findall(r"EstimatedEPS='([-,\d]*)',", response)[0]), 2)
            p_e_ratio = round(adj_close / eps, 2)
            group_p_e_ratio = round(float(re.findall(r"SectorPE='([\d.]*)',", response)[0]), 2)
        except:
            eps = 'موجود نیست.'
            p_e_ratio = 'موجود نیست.'
            group_p_e_ratio = 'موجود نیست.'

        base_volume = float(re.findall(r"BaseVol=([-,\d]*),", response)[0])
        instrument_id = re.findall(r"InstrumentID='([\w\d]*)|',$", response)[0]

        data = {
            'Id_Original': instrument_id,
            'Base_Volume': '{:,}'.format(int(base_volume)),
            'P_E': p_e_ratio,
            'P_E_Group': group_p_e_ratio,
            'EPS': eps,
        }
        return data

    @property
    def history(self) -> Dict[str, Dict[str, Any]]:
        index = 0
        while index != 1:
            try:
                url = f"http://tsetmc.com/tsev2/data/Export-txt.aspx?t=i&a=1&b=0&i={self.ID_InsCode}"
                response = requests.get(url, timeout=self.timeout).text

                data = StringIO(response)
                df: pd.DataFrame = pd.read_csv(data)
                df = df.iloc[::-1]
                df = df.drop(columns=["<PER>", "<TICKER>"])
                _adjust_data_frame(df, '<DTYYYYMMDD>')

                if self.Limitations_Date is not None:
                    df = df[df['jdate'] > jdatetime.datetime.strptime(f'{self.Limitations_Date}', '%Y-%m-%d').date()]
                if self.Limitations_Len is not None:
                    df = df.tail(self.Limitations_Len)

                df['percent_close'] = (((df['<LAST>'] - df['<OPEN>']) / df['<OPEN>']) * 100).round(
                    2)  # .astype(str) + '%'
                df['percent_adjClose'] = (((df['<CLOSE>'] - df['<OPEN>']) / df['<OPEN>']) * 100).round(
                    2)  # .astype(str) + '%'

                df_list = {
                    "Date": (df['jdate'].astype(str)).tolist(),
                    "Date_M": (df['<DTYYYYMMDD>'].astype(str)).tolist(),
                    "Open": df['<FIRST>'].tolist(),
                    "High": df['<HIGH>'].tolist(),
                    "Low": df['<LOW>'].tolist(),
                    "Close": df['<LAST>'].tolist(),
                    "Percent_Close": df['percent_close'].tolist(),
                    "AdjClose": df['<CLOSE>'].tolist(),
                    "Percent_AdjClose": df['percent_adjClose'].tolist(),
                    "Yesterday_price": df['<OPEN>'].tolist(),
                    "Volume": df['<VOL>'].tolist(),
                    "Count": df['<OPENINT>'].tolist(),
                    "Value": df['<VALUE>'].tolist(),
                }
                index += 1
                return df_list
            except:
                print('خطا در برقراری ارتباط لطفا 5 ثانیه صبر کنید تا برطرف شود')
                x = jdatetime.datetime.now()
                y = x + jdatetime.timedelta(seconds=5)
                while jdatetime.datetime.now() < y:
                    time.sleep(1)


    @property
    def client_types_records(self):
        index = 0
        while index != 1:
            try:
                url = f"http://www.tsetmc.com/tsev2/data/clienttype.aspx?i={self.ID_InsCode}"
                response = requests.get(url, timeout=self.timeout).text

                data = [row.split(",") for row in response.split(";")]

                if data != [[""]]:
                    client_frame = pd.DataFrame(data, columns=[
                        "date", "individual_buy_count", "corporate_buy_count", "individual_sell_count",
                        "corporate_sell_count", "individual_buy_vol", "corporate_buy_vol",
                        "individual_sell_vol", "corporate_sell_vol", "individual_buy_value",
                        "corporate_buy_value", "individual_sell_value", "corporate_sell_value"
                    ])
                    for i in ["individual_buy_", "individual_sell_", "corporate_buy_", "corporate_sell_"]:
                        client_frame[f"{i}mean_price"] = (
                                client_frame[f"{i}value"].astype(float) / client_frame[f"{i}vol"].astype(float)
                        ).astype(float)

                    client_frame["individual_ownership_change"] = (
                            client_frame["corporate_sell_vol"].astype(float) - client_frame["corporate_buy_vol"].astype(float)
                    ).astype(float)

                    df = client_frame
                    df = df.iloc[::-1]
                    _adjust_data_frame(df, 'date')

                    if self.Limitations_Date is not None:
                        df = df[df['jdate'] > jdatetime.datetime.strptime(f'{self.Limitations_Date}', '%Y-%m-%d').date()]
                    if self.Limitations_Len is not None:
                        df = df[-self.Limitations_Len:]
                    df = df.iloc[::-1]

                    df['date'] = df['date'].astype(str)
                    df['individual_buy_count'] = df['individual_buy_count'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)
                    df['corporate_buy_count'] = df['corporate_buy_count'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)
                    df['individual_sell_count'] = df['individual_sell_count'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)
                    df['corporate_sell_count'] = df['corporate_sell_count'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)
                    df['individual_buy_vol'] = df['individual_buy_vol'].fillna(0).astype(float).astype(int).apply('{:,}'.format)
                    df['corporate_buy_vol'] = df['corporate_buy_vol'].fillna(0).astype(float).astype(int).apply('{:,}'.format)
                    df['individual_sell_vol'] = df['individual_sell_vol'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)
                    df['corporate_sell_value'] = df['corporate_sell_value'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)

                    df['corporate_sell_vol'] = df['corporate_sell_vol'].fillna(0).astype(float).astype(int).apply('{:,}'.format)
                    df['individual_buy_value'] = df['individual_buy_value'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)
                    df['corporate_buy_value'] = df['corporate_buy_value'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)
                    df['individual_sell_value'] = df['individual_sell_value'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)

                    df['individual_buy_mean_price'] = df['individual_buy_mean_price'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)
                    df['individual_sell_mean_price'] = df['individual_sell_mean_price'].fillna(0).astype(float).astype(
                        int).apply('{:,}'.format)
                    df['corporate_buy_mean_price'] = df['corporate_buy_mean_price'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)
                    df['corporate_sell_mean_price'] = df['corporate_sell_mean_price'].fillna(0).astype(float).astype(int).apply(
                        '{:,}'.format)
                    df['individual_ownership_change'] = df['individual_ownership_change'].fillna(0).astype(float).astype(
                        int).apply('{:,}'.format)

                    df = df.reindex(['jdate'] + list(df.columns[:-1]), axis=1)
                    # df.index = df['jdate'].values
                    df.rename(columns={
                        'jdate': 'تاریخ شمسی',
                        'date': 'تاریخ میلادی',
                        'individual_buy_count': 'تعداد معاملات خرید حقیقی',
                        'corporate_buy_count': 'تعداد معلاملات خرید حقوقی',
                        'individual_sell_count': 'تعداد معاملات فروش حقیقی',
                        'corporate_sell_count': 'تعداد معلاملات فروش حقوقی',

                        'individual_buy_vol': 'حجم خرید حقیقی',
                        'corporate_buy_vol': 'حجم خرید حقوقی',
                        'individual_sell_vol': 'حجم فروش حقیقی',
                        'corporate_sell_value': 'حجم فروش حقوقی',

                        'corporate_sell_vol': 'مقدار سهم فروش حقوقی',
                        'individual_buy_value': 'مقدار سهم خرید حقیقی',
                        'corporate_buy_value': 'مقدار سهم خرید حقوقی',
                        'individual_sell_value': 'مقدار سهم فروش حقیقی',

                        'individual_buy_mean_price': 'قیمت میانگین خرید حقیقی',
                        'individual_sell_mean_price': 'قیمت میانگین فروش حقیقی',
                        'corporate_buy_mean_price': 'قیمت میانگین خرید حقوقی',
                        'corporate_sell_mean_price': 'قیمت میانگین فروش حقوقی',
                        'individual_ownership_change': 'تغییر مالکیت حقوقی به حقیقی',
                    }, inplace=True)

                    df = df.to_html().replace('<table border="1" class="dataframe">', '').replace('</table>', '') \
                        .replace('<tbody>', '<tbody class="cart-item">').replace('<tr style="text-align: right;">', '<tr>')
                    index += 1
                    return df
            except:
                print('خطا در برقراری ارتباط لطفا 5 ثانیه صبر کنید تا برطرف شود')
                x = jdatetime.datetime.now()
                y = x + jdatetime.timedelta(seconds=5)
                while jdatetime.datetime.now() < y:
                    time.sleep(1)


def update_history(Real_legal_sales: bool = True) -> Dict[str, Dict[str, Any]]:
    url = "http://www.tsetmc.com/tsev2/data/MarketWatchInit.aspx?h=0&r=0"
    page_body = to_farsi(_loop_(requests.get(url, timeout=30).text))

    InsCode = {}
    data = {}
    page_body = page_body.split("@")
    body_0 = page_body[1].split(',')
    date = body_0[0].split(' ')

    symbols_data = page_body[2].split(";")
    for symbols in symbols_data:
        symbol = symbols.split(",")

        eps = "" if symbol[14] == "" else int(symbol[14])
        Price_Change_AdjClose = float(symbol[6]) - float(symbol[13])
        Percent_AdjClose = round(100 * Price_Change_AdjClose / float(symbol[13]), 2)
        Price_Change_Close = float(symbol[7]) - float(symbol[13])
        Percent_Close = round(100 * Price_Change_Close / float(symbol[13]), 2)
        try:
            P_E = round(float(symbol[6]) / float(symbol[14]), 2)
        except:
            P_E = ""

        name = to_farsi(symbol[2])
        InsCode.update({symbol[0]: name})
        jtime = symbol[4]
        if not re.search('^1', jtime):
            jtime = f'0{jtime}'
        jtime = jdatetime.datetime.strptime(f'{jtime}', '%H%M%S').time()

        data.update({symbol[0]: {
            'Time_of_last': jtime,
            'InsCode': symbol[0],
            'Name': name,
            'Full_Name': to_farsi(symbol[3]),
            'Group_Name': symbol[18],
            'Id_Shareholders': symbol[1],
            'High': int(symbol[12]),
            'Close': int(symbol[7]),
            'Open': int(symbol[5]),
            'Low': int(symbol[11]),
            'AdjClose': int(symbol[6]),
            'Yesterday_Price': int(symbol[13]),
            'Price_Change_AdjClose': "" if eps == "" else int(Price_Change_AdjClose),
            'Percent_AdjClose': "" if eps == "" else round(Percent_AdjClose, 2),
            'Price_Change_Close': "" if eps == "" else int(Price_Change_Close),
            'Percent_Close': "" if eps == "" else round(Percent_Close, 2),

            'Threshold_High': round(float(symbol[19])),
            'Threshold_Low': round(float(symbol[20])),
            'Count_Shares': round(float(symbol[21])),

            'Count': int(symbol[8]),
            'Value': int(symbol[10]),
            'Volume': int(symbol[9]),

            'Base_Volume': int(symbol[15]),

            'Eps': "" if eps == "" else float(eps),
            'P_E': "" if P_E == "" else float(P_E),
            'visitcount': int(symbol[16]),
            'flow': int(symbol[17]),
            'yval': int(symbol[22]),
        }})

    bay_and_sell = {}
    symbols_data = page_body[3].split(";")
    for symbols in symbols_data:
        symbol = symbols.split(",")
        bay_sell = bay_and_sell.get(symbol[0])
        if bay_sell is not None:
            bay_sell.update({symbol[1]: [
                '{:,}'.format(int(symbol[2])), '{:,}'.format(int(symbol[7])),
                '{:,}'.format(int(symbol[5])), '{:,}'.format(int(symbol[4])),
                '{:,}'.format(int(symbol[6])), '{:,}'.format(int(symbol[3]))
            ]})

            # if len(bay_sell.keys()) == 5:
            #     data_symbol = data.get(symbol[0])
            #     if data_symbol:
            #         data_symbol.update(
            #             dict(Table_BayAndSell=list(map(list, zip(*dict(sorted(bay_sell.items())).values()))))
            #         )
        else:
            bay_and_sell.update({symbol[0]: {symbol[1]: [
                '{:,}'.format(int(symbol[2])), '{:,}'.format(int(symbol[7])),
                '{:,}'.format(int(symbol[5])), '{:,}'.format(int(symbol[4])),
                '{:,}'.format(int(symbol[6])), '{:,}'.format(int(symbol[3]))
            ]}})

    for code, bay_sell in bay_and_sell.items():
        data_symbol = data.get(code)
        if data_symbol is not None:
            data_symbol.update(
                dict(Table_BayAndSell=list(map(list, zip(*dict(sorted(bay_sell.items())).values()))))
            )


    if Real_legal_sales:
        url = "http://www.tsetmc.com/tsev2/data/ClientTypeAll.aspx"
        client_type_body = to_farsi(_loop_(requests.get(url, timeout=30).text))

        symbols_data = client_type_body.split(";")
        for symbols in symbols_data:
            symbol = symbols.split(",")
            data_symbol = data.get(symbol[0])
            if data_symbol is not None:
                data_symbol.update({
                    'Real_count_buy': '{:,}'.format(int(symbol[1])),
                    'Real_count_sell': '{:,}'.format(int(symbol[5])),
                    'Real_buy': '{:,}'.format(int(symbol[3])),
                    'Real_sell': '{:,}'.format(int(symbol[7])),
                    'Legal_count_buy': '{:,}'.format(int(symbol[2])),
                    'Legal_count_sell': '{:,}'.format(int(symbol[6])),
                    'Legal_buy': '{:,}'.format(int(symbol[4])),
                    'Legal_sell': '{:,}'.format(int(symbol[8])),
                })

    output = {}
    jdate = date[0].split('/')
    jdate_0 = jdate[0]
    date_now = str(jdatetime.datetime.now().strftime('%Y'))
    if not re.search(f'^{date_now[:2]}', jdate_0):
        jdate_0 = f'{date_now[:2]}{jdate_0}'
    jdate = jdatetime.datetime.strptime(f'{jdate_0}-{jdate[1]}-{jdate[2]}', '%Y-%m-%d').date()
    date_m = jdatetime.JalaliToGregorian(jdate.year, jdate.month, jdate.day).getGregorianList()
    date_m = jdatetime.datetime.strptime(f'{date_m[0]}-{date_m[1]}-{date_m[2]}', '%Y-%m-%d')

    output.update({'Datetime': {
        'Date': jdate.strftime("%Y-%m-%d"),
        'Date_M': date_m.strftime("%Y-%m-%d"),
        'Time': date[1],
    }})
    for inscode, name in InsCode.items():
        val = data.get(inscode)
        output.update({name: val})

    return output


def Total_stock_index(timeout=30) -> Dict[str, Dict[str, Any]]:
    url = f"http://www.tsetmc.com/tsev2/chart/data/Index.aspx?i=32097828799138957&t=value"
    response = _loop_(requests.get(url, timeout=timeout).text.replace('/', '-'))
    res = tse_split(response)
    df = pd.DataFrame(res, columns=['Date', 'Close'])
    df['Close'] = df['Close'].astype(float)
    Percent_Close = []
    Date_M = []
    for i in range(len(df)):
        Percent_Close.append(round(((df['Close'][i] - df['Close'][i - 1]) / df['Close'][i - 1]) * 100, 2))
        date = df['Date'][i - 1].split('-')
        date = jdatetime.JalaliToGregorian(date[0], date[1], date[2]).getGregorianList()
        Date_M.append(f'{date[0]}-{date[1]}-{date[2]}')

    result = {
        'Date': df['Date'].tolist(),
        'Date_M': Date_M,
        'Percent_Close': Percent_Close,
        'Close': df['Close'].tolist(),
    }
    return result


def get_symbol_history(Symbol):
    Symbol_InsCode = Ticker_To_InsCode(Symbol)
    inscode = Symbol_InsCode[3]
    url = f"http://www.tsetmc.com/tsev2/data/Export-txt.aspx?t=i&a=1&b=0&i={inscode}"
    symbol_history_raw = _loop_(requests.get(url, timeout=30).text)
    data = filter(lambda x: len(x) > 11, map(lambda row: row.split(","), symbol_history_raw.split("\r\n")[1:]))
    parsed_data = dict(map(lambda x: (x[1], {
        "Date": x[1],
        "FIRST": float(x[2]),
        "HIGH": float(x[3]),
        "LOW": float(x[4]),
        "CLOSE": float(x[5]),
        "VALUE": float(x[6]),
        "VOL": float(x[7]),
        "OPENINT": float(x[8]),
        "PER": x[9],
        "OPEN": float(x[10]),
        "LAST": float(x[11])}), data)
                       )
    return parsed_data
