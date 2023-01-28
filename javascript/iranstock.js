// author: "navid nasiri"
// github: "https://github.com/goldaaa"
// gmail: "goldaaa.program@gmail.com"


class Datetime extends Date {
    constructor(format_date='/', format_time=':') {
        super();
        this.f_date = format_date;
        this.f_time = format_time;
        this.options = {
            year: 'numeric', month: 'numeric', day: 'numeric',
            hour: 'numeric', minute: 'numeric', second: 'numeric',
            hour12: false,
            timeZone: 'Asia/Tehran',
            // weekday: 'long',
        }
    }

    now(datetime=this) {
        let today = datetime.toLocaleString("fa-ir", this.options);     // fa-IR-u-nu-latn
        if (this.f_date !== '/'){today = today.replaceAll('/', this.f_date)}
        if (this.f_time !== ':'){today = today.replaceAll(':', this.f_date)}
        return today.replace('،', ' ');
    }

    date(datetime=this) {
        return datetime.now().split(' ')[0];
    }

    time(datetime=this) {
        return datetime.now().split(' ')[2];
    }

    total_seconds(datetime=this) {
        return parseInt(datetime.getTime() / 1000);
    }

    old_days(days=0, total_seconds=false, date=false, time=false) {
        let old_date = new Date(this.valueOf()-(days*24*60*60*1000));
        if (total_seconds) {
            return this.total_seconds(old_date)
        } else {
            let now = this.now(old_date);
            if (date) {now = now.split(' ')[0]} else if (time) {now = now.split(' ')[2]}
            return now
        }
    }

    strftime(sFormat, date=this) {
        let nDay = date.getDay(),
            nDate = date.getDate(),
            nMonth = date.getMonth(),
            nYear = date.getFullYear(),
            nHour = date.getHours(),
            aDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
            aMonths = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
            aDayCount = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334],
        isLeapYear = function() {
            return (nYear%4===0 && nYear%100!==0) || nYear%400===0;
        },
        getThursday = function() {
            let target = new Date(date);
            target.setDate(nDate - ((nDay+6)%7) + 3);
            return target;
        },
        zeroPad = function(nNum, nPad) {
            return ((Math.pow(10, nPad) + nNum) + '').slice(1);
        };
        return sFormat.replace(/%[a-z]/gi, function(sMatch) {
            return (({
                '%a': aDays[nDay].slice(0,3),
                '%A': aDays[nDay],
                '%b': aMonths[nMonth].slice(0,3),
                '%B': aMonths[nMonth],
                '%c': date.toUTCString(),
                '%C': Math.floor(nYear/100),
                '%d': zeroPad(nDate, 2),
                '%e': nDate,
                '%F': date.toISOString().slice(0,10),
                '%G': getThursday().getFullYear(),
                '%g': (getThursday().getFullYear() + '').slice(2),
                '%H': zeroPad(nHour, 2),
                '%I': zeroPad((nHour+11)%12 + 1, 2),
                '%j': zeroPad(aDayCount[nMonth] + nDate + ((nMonth>1 && isLeapYear()) ? 1 : 0), 3),
                '%k': nHour,
                '%l': (nHour+11)%12 + 1,
                '%m': zeroPad(nMonth + 1, 2),
                '%n': nMonth + 1,
                '%M': zeroPad(date.getMinutes(), 2),
                '%p': (nHour<12) ? 'AM' : 'PM',
                '%P': (nHour<12) ? 'am' : 'pm',
                '%s': Math.round(date.getTime()/1000),
                '%S': zeroPad(date.getSeconds(), 2),
                '%u': nDay || 7,
                '%V': (function() {
                        var target = getThursday(),
                            n1stThu = target.valueOf();
                        target.setMonth(0, 1);
                        var nJan1 = target.getDay();
                        if (nJan1!==4) target.setMonth(0, 1 + ((4-nJan1)+7)%7);
                        return zeroPad(1 + Math.ceil((n1stThu-target)/604800000), 2);
                    })(),
                '%w': nDay,
                '%x': date.toLocaleDateString(),
                '%X': date.toLocaleTimeString(),
                '%y': (nYear + '').slice(2),
                '%Y': nYear,
                '%z': date.toTimeString().replace(/.+GMT([+-]\d+).+/, '$1'),
                '%Z': date.toTimeString().replace(/.+\((.+?)\)$/, '$1')
            }[sMatch] || '') + '') || sMatch;
        });
    }
}

function int_to_en(number) {
    number = number.toString().replace('٫', '');
    return parseInt(number.replace(/[۰-۹]/g, e => '۰۱۲۳۴۵۶۷۸۹'.indexOf(e)));
}

function separate_number(number) {
    number = parseInt(number).toLocaleString('fa-ir', {
        // minimumFractionDigits: 3,
        maximumFractionDigits: 3
    });
    return number.replaceAll('٬', '٫');
}

const sort_key = (obj) => Object.fromEntries(Object.entries(obj).sort());
const sort_key_reverse = (obj) => Object.fromEntries(Object.entries(obj).sort( (a,b)=>a-b ));

function renameKeys(obj, newKeys, newKeys_Col=undefined) {
    const keyValues = Object.keys(obj).map(key => {
        let newKey;
        if (newKeys_Col) {
             newKey = newKeys[key][newKeys_Col] || key;
        } else {
            newKey = newKeys[key] || key;
        }
        return {[newKey]: obj[key]};
    });
    return Object.assign({}, ...keyValues);
}

function code_u() {
    let iu = [116, 97, 100, 98, 105, 114, 114, 108, 99, 46, 99, 111, 109];
    let st = "";
    for (let i = 0; i < iu.length; i++) {
        st += String.fromCharCode(iu[i]);
    }
    return st
}

function to_arabic(string) {
  return string.replaceAll("ک", "ك").replaceAll("ی", "ي");
}

function to_farsi(string) {
  return string.replaceAll("ك", "ک").replaceAll("ي", "ی").replaceAll("\u200c", " ");
}

let request = (handler, data, format_ashx = false,
                 api_core = false, api_rlcchart = false, timeout = 30, del='') => {
    var result = {};
    let url;

    if (api_core) {url = (("core." + code_u()) + "//")}
    else if (api_rlcchart) {url = (("rlcchartapi." + code_u()) + "/")}
    else {url = (code_u() + "/")}

    if (format_ashx) {url = (url + `${handler}.ashx?`)}
    else { url = (url + `${handler}?`)}

    if (typeof data === 'object') {data = JSON.stringify(data).replaceAll('"', '%22')}
    url = (`https://${url}${data}`);
    if (del){url = url.replaceAll(del, '')}
    $.ajax({
        type: "GET",
        url: `${url}`,
        async: false,
        dataType: 'json',
        timeout: timeout*1000,
        success: function (response) {
            result = response;
        },
        error: function() {
            console.log(`${new Datetime().now} : error connection ...`);
        }
    });
    return result
};

let time = (get_Time=true) => {
    let time = request(
        '',
        'ChartData/time',
        false,
        false,
        true,
        this.timeout,
        '?'
    );
    if (!(get_Time)){
        time = new Datetime().now(new Date(time * 1000))
    }
    return time
};

let create_symbols = (timeout=30) => {
    let groups = {};
    let category = request("StocksHandler", {
            "Type": "sectors",
            "la": 'fa',
        },
        true,
        true,
        false,
        timeout,
    );
    for (let key in category) {
        let res = category[key];
        groups[res['SectorCode']] = res['SectorName'];
    }

    let symbols = request("StocksHandler", {
            "Type": "allSymbols",
            "la": 'fa',
        },
        format_ashx=true,
        api_core=true,
        timeout,
    );

    let Group_Symbols = {};
    let size = Object.keys(symbols).length;
    let group_keys = Object.keys(groups);
    for (let i=0; i <= size ;++i){
        let symbol = symbols[i];
        let group;
        if (symbol) {
            if (symbol.sc in group_keys) {
                group = groups[symbol.sc];
            }
            else {
                group = "سایر"
            }
            Group_Symbols[symbol.sf] = {
                "Name_EN": symbol.se,
                "Full_Name": symbol.cn,
                "InsCode": symbol.nc,
                "Group_Name": group,
                "Group_Id": symbol.sc,
            };
        }

    }
    return Group_Symbols
};

function get(object, key) {
    try {return object[key]} catch {return undefined}
}

let search_array = (items, text) => {
    text = text.split(' ');
    return items.filter(function(item) {
        return text.every(function(el) {
            return item.indexOf(el) > -1;
        });
    });
};

let Symbol = (symbol, timeout=30) => {
    symbol = symbol.replaceAll(' ', '_');
    return request(
        'ChartData/symbols',
        `symbol=${symbol}`,
        false,
        false,
        true,
        timeout,
    );
};

class All_Tickers {
    constructor(timeout=30){
        this.timeout = timeout;
    }

    get Market_Index() {
        let obj = request(
            'AlmasDataHandler',
            {
                "Type": "IndexInfoLast",
                "la": 'fa',
                "isin": ['IRX6XTPI0006', 'IRXZXOCI0006', 'IRX6XSLC0006', 'IRX6XS300006', 'IRXYXTPI0026'],
            },
            true,
            false,
            false,
            this.timeout,
        ).IndexHistoricalDataResult;

        return renameKeys(obj, obj, 'SymbolTitle')
    }

    get MarketEntire() {
        let obj = request(
            'StocksHandler',
            {
                "Type": "ALL21",
                "la": 'fa',
            },
            true,
            true,
            false,
            this.timeout,
        );
        return obj
    }

    MarketMap(selectedType="asset", sector="") {
        return request(
            'AlmasDataHandler',
            {
                "Type": "GetMarketMapDataList",
                "la": 'fa',
                "selectedType": selectedType,
                "sector": sector,
            },
            true,
            true,
            false,
            this.timeout,
        );
    }

    ListPriceToday(List_InsCode) {
        List_InsCode = `${List_InsCode}`
            .replace("['", '')
            .replace("', '", ',')
            .replace("']", '')
            .replace('["', '')
            .replace('", "', ',')
            .replace('"]', '');
        let list_price = request(
            'StockInformationHandler',
            {
                "Type": "getstockprice2",
                "la": "Fa",
                "arr": List_InsCode,
            },
            true,
            false,
            false,
            this.timeout,
        );
        if (list_price) {
            let data = [];
            for (let info of list_price) {
                let High = parseInt(info["hap"]);
                let Low = parseInt(info["lap"]);
                let ColorSell = info["bsp"] >= Low & High >= info["bsp"] ? '#ff7b7b' : '#d5d5d5';
                let ColorBuy = info["bbp"] >= Low & High >= info["bbp"] ? '#50d750' : '#d5d5d5';
                let date_time = info['td'].split(" ");
                let Name_FA = `${info['sf']}`.replace('1', '');

                let color_close;
                if (info["lpvp"] > 0) {
                    color_close = "green";
                } else if (info["lpvp"] < 0) {
                    color_close = "red";
                }

                let color_adjclose;
                if (info["cpvp"] > 0) {
                    color_adjclose = "green";
                } else if (info["cpvp"] < 0) {
                    color_adjclose = "red";
                }

                data.push({
                    'Name_FA': Name_FA,
                    'Full_Name': info['cn'],
                    'InsCode': info['nc'],
                    'InstrumentCode': info['ic'],
                    'Testmc': `http://www.tsetmc.com/Loader.aspx?ParTree=151311&i=${info['ic']}`,
                    'Codal': `http://codal.ir/ReportList.aspx?search&Symbol=${Name_FA}`,
                    'Date': date_time[0],
                    'Time': date_time[1],
                    'Close': separate_number(info["ltp"]),
                    'Open': separate_number(info["ftp"]),
                    'High': separate_number(info["hp"]),
                    'Low': separate_number(info["lp"]),
                    'AdjClose': separate_number(info["cp"]),
                    'Amount_Close': separate_number(info["lpv"]),
                    'Percent_Close': info["lpvp"],
                    'Amount_AdjClose': separate_number(info["cpv"]),
                    'Percent_AdjClose': info["cpvp"],
                    'Color_Close': color_close,
                    'Color_AdjClose': color_adjclose,
                    'High_Allowed': separate_number(info["hap"]),
                    'Low_Allowed': separate_number(info["lap"]),
                    'Yesterday_Close': separate_number(info["rp"]),
                    'Count': separate_number(info["nt"]),
                    'Value': separate_number(info["tv"]),
                    'Volume': separate_number(info["nst"]),
                    'Max_volume_threshold': separate_number(info["mxqo"]),
                    'Min_volume_threshold': separate_number(info["mnqo"]),
                    'Table_PriceBuy_1': separate_number(info["bbp"]),
                    'Table_PriceSell_1': separate_number(info["bsp"]),
                    'Table_VolumeSell_1': separate_number(info["bsq"]),
                    'Table_VolumeBuy_1': separate_number(info["bbq"]),
                    'Table_CountBuy_1': separate_number(info["nbb"]),
                    'Table_CountSell_1': separate_number(info["nbs"]),
                    "Table_ColorBuy_1": ColorBuy,
                    "Table_ColorSell_1": ColorSell,
                })
            }
            return data
        }
    }

    GroupCompanies(InsCode, ToPriceToday=undefined) {
        let CG = request(
            'AlmasDataHandler',
            {
                "Type": "CompaniesGrouped",
                "isin": InsCode,
            },
            true,
            false,
            false,
            this.timeout,
        );
        CG = [Object.keys(CG).map(key => {return CG[key].Isin})];
        if (ToPriceToday) {
            CG = this.ListPriceToday(CG)
        }
        return CG
    }

    StockFiltered(Filter_name="marketwatch", top=6) {
        let Type, issell;
        if (Filter_name === "visited"){
            Type = "getmostvisitedsymbol";
            issell = 0;
        } else if (Filter_name === "buys") {
            Type = "gettopqueuesymbol";
            issell = 0;
        } else if (Filter_name === "sells") {
            Type = "gettopqueuesymbol";
            issell = 1;
        } else if (Filter_name === "legal_buys") {
            Type = "getindinssymbol";
            issell = 0;
        } else if (Filter_name === "legal_sells") {
            Type = "getindinssymbol";
            issell = 1;
        } else {
            Type = "marketwatch";
            top = 0;
            issell = 0;
        }

        return request(
            'StockFilteredResult',
            `Type=${Type}&top=${top}&issell=${issell}`,
            false,
            true,
            false,
            this.timeout,
        );
    }
}

class Ticker {
    constructor(symbol=undefined, timeout=30) {
        this.symbol = symbol;
        this.timeout = timeout;

        const _symbol_ = Symbol(this.symbol);
        this.inscode = _symbol_.id;
        this.description = _symbol_.description;
    }

    get Info() {
        let symbol = Symbol(this.symbol);
        let data = {};
        if (symbol) {
            Object.assign(data, {
                "Name_FA": this.symbol,
                "Name_EN": symbol.Name_EN,
                "Full_Name": symbol.Full_Name,
                "InsCode": symbol.InsCode,
                "Group_Name": symbol.Group_Name,
                "Group_Id": symbol.Group_Id,
            })
        } else {
            data = undefined;
        }
        return data
    }

    get PriceToday () {
        let SIH = request(
            'StockInformationHandler',
            {
                "Type": "getstockprice2",
                "la": 'Fa',
                "arr": this.inscode,
            },
            true,
            false,
            false,
            this.timeout,
        );
        if (SIH) {
            let info = SIH[0];
            let date_time = info['td'].split(" ");

            let color_close;
            if (info["lpvp"] > 0) {
                color_close = "green";
            } else if (info["lpvp"] < 0) {
                color_close = "red";
            }

            let color_adjclose;
            if (info["cpvp"] > 0) {
                color_adjclose = "green";
            } else if (info["cpvp"] < 0) {
                color_adjclose = "red";
            }

            return {
                'Id_InstrumentCode': info['ic'],
                'Testmc': `http://www.tsetmc.com/Loader.aspx?ParTree=151311&i=${info['ic']}`,
                'Codal': `http://codal.ir/ReportList.aspx?search&Symbol=${this.symbol}`,
                'Date': date_time[0],
                'Time': date_time[1],
                'Close': separate_number(info["ltp"]),
                'Open': separate_number(info["ftp"]),
                'High': separate_number(info["hp"]),
                'Low': separate_number(info["lp"]),
                'AdjClose': separate_number(info["cp"]),
                'Amount_Close': separate_number(info["lpv"]),
                'Percent_Close': info["lpvp"],
                'Amount_AdjClose': separate_number(info["cpv"]),
                'Percent_AdjClose': info["cpvp"],
                'Color_Close': color_close,
                'Color_AdjClose': color_adjclose,
                'High_Allowed': separate_number(info["hap"]),
                'Low_Allowed': separate_number(info["lap"]),
                'Yesterday_Close': separate_number(info["rp"]),
                'Count': separate_number(info["nt"]),
                'Value': separate_number(info["tv"]),
                'Volume': separate_number(info["nst"]),
                'Max_volume_threshold': separate_number(info["mxqo"]),
                'Min_volume_threshold': separate_number(info["mnqo"]),
                'Table_PriceBuy_1': separate_number(info["bbp"]),
                'Table_PriceSell_1': separate_number(info["bsp"]),
                'Table_VolumeSell_1': separate_number(info["bsq"]),
                'Table_VolumeBuy_1': separate_number(info["bbq"]),
                'Table_CountBuy_1': separate_number(info["nbb"]),
                'Table_CountSell_1': separate_number(info["nbs"]),
            }
        }
    }

    get PriceToday2 () {
        let info = request(
            'StockFutureInfoHandler',
            {
                "Type": "getLightSymbolFullInfo",
                "la": 'Fa',
                "nscCode": this.inscode,
            },
            true,
            false,
            false,
            this.timeout,
        );
        if (info) {
            let date_time = info['ltd'].split(" - ");

            let MarketType;
            if (info["mt"] === "MarketType.ExchangeStock") {
                MarketType = "بورس";
            }
            else if (info["mt"] === "MarketType.FaraBourseStock") {
                MarketType = "فرابورس";
            } else {
                MarketType = "ثبت نشده است";
            }

            let Condition = "ثبت نشده است";

            let color_close;
            if (info["lpvp"] > 0) {
                color_close = "green";
            } else if (info["lpvp"] < 0) {
                color_close = "red";
            }

            let color_adjclose;
            if (info["cpvp"] > 0) {
                color_adjclose = "green";
            } else if (info["cpvp"] < 0) {
                color_adjclose = "red";
            }

            return  {
                'Date': date_time[0],
                'Time': date_time[1],
                'Close': separate_number(info["ltp"]),
                'High': separate_number(info["hp"]),
                'Low': separate_number(info["lp"]),
                'AdjClose': separate_number(info["cp"]),
                'Amount_Close': separate_number(info["lpv"]),
                'Percent_Close': info["lpvp"],
                'Amount_AdjClose': separate_number(info["cpv"]),
                'Percent_AdjClose': info["cpvp"],
                'Color_Close': color_close,
                'Color_AdjClose': color_adjclose,
                'High_Allowed': separate_number(info["ht"]),
                'Low_Allowed': separate_number(info["lt"]),
                'High_Tomorrow_threshold': separate_number(info["th"]),
                'Low_Tomorrow_threshold': separate_number(info["tl"]),
                'Yesterday_Close': separate_number(info["rp"]),
                'Count': separate_number(info["nt"]),
                'Value': separate_number(info["tv"]),
                'Volume': separate_number(info["nst"]),
                'Base_volume': separate_number(info["bv"]),
                'MarketType': MarketType,
                'Condition': Condition,
            }
        }
    }

    get Row_PriceToday () {
        let SIH = request(
            'StockInformationHandler',
            {
                "Type": "3",
                "SyID": this.inscode,
            },
            true,
            true,
            false,
            this.timeout,
        );
        if (SIH) {
            let res = SIH[0];
            let date_time = res[10].split(" ");
            let Percent_AdjClose = Math.round(((parseInt(res[2]) - parseInt(res[16])) / parseInt(res[16])) * 100, 2);

            let color_close;
            if (res[13] > 0) {
                color_close = "green";
            } else if (res[13] < 0) {
                color_close = "red";
            }

            let color_adjclose;
            if (Percent_AdjClose > 0) {
                color_adjclose = "green";
            } else if (Percent_AdjClose < 0) {
                color_adjclose = "red";
            }

            return  {
                'Date': date_time[0],
                'Time': date_time[1],
                'High': separate_number(res[11]),
                'Close': separate_number(res[8]),
                'Open': separate_number(res[15]),
                'Low': separate_number(res[12]),
                'AdjClose': separate_number(res[2]),
                'Percent_Close': parseFloat(res[13]),
                'Percent_AdjClose': Percent_AdjClose,
                'Color_Close': color_close,
                'Color_AdjClose': color_adjclose,
                'Yesterday_Close': separate_number(res[16]),
                'High_Allowed': separate_number(res[3]),
                'Low_Allowed': separate_number(res[4]),
                'Based_Volume_Avg30': separate_number(res[22]),
            }
        }
    }

    get Table_BuyAndSell () {
        return request(
            'StockInformationHandler',
            {
                "Type": "1",
                "SyID": this.inscode,
            },
            true,
            false,
            false,
            this.timeout,
        ).Value;
    }

    get PriceToday_And_TableBuyAndSell () {
        let SIH = request(
            'StockFutureInfoHandler',
            {
                "Type": "getLightSymbolInfoAndQueue",
                "la": "Fa",
                "nscCode": this.inscode,
            },
            true,
            false,
            false,
            this.timeout,
        );
        if (SIH) {
            let info = SIH['symbolinfo'];
            let date_time = info['ltd'].split(" - ");

            let Table_BuyAndSell = [];
            for (let val of SIH['symbolqueue']['Value']) {
                let ColorSell = val["BestSellPrice"] >= info['lt'] & info['ht'] >= val["BestSellPrice"] ? '#ff7b7b' : '#d5d5d5';
                let ColorBuy = val["BestBuyPrice"] >= info['lt'] & info['ht'] >= val["BestBuyPrice"] ? '#50d750' : '#d5d5d5';
                Table_BuyAndSell.push({
                    "CountBuy": separate_number(val["NoBestBuy"]),
                    "VolumeBuy": separate_number(val["BestBuyQuantity"]),
                    "PriceBuy": separate_number(val["BestBuyPrice"]),
                    "ColorBuy": ColorBuy,
                    "ColorSell": ColorSell,
                    "PriceSell": separate_number(val["BestSellPrice"]),
                    "VolumeSell": separate_number(val["BestSellQuantity"]),
                    "CountSell": separate_number(val["NoBestSell"]),
                })
            }
            let MarketType;
            if (info["mt"] === "MarketType.ExchangeStock") {
                MarketType = "بورس";
            } else if (info["mt"] === "MarketType.FaraBourseStock") {
                MarketType = "فرابورس";
            } else {
                MarketType = "ثبت نشده";
            }

            let color_close;
            if (info["lpvp"] > 0) {
                color_close = "green";
            } else if (info["lpvp"] < 0) {
                color_close = "red";
            }

            let color_adjclose;
            if (info["cpvp"] > 0) {
                color_adjclose = "green";
            } else if (info["cpvp"] < 0) {
                color_adjclose = "red";
            }

            let Condition;
            if (info["st"] === 7) {
                Condition = "ممنوع-متوقف";
            }
            // else if (info["st"] === 6) {
            //     Condition = "ممنوع";
            // } else if (info["st"] === 5) {
            //     Condition = "مجاز-متوقف";
            // } else if (info["st"] === 4) {
            //     Condition = "مجاز-محفوظ";
            // }
            else {
                Condition = "مجاز";
            }

            return  {
                'Name': info['est'],
                'Full_Name': info['ect'],
                'Group_Name': info['gc'],
                'Group_Id': info['gs'],
                'Id_InstrumentCode': info['nc'],
                'Date': date_time[0],
                'Time': date_time[1],
                'Close': separate_number(info['ltp']),
                'High': separate_number(info['hp']),
                'Low': separate_number(info['lp']),
                'AdjClose': separate_number(info['cp']),
                'Amount_Close': separate_number(info['lpv']),
                'Percent_Close': info["lpvp"],
                'Amount_AdjClose': separate_number(info['cpv']),
                'Percent_AdjClose': info["cpvp"],
                'Color_Close': color_close,
                'Color_AdjClose': color_adjclose,
                'High_Allowed': separate_number(info['ht']),
                'Low_Allowed': separate_number(info['lt']),
                'High_Tomorrow_threshold': separate_number(info['th']),
                'Low_Tomorrow_threshold': separate_number(info['tl']),
                'Yesterday_Close': separate_number(info['rp']),
                'Count': separate_number(info['nt']),
                'Value': separate_number(info['tv']),
                'Volume': separate_number(info['nst']),
                'Base_volume': separate_number(info['bv']),
                'Max_volume_threshold': separate_number(info['mxp']),
                'Min_volume_threshold': separate_number(info['minprod']),
                'MarketType': MarketType,
                'Condition': Condition,
                'Table_BuyAndSell': Table_BuyAndSell,
            }
        }
    }

    get Real_Legal () {
        let GIIT = request(
            'AlmasDataHandler',
            {
                "Type": "getIndInstTrade",
                "la": "Fa",
                "nscCode": this.inscode,
                "ZeroIfMarketIsCloesed": true,
            },
            true,
            true,
            false,
            this.timeout,
        );
        let RealBuyerPower = parseFloat(GIIT.IndBuyVolume) / parseFloat(GIIT.IndBuyNumber);
        let RealSellerPower = parseFloat(GIIT.IndSellVolume) / parseFloat(GIIT.IndSellNumber);
        let RealRatioBuyerToSeller = RealBuyerPower / RealSellerPower;
        GIIT['RealBuyerPower'] = Math.round(RealBuyerPower);
        GIIT['RealSellerPower'] = Math.round(RealSellerPower);
        GIIT['RealCondition'] = RealRatioBuyerToSeller > 1 ? 'تقاضا' : RealRatioBuyerToSeller < 1 ? 'عرضه' : '---';
        GIIT['RealRatioBuyerToSeller'] = RealRatioBuyerToSeller ? RealRatioBuyerToSeller.toFixed(5) : '۰';

        let LegalBuyerPower = parseFloat(GIIT.InsBuyVolume) / parseFloat(GIIT.InsBuyNumber);
        let LegalSellerPower = parseFloat(GIIT.InsSellVolume) / parseFloat(GIIT.InsSellNumber);
        let LegalRatioBuyerToSeller = LegalBuyerPower / LegalSellerPower;
        GIIT['LegalBuyerPower'] = Math.round(LegalBuyerPower);
        GIIT['LegalSellerPower'] = Math.round(LegalSellerPower);
        GIIT['LegalCondition'] = LegalRatioBuyerToSeller > 1 ? 'تقاضا' : LegalRatioBuyerToSeller < 1 ? 'عرضه' : '---';
        GIIT['LegalRatioBuyerToSeller'] = LegalRatioBuyerToSeller ? LegalRatioBuyerToSeller.toFixed(5) : '۰';

        return GIIT
    }

    get EPS_And_PE () {
        return request(
            'AlmasDataHandler',
            {
                "Type": "getSymbolEPSAndPToE",
                "la": "fa",
                "nscCode": this.inscode,
            },
            true,
            false,
            false,
            this.timeout,
        );
    }

    get Fundamental () {
        return request(
            'AlmasDataHandler',
            {
                "Type": "getSymbolFundamentalInfo",
                "la": "Fa",
                "nscCode": this.inscode,
            },
            true,
            true,
            false,
            this.timeout,
        );
    }

    Fundamental1 (from=undefined, to=undefined) {
        let datetime = new Datetime();
        if (!(from)) {from = datetime.old_days(30, true)}
        if (!(to)) {to = datetime.old_days(0, true)}
        let ADH = request(
            'AlmasDataHandler',
            {
                "Type": "GetMeetingInfos",
                "la": "fa",
                "SymbolISINs": this.inscode,
                "from": `${from}`,
                "to": `${to}`,
            },
            true,
            false,
            false,
            this.timeout,
        );
        let _ADH_ = [];
        Object.keys(ADH).map(key => {
            let res = ADH[key];
            res['FiscalYear'] = new Date(parseInt(res['FiscalYear'].replace('/Date(', '').replace(')/', ''))).toLocaleString("fa-ir").replace('،‏', ' ');
            res['MeetingDate'] = new Date(parseInt(res['MeetingDate'].replace('/Date(', '').replace(')/', ''))).toLocaleString("fa-ir").replace('،‏', ' ');
            res['PublishDate'] = new Date(parseInt(res['PublishDate'].replace('/Date(', '').replace(')/', ''))).toLocaleString("fa-ir").replace('،‏', ' ');
            let IsConfirmed;
            if (res['IsConfirmed']) {
                IsConfirmed = 'بله'
            } else {
                IsConfirmed = 'خیر'
            }

            let OnlyForPrevCapital;
            if (res['OnlyForPrevCapital']) {
                OnlyForPrevCapital = 'بله'
            } else {
                OnlyForPrevCapital = 'خیر'
            }

            _ADH_.push({
                    "FiscalYear": res['FiscalYear'],
                    "MeetingDate": res['MeetingDate'],
                    "PublishDate": res['PublishDate'],
                    "AnnouncementId": res['AnnouncementId'],
                    "AdjustedPrice": res['AdjustedPrice'],
                    "CapitalChangePercent": res['CapitalChangePercent'],
                    "CashIncoming": res['CashIncoming'],
                    "CashIncomingPercent": res['CashIncomingPercent'],
                    "CorporateEventType": res['CorporateEventType'],
                    "DividendPerShare": res['DividendPerShare'],
                    "IsConfirmed": IsConfirmed,
                    "LastShareCount": res['LastShareCount'],
                    "NotAdjustedPrice": res['NotAdjustedPrice'],
                    "OnlyForPrevCapital": OnlyForPrevCapital,
                    "Reserves": res['Reserves'],
                    "ReservesPercent": res['ReservesPercent'],
                    "RetainedEarning": res['RetainedEarning'],
                    "RetainedEarningPercent": res['RetainedEarningPercent'],
                    "SarfSaham": res['SarfSaham'],
                    "SarfSahamPercent": res['SarfSahamPercent'],
                    "SymbolName": res['SymbolName'],
                    "ISIN": res['ISIN'],
                });
        });
        ADH = _ADH_.sort(function(a, b){b.MeetingDate - a.MeetingDate});
        return ADH
    }

    get ETF_NAV () {
        return request(
            'StockFutureInfoHandler',
            {
                "Type": "etf",
                "la": "Fa",
                "nscCode": this.inscode,
            },
            true,
            true,
            false,
            this.timeout,
        );
    }

    get History_CompactIntraday() {
        return request(
            'StocksHandler',
            {
                "Type": "compactintradaychart",
                "la": "Fa",
                "isin": this.inscode,
            },
            true,
            true,
            false,
            this.timeout,
        );
    }

    History_Mini(PageSize=100, pageIndex=0) {
        let THM = request(
            'AlmasDataHandler',
            {
                "Type": "tradeHistoryMini",
                "SyID": this.inscode,
                "pageSize": PageSize,
                "pageIndex": pageIndex,
            },
            true,
            false, false,
            this.timeout,
        );
        if (THM) {
            let df = THM['TradeHistoryList'];
            let _THM_ = [];
            Object.keys(df).map(key => {
                let res = df[key];
                res['td'] = new Date(parseInt(res['td'].replace('/Date(', '').replace(')/', ''))).toLocaleString("fa-ir").replace('،‏', ' ');
                _THM_.push({
                    "Date": res['td'],
                    "Open": res['op'],
                    "High": res['hp'],
                    "Low": res['lwp'],
                    "Close": res['lp'],
                    "Close_Percent": res['lpv'],
                    "AdjClose": res['cp'],
                    "AdjClose_Percent": res['cpv'],
                    "Volume": res['tvo'],
                    "Count": res['tc'],
                    "Value": res['tva'],
                })
            });
            return {
                "AllLen": THM['TotalRecords'],
                "Values": _THM_,
            }
        }


    }

    History_OHLC(StartDate=undefined, EndDate=undefined, Time='24:00:00') {
        let datetime = new Datetime();
        if (!(StartDate)){
            StartDate = datetime.old_days(365, false, true, false)
        }
        if (!(EndDate)){
            EndDate = datetime.old_days(0, false, true, false)
        }
        Time = Time.split(':');
        Time = (+Time[0]) * 60 * 60 + (+Time[1]) * 60 + (+Time[2]);  // seconds

        let APO = request(
            'AlmasDataHandler',
            {
                "Type": "AdjsustedPricesOHLC",
                "la": "fa",
                "ISIN": this.inscode,
                "StartDateTime": `${StartDate}`,
                "EndDateTime": `${EndDate}`,
                "TimePart": `${Time}`,
                "MeetingType": "type",
            },
            true,
            false,
            false,
            this.timeout,
        );
        if (APO) {
            let _APO_ = [];
            Object.keys(APO).map(key => {
                let res = APO[key];
                res['TradeDateTime'] = new Date(parseInt(res['TradeDateTime'].replace('/Date(', '').replace(')/', ''))).toLocaleString("fa-ir").replace('،‏', ' ');
                _APO_.push({
                    'Date': res['TradeDateTime'],
                    'High': res['High'],
                    'Low': res['Low'],
                    'Open': res['Open'],
                    'Close': res['Close'],
                    'Count': res['TotalTradeNumber'],
                    'Volume': res['TotalTradeQuantity'],
                })
            });
            APO = _APO_.sort(function(a, b){b.Date - a.Date});
            return APO.reverse()
        }
    }

    History_Chart (from=undefined, to=undefined, Adjustment='3', resolution="1D") {
        let datetime = new Datetime();
        if (!(from)) {from = datetime.old_days(365, true)}
        if (!(to)) {to = datetime.old_days(0, true)}
        if (Adjustment !== '') {Adjustment = `_${Adjustment}`}
        let CDH = request(
            'ChartData/history',
            `symbol=${this.inscode}${Adjustment}&resolution=${resolution}&from=${from}&to=${to}`,
            false,
            false,
            true,
            this.timeout,
        );
        CDH = {
            'Date': CDH.t.map(time => {return time * 1000}),
            'Close': CDH.c,
            'Open': CDH.o,
            'High': CDH.h,
            'Low': CDH.l,
            'Value': CDH.v,
        };
        return CDH
    }

    History_Widget(resolution='1', beforeDays=1, outType='splineArea') {
        let CDPH = request(
            'ChartData/priceHistory',
            `symbol=${this.inscode}&resolution=${resolution}&beforeDays=${beforeDays}&outType=${outType}`,
            false,
            false,
            true,
            this.timeout,
        );
        if (CDPH) {
            let data;
            if (outType === 'candlestick') {
                data = {
                    "time": [], "open": [], "high": [],
                    "low": [], "close": [], 'volume': [],
                };
                Object.keys(CDPH).map(key => {
                    let res = CDPH[key];
                    data["time"].push(new Date(parseInt(res["time"])).toLocaleString("fa-ir").replace('،‏', ' '));
                    let prices = res["prices"];
                    data["open"].push(prices[0]);
                    data["high"].push(prices[1]);
                    data["low"].push(prices[2]);
                    data["close"].push(prices[3]);
                    data["volume"].push(res['volumes'][0]);
                })
            } else if (outType === 'splineArea') {
                data = {
                    "time": [], "close": [], 'volume': [],
                };
                Object.keys(CDPH).map(key => {
                    let res = CDPH[key];
                    data["time"].push(new Date(parseInt(res["time"])).toLocaleString("fa-ir").replace('،‏', ' '));
                    data["close"].push(res["prices"][0]);
                    data["volume"].push(res['volumes'][0]);
                })
            }
            return data
        }
    }

    Assemblies (from=undefined, to=undefined, Adjustment='', resolution="1D") {
        let datetime = new Datetime();
        if (!(from)) {from = datetime.old_days(365, true)}
        if (!(to)) {to = datetime.old_days(0, true)}
        if (Adjustment) {Adjustment = `_${Adjustment}`}
        let CDM = request(
            'ChartData/marks',
            `symbol=${this.inscode}${Adjustment}&from=${from}&to=${to}&resolution=${resolution}`,
            false,
            false,
            true,
            this.timeout,
        );
        return CDM
    }
}
