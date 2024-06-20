from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import datetime
import configparser
import csv
import os
import platform
import sys
from typing import Union, Optional, List, Dict, Tuple, TextIO, Any
import pandas
import requests
import streamtologger

# Create your views here.

first_run: bool =  True
stop: bool = False
dates: List[str] = [""]
indices: List[str] = []
stocks: List[str] = []
dates: List[str] = [""]
session: requests.Session = requests.Session()
cookies: Dict[str, str] = {}
headers: Dict[str, str] = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8',
            'accept-encoding': 'gzip, deflate, br'}
url_oc: str = "https://www.nseindia.com/option-chain"
url_index: str = "https://www.nseindia.com/api/option-chain-indices?symbol="
url_stock: str = "https://www.nseindia.com/api/option-chain-equities?symbol="
url_symbols: str = "https://www.nseindia.com/api/underlying-information"

def optionChainAna(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            global sp_entry
            global index
            global option_mode
            global expiry_date
            sp_entry = request.POST.get('strikePrice')
            index = request.POST.get('choseindex')
            option_mode = request.POST.get('mode')
            minutes = request.POST.get('refreshInterval')
            # expiry_date=datetime.today()
            # expiry_date = expiry_date.strftime('%d-%m-%Y')
            expiry_date = "03-Jul-2024"
            
            units_str: str = 'in K' if option_mode == 'Index' else 'in 10s'
            csv_headers: Tuple[str, str, str, str, str, str, str, str, str] = (
            'Time', 'Value', f'Call Sum ({units_str})', f'Put Sum ({units_str})',
            f'Difference ({units_str})',
            f'Call Boundary ({units_str})', f'Put Boundary ({units_str})', 'Call ITM', 'Put ITM')
            
            # seconds = int(intervals_var.get()) * 60
            seconds = minutes * 60
            # print(expiry_date)

            # export_row(None)
            try:
                messages.success(request, "workn")
                export_row(index,sp_entry,option_mode,expiry_date,csv_headers, stock=None)
                return HttpResponseRedirect("/option_chain_analyzer/result")
            except ValueError as err:
                messages.error(request, "Incorrect Strike Price.\nPlease enter correct Strike Price.")
        return render(request, 'optionForm.html')
    else:
        messages.error(request, 'You have to login first to use this feature')
        return HttpResponseRedirect("/login")

def export_row(index,sp_entry,option_mode,expiry_date,csv_headers,stock):
            csv_exists: bool = os.path.isfile(
                f"NSE-OCA-{index if option_mode == 'Index' else stock}-{expiry_date}.csv")
            try:
                if not csv_exists:
                    with open(
                            f"NSE-OCA-{index if option_mode == 'Index' else stock}-"
                            f"{expiry_date}.csv",
                            "a", newline="") as row:
                        data_writer: csv.writer = csv.writer(row)
                        data_writer.writerow(csv_headers)
            except PermissionError as err:
                print(err, sys.exc_info()[0], "13")
                # messages.error(request,
                #                      message=f"Failed to access NSE-OCA-"
                #                              f"{index if option_mode == 'Index' else stock}-"
                #                              f"{expiry_date}.csv.\n"
                #                              f"Permission Denied. Try closing any apps using it.")
            except Exception as err:
                print(err, sys.exc_info()[0], "9")
                

def optionChainAnaResult(request) -> Optional[Tuple[pandas.DataFrame, str, float]]:
    response: Optional[requests.Response]
    json_data: Any
    response, json_data = get_data()
    # print(",ajbckahbcihbc")
    if response is None or json_data is None:
        print("response is None or json_data is None")

    pandas.set_option('display.max_rows', None)
    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 100)

    df: pandas.DataFrame = pandas.read_json(response.text)
    df = df.transpose()

    ce_values: List[dict] = [data['CE'] for data in json_data['records']['data'] if
                                 "CE" in data and data['expiryDate'].lower() == expiry_date.lower()]
    pe_values: List[dict] = [data['PE'] for data in json_data['records']['data'] if
                                 "PE" in data and data['expiryDate'].lower() == expiry_date.lower()]
    print(len(pe_values))
    points: float = pe_values[0]['underlyingValue']
    if points == 0:
        for item in pe_values:
            if item['underlyingValue'] != 0:
                points = item['underlyingValue']
                break
    ce_data_f: pandas.DataFrame = pandas.DataFrame(ce_values)
    pe_data_f: pandas.DataFrame = pandas.DataFrame(pe_values)

    if ce_data_f.empty:
        messages.error(request, "Invalid Expiry Date.\nPlease restart and enter a new Expiry Date.")
        change_state()
        return HttpResponseRedirect("/option_chain_analyzer")
    columns_ce: List[str] = ['openInterest', 'changeinOpenInterest', 'totalTradedVolume', 'impliedVolatility',
                                 'lastPrice',
                                 'change', 'bidQty', 'bidprice', 'askPrice', 'askQty', 'strikePrice']
    columns_pe: List[str] = ['strikePrice', 'bidQty', 'bidprice', 'askPrice', 'askQty', 'change', 'lastPrice',
                                 'impliedVolatility', 'totalTradedVolume', 'changeinOpenInterest', 'openInterest']
    ce_data_f = ce_data_f[columns_ce]
    pe_data_f = pe_data_f[columns_pe]
    merged_inner: pandas.DataFrame = pandas.merge(left=ce_data_f, right=pe_data_f, left_on='strikePrice',
                                                      right_on='strikePrice')
    merged_inner.columns = ['Open Interest', 'Change in Open Interest', 'Traded Volume', 'Implied Volatility',
                                'Last Traded Price', 'Net Change', 'Bid Quantity', 'Bid Price', 'Ask Price',
                                'Ask Quantity', 'Strike Price', 'Bid Quantity', 'Bid Price', 'Ask Price',
                                'Ask Quantity', 'Net Change', 'Last Traded Price', 'Implied Volatility',
                                'Traded Volume', 'Change in Open Interest', 'Open Interest']
    current_time: str = df['timestamp']['records']
    # print(type(merged_inner))
    # merged_inner = merged_inner.to_html()
    # current_time = current_time.to_html()
    # points = points.to_html()
    # context = {'df': df.to_html(escape=False, index=False, index_names=False)}
    print(points)
    merged_inner = {'merged_inner': merged_inner.to_html(escape=False, index=False, index_names=False)}
    return render(request, "optionchainchart.html",merged_inner)
        # return merged_inner, current_time, points
    

def get_data():
        if first_run == True:
            return get_data_first_run()
        else:
            return get_data_refresh()
        
def change_state():
        if not stop:
            stop = True
        else:
            stop = False

def get_data_first_run()-> Optional[Tuple[Optional[requests.Response], Any]]:
        # url: str = url_index + index if option_mode == 'Index' else url_stock + stock
    url: str = url_index + index
    print(url)
    try:
        response = session.get(url, headers=headers, timeout=5, cookies=cookies)
    except Exception as err:
        print(response)
            # print("..............................")
        print(err, sys.exc_info()[0], "1")
            # messagebox.showerror(title="Error", message="Error in fetching dates.\nPlease retry.")
            # dates.clear()
            # dates = [""]
            # date_menu.config(values=tuple(dates))
            # date_menu.current(0)
        return
    json_data: Dict[str, Any]
    if response is not None:
        try:
            json_data = response.json()
            # print("json")
        except Exception as err:
            print(response)
            print(err, sys.exc_info()[0], "2")
            json_data = {}
    else:
        json_data = {}
    if json_data == {}:
            # print("///////////////////")
            # messagebox.showerror(title="Error", message="Error in fetching dates.\nPlease retry.")
            # dates.clear()
            # dates = [""]
            # try:
            #     # date_menu.config(values=tuple(dates))
            #     # date_menu.current(0)
            # except TclError as err:
            #     print(err, sys.exc_info()[0], "3")
        return response, json_data
        # dates.clear()
        # for dates in json_data['records']['expiryDates']:
        #     dates.append(dates)
        # try:
        #     date_menu.config(values=tuple(dates))
        #     date_menu.current(0)
        # except TclError:
        #     pass
        # print("holo")
    return response, json_data

def get_data_refresh():
    request: Optional[requests.Response] = None
    response: Optional[requests.Response] = None
        # url: str = url_index + index if option_mode == 'Index' else url_stock + stock
    url: str = url_index + index
    print(url)
    try:
        response = session.get(url, headers=headers, timeout=5, cookies=cookies)
        if response.status_code == 401:
            session.close()
            cookies.clear()
            session = requests.Session()
            request = session.get(url_oc, headers=headers, timeout=5)
            cookies = dict(request.cookies)
            response = session.get(url, headers=headers, timeout=5, cookies=cookies)
            print("reset cookies")
    except Exception as err:
            print(request)
            print(response)
            print(err, sys.exc_info()[0], "4")
            try:
                session.close()
                session = requests.Session()
                request = session.get(url_oc, headers=headers, timeout=5)
                cookies = dict(request.cookies)
                response = session.get(url, headers=headers, timeout=5, cookies=cookies)
                print("reset cookies")
            except Exception as err:
                print(request)
                print(response)
                print(err, sys.exc_info()[0], "5")
                return
    if response is not None:
            try:
                json_data: Any = response.json()
            except Exception as err:
                print(response)
                print(err, sys.exc_info()[0], "6")
                json_data = {}
    else:
            json_data = {}
    if json_data == {}:
            return response, json_data
    return response, json_data
    
def resetCookies(request):
    cookies.clear()
    # get_data_refresh()
    return HttpResponseRedirect("/option_chain_analyzer/")
    