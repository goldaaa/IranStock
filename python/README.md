# IranStock python

Extracted api version of Iran's financial market for free for global use.

    ticker = Ticker(Symbol="وبوعلی", loop_Fixed_error=1, timeout=30)

    print(ticker.PriceToday)            # اطلاعات قیمت و تیبل شماره یکم

    print(ticker.PriceToday2)           # اطلاعات قیمت تکمیلی صفحه

    print(ticker.Row_PriceToday)        # اطلاعات قیمتی ستون خرید و فروش

    print(ticker.Table_BuyAndSell)      # تیبل خرید و فروش ها

    print(ticker.PriceToday_And_TableBuyAndSell)        # اطلاعات قیمتی و تیبل خرید و فروش ها

    print(ticker.Real_Legal)            # خرید و فروش حقیقی و حقوقی

    print(ticker.EPS_And_PE)            # نمایش سود سازی شرکت و پی بر ایی

    print(ticker.Fundamental)           # اطلاعات بنیادی

    print(ticker.Fundamental1)          # سایر اطلاعات بنیادی
    AdjustedPrice                قیمت تعدیل شده
    AnnouncementId               شناسه اعلان
    CapitalChangePercent         درصد تغییر سرمایه
    CashIncoming                 ورود نقدی
    CashIncomingPercent          درصد نقدی
    CorporateEventType           نوع رویداد شرکتی
    DividendPerShare             پایان تقسیم بر سهم
    FiscalYear                   سال مالی
    ISIN                         آیدی سهامداری
    IsConfirmed                  تایید شده است
    LastShareCount               آخرین تعداد سهم
    MeetingDate                  تاریخ ملاقات
    NotAdjustedPrice             قیمت تعدیل نشده
    OnlyForPrevCapital           فقط برای سرمایه قبلی
    PublishDate                  تاریخ انتشار
    Reserves                     ذخایر
    ReservesPercent              درصد ذخیره
    RetainedEarning              سود حفظ شده
    RetainedEarning Percent      درصد سود را حفظ کرد
    SarfSaham                    صرف سهام
    SarfSahamPercent             صرف سهم درصد
    SymbolName                   نام نماد

    print(ticker.ETF_NAV)           # اطلاعات ناو صندوق ها و سرمایه گذاریها

    _____________________________________________________________________

    print(ticker.History_CompactIntraday)               # تاریخچه جمع و جور روزانه

    # تاریخچه با سایز کوچک
    print(ticker.History_Mini(PageSize=200))            # تاریخچه قیمتی بر اساس تعداد

    # تاریخچه نمودار بر اساس تاریخ
    t = ticker.History_OHLC(Time="23:59:59", StartDate='1399-01-01', EndDate='1400-07-29')
    print(pd.DataFrame(t))

    # تاریخچه نمودار بر اساس تعداد
    t = ticker.History_OHLCPagination(Time="23:59:59", PageIndex=0, PageSize=10)
    print(pd.DataFrame(t))

    # تاریخچه نمودار
    t = ticker.History_Chart(
        from_date='1399-07-28', from_time='00:00:00',
        to_date='1400-07-29', to_time='00:00:00',
        Adjustment='0', resolution="D",
    )
    print(t)
    print(pd.DataFrame(t))

    # تاریخچه ابزارک
    print(ticker.History_Widget(resolution="1", beforeDays=1, outType="splineArea"))      # نمودار خطی
    print(ticker.History_Widget(resolution="1", beforeDays=1, outType="candlestick"))     # نمودار تاریخچه کندلی

    _____________________________________________________________________

    # مجامع
    print(ticker.Assemblies(
        from_date='1399-01-01', from_time='00:00:00',
        to_date='1400-01-01', to_time='00:00:00',
        Adjustment='0', resolution="D",
    ))

    _____________________________________________________________________

    tickers = All_Tickers(loop_Fixed_error=1, timeout=30)

    print(tickers.Market_Index)       # اطلاعات مربوط به پنج شاخص

    print(tickers.MarketEntire)       # اطلاعات کلی نمادها

    print(tickers.MarketMap(selectedType="asset", sector=""))     # اطلاعات نقشه بازار

    print(tickers.GroupCompanies('IRO3BAHZ0001', ToPriceToday=True))    # یافتن آیدی سهامداری هم گروه ها

    print(tickers.ListPriceToday(['IRO3ZMMZ0001', 'IRO3MAHZ0001', 'IRO3TLIZ0001']))    # تبدیل لیست آیدی سهامداری به قیمت روزانه

    print(pd.DataFrame(tickers.StockFiltered(Filter_name="visited", top=6)))    # فیلتر نمادها
    visited     -->     بیشترین بازدیدهای امروز
    buys        -->     بیشترین تقاضای امروز
    sells       -->     بیشترین عرضه های امروز
    legal_buys  -->     بیشترین خرید حقوقی
    legal_sells -->     بیشترین فروش حقوقی
    marketwatch -->     تمام لیست نمادها


    

    p = Pages_Symbols(page=143, paginator=8)
    print(p['num_list'])
    print(p['is_paginated'])
    print(p['Value_list'])

    print(create_symbols())                # آپدیت جزئیات کل نمادها

    print(Test_File_Symbols())                # جزئیات کل نمادها

    print(Search_Symbols('بوعلی'))              # جستجو نام های مشابه در نمادها

    print(View_Symbol('بوعلی'))                 # یافتن جزئیات یک نماد

    print(Symbol_TO_InsCode('بوعلی', loop_Fixed_error=10))           # تبدیل نماد به آیدی سهامداری


Install the required package
--------
    requests
    pandas
    jdatetime
