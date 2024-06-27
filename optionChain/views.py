from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import datetime
from .models import *
import configparser
import csv
import os
import platform
import sys
from typing import Union, Optional, List, Dict, Tuple, TextIO, Any
import pandas
import requests
import streamtologger
import schedule
import time
import json

# Create your views here.

stop = False
# dates = [""]
indices: List[str] = []
stocks: List[str] = []
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
            global indexer
            global option_mode
            sp_entry = request.POST.get('strikePrice')
            sp_entry = int(sp_entry)
            indexer = request.POST.get('choseindex')
            option_mode = request.POST.get('mode')
            
            # units_str: str = 'in K' if option_mode == 'Index' else 'in 10s'
            # csv_headers: Tuple[str, str, str, str, str, str, str, str, str] = (
            # 'Time', 'Value', f'Call Sum ({units_str})', f'Put Sum ({units_str})',
            # f'Difference ({units_str})',
            # f'Call Boundary ({units_str})', f'Put Boundary ({units_str})', 'Call ITM', 'Put ITM')
            
            # seconds = int(intervals_var.get()) * 60
            # seconds = minutes * 60
            # print(expiry_date)

            # export_row(None)
            try:
                # messages.success(request, "workn")
                # export_row(index,sp_entry,option_mode,expiry_date,csv_headers, stock=None)
                # NSEOptionChainAnalyzer.objects.create(index = indexer, sp_entry = sp_entry)
                return HttpResponseRedirect("/option_chain_analyzer/enter_expiry_date")
            except ValueError as err:
                messages.error(request, "Incorrect Strike Price.\nPlease enter correct Strike Price.")
        return render(request, 'optionForm.html')
    else:
        messages.error(request, 'You have to login first to use this feature')
        return HttpResponseRedirect("/login")
    
def optionChainAnaExpDate(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            global expiry_date
            expiry_date = request.POST.get('exp_date')
            # expiry_date= datetime.strptime(expiry_date, "%Y-%m-%d").strftime("%d-%b-%Y")
            # print(type(expiry_date),expiry_date)
            # expiry_date = str(expiry_date)
            # print(type(expiry_date),expiry_date)
            # units_str: str = 'in K' if option_mode == 'Index' else 'in 10s'
            # csv_headers: Tuple[str, str, str, str, str, str, str, str, str] = (
            # 'Time', 'Value', f'Call Sum ({units_str})', f'Put Sum ({units_str})',
            # f'Difference ({units_str})',
            # f'Call Boundary ({units_str})', f'Put Boundary ({units_str})', 'Call ITM', 'Put ITM')
            
            # seconds = int(intervals_var.get()) * 60
            # seconds = minutes * 60
            # print(expiry_date)

            # export_row(None)
            try:
                # messages.success(request, "workn")
                # export_row(index,sp_entry,option_mode,expiry_date,csv_headers, stock=None)
                return HttpResponseRedirect("/option_chain_analyzer/result")
            except ValueError as err:
                messages.error(request, "Incorrect Strike Price.\nPlease enter correct Strike Price.")
        exp = IndexExpDates.objects.filter(index = indexer)
        return render(request, 'optionFormWithExp.html', {"exp":exp} )
    else:
        messages.error(request, 'You have to login first to use this feature')
        return HttpResponseRedirect("/login")

def optionChainAnaResult(request):
    global uname
    uname = request.user.username
    if type(showRes()) is str:
        messages.error(request, showRes())
        return render(request, "optionchainchart.html" )
    else:
        return render(request, "optionchainchart.html", {"chart": showRes() } )
    
def optionChainAnaResultDel(request):
    if request.user.is_authenticated:
        uname = request.user.username
        NSEOptionChainAnalyzer.objects.filter(uname = uname).delete()
        messages.success(request, "Old record deleted")
        return HttpResponseRedirect('/option_chain_analyzer/result')
    else:
        messages.error(request, "You have to login first to use this feature")
        return HttpResponseRedirect('/login')
    
def showRes():
    merged_inner = main()
    if merged_inner == 1:
        return("Incorrect Strike Price.")
    elif merged_inner == 2:
        return("Error occured while fetching details from nseindia.com/api")
    elif merged_inner == 3:
        return("please go back to '/option_chain_analyzer' and fill the form properly")
    else:
        NSEOptionChainAnalyzer.objects.get_or_create(uname = uname, index = indexer , expiry_date = merged_inner['expiry_date'], sp_entry= sp_entry, str_current_time = merged_inner['str_current_time'], points = merged_inner['points'], call_sum=merged_inner['call_sum'], put_sum=merged_inner['put_sum'], difference=merged_inner['difference'], call_boundary=merged_inner['call_boundary'], put_boundary=merged_inner['put_boundary'], call_itm=merged_inner['call_itm'], put_itm=merged_inner['put_itm'], oi_label = merged_inner['oi_label'], put_call_ratio = merged_inner['put_call_ratio'], call_exits_label = merged_inner['call_exits_label'], call_itm_val = merged_inner['call_itm_val'], put_exits_label = merged_inner['put_exits_label'], put_itm_val = merged_inner['put_itm_val'])
        chart = NSEOptionChainAnalyzer.objects.filter(uname = uname)
    return chart

def optionChainDownloadExel(request):
    queryset = NSEOptionChainAnalyzer.objects.filter(uname=uname)
    df = pandas.DataFrame(list(queryset.values()))
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="my_data.xlsx"'

    with pandas.ExcelWriter(response) as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return response

def change_state():
    global stop
    if not stop:
        stop = True
    else:
        stop = False

def get_data_first_run()-> Optional[Tuple[Optional[requests.Response], Any]]:
        # url: str = url_index + index if option_mode == 'Index' else url_stock + stock
    try:
        global round_factor
        round_factor = 1000 if option_mode == 'Index' else 10
    except:
        return 3
    url: str = url_index + indexer
    print(url)
    
    # session.close()
    # cookies.clear()
    session = requests.Session()
    request = session.get(url_oc, headers=headers, timeout=10)
    cookies = dict(request.cookies)
    response = session.get(url, headers=headers, timeout=10, cookies=cookies)
    # if response.status_code == 401:
    #     session.close()
    #     cookies.clear()
    #     session = requests.Session()
    #     request = session.get(url_oc, headers=headers, timeout=10)
    #     cookies = dict(request.cookies)
    #     response = session.get(url, headers=headers, timeout=10, cookies=cookies)
    
    json_data: Dict[str, Any]
    if response is not None:
        try:
            json_data = response.json() ############################33
        except Exception as err:
            # print(response)
            # print(err, sys.exc_info()[0], "2")
            json_data = {}
            return 2
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
    
    global dates
    dates = [""]
    dates.clear()
    IndexExpDates.objects.filter(index = indexer).delete()
    for date in json_data['records']['expiryDates']:
        IndexExpDates.objects.create(index = indexer, expiry_date = date)
        dates.append(date)
    # try:
    #     date_menu.config(values=tuple(dates))
    #     date_menu.current(0)
    # except TclError:
    #     pass
    # print(dates)
    return response, json_data
    
def resetCookies(request):
    cookies.clear()
    # get_data_refresh()
    return HttpResponseRedirect("/option_chain_analyzer/")
    
def get_dataframe() -> Optional[Tuple[pandas.DataFrame, str, float]]:
        try:
            response: Optional[requests.Response]
            json_data: Any
            response, json_data = get_data_first_run()
        except TypeError:
            return
        if response is None or json_data is None:
            return

        pandas.set_option('display.max_rows', None)
        pandas.set_option('display.max_columns', None)
        pandas.set_option('display.width', 400)

        df: pandas.DataFrame = pandas.read_json(response.text)
        df = df.transpose()
        
        ce_values: List[dict] = [data['CE'] for data in json_data['records']['data'] if
                                 "CE" in data and data['expiryDate'].lower() == expiry_date.lower()]
        pe_values: List[dict] = [data['PE'] for data in json_data['records']['data'] if
                                 "PE" in data and data['expiryDate'].lower() == expiry_date.lower()]

        points: float = pe_values[0]['underlyingValue']
        if points == 0:
            for item in pe_values:
                if item['underlyingValue'] != 0:
                    points = item['underlyingValue']
                    break
        ce_data_f: pandas.DataFrame = pandas.DataFrame(ce_values)
        pe_data_f: pandas.DataFrame = pandas.DataFrame(pe_values)

        if ce_data_f.empty:
            # messagebox.showerror(title="Error",
            #                      message="Invalid Expiry Date.\nPlease restart and enter a new Expiry Date.")
            change_state()
            return
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
        # print( current_time, points)
        return merged_inner, current_time, points
    
def set_values(max_call_oi, max_call_oi_sp, max_call_oi_2, max_call_oi_sp_2, max_put_oi, max_put_oi_sp, max_put_oi_2, max_put_oi_sp_2, call_sum, put_sum, put_call_ratio, call_boundary,p4, p5, p6, p7, put_boundary, difference, call_itm, put_itm, str_current_time, points) -> None:
        # if first_run:
        #     root.title(f"NSE-Option-Chain-Analyzer - {index if option_mode == 'Index' else stock} "
        #                     f"- {expiry_date} - {sp}")

        old_max_call_oi_sp = 0.0
        old_max_call_oi_sp_2= 0.0
        old_max_put_oi_sp= 0.0
        old_max_put_oi_sp_2= 0.0

        # max_call_oi_val.config(text=max_call_oi)
        # max_call_oi_sp_val.config(text=max_call_oi_sp)
        # max_call_oi_2_val.config(text=max_call_oi_2)
        # max_call_oi_sp_2_val.config(text=max_call_oi_sp_2)
        # max_put_oi_val.config(text=max_put_oi)
        # max_put_oi_sp_val.config(text=max_put_oi_sp)
        # max_put_oi_2_val.config(text=max_put_oi_2)
        # max_put_oi_sp_2_val.config(text=max_put_oi_sp_2)

        if old_max_call_oi_sp == max_call_oi_sp:
            old_max_call_oi_sp = max_call_oi_sp
        else:
            # if notifications:
            #     toaster.show_toast("Upper Boundary Strike Price changed "
            #                             f"for {index if option_mode == 'Index' else stock}",
            #                             f"Changed from {old_max_call_oi_sp} to {max_call_oi_sp}",
            #                             duration=4, threaded=True,
            #                             icon_path=icon_ico_path if load_nse_icon else None)
            old_max_call_oi_sp = max_call_oi_sp

        if old_max_call_oi_sp_2 == max_call_oi_sp_2:
            old_max_call_oi_sp_2 = max_call_oi_sp_2
        else:
            # if notifications:
            #     toaster.show_toast("Upper Boundary Strike Price 2 changed "
            #                             f"for {index if option_mode == 'Index' else stock}",
            #                             f"Changed from {old_max_call_oi_sp_2} to {max_call_oi_sp_2}",
            #                             duration=4, threaded=True,
            #                             icon_path=icon_ico_path if load_nse_icon else None)
            old_max_call_oi_sp_2 = max_call_oi_sp_2

        if old_max_put_oi_sp == max_put_oi_sp:
            old_max_put_oi_sp = max_put_oi_sp
        else:
            # if notifications:
            #     toaster.show_toast("Lower Boundary Strike Price changed "
            #                             f"for {index if option_mode == 'Index' else stock}",
            #                             f"Changed from {old_max_put_oi_sp} to {max_put_oi_sp}",
            #                             duration=4, threaded=True,
            #                             icon_path=icon_ico_path if load_nse_icon else None)
            old_max_put_oi_sp = max_put_oi_sp

        if  old_max_put_oi_sp_2 == max_put_oi_sp_2:
            old_max_put_oi_sp_2 = max_put_oi_sp_2
        else:
            # if notifications:
            #     toaster.show_toast("Lower Boundary Strike Price 2 changed "
            #                             f"for {index if option_mode == 'Index' else stock}",
            #                             f"Changed from {old_max_put_oi_sp_2} to {max_put_oi_sp_2}",
            #                             duration=4, threaded=True,
            #                             icon_path=icon_ico_path if load_nse_icon else None)
            old_max_put_oi_sp_2 = max_put_oi_sp_2

        # red: str = "#e53935"
        # green: str = "#00e676"
        # default: str = "SystemButtonFace" if is_windows else "#d9d9d9"

        # bg: str

        old_oi_label= ""
        oi_label= ""

        if call_sum >= put_sum:
            oi_label = "Bearish"
            # bg = red
        else:
            oi_label = "Bullish"
            # bg = green
        # oi_val.config(text=oi_label, bg=bg)

        if old_oi_label == oi_label:
            old_oi_label = oi_label
        else:
            # if notifications:
            #     toaster.show_toast("Open Interest changed "
            #                             f"for {index if option_mode == 'Index' else stock}",
            #                             f"Changed from {old_oi_label} to {oi_label}",
            #                             duration=4, threaded=True,
            #                             icon_path=icon_ico_path if load_nse_icon else None)
            old_oi_label = oi_label

        if put_call_ratio >= 1:
            pcr_val = "Good"
            # pcr_val.config(text=put_call_ratio, bg=green)
        else:
            # pcr_val.config(text=put_call_ratio, bg=red)
            pcr_val = "Bad"

        def set_itm_labels(call_change: float, put_change: float) -> str:
            label: str = "No"
            if put_change > call_change:
                if put_change >= 0:
                    if call_change <= 0:
                        label = "Yes"
                    elif put_change / call_change > 1.5:
                        label = "Yes"
                else:
                    if put_change / call_change < 0.5:
                        label = "Yes"
            if call_change <= 0:
                label = "Yes"
            return label

        old_call_label = ""
        call: str = set_itm_labels(call_change=p5, put_change=p4)

        if call == "No":
            # call_itm_val.config(text="No", bg=default)
            call_itm_val = "No"
        else:
            # call_itm_val.config(text="Yes", bg=green)
            call_itm_val = "Yes"

        if old_call_label == call:
            old_call_label = call
        else:
            # if notifications:
            #     toaster.show_toast("Call ITM changed "
            #                             f"for {index if option_mode == 'Index' else stock}",
            #                             f"Changed from {old_call_label} to {call}",
            #                             duration=4, threaded=True,
            #                             icon_path=icon_ico_path if load_nse_icon else None)
            old_call_label = call

        old_put_label= ""
        put: str = set_itm_labels(call_change=p7, put_change=p6)

        if put == "No":
            # put_itm_val.config(text="No", bg=default)
            put_itm_val = "No"
        else:
            # put_itm_val.config(text="Yes", bg=red)
            put_itm_val = "Yes"

        if old_put_label == put:
            old_put_label = put
        else:
            # if notifications:
            #     toaster.show_toast("Put ITM changed "
            #                             f"for {index if option_mode == 'Index' else stock}",
            #                             f"Changed from {old_put_label} to {put}",
            #                             duration=4, threaded=True,
            #                             icon_path=icon_ico_path if load_nse_icon else None)
            old_put_label = put

        old_call_exits_label= ""
        call_exits_label=""

        if call_boundary <= 0:
            call_exits_label = "Yes"
            # bg = green
        elif call_sum <= 0:
            call_exits_label = "Yes"
            # bg = green
        else:
            call_exits_label = "No"
            # bg = default

        # call_exits_val.config(text=call_exits_label, bg=bg)
        if old_call_exits_label == call_exits_label:
            old_call_exits_label = call_exits_label
        else:
            # if notifications:
            #     toaster.show_toast("Call Exits changed "
            #                             f"for {index if option_mode == 'Index' else stock}",
            #                             f"Changed from {old_call_exits_label} to {call_exits_label}",
            #                             duration=4, threaded=True,
            #                             icon_path=icon_ico_path if load_nse_icon else None)
            old_call_exits_label = call_exits_label

        old_put_exits_label= ""
        put_exits_label=""

        if put_boundary <= 0:
            put_exits_label = "Yes"
            # bg = red
        elif put_sum <= 0:
            put_exits_label = "Yes"
            # bg = red
        else:
            put_exits_label = "No"
            # bg = default

        # put_exits_val.config(text=put_exits_label, bg=bg)
        if old_put_exits_label == put_exits_label:
            old_put_exits_label = put_exits_label
        else:
            # if notifications:
            #     toaster.show_toast("Put Exits changed "
            #                             f"for {index if option_mode == 'Index' else stock}",
            #                             f"Changed from {old_put_exits_label} to {put_exits_label}",
            #                             duration=4, threaded=True,
            #                             icon_path=icon_ico_path if load_nse_icon else None)
            old_put_exits_label = put_exits_label

        # output_values: List[Union[str, float]] = [str_current_time, points, call_sum,
        #                                           put_sum, difference,
        #                                           call_boundary, put_boundary, call_itm,
        #                                           put_itm]    ################################## went to line 675
        # sheet.insert_row(output_values)
        # if live_export:
        #     export_row(output_values)

        # last_row: int = sheet.get_total_rows() - 1

        old_points = 0.0
        if points == old_points:
            old_points = points
        elif points > old_points:
            # sheet.highlight_cells(row=last_row, column=1, bg=green)
            old_points = points
        else:
            # sheet.highlight_cells(row=last_row, column=1, bg=red)
            old_points = points
        old_call_sum = 0.0
        if old_call_sum == call_sum:
            old_call_sum = call_sum
        elif call_sum > old_call_sum:
            # sheet.highlight_cells(row=last_row, column=2, bg=red)
            old_call_sum = call_sum
        else:
            # sheet.highlight_cells(row=last_row, column=2, bg=green)
            old_call_sum = call_sum
        old_put_sum = 0.0
        if old_put_sum == put_sum:
            old_put_sum = put_sum
        elif put_sum > old_put_sum:
            # sheet.highlight_cells(row=last_row, column=3, bg=green)
            old_put_sum = put_sum
        else:
            # sheet.highlight_cells(row=last_row, column=3, bg=red)
            old_put_sum = put_sum
        old_difference = 0.0
        if old_difference == difference:
            old_difference = difference
        elif difference > old_difference:
            # sheet.highlight_cells(row=last_row, column=4, bg=red)
            old_difference = difference
        else:
            # sheet.highlight_cells(row=last_row, column=4, bg=green)
            old_difference = difference
        old_call_boundary = 0.0
        if old_call_boundary == call_boundary:
            old_call_boundary = call_boundary
        elif call_boundary > old_call_boundary:
            # sheet.highlight_cells(row=last_row, column=5, bg=red)
            old_call_boundary = call_boundary
        else:
            # sheet.highlight_cells(row=last_row, column=5, bg=green)
            old_call_boundary = call_boundary
        old_put_boundary = 0.0
        if old_put_boundary == put_boundary:
            old_put_boundary = put_boundary
        elif put_boundary > old_put_boundary:
            # sheet.highlight_cells(row=last_row, column=6, bg=green)
            old_put_boundary = put_boundary
        else:
            # sheet.highlight_cells(row=last_row, column=6, bg=red)
            old_put_boundary = put_boundary
        old_call_itm = 0.0
        if old_call_itm == call_itm:
            old_call_itm = call_itm
        elif call_itm > old_call_itm:
            # sheet.highlight_cells(row=last_row, column=7, bg=green)
            old_call_itm = call_itm
        else:
            # sheet.highlight_cells(row=last_row, column=7, bg=red)
            old_call_itm = call_itm
        old_put_itm = 0.0
        if old_put_itm == put_itm:
            old_put_itm = put_itm
        elif put_itm > old_put_itm:
            # sheet.highlight_cells(row=last_row, column=8, bg=red)
            old_put_itm = put_itm
        else:
            # sheet.highlight_cells(row=last_row, column=8, bg=green)
            old_put_itm = put_itm

        # if sheet.get_yview()[1] >= 0.9:
        #     sheet.see(last_row)
        #     sheet.set_yview(1)
        # sheet.refresh()
        
        output_values: Dict[Union[str, float]] = {"str_current_time" : str_current_time, "points": points, "call_sum":call_sum,
                                                  "put_sum":put_sum,"difference": difference,
                                                  "call_boundary":call_boundary,"put_boundary": put_boundary,"call_itm": call_itm,
                                                  "put_itm":put_itm,"expiry_date": expiry_date, "oi_label": oi_label, "put_call_ratio":put_call_ratio, "call_exits_label":call_exits_label, "call_itm_val":call_itm_val, "put_exits_label":put_exits_label,"put_itm_val":put_itm_val}
        # output_values: List[Union[str, float]] = [str_current_time, points, call_sum,
        #                                           put_sum, difference,
        #                                           call_boundary, put_boundary, call_itm,
        #                                           put_itm, expiry_date] 
        return output_values
        
def main():
        if stop:
            return

        # first_run =  True
        # print("line 630", first_run)
        try:
            entire_oc: pandas.DataFrame
            current_time: str
            points: float
            entire_oc, current_time, points = get_dataframe()
            # print(len(entire_oc))
        except TypeError:
            main() ##########################
            return

        str_current_time: str = current_time.split(" ")[1]
        current_date: datetime.date = datetime.strptime(current_time.split(" ")[0], '%d-%b-%Y').date()
        current_time: datetime.time = datetime.strptime(current_time.split(" ")[1], '%H:%M:%S').time()
        
        # if first_run is :
        #     previous_date = current_date
        #     previous_time = current_time
        # elif current_date > previous_date:
        #     previous_date = current_date
        #     previous_time = current_time
        # elif current_date == previous_date:
        #     if current_time > previous_time:
        #         global time_difference
        #         if current_time.hour > previous_time.hour:
        #             time_difference = (60 - previous_time.minute) + current_time.minute + \
        #                               ((60 - previous_time.second) + current_time.second) / 60
        #         elif current_time.hour == previous_time.hour:
        #             time_difference = current_time.minute - previous_time.minute + \
        #                               (current_time.second - previous_time.second) / 60
        #         # if time_difference >= time_difference_factor and warn_late_update:
        #         #     root.after(2000,
        #         #                     (lambda title="Late Update", message=f"The data from the server was last updated "
        #         #                                                          f"about {int(time_difference)} minutes ago.":
        #         #                      messagebox.showinfo(title=title, message=message)))
        #         previous_time = current_time
        #     else:
        #         # main() ################
        #         return

        call_oi_list: List[int] = []
        for i in range(len(entire_oc)):
            int_call_oi: int = int(entire_oc.iloc[i, [0]][0])
            call_oi_list.append(int_call_oi)
        call_oi_index: int = call_oi_list.index(max(call_oi_list))
        max_call_oi: float = round(max(call_oi_list) / round_factor, 1)
        max_call_oi_sp: float = float(entire_oc.iloc[call_oi_index]['Strike Price'])

        put_oi_list: List[int] = []
        for i in range(len(entire_oc)):
            int_put_oi: int = int(entire_oc.iloc[i, [20]][0])
            put_oi_list.append(int_put_oi)
        put_oi_index: int = put_oi_list.index(max(put_oi_list))
        max_put_oi: float = round(max(put_oi_list) / round_factor, 1)
        max_put_oi_sp: float = float(entire_oc.iloc[put_oi_index]['Strike Price'])

        sp_range_list: List[float] = []
        for i in range(put_oi_index, call_oi_index + 1):
            sp_range_list.append(float(entire_oc.iloc[i]['Strike Price']))

        # max_call_oi_2
        # max_call_oi_sp_2
        # max_put_oi_2
        # max_put_oi_sp_2
        if max_call_oi_sp == max_put_oi_sp:
            max_call_oi_2 = max_call_oi
            max_call_oi_sp_2 = max_call_oi_sp
            max_put_oi_2 = max_put_oi
            max_put_oi_sp_2 = max_put_oi_sp
        elif len(sp_range_list) == 2:
            max_call_oi_2 = round((entire_oc[entire_oc['Strike Price'] == max_put_oi_sp].iloc[0, 0]) /
                                       round_factor, 1)
            max_call_oi_sp_2 = max_put_oi_sp
            max_put_oi_2 = round((entire_oc[entire_oc['Strike Price'] == max_call_oi_sp].iloc[0, 20]) /
                                      round_factor, 1)
            max_put_oi_sp_2 = max_call_oi_sp
        else:
            call_oi_list_2: List[int] = []
            for i in range(put_oi_index, call_oi_index):
                int_call_oi_2: int = int(entire_oc.iloc[i, [0]][0])
                call_oi_list_2.append(int_call_oi_2)
            call_oi_index_2: int = put_oi_index + call_oi_list_2.index(max(call_oi_list_2))
            max_call_oi_2 = round(max(call_oi_list_2) / round_factor, 1)
            max_call_oi_sp_2 = float(entire_oc.iloc[call_oi_index_2]['Strike Price'])

            put_oi_list_2: List[int] = []
            for i in range(put_oi_index + 1, call_oi_index + 1):
                int_put_oi_2: int = int(entire_oc.iloc[i, [20]][0])
                put_oi_list_2.append(int_put_oi_2)
            put_oi_index_2: int = put_oi_index + 1 + put_oi_list_2.index(max(put_oi_list_2))
            max_put_oi_2 = round(max(put_oi_list_2) / round_factor, 1)
            max_put_oi_sp_2 = float(entire_oc.iloc[put_oi_index_2]['Strike Price'])

        total_call_oi: int = sum(call_oi_list)
        total_put_oi: int = sum(put_oi_list)
        try:
            put_call_ratio = round(total_put_oi / total_call_oi, 2)
        except ZeroDivisionError:
            put_call_ratio = 0

        try:
            # print(entire_oc)
            # print(entire_oc[entire_oc['Strike Price'] == sp_entry])
            index = entire_oc[entire_oc['Strike Price'] == sp_entry].index.tolist()[0]
            # print(index)
        except IndexError as err:
            # print(err, sys.exc_info()[0], "line 777")
            # print("Incorrect Strike Price.\nPlease enter correct Strike Price.")
            return 1

        a: pandas.DataFrame = entire_oc[['Change in Open Interest']][entire_oc['Strike Price'] == sp_entry]
        b1: pandas.Series = a.iloc[:, 0]
        c1: int = int(b1.get(index))
        b2: pandas.Series = entire_oc.iloc[:, 1]
        c2: int = int(b2.get((index + 1), 'Change in Open Interest'))
        b3: pandas.Series = entire_oc.iloc[:, 1]
        c3: int = int(b3.get((index + 2), 'Change in Open Interest'))
        if isinstance(c2, str):
            c2 = 0
        if isinstance(c3, str):
            c3 = 0
        call_sum: float = round((c1 + c2 + c3) / round_factor, 1)
        if call_sum == -0:
            call_sum = 0.0
        call_boundary: float = round(c3 / round_factor, 1)

        o1: pandas.Series = a.iloc[:, 1]
        p1: int = int(o1.get(index))
        o2: pandas.Series = entire_oc.iloc[:, 19]
        p2: int = int(o2.get((index + 1), 'Change in Open Interest'))
        p3: int = int(o2.get((index + 2), 'Change in Open Interest'))
        p4: int = int(o2.get((index + 4), 'Change in Open Interest'))
        o3: pandas.Series = entire_oc.iloc[:, 1]
        p5: int = int(o3.get((index + 4), 'Change in Open Interest'))
        p6: int = int(o3.get((index - 2), 'Change in Open Interest'))
        p7: int = int(o2.get((index - 2), 'Change in Open Interest'))
        if isinstance(p2, str):
            p2 = 0
        if isinstance(p3, str):
            p3 = 0
        if isinstance(p4, str):
            p4 = 0
        if isinstance(p5, str):
            p5 = 0
        put_sum: float = round((p1 + p2 + p3) / round_factor, 1)
        put_boundary: float = round(p1 / round_factor, 1)
        difference: float = round(call_sum - put_sum, 1)
        call_itm: float
        if p5 == 0:
            call_itm = 0.0
        else:
            call_itm = round(p4 / p5, 1)
            if call_itm == -0:
                call_itm = 0.0
        if isinstance(p6, str):
            p6 = 0
        if isinstance(p7, str):
            p7 = 0
        put_itm: float
        if p7 == 0:
            put_itm = 0.0
        else:
            put_itm = round(p6 / p7, 1)
            if put_itm == -0:
                put_itm = 0.0

        if stop:
            return


        # if save_oc:
        #     try:
        #         entire_oc.to_csv(
        #             f"NSE-OCA-{index if option_mode == 'Index' else stock}-{expiry_date}-Full.csv",
        #             index=False)
        #     except PermissionError as err:
        #         print(err, sys.exc_info()[0], "11")
        #         # messagebox.showerror(title="Export Failed",
        #         #                      message=f"Failed to access NSE-OCA-"
        #         #                              f"{index if option_mode == 'Index' else stock}-"
        #         #                              f"{expiry_date}-Full.csv.\n"
        #         #                              f"Permission Denied. Try closing any apps using it.")
        #     except Exception as err:
        #         print(err, sys.exc_info()[0], "16")

        # if first_run == True:
        # first_run = False
        # print("main theke...............",first_run)
        return (set_values(max_call_oi, max_call_oi_sp, max_call_oi_2, max_call_oi_sp_2, max_put_oi, max_put_oi_sp, max_put_oi_2, max_put_oi_sp_2, call_sum, put_sum, put_call_ratio, call_boundary, p4, p5, p6, p7, put_boundary, difference, call_itm, put_itm, str_current_time, points))
        # if str_current_time == '15:30:00' and not stop and auto_stop \
        #         and previous_date == datetime.datetime.strptime(time.strftime("%d-%b-%Y", time.localtime()),
        #                                                              "%d-%b-%Y").date():
        #     stop = True
            
        #     # messagebox.showinfo(title="Market Closed", message="Retrieving new data has been stopped.")
        #     return
        # # root.after((seconds * 1000), main)
        
        # return ("alright")