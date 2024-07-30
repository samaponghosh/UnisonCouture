from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

import pandas as pd
from django.template import loader

import pandas as pd
import os
import random
import requests
import configparser
import urllib
import datetime
from num2words import num2words
from time import sleep
from pathlib import Path
from threading import Thread
from time import sleep
from math import floor
import unisonapp.ConfigManager as ConfigManager
import unisonapp.Utility as Utility
import unisonapp.Fetcher as Fetcher
from unisonapp.screenipy import main


try:
    proxyServer = urllib.request.getproxies()['http']
except KeyError:
    proxyServer = ""
    
# execute_inputs = []
backtestDate = datetime.date.today()
isDevVersion = None

def home(request):
    return render(request, 'index.html')

def user_signup(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            fname = request.POST['fname']
            lname = request.POST['lname']
            user = request.POST['username']
            pass1 = request.POST['password']
            pass2 = request.POST['passwordconf']
            emailInp = request.POST['email1']
            # now = datetime.now()
            if(pass1 == pass2):
                user_exist = User.objects.filter(email=emailInp).exists()
                if user_exist:
                    messages.error(
                        request, 'This email id already exists. Please use a different one.')
                    return HttpResponseRedirect("/signup")
                else:
                    if(pass1.isalnum() and pass1.isalpha() == False and pass1.isdigit() == False and len(pass1) >= 8):
                        if str(pass1).find(user) != -1:
                            messages.error(
                                request, 'Password should not contain username.')
                            return HttpResponseRedirect("/signup")
                        else:
                            myuser = User.objects.create_user(user, emailInp, pass1)
                            myuser.first_name = fname
                            myuser.last_name = lname
                            # myuser.acCreated = now
                            myuser.save()

                            # return HttpResponseRedirect('/')
                            # for login after signup
                            user = authenticate(request, username=user, email=emailInp, password=pass1)
                            # print(user)
                            if user is not None:
                                login(request, user)
                                return HttpResponseRedirect('/')
                            else:
                                messages.error(request, 'User not found')
                                return HttpResponseRedirect('/signup')                
                    else:
                        messages.error(
                            request, 'Password should be alphanumeric and should contain atleast 8 characters.')
                        return HttpResponseRedirect("/signup")
            else:
                messages.error(
                    request, "Password Not match. Re-enter password correctly.")
                return HttpResponseRedirect("/signup")
        else:
            return render(request, 'signup.html')
    else:
        return HttpResponseRedirect('/')

def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            emailInp = request.POST.get('email1')
            password = request.POST.get('password')
            user = authenticate(request, username=username, email=emailInp, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                messages.error(
                    request, "Password Not match. Re-enter password correctly.")
                return HttpResponseRedirect('/login')
        else:
            return render(request, 'login.html')
    else:
        return HttpResponseRedirect('/')
    
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/')


def nifty_predict(request):
    if request.user.is_authenticated:
        import unisonapp.Fetcher as Fetcher
        import unisonapp.Screener as Screener
        configManager = ConfigManager.tools()
        fetcher = Fetcher.tools(configManager)
        screener = Screener.tools(configManager)
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
        prediction, trend, confidence, data_used = screener.getNiftyPrediction(
            data=fetcher.fetchLatestNiftyDaily(proxyServer=proxyServer), 
            proxyServer=proxyServer
        )
    
        if 'BULLISH' in trend:
            messages.success(request, f'Market may Open **Gap Up** next day!\n\nProbability/Strength of Prediction = {confidence} %')
        elif 'BEARISH' in trend:
            messages.error(request, f'Market may Open **Gap Down** next day!\n\nProbability/Strength of Prediction =  {confidence} %')
        else:
            messages.error(request, "Couldn't determine the Trend. Try again later!")
        messages.warning(request,'The AI prediction should be executed After 3 PM or Around the Closing hours as the Prediction Accuracy is based on the Closing price!\n\nThis is Just a Statistical Prediction and There are Chances of **False** Predictions!')
        messages.info(request,"Machine Learning model uses Nifty, Crude and Gold Historical prices to Predict the Gap!")
        messages.info(request,"**Following data is used to make above prediction:**")
        df_html = data_used.to_html(classes="table table-striped")
        context = {'df_html': df_html}
        return render(request, 'GapPredict.html', context)
        #return render(request, 'GapPredict.html')
    else:
        messages.error(request,"You have to login first to use the service")
        return HttpResponseRedirect('/login')
    
def pos_calc(request):
    if request.user.is_authenticated:
        return render(request, 'PosCalc.html')
    else:
        messages.error(request,"You have to login first to use the service")
        return HttpResponseRedirect('/login')

def on_start_button_click(execute_inputs):
    # print(".........................",execute_inputs)
    def dummy_call():
        try:
            main(execute_inputs=execute_inputs)
        except StopIteration:
            pass
        except requests.exceptions.RequestException:
            os.environ['SCREENIPY_REQ_ERROR'] = "TRUE"
    
    if Utility.tools.isBacktesting(backtestDate=backtestDate):
        msg1 = f'Running in :red[**Backtesting Mode**] for *T = {str(backtestDate)}* (Y-M-D) : [Backtesting data is subjected to availability as per the API limits]'
        msg2 = 'Backtesting is :red[Not Supported] for Intraday timeframes'
        print(msg1,msg2)
    t = Thread(target=dummy_call)
    t.start()

    # progress_text = "🚀 Preparing Screener, Please Wait! "
    # progress_bar = st.progress(0, text=progress_text)

    os.environ['SCREENIPY_SCREEN_COUNTER'] = '0'
    while int(os.environ.get('SCREENIPY_SCREEN_COUNTER')) < 100:
        sleep(0.05)
        cnt = int(os.environ.get('SCREENIPY_SCREEN_COUNTER'))
        if cnt > 0:
            print("Screening stocks for you... ")
            # progress_bar.progress(cnt, text=progress_text + f"**:red[{cnt}%]** Done")
        if os.environ.get('SCREENIPY_REQ_ERROR') and "TRUE" in os.environ.get('SCREENIPY_REQ_ERROR'):
            print(':disappointed: Failed to reach Screeni-py server!')
            del os.environ['SCREENIPY_REQ_ERROR']
            break
    t.join()
    # sleep(3)
    return show_df_as_result_table(execute_inputs)

def show_df_as_result_table(execute_inputs):
    try:
        df = pd.read_pickle('unisonapp\last_screened_unformatted_results.pkl')
        if type(execute_inputs[0]) == str or int(execute_inputs[0]) < 15:
            df.index = df.index.map(lambda x: "https://in.tradingview.com/chart?symbol=NSE%3A" + x)
            df.index = df.index.map(lambda x: f'<a href="{x}" target="_blank">{x.split("%3A")[-1]}</a>')
        elif execute_inputs[0] == '16':
            try:
                fetcher = Fetcher.tools(configManager=ConfigManager.tools())
                url_dict_reversed = {key.replace('^','').replace('.NS',''): value for key, value in fetcher.getAllNiftyIndices().items()}
                url_dict_reversed = {v: k for k, v in url_dict_reversed.items()}
                df.index = df.index.map(lambda x: "https://in.tradingview.com/chart?symbol=NSE%3A" + url_dict_reversed[x])
                url_dict_reversed = {v: k for k, v in url_dict_reversed.items()}
                df.index = df.index.map(lambda x: f'<a href="{x}" target="_blank">{url_dict_reversed[x.split("%3A")[-1]]}</a>')
            except KeyError:
                pass
        else:
            df.index = df.index.map(lambda x: "https://in.tradingview.com/chart?symbol=" + x)
            df.index = df.index.map(lambda x: f'<a href="{x}" target="_blank">{x.split("=")[-1]}</a>')
        
        df['Stock'] = df.index
        stock_column = df.pop('Stock')  # Remove 'Age' column and store it separately
        df.insert(0, 'Stock', stock_column)
        context = {'df': df.to_html(escape=False, index=False, index_names=False)}
        return context

    except FileNotFoundError:
        # print('Last Screened results are not available at the moment')
        return ('LS')
    except Exception as e:
        # print('No Dataframe found for last_screened_results.pkl')
        return ('ND')

def get_extra_inputs(tickerOption, executeOption, stock_codes, num_candles, min_rsi, max_rsi, select_reversal, ma_length, range_value, signal_type, select_pattern, confluence_percentage ):
    if not tickerOption.isnumeric():
        execute_inputs = [tickerOption, 0, 'N']
    elif int(tickerOption) == 0 or tickerOption is None:
        execute_inputs = [tickerOption, executeOption, stock_codes, 'N']
    elif int(executeOption) >= 0 and int(executeOption) < 4:
        execute_inputs = [tickerOption, executeOption, 'N']
    elif int(executeOption) == 4:
        if num_candles is not None:
            execute_inputs = [tickerOption, executeOption, num_candles, 'N']
        else:
            return HttpResponse("Number of Candles can't be left blank!", status=400)
    elif int(executeOption) == 5:
        if min_rsi is not None and max_rsi is not None:
            if min_rsi >= max_rsi:
                return HttpResponse('WARNING: Min RSI ≥ Max RSI', status=400)
            execute_inputs = [tickerOption, executeOption, min_rsi, max_rsi, 'N']
        else:
            return HttpResponse("Min and Max RSI values are required!", status=400)
    elif int(executeOption) == 6:
        if select_reversal == '4':
            if ma_length is not None:
                execute_inputs = [tickerOption, executeOption, select_reversal, ma_length, 'N']
            else:
                return HttpResponse("MA Length can't be left blank!", status=400)
        elif select_reversal == '6':
            if range_value is not None:
                execute_inputs = [tickerOption, executeOption, select_reversal, range_value, 'N']
            else:
                return HttpResponse("NR(x) value can't be left blank!", status=400)
        elif select_reversal == '7':
            if signal_type is not None:
                execute_inputs = [tickerOption, executeOption, select_reversal, signal_type, 'N']
            else:
                return HttpResponse("Signal Type can't be left blank!", status=400)
        else:
            execute_inputs = [tickerOption, executeOption, select_reversal, 'N']
    elif int(executeOption) == 7:
        if select_pattern:
            if select_pattern in ('1', '2'):
                if num_candles is not None:
                    execute_inputs = [tickerOption, executeOption, select_pattern, num_candles, 'N']
                else:
                    return HttpResponse("Lookback Candles can't be left blank!", status=400)
            elif select_pattern == '3':
                if confluence_percentage is not None:
                    execute_inputs = [tickerOption, executeOption, select_pattern, confluence_percentage, 'N']
                else:
                    return HttpResponse("Confluence Percentage can't be left blank!", status=400)
            else:
                execute_inputs = [tickerOption, executeOption, select_pattern, 'N']
        else:
            return HttpResponse("Chart Pattern selection is required!", status=400)
    return on_start_button_click(execute_inputs)

def stockScreen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            c_index = request.POST.get('list_index')
            c_criteria = request.POST.get('list_criteria')
            stock_codes = request.POST.get('stock_codes')
            num_candles = request.POST.get('num_candles')
            min_rsi = request.POST.get('min_rsi')
            max_rsi = request.POST.get('max_rsi')
            select_reversal = request.POST.get('select_reversal')
            ma_length = request.POST.get('ma_length')
            range_value = request.POST.get('range_value')
            signal_type = request.POST.get('signal_type')
            select_pattern = request.POST.get('select_pattern')
            confluence_percentage = request.POST.get('confluence_percentage')
            # c_datepick = datetime.date.today()
            # print(c_index)
            # print(c_criteria)

            configManager = ConfigManager.tools()
            configManager.getConfig(parser=ConfigManager.parser)

            tickerOption = c_index.split(' ')
            tickerOption = str(12 if '>' not in tickerOption else int(tickerOption[0]) if tickerOption[0].isnumeric() else str(tickerOption[0]))
            # picked_date = c_datepick
            # if picked_date:
                # backtestDate = picked_date

            executeOption = str(c_criteria).split(' ')[0]

            res = get_extra_inputs(tickerOption, executeOption, stock_codes, num_candles, min_rsi, max_rsi, select_reversal, ma_length, range_value, signal_type, select_pattern, confluence_percentage)
            
            if res == 'LS':
                messages.error(request, "Last Screened results are not available at the moment")
                return render(request, 'result_table.html')
            elif res == 'ND':
                messages.error(request, "No Dataframe found for last_screened_results.pkl")
                return render(request, 'result_table.html')
            else:
                return render(request, 'result_table.html', res)
        else:
            return render(request, 'ScreeningForm.html')
    else:
        messages.error(request,"You have to login first to use this service")
        return HttpResponseRedirect('/login')

def find_similar_stocks(stockCode:str, candles:int):
    global execute_inputs
    stockCode = stockCode.upper()
    if ',' in stockCode or ' ' in stockCode or stockCode == '':
        # st.error('Invalid Character in Stock Name!', icon='😾')
        return False
    else:
        execute_inputs = ['S', 0, stockCode, candles, 'N']
        on_start_button_click()
        # st.toast('Screening Completed!', icon='🎉')
    return True

def simSearch(request):
    if request.user.is_authenticated:
        if request.method == 'POST':        
            stockCode = request.POST.get('stockName')
            candles = request.POST.get('candleNo')

            result = find_similar_stocks(stockCode, candles)
            if result:
                res = show_df_as_result_table()
                if res == 'LS':
                    messages.error(request, "Last Screened results are not available at the moment")
                    return render(request, 'result_table.html')
                elif res == 'ND':
                    messages.error(request, "No Dataframe found for last_screened_results.pkl")
                    return render(request, 'result_table.html')
                else:
                    return render(request, 'result_table.html', res)
        else:
            return render(request, 'simSearch.html')
    else:
        messages.error(request,"You have to login first to use this service")
        return HttpResponseRedirect('/login')

def on_config_change(period,daystolookback,duration,minprice,maxprice,volumeratio,consolidationpercentage,shuffle,cache,stagetwo,useema):
    configManager = ConfigManager.tools()
    configManager.period = period
    configManager.daysToLookback = daystolookback
    configManager.duration = duration
    configManager.minLTP, configManager.maxLTP = minprice, maxprice
    configManager.volumeRatio, configManager.consolidationPercentage = volumeratio, consolidationpercentage
    configManager.shuffle = shuffle
    configManager.cacheEnabled = cache
    configManager.stageTwo = stagetwo
    configManager.useEMA = useema
    configManager.setConfig(configparser.ConfigParser(strict=False), default=True, showFileCreatedText=False)
    msg0 = True
    return msg0
    
def screenConfig(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            period = request.POST.get('period')
            daystolookback = request.POST.get('daystolookback')
            duration = request.POST.get('duration')
            minprice = request.POST.get('minprice')
            maxprice = request.POST.get('maxprice')
            volumeratio = request.POST.get('volumeratio')
            consolidationpercentage = request.POST.get('consolidationpercentage')
            shuffle = request.POST.get('shuffle')
            cache = request.POST.get('cache')
            stagetwo = request.POST.get('stagetwo')
            useema = request.POST.get('useema')
            
            configManager = ConfigManager.tools()
            configManager.getConfig(parser=ConfigManager.parser)

            res = on_config_change(period,daystolookback,duration,minprice,maxprice,volumeratio,consolidationpercentage,shuffle,cache,stagetwo,useema)
            if res:	
                messages.success(request, "New configuration saved successfully")
                return HttpResponseRedirect('/screen_config')
            else:
                messages.error(request, "Something went wrong !!!")
        else:
            return render(request, 'configMenu.html')
    else:
        messages.error(request, "You have to login first to use this service")
        return HttpResponseRedirect('/login')

def about(request):
    return render(request, 'about.html')