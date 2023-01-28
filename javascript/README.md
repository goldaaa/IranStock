let datetime = new Datetime();
datetime.total_seconds();
datetime.now();
datetime.date();
datetime.time();
datetime.old_days(20, false);
datetime.strftime('%Y-%m-%d %H:%M:%S');

time(false);

let symbols = create_symbols();
symbols;
get(symbols, 'آبادا');
let search = search_array(Object.keys(symbols), 'آ');
Symbol('بوعلی');

let alltickers = new All_Tickers(30);
alltickers.Market_Index;
alltickers.MarketEntire;
alltickers.MarketMap();
alltickers.ListPriceToday(["IRO3BAHZ0001", "IRR3GDSZ0101", "IRO1MAGS0001"]);
alltickers.GroupCompanies('IRO3BAHZ0001', true);
alltickers.StockFiltered("visited", 6);

let ticker = new Ticker('وبوعلی');
ticker.Info;
ticker.PriceToday;
ticker.PriceToday2;
ticker.Row_PriceToday;
ticker.Table_BuyAndSell;
ticker.PriceToday_And_TableBuyAndSell;
ticker.Real_Legal;
ticker.EPS_And_PE;
ticker.Fundamental;

let datetime = new Datetime();
let from = datetime.old_days(30, true);
let to = datetime.old_days(0, true);

ticker.Fundamental1(from, to);

ticker.ETF_NAV;
ticker.History_CompactIntraday;
ticker.History_Mini();
ticker.History_OHLC('1399/01/01', '1400/07/29', '23:59:59');

ticker.History_Chart();
ticker.History_Widget(1, -1, 'splineArea');
ticker.History_Widget(1, -1, 'candlestick');

ticker.Assemblies();
