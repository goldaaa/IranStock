import os
import json
import requests
from pathlib import Path
import pandas as pd
import jdatetime
from datetime import datetime, timedelta

TSE_dir = Path(__file__).resolve().parent
FILE_SYMBOLS = os.path.normpath(str(TSE_dir) + '/data' + "/tehran_stock.csv")
ERROR_CONNECTION_API = "در ارتباط با شبکه مشکلی به وجود آمد لطفا دوباره تلاش کنید."


def request_tadbirrlc(handler: str, data, format_ashx: bool = False,
                      api_core: bool = False, api_rlcchart: bool = False,
                      loop_Fixed_error=1, timeout=30):
    url_tadbir = "tadbirrlc.com"
    if api_core:
        url = "core." + url_tadbir + "//"
    elif api_rlcchart:
        url = "rlcchartapi." + url_tadbir + "/"
    else:
        url = url_tadbir + "/"

    if format_ashx:
        url = url + f"{handler}.ashx?"
    else:
        url = url + f"{handler}?"

    if type(data) == dict:
        url = url + json.dumps(data, separators=(',', ':'))
    else:
        url = url + data

    url = 'https://' + url

    num = 0
    while True:
        num += 1
        try:
            result = json.loads(to_farsi(requests.get(url, timeout=timeout).text))
            break
        except:
            print(f'{num}-{str(jdatetime.datetime.now())} : error connection tadbirrlc...')
            if num == loop_Fixed_error:
                result = None
                break
    return result


def to_arabic(string: str):
    return string.replace('ک', 'ك').replace('ی', 'ي').strip()


def to_farsi(string: str):
    return string.replace('ك', 'ک').replace('ي', 'ی').replace('\u200c', ' ').strip()


def _adjust_data_frame(df, column: str):
    df['jdate'] = pd.to_datetime(df[column], infer_datetime_format=True).apply(
        lambda gregorian: jdatetime.date.fromgregorian(date=gregorian))


def create_symbols(timeout=30, loop_Fixed_error=-1):
    groups = {}
    Category = request_tadbirrlc("StocksHandler", {
        "Type": "sectors",
        "la": 'fa',
    }, format_ashx=True, api_core=True, loop_Fixed_error=loop_Fixed_error, timeout=timeout)
    Symbols = request_tadbirrlc("StocksHandler", {
        "Type": "allSymbols",
        "la": 'fa',
    }, format_ashx=True, api_core=True, loop_Fixed_error=loop_Fixed_error, timeout=timeout)
    for res in Category:
        groups.update({res['SectorCode']: res['SectorName']})

    Group_Symbols = []
    for i in range(len(Symbols)):
        Symbol = Symbols[i]
        if Symbol.get("sc") in groups.keys():
            group_name = groups[Symbol["sc"]]
        else:
            group_name = "سایر"

        Group_Symbols.append({
            "Name_FA": Symbol["sf"],
            "Name_EN": Symbol["se"],
            "Full_Name": Symbol["cn"],
            "InsCode": Symbol["nc"],
            "Group_Name": group_name,
            "Group_Id": Symbol["sc"],
        })

    result = pd.DataFrame(Group_Symbols)
    result = result.sort_values('Group_Id')
    result.reset_index(drop=True, inplace=True)
    result.to_csv(FILE_SYMBOLS)
    return result


def Test_File_Symbols():
    if os.path.isfile(FILE_SYMBOLS):
        result = pd.read_csv(FILE_SYMBOLS, index_col=[0])
    else:
        result = create_symbols()
    return result


def Pages_Symbols(page: int = 0, paginator: int = 8, bottom_len=6):
    df = Test_File_Symbols()
    len_df = len(df)

    max_page = len_df / paginator
    if type(max_page) == float: max_page = int(max_page) + 1

    paginator = paginator - 1
    num_page = (paginator * page) + (page - 1)

    is_min_page, is_max_page = True, True
    if page <= 0:
        is_min_page = False
    elif page >= max_page:
        is_max_page = False

    total_paginated = True
    if len_df <= paginator: total_paginated = False

    df = df.loc[num_page-paginator:num_page].to_dict(orient='records')

    _bottom_ = int(bottom_len / 2)
    if _bottom_ > page:
        range_min, range_max = page, page + bottom_len
    elif max_page > page:
        range_min, range_max = page - _bottom_, page + _bottom_
    else:
        range_min, range_max = page - bottom_len, page

    context = {
        'num_list': {'range': [i for i in range(range_min, range_max)], 'page': page, 'min': 1, 'max': max_page},
        'is_paginated': {'has_total': total_paginated, 'has_previous': is_min_page, 'has_next': is_max_page},
        'value': df,
    }
    return context


def Search_Symbols(Symbol: str):
    """Symbols Search"""
    df = Test_File_Symbols()
    df = df[df.Name_FA.str.contains(Symbol, regex=False, case=False, na=False)]
    return df.to_dict(orient='records')


def View_Symbol(Symbol_FA=False, Symbol_EN=False, InsCode=False):
    """View Symbol Data"""
    Data = Test_File_Symbols()
    if Symbol_FA: Data = Data[Data.Name_FA == Symbol_FA]
    elif Symbol_EN: Data = Data[Data.Name_EN == Symbol_EN]
    elif InsCode: Data = Data[Data.InsCode == InsCode]

    if list(Data.index):
        return Data.loc[Data.index[0]]
    else:
        return None


def Symbol_TO_InsCode(symbol, timeout=30, loop_Fixed_error=1):
    result = request_tadbirrlc(
        'ChartData/symbols',
        f"symbol={symbol}",
        api_rlcchart=True, loop_Fixed_error=loop_Fixed_error, timeout=timeout
    )
    if result:
        return result
    else:
        return ERROR_CONNECTION_API


class All_Tickers:
    def __init__(self, loop_Fixed_error=1, timeout: int = 30):
        self.timeout = timeout
        self.loop_Fixed_error = loop_Fixed_error


    @property
    def Market_Index(self):
        result = request_tadbirrlc("AlmasDataHandler", {
            "Type": "IndexInfoLast",
            "la": 'fa',
            "isin": ['IRX6XTPI0006', 'IRXZXOCI0006', 'IRX6XSLC0006', 'IRX6XS300006', 'IRXYXTPI0026'],
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if result:
            df = pd.DataFrame(result['IndexHistoricalDataResult']).T
            df.reset_index(drop=True, inplace=True)
            return result
        else:
            return ERROR_CONNECTION_API

    @property
    def MarketEntire(self):
        result = request_tadbirrlc("StocksHandler", {
            "Type": "ALL21",
            "la": 'fa',
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, api_core=True, timeout=self.timeout)
        if result:
            result = pd.DataFrame(result)
            return result
        else:
            return ERROR_CONNECTION_API

    def MarketMap(self, selectedType: str = "asset", sector: str = ""):
        result = request_tadbirrlc("AlmasDataHandler", {
            "Type": "GetMarketMapDataList",
            "la": 'fa',
            "selectedType": selectedType,
            "sector": sector,
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, api_core=True, timeout=self.timeout)
        if result:
            result = pd.DataFrame(result)
            return result
        else:
            return ERROR_CONNECTION_API

    def GroupCompanies(self, InsCode, ToPriceToday=False):
        """
        :param InsCode: IRO3ZMMZ0001
        :param ToPriceToday: True
        :return: {}
        """
        result = request_tadbirrlc("AlmasDataHandler", {
            "Type": "CompaniesGrouped",
            "isin": InsCode,
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if result:
            result = pd.DataFrame(result)
            df = result['Isin'].to_list()
            if ToPriceToday:
                df = self.ListPriceToday(df)
            return df
        else:
            return ERROR_CONNECTION_API

    def ListPriceToday(self, List_InsCode: list):
        List_InsCode = f"{List_InsCode}".replace("['", '').replace("', '", ',').replace("']", '')\
            .replace('["', '').replace('", "', ',').replace('"]', '')
        result = request_tadbirrlc("StockInformationHandler", {
            "Type": "getstockprice2",
            "la": "Fa",
            "arr": List_InsCode,
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if result:
            data = []
            for info in result:
                High_Allowed = int(info["hap"])
                Low_Allowed = int(info["lap"])

                if High_Allowed >= int(info["bsp"]) >= Low_Allowed:
                    ColorSell = '#ff7b7b'
                else:
                    ColorSell = '#d5d5d5'

                if High_Allowed >= int(info["bbp"]) >= Low_Allowed:
                    ColorBuy = '#50d750'
                else:
                    ColorBuy = '#d5d5d5'

                date_time = info['td'].split(" ")
                Name_FA = str(info['sf']).replace('1', '')
                data.append({
                    'Name_FA': Name_FA,
                    'Full_Name': info['cn'],
                    'InsCode': info['nc'],
                    'InstrumentCode': info['ic'],
                    'Testmc': f"http://www.tsetmc.com/Loader.aspx?ParTree=151311&i={info['ic']}",
                    'Codal': f"http://codal.ir/ReportList.aspx?search&Symbol={Name_FA}",
                    'Date': str(date_time[0]),
                    'Time': str(date_time[1]),
                    'Close': '{:,}'.format(int(info["ltp"])),
                    'Open': '{:,}'.format(int(info["ftp"])),
                    'High': '{:,}'.format(int(info["hp"])),
                    'Low': '{:,}'.format(int(info["lp"])),
                    'AdjClose': '{:,}'.format(int(info["cp"])),
                    'Amount_Close': '{:,}'.format(int(info["lpv"])),
                    'Percent_Close': info["lpvp"],
                    'Amount_AdjClose': '{:,}'.format(int(info["cpv"])),
                    'Percent_AdjClose': info["cpvp"],
                    'High_Allowed': '{:,}'.format(int(info["hap"])),
                    'Low_Allowed': '{:,}'.format(int(info["lap"])),
                    'Yesterday_Close': '{:,}'.format(int(info["rp"])),
                    'Count': '{:,}'.format(int(info["nt"])),
                    'Value': '{:,}'.format(int(info["tv"])),
                    'Volume': '{:,}'.format(int(info["nst"])),
                    'Max_volume_threshold': '{:,}'.format(int(info["mxqo"])),
                    'Min_volume_threshold': '{:,}'.format(int(info["mnqo"])),
                    'Table_PriceBuy_1': '{:,}'.format(int(info["bbp"])),
                    'Table_PriceSell_1': '{:,}'.format(int(info["bsp"])),
                    'Table_VolumeSell_1': '{:,}'.format(int(info["bsq"])),
                    'Table_VolumeBuy_1': '{:,}'.format(int(info["bbq"])),
                    'Table_CountBuy_1': '{:,}'.format(int(info["nbb"])),
                    'Table_CountSell_1': '{:,}'.format(int(info["nbs"])),
                    "Table_ColorBuy_1": ColorBuy,
                    "Table_ColorSell_1": ColorSell,
                })
            return data
        else:
            return ERROR_CONNECTION_API

    @staticmethod
    def StockFiltered(Filter_name: str = "marketwatch", top=6):
        if Filter_name == "visited":
            Type = "getmostvisitedsymbol"
            issell = 0
        elif Filter_name == "buys":
            Type = "gettopqueuesymbol"
            issell = 0
        elif Filter_name == "sells":
            Type = "gettopqueuesymbol"
            issell = 1
        elif Filter_name == "legal_buys":
            Type = "getindinssymbol"
            issell = 0
        elif Filter_name == "legal_sells":
            Type = "getindinssymbol"
            issell = 1
        else:
            Type = "marketwatch"
            top = 0
            issell = 0

        result = request_tadbirrlc(
            "StockFilteredResult", f"Type={Type}&top={top}&issell={issell}",
            api_core=True
        )
        return result


class Ticker:
    def __init__(self, Symbol_FA=False, Symbol_EN=False, InsCode=False, loop_Fixed_error=1, timeout: int = 30):
        self.Symbol_FA = Symbol_FA
        self.Symbol_EN = Symbol_EN
        self.InsCode = InsCode
        self.loop_Fixed_error = loop_Fixed_error
        self.timeout = timeout

    @property
    def Info(self):
        if self.Symbol_FA: symbol = View_Symbol(Symbol_FA=self.Symbol_FA)
        elif self.Symbol_EN: symbol = View_Symbol(Symbol_EN=self.Symbol_EN)
        elif self.InsCode: symbol = View_Symbol(InsCode=self.InsCode)
        else: symbol = None

        data = {}
        if symbol is not None:
            data.update({
                "Name_FA": symbol.Name_FA,
                "Name_EN": symbol.Name_EN,
                "Full_Name": symbol.Full_Name,
                "InsCode": symbol.InsCode,
                "Group_Name": symbol.Group_Name,
                "Group_Id": symbol.Group_Id,
                "Error": False,
            })
        else:
            data.update({'Error': True})
        return data

    @property
    def PriceToday(self):
        result = request_tadbirrlc("StockInformationHandler", {
            "Type": "getstockprice2",
            "la": "Fa",
            "arr": self.Info['InsCode'],
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if result:
            info = result[0]
            date_time = info['td'].split(" ")

            data = {
                'Id_InstrumentCode': info['ic'],
                'Testmc': f"http://www.tsetmc.com/Loader.aspx?ParTree=151311&i={info['ic']}",
                'Codal': f"http://codal.ir/ReportList.aspx?search&Symbol={self.Info['Name_FA']}",
                'Date': str(date_time[0]),
                'Time': str(date_time[1]),
                'Close': '{:,}'.format(int(info["ltp"])),
                'Open': '{:,}'.format(int(info["ftp"])),
                'High': '{:,}'.format(int(info["hp"])),
                'Low': '{:,}'.format(int(info["lp"])),
                'AdjClose': '{:,}'.format(int(info["cp"])),
                'Amount_Close': '{:,}'.format(int(info["lpv"])),
                'Percent_Close': info["lpvp"],
                'Amount_AdjClose': '{:,}'.format(int(info["cpv"])),
                'Percent_AdjClose': info["cpvp"],
                'High_Allowed': '{:,}'.format(int(info["hap"])),
                'Low_Allowed': '{:,}'.format(int(info["lap"])),
                'Yesterday_Close': '{:,}'.format(int(info["rp"])),
                'Count': '{:,}'.format(int(info["nt"])),
                'Value': '{:,}'.format(int(info["tv"])),
                'Volume': '{:,}'.format(int(info["nst"])),
                'Max_volume_threshold': '{:,}'.format(int(info["mxqo"])),
                'Min_volume_threshold': '{:,}'.format(int(info["mnqo"])),
                'Table_PriceBuy_1': '{:,}'.format(int(info["bbp"])),
                'Table_PriceSell_1': '{:,}'.format(int(info["bsp"])),
                'Table_VolumeSell_1': '{:,}'.format(int(info["bsq"])),
                'Table_VolumeBuy_1': '{:,}'.format(int(info["bbq"])),
                'Table_CountBuy_1': '{:,}'.format(int(info["nbb"])),
                'Table_CountSell_1': '{:,}'.format(int(info["nbs"])),
            }
            return data
        else:
            return ERROR_CONNECTION_API

    @property
    def PriceToday2(self):
        result = request_tadbirrlc("StockFutureInfoHandler", {
            "Type": "getLightSymbolFullInfo",
            "la": 'Fa',
            "nscCode": self.Info['InsCode'],
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if result:
            info = result
            date_time = info['ltd'].split(" - ")

            if info["mt"] == "MarketType.ExchangeStock":
                MarketType = "بورس"
            elif info["mt"] == "MarketType.FaraBourseStock":
                MarketType = "فرابورس"
            else:
                MarketType = "ثبت نشده است"

            Condition = "ثبت نشده است"

            data = {
                'Date': str(date_time[0]),
                'Time': str(date_time[1]),
                'Close': '{:,}'.format(int(info["ltp"])),
                'High': '{:,}'.format(int(info["hp"])),
                'Low': '{:,}'.format(int(info["lp"])),
                'AdjClose': '{:,}'.format(int(info["cp"])),
                'Amount_Close': '{:,}'.format(int(info["lpv"])),
                'Percent_Close': info["lpvp"],
                'Amount_AdjClose': '{:,}'.format(int(info["cpv"])),
                'Percent_AdjClose': info["cpvp"],
                'High_Allowed': '{:,}'.format(int(info["ht"])),
                'Low_Allowed': '{:,}'.format(int(info["lt"])),
                'High_Tomorrow_threshold': '{:,}'.format(int(info["th"])),
                'Low_Tomorrow_threshold': '{:,}'.format(int(info["tl"])),
                'Yesterday_Close': '{:,}'.format(int(info["rp"])),
                'Count': '{:,}'.format(int(info["nt"])),
                'Value': '{:,}'.format(int(info["tv"])),
                'Volume': '{:,}'.format(int(info["nst"])),
                'Base_volume': '{:,}'.format(int(info["bv"])),
                # 'Max_volume_threshold': '{:,}'.format(int(info["mxp"])),
                # 'Min_volume_threshold': '{:,}'.format(int(info["minprod"])),
                'MarketType': MarketType,
                'Condition': Condition,
            }
            return data
        else:
            return ERROR_CONNECTION_API

    @property
    def Row_PriceToday(self):
        res = request_tadbirrlc("StockInformationHandler", {
            "Type": "3",
            "SyID": self.Info['InsCode'],
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if res:
            date_time = res[0][10].split(" ")

            data = {
                'Date': str(date_time[0]),
                'Time': str(date_time[1]),
                'High': '{:,}'.format(int(res[0][11])),
                'Close': '{:,}'.format(int(res[0][8])),
                'Open': '{:,}'.format(int(res[0][15])),
                'Low': '{:,}'.format(int(res[0][12])),
                'AdjClose': '{:,}'.format(int(res[0][2])),  # res[0][9]
                'Percent_Close': float(res[0][13]),
                'Percent_AdjClose': round((((int(res[0][2]) - int(res[0][16])) / int(res[0][16])) * 100), 2),
                'Yesterday_Close': '{:,}'.format(int(res[0][16])),  # res[0][17]
                'High_Allowed': '{:,}'.format(int(res[0][3])),
                'Low_Allowed': '{:,}'.format(int(res[0][4])),
                'Based_Volume_Avg30': '{:,}'.format(int(res[0][22])),
            }
            return data
        else:
            return ERROR_CONNECTION_API

    @property
    def Table_BuyAndSell(self):
        res = request_tadbirrlc("StockInformationHandler", {
            "Type": "1",  # 1, 2, 3
            "SyID": self.Info['InsCode'],
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if res:
            return res['Value']
        else:
            return ERROR_CONNECTION_API

    @property
    def PriceToday_And_TableBuyAndSell(self):
        result = request_tadbirrlc("StockFutureInfoHandler", {
            "Type": "getLightSymbolInfoAndQueue",
            "la": 'Fa',
            "nscCode": self.Info['InsCode'],
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, api_core=True, timeout=self.timeout)
        if result:
            info = result['symbolinfo']
            queue = result['symbolqueue']['Value']
            date_time = info['ltd'].split(" - ")

            if info["ltp"] == "MarketType.ExchangeStock":
                MarketType = "بورس"
            elif info["ltp"] == "MarketType.FaraBourseStock":
                MarketType = "فرابورس"
            else:
                MarketType = "ثبت نشده است"

            Condition = "ثبت نشده است"

            data = {
                'Id_InstrumentCode': info['ic'],
                'Date': str(date_time[0]),
                'Time': str(date_time[1]),
                'Close': '{:,}'.format(int(info["ltp"])),
                'High': '{:,}'.format(int(info["hp"])),
                'Low': '{:,}'.format(int(info["lp"])),
                'AdjClose': '{:,}'.format(int(info["cp"])),
                'Amount_Close': '{:,}'.format(int(info["lpv"])),
                'Percent_Close': info["lpvp"],
                'Amount_AdjClose': '{:,}'.format(int(info["cpv"])),
                'Percent_AdjClose': info["cpvp"],
                'High_Allowed': '{:,}'.format(int(info["ht"])),
                'Low_Allowed': '{:,}'.format(int(info["lt"])),
                'High_Tomorrow_threshold': '{:,}'.format(int(info["th"])),
                'Low_Tomorrow_threshold': '{:,}'.format(int(info["tl"])),
                'Yesterday_Close': '{:,}'.format(int(info["rp"])),
                'Count': '{:,}'.format(int(info["nt"])),
                'Value': '{:,}'.format(int(info["tv"])),
                'Volume': '{:,}'.format(int(info["nst"])),
                'Base_volume': '{:,}'.format(int(info["bv"])),
                'Max_volume_threshold': '{:,}'.format(int(info["mxp"])),
                'Min_volume_threshold': '{:,}'.format(int(info["minprod"])),
                'MarketType': MarketType,
                'Condition': Condition,
                'Table_BuyAndSell': queue,
            }
            return data
        else:
            return ERROR_CONNECTION_API

    @property
    def Real_Legal(self):
        result = request_tadbirrlc("AlmasDataHandler", {
            "Type": "getIndInstTrade",
            "la": 'Fa',
            "nscCode": self.Info['InsCode'],
            "ZeroIfMarketIsCloesed": True,
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, api_core=True, timeout=self.timeout)
        if result:
            data = {
                'Real_count_buy': '{:,}'.format(int(result["IndBuyNumber"])),
                'Real_count_sell': '{:,}'.format(int(result["IndSellNumber"])),
                'Real_buy': '{:,}'.format(int(result["IndBuyVolume"])),
                'Real_sell': '{:,}'.format(int(result["IndSellVolume"])),
                'Legal_count_buy': '{:,}'.format(int(result["InsBuyNumber"])),
                'Legal_count_sell': '{:,}'.format(int(result["InsSellNumber"])),
                'Legal_buy': '{:,}'.format(int(result["InsBuyVolume"])),
                'Legal_sell': '{:,}'.format(int(result["InsSellVolume"])),
            }
            # IndBuyValue: 0
            # IndSellValue: 0
            # InsBuyValue: 0
            # InsSellValue: 0

            # day: "20211016"
            # isin: "IRO3SJSZ0001"
            # tickerFa: ""
            # tickerKey: 0
            # tradeKey: 0

            return data
        else:
            return ERROR_CONNECTION_API

    @property
    def EPS_And_PE(self):
        result = request_tadbirrlc("AlmasDataHandler", {
            "Type": "getSymbolEPSAndPToE",
            "la": 'fa',
            "nscCode": self.Info['InsCode'],
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)

        if result:
            data = {
                'EPS': round(result["EPS"], 2),
                'P_E': round(result["PtoE"], 2),
            }
            return data
        else:
            return ERROR_CONNECTION_API

    @property
    def Fundamental(self):
        result = request_tadbirrlc("AlmasDataHandler", {
            "Type": "getSymbolFundamentalInfo",
            "la": 'Fa',
            "nscCode": self.Info['InsCode'],
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, api_core=True, timeout=self.timeout)
        if result:
            data = {
                'DPS': result["DPS"],
                'DPSVal': '{:,}'.format(int(result["DPSVal"])),
                'Group_P_E': round(float(result["GPE"]), 2),
                'P_E': round(float(result["PE"]), 2),
                'EPS': round(float(result["EPS"]), 2),
                'Efficiency_30': round(float(result["E30"]) * 100, 2),
                'Efficiency_90': round(float(result["E90"]) * 100, 2),
                'Efficiency_180': round(float(result["E180"]) * 100, 2),
                'Efficiency_360': round(float(result["E360"]) * 100, 2),
                'Fiscal_year': result["FYear"],
                'Float_Percent': round(float(result["FloatPercent"]) * 100, 2),
                'Valume30AVG': '{:,}'.format(round(result["Valume30AVG"])),
                'Valume90AVG': '{:,}'.format(round(result["Valume90AVG"])),
                'Valume360AVG': '{:,}'.format(round(result["Valume1yAVG"])),
            }
            return data
        else:
            return ERROR_CONNECTION_API

    @property
    def Fundamental1(self, from_date=str((jdatetime.datetime.now() - timedelta(days=1000)).date()), from_time="00:00:00",
                     to_date=str(jdatetime.datetime.now().date()), to_time="00:00:00"):

        from_date_time = f"{from_date} {from_time}"
        to_date_time = f"{to_date} {to_time}"

        from_date = int(jdatetime.datetime.strptime(f'{from_date_time}', '%Y-%m-%d %H:%M:%S').timestamp())
        to_date = int(jdatetime.datetime.strptime(f'{to_date_time}', '%Y-%m-%d %H:%M:%S').timestamp())

        result = request_tadbirrlc("AlmasDataHandler", {
            "Type": "GetMeetingInfos",
            "la": 'fa',
            "SymbolISINs": self.Info['InsCode'],
            "from": f"{from_date}",
            "to": f"{to_date}",
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if result:
            df = pd.DataFrame(result)
            df["FiscalYear"] = df["FiscalYear"].apply(lambda x: x.replace("/Date(", "").replace(")/", ""))
            df["FiscalYear"] = pd.to_datetime(df["FiscalYear"], unit='ms')  # .dt.strftime('%Y-%m-%d')
            df["FiscalYear"] = pd.to_datetime(df["FiscalYear"], infer_datetime_format=True).apply(
                lambda td: jdatetime.date.fromgregorian(date=td)).astype(str)

            df["PublishDate"] = df["PublishDate"].apply(lambda x: x.replace("/Date(", "").replace(")/", ""))
            df["PublishDate"] = pd.to_datetime(df["PublishDate"], unit='ms')
            df["PublishDate"] = pd.to_datetime(df["PublishDate"], infer_datetime_format=True).apply(
                lambda td: jdatetime.date.fromgregorian(date=td)).astype(str)

            df["MeetingDate"] = df["MeetingDate"].apply(lambda x: x.replace("/Date(", "").replace(")/", ""))
            df["MeetingDate"] = pd.to_datetime(df["MeetingDate"], unit='ms')
            df["MeetingDate"] = pd.to_datetime(df["MeetingDate"], infer_datetime_format=True).apply(
                lambda td: jdatetime.date.fromgregorian(date=td)).astype(str)

            df = df.sort_values('MeetingDate').iloc[::-1]
            df.reset_index(drop=True, inplace=True)

            df_list = []
            for i in range(len(df)):
                loc_df = df.loc[i]

                if loc_df['IsConfirmed']:
                    IsConfirmed = 'بله'
                else:
                    IsConfirmed = 'خیر'

                if loc_df['OnlyForPrevCapital']:
                    OnlyForPrevCapital = 'بله'
                else:
                    OnlyForPrevCapital = 'خیر'

                df_list.append({
                    "FiscalYear": loc_df['FiscalYear'],
                    "MeetingDate": loc_df['MeetingDate'],
                    "PublishDate": loc_df['PublishDate'],
                    "AnnouncementId": loc_df['AnnouncementId'],
                    "AdjustedPrice": loc_df['AdjustedPrice'],
                    "CapitalChangePercent": loc_df['CapitalChangePercent'],
                    "CashIncoming": loc_df['CashIncoming'],
                    "CashIncomingPercent": loc_df['CashIncomingPercent'],
                    "CorporateEventType": loc_df['CorporateEventType'],
                    "DividendPerShare": loc_df['DividendPerShare'],
                    "IsConfirmed": IsConfirmed,
                    "LastShareCount": loc_df['LastShareCount'],
                    "NotAdjustedPrice": loc_df['NotAdjustedPrice'],
                    "OnlyForPrevCapital": OnlyForPrevCapital,
                    "Reserves": loc_df['Reserves'],
                    "ReservesPercent": loc_df['ReservesPercent'],
                    "RetainedEarning": loc_df['RetainedEarning'],
                    "RetainedEarningPercent": loc_df['RetainedEarningPercent'],
                    "SarfSaham": loc_df['SarfSaham'],
                    "SarfSahamPercent": loc_df['SarfSahamPercent'],
                    "SymbolName": loc_df['SymbolName'],
                    "ISIN": loc_df['ISIN'],
                })

            return df_list
        else:
            return ERROR_CONNECTION_API

    @property
    def ETF_NAV(self):
        result = request_tadbirrlc("StockFutureInfoHandler", {
            "Type": "etf",
            "la": 'Fa',
            "nscCode": self.Info['InsCode'],
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, api_core=True, timeout=self.timeout)
        if result:
            return result
        else:
            return ERROR_CONNECTION_API

    @property
    def History_CompactIntraday(self):
        result = request_tadbirrlc("StocksHandler", {
            "Type": "compactintradaychart",
            "la": 'Fa',
            "isin": self.Info['InsCode'],
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, api_core=True, timeout=self.timeout)
        if result:
            return result
        else:
            return ERROR_CONNECTION_API

    def History_Mini(self, PageSize=100, pageIndex=0):
        result = request_tadbirrlc("AlmasDataHandler", {
            "Type": "tradeHistoryMini",
            "SyID": self.Info['InsCode'],
            "pageSize": PageSize,
            "pageIndex": pageIndex,
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if result:
            df = pd.DataFrame(result['TradeHistoryList'])
            df["td"] = df["td"].apply(lambda x: x.replace("/Date(", "").replace(")/", ""))
            df["td"] = pd.to_datetime(df["td"], unit='ms').dt.strftime('%Y-%m-%d')
            df["jtd"] = pd.to_datetime(df["td"], format='%Y-%m-%d').apply(
                lambda td: jdatetime.date.fromgregorian(date=td))

            df_list = {
                "Date": (df['jtd'].astype(str)).tolist(),
                "Date_M": (df['td'].astype(str)).tolist(),
                "Open": df['op'].tolist(),
                "High": df['hp'].tolist(),
                "Low": df['lwp'].tolist(),
                "Close": df['lp'].tolist(),
                "Close_Percent": df['lpv'].tolist(),
                "AdjClose": df['cp'].tolist(),
                "AdjClose_Percent": df['cpv'].tolist(),
                "Volume": df['tvo'].tolist(),
                "Count": df['tc'].tolist(),
                "Value": df['tva'].tolist(),
                "AllLen": result['TotalRecords'],
            }
            return df_list
        else:
            return ERROR_CONNECTION_API

    def History_OHLC(self, Time="23:59:59",
                     StartDate=str((jdatetime.datetime.now() - timedelta(days=365)).date()),
                     EndDate=str(jdatetime.datetime.now().date())):
        """
        :param Time: '23:59:59'
        :param StartDate: '1399-01-01'
        :param EndDate: '1400-07-29'
        :return: {}
        """
        Time = datetime.strptime(Time, "%H:%M:%S").time()
        Time = int(timedelta(hours=Time.hour, minutes=Time.minute, seconds=Time.second).total_seconds())

        result = request_tadbirrlc("AlmasDataHandler", {
            "Type": 'AdjsustedPricesOHLC',
            "la": 'fa',
            "ISIN": self.Info['InsCode'],
            "StartDateTime": StartDate.replace('-', '/'),
            "EndDateTime": EndDate.replace('-', '/'),
            "TimePart": str(Time),
            "MeetingType": "type",
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if result:
            df = pd.DataFrame(result)
            df.drop(columns=["Variation"], inplace=True)
            df["TradeDateTime"] = df["TradeDateTime"].apply(lambda x: x.replace("/Date(", "").replace(")/", ""))
            df["TradeDateTime"] = pd.to_datetime(df["TradeDateTime"], unit='ms').dt.strftime('%Y-%m-%d')
            df["TradeJDateTime"] = pd.to_datetime(df["TradeDateTime"], format='%Y-%m-%d').apply(
                lambda td: jdatetime.date.fromgregorian(date=td))
            df = df.iloc[::-1]
            df.reset_index(drop=True, inplace=True)

            df_list = {
                'Date': df['TradeJDateTime'].to_list(),
                'Date_M': df['TradeDateTime'].to_list(),
                'High': df['High'].to_list(),
                'Low': df['Low'].to_list(),
                'Open': df['Open'].to_list(),
                'Close': df['Close'].to_list(),
                'Count': df['TotalTradeNumber'].to_list(),
                'Volume': df['TotalTradeQuantity'].to_list(),
            }
            return df_list
        else:
            return ERROR_CONNECTION_API

    def History_OHLCPagination(self, Time=None, PageIndex=0, PageSize=10):
        """
        :param Time: '23:59:59'
        :param PageIndex: 1
        :param PageSize: 10
        :return: {}
        """
        if Time:
            Time = datetime.strptime(Time, "%H:%M:%S").time()
            Time = f"{int(timedelta(hours=Time.hour, minutes=Time.minute, seconds=Time.second).total_seconds())}"
        else:
            Time = "86400"      # seconds (1 day)

        result = request_tadbirrlc("AlmasDataHandler", {
            "Type": "GetSavedAdjustedPriceOHLCPagination",
            "la": 'fa',
            "ISIN": str(self.Info['InsCode']),
            "PageIndex": str(PageIndex),
            "PageSize": str(PageSize),
            "TimePart": Time,
        }, format_ashx=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout)
        if result:
            df = pd.DataFrame(result)
            df.drop(columns=["Variation"], inplace=True)
            df["TradeDateTime"] = df["TradeDateTime"].apply(lambda x: x.replace("/Date(", "").replace(")/", ""))
            df["TradeDateTime"] = pd.to_datetime(df["TradeDateTime"], unit='ms').dt.strftime('%Y-%m-%d')
            df["TradeJDateTime"] = pd.to_datetime(df["TradeDateTime"], format='%Y-%m-%d').apply(
                lambda td: jdatetime.date.fromgregorian(date=td))
            df = df.iloc[::-1]
            df.reset_index(drop=True, inplace=True)

            df_list = {
                'Date': df['TradeJDateTime'].to_list(),
                'Date_M': df['TradeDateTime'].to_list(),
                'High': df['High'].to_list(),
                'Low': df['Low'].to_list(),
                'Open': df['Open'].to_list(),
                'Close': df['Close'].to_list(),
                'Count': df['TotalTradeNumber'].to_list(),
                'Volume': df['TotalTradeQuantity'].to_list(),
            }
            return df_list
        else:
            return ERROR_CONNECTION_API


    def History_Chart(self, from_date=str((jdatetime.datetime.now() - timedelta(days=365)).date()), from_time="00:00:00",
                      to_date=str(jdatetime.datetime.now().date()), to_time="00:00:00",
                      Adjustment="", resolution: str = "1D"):
        """
        :param from_date: -> 1400-01-01
        :param from_time: Sample -> 00:00:00
        :param to_date: Sample -> 1401-01-01
        :param to_time: Sample -> 00:00:00
        :param Adjustment: Sample -> 0, 1, 2, 3
        :param resolution: Sample -> "1","5","10","15","30","60","180","D","W","M"
        :return: {}
        """
        if Adjustment != "": Adjustment = f"_{Adjustment}"

        from_date_time = f"{from_date} {from_time}"
        to_date_time = f"{to_date} {to_time}"

        from_date = int(jdatetime.datetime.strptime(f'{from_date_time}', '%Y-%m-%d %H:%M:%S').timestamp())
        to_date = int(jdatetime.datetime.strptime(f'{to_date_time}', '%Y-%m-%d %H:%M:%S').timestamp())
        result = request_tadbirrlc(
            'ChartData/history',
            f"symbol={self.Info['InsCode']}{Adjustment}&resolution={resolution}&from={from_date}&to={to_date}",
            api_rlcchart=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout
        )
        if result:
            df: pd.DataFrame = pd.DataFrame(result)
            df.drop(columns=["s"], inplace=True)
            df["t"] = pd.to_datetime(df["t"], unit='s').dt.strftime('%Y-%m-%d')
            df["jt"] = pd.to_datetime(df["t"], format='%Y-%m-%d').apply(
                lambda td: jdatetime.date.fromgregorian(date=td))

            df_list = {
                "Date": (df['jt'].astype(str)).tolist(),
                "Date_M": (df['t'].astype(str)).tolist(),
                "Open": df['o'].tolist(),
                "High": df['h'].tolist(),
                "Low": df['l'].tolist(),
                "Close": df['c'].tolist(),
                "Value": df['v'].tolist(),
            }
            return df_list
        else:
            return ERROR_CONNECTION_API

    def History_Widget(self, resolution, beforeDays: int, outType: str):
        """
        :param resolution: Sample -> "1","5","10","15","30","60","180","1D","1W","1M"
        :param beforeDays: Sample -> 1, 2, 3, ..., 363, 364, 365, ...   day
        :param outType: Sample -> 'candlestick', 'splineArea'
        :return: {}
        """
        result = request_tadbirrlc(
            'ChartData/priceHistory',
            f"symbol={self.Info['InsCode']}&resolution={resolution}&beforeDays={beforeDays}&outType={outType}",
            api_rlcchart=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout
        )
        if result:
            if outType == 'candlestick':
                data = {
                    "time": [], "open": [], "high": [],
                    "low": [], "close": [],
                }
                for res in result:
                    data["time"].append(res["time"])
                    prices = res["prices"]
                    data["open"].append(prices[0]), data["high"].append(prices[1])
                    data["low"].append(prices[2]), data["close"].append(prices[3])
            elif outType == 'splineArea':
                data = {
                    "time": [], "close": [],
                }
                for res in result:
                    data["time"].append(res["time"])
                    data["close"].append(res["prices"][0])
            else:
                data = {}
                assert "Please check the outType field you filled out."

            result = pd.DataFrame(data)
            result["time"] = pd.to_datetime(result["time"], unit='ms').dt.strftime('%H:%M:%S')

            df_list = {
                'Date': result["time"].astype(str).to_list(),
                'Close': result["close"].to_list(),
            }
            if outType == 'candlestick':
                df_list.update({
                    'Open': result["open"].to_list(),
                    'High': result["high"].to_list(),
                    'Low': result["low"].to_list(),
                })
            return df_list
        else:
            return ERROR_CONNECTION_API

    def Assemblies(self, from_date=str((jdatetime.datetime.now() - timedelta(days=365)).date()), from_time="00:00:00",
                   to_date=str(jdatetime.datetime.now().date()), to_time="00:00:00",
                   Adjustment: str = "", resolution: str = "1"):
        """
        :param from_date: Sample -> 1400-01-01
        :param from_time: Sample -> 00:00:00
        :param to_date: Sample -> 1400-01-01
        :param to_time: Sample -> 00:00:00
        :param Adjustment: Sample -> 0, 1, 2, 3
        :param resolution: Sample -> "1","5","10","15","30","60","180","D","W","M"
        :return: {}
        """
        if Adjustment != "": Adjustment = f"_{Adjustment}"

        from_date_time = f"{from_date} {from_time}"
        to_date_time = f"{to_date} {to_time}"
        from_date = int(jdatetime.datetime.strptime(f'{from_date_time}', '%Y-%m-%d %H:%M:%S').timestamp())
        to_date = int(jdatetime.datetime.strptime(f'{to_date_time}', '%Y-%m-%d %H:%M:%S').timestamp())

        result = request_tadbirrlc(
            'ChartData/marks',
            f"symbol={self.Info['InsCode']}{Adjustment}&from={from_date}&to={to_date}&resolution={resolution}",
            api_rlcchart=True, loop_Fixed_error=self.loop_Fixed_error, timeout=self.timeout
        )
        if result:
            return result
        else:
            return ERROR_CONNECTION_API
