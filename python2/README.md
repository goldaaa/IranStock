# IranStock python

Extracted api version of Iran's financial market for free for global use.

    Total_stock_index()     # شاخص کل بورس

    Ticker('وبوعلی', Lim_Date='1399-01-10', Lim_Len=60).history   # ساختار نمونه

    symbols_history()   # اطلاعات لحظه ای کامل تاریخچه روزانه کل نمادها
    symbols_history('وبوعلی')   # فیلتر کردن نام نماد در لیست کل نمادها
    Ticker('نماد').get_ticker # قیمت لحظه ای
    Ticker('نماد').get_ticker_other   # p/e لحظه ای
    Ticker('نماد').shareholders  # اطلاعات سهامداران عمده
    Ticker('نماد').history   # سابقه قیمت سهم
    Ticker('نماد').client_types_records  # سابقه خرید و فروش های حقوقی و حقیقی

    # ____________________________________________________________________________
    date : تاریخ
    individual_buy_count : تعداد معاملات خرید حقیقی
    corporate_buy_count : تعداد معلاملات خرید حقوقی
    individual_sell_count : تعداد معاملات فروش حقیقی
    corporate_sell_count : تعداد معلاملات فروش حقوقی
    individual_buy_vol : حجم خرید حقیقی
    corporate_buy_vol : حجم خرید حقوقی
    individual_sell_vol : حجم فروش حقیقی
    corporate_sell_value : حجم فروش حقوقی
    individual_buy_mean_price : قیمت میانگین خرید حقیقی
    individual_sell_mean_price : قیمت میانگین فروش حقیقی
    corporate_buy_mean_price : قیمت میانگین خرید حقوقی
    corporate_sell_mean_price : قیمت میانگین فروش حقوقی
    individual_ownership_change : تغییر مالکیت حقوقی به حقیقی


Install the required package
--------
    requests
    pandas
    jdatetime
