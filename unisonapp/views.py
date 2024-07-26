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
    proxyServer = urllib.request.getproxies()['https']
except KeyError:
    proxyServer = ""
    
execute_inputs = []
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
    # if request.method == 'POST':
    #     capital = request.POST.get('capitalSize')
    #     risk = request.POST.get('riskOnCapital')
    #     sl = request.POST.get('stoplossPoints')
        
    #     capital = float(capital)
    #     risk = float(risk)
        
    #     risk_rs = capital * (risk/100.0)
    #     print(risk_rs)
    # # return render(request, 'PosCalc.html', {'risk_rs': risk_rs})
        return render(request, 'PosCalc.html')
    else:
        messages.error(request,"You have to login first to use the service")
        return HttpResponseRedirect('/login')

def on_start_button_click():
    global execute_inputs
    print(execute_inputs)
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

def show_df_as_result_table():
    try:
        df = pd.read_pickle('last_screened_unformatted_results.pkl')
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
        
        # template = loader.get_template('result_table.html')
        context = {'df': df.to_html(escape=False, index=False, index_names=False)}
        # return HttpResponse(template.render(context, request))
        return context

    except FileNotFoundError:
        print('Last Screened results are not available at the moment')
        return ('LS')
    except Exception as e:
        print('No Dataframe found for last_screened_results.pkl')
        return ('ND')

def get_extra_inputs(tickerOption, executeOption):
    global execute_inputs
    if not tickerOption.isnumeric():
        execute_inputs = [tickerOption, 0, 'N']
        # return execute_inputs
    # elif int(tickerOption) == 0 or tickerOption is None:
    #     # stock_codes:str = c_index.text_input('Enter Stock Code(s)', placeholder='SBIN, INFY, ITC')
    #     execute_inputs = [tickerOption, executeOption, stock_codes.upper(), 'N']
    #     return
    # elif int(executeOption) >= 0 and int(executeOption) < 4:
    #     execute_inputs = [tickerOption, executeOption, 'N']
    # elif int(executeOption) == 4:
    #     # num_candles = c_criteria.text_input('The Volume should be lowest since last how many candles?', value='20')
    #     if num_candles:
    #         execute_inputs = [tickerOption, executeOption, num_candles, 'N']
    #     else:
    #         c_criteria.error("Number of Candles can't be left blank!")    
    # elif int(executeOption) == 5:
    #     min_rsi, max_rsi = c_criteria.columns((1,1))
    #     min_rsi = min_rsi.number_input('Min RSI', min_value=0, max_value=100, value=50, step=1, format="%d")
    #     max_rsi = max_rsi.number_input('Max RSI', min_value=0, max_value=100, value=70, step=1, format="%d")
    #     if min_rsi >= max_rsi:
    #         c_criteria.warning('WARNING: Min RSI ≥ Max RSI')
    #     else:
    #         execute_inputs = [tickerOption, executeOption, min_rsi, max_rsi, 'N']
    # elif int(executeOption) == 6:
    #     c1, c2 = c_criteria.columns((7,2))
    #     select_reversal = int(c1.selectbox('Select Type of Reversal',
    #                         options = [
    #                             '1 > Buy Signal (Bullish Reversal)',
    #                             '2 > Sell Signal (Bearish Reversal)',
    #                             '3 > Momentum Gainers (Rising Bullish Momentum)',
    #                             '4 > Reversal at Moving Average (Bullish Reversal)',
    #                             '5 > Volume Spread Analysis (Bullish VSA Reversal)',
    #                             '6 > Narrow Range (NRx) Reversal',
    #                             '7 > Lorentzian Classifier (Machine Learning based indicator)',
    #                             '8 > RSI Crossing with 9 SMA of RSI itself'
    #                         ]
    #                     ).split(' ')[0])
    #     if select_reversal == 4:
    #         ma_length = c2.number_input('MA Length', value=44, step=1, format="%d")
    #         execute_inputs = [tickerOption, executeOption, select_reversal, ma_length, 'N']
    #     elif select_reversal == 6:
    #         range = c2.number_input('NR(x)',min_value=1, max_value=14, value=4, step=1, format="%d")
    #         execute_inputs = [tickerOption, executeOption, select_reversal, range, 'N']
    #     elif select_reversal == 7:
    #         signal = int(c2.selectbox('Signal Type',
    #                         options = [
    #                             '1 > Any',
    #                             '2 > Buy',
    #                             '3 > Sell',
    #                         ]
    #                     ).split(' ')[0])
    #         execute_inputs = [tickerOption, executeOption, select_reversal, signal, 'N']
    #     else:
    #         execute_inputs = [tickerOption, executeOption, select_reversal, 'N']
    # elif int(executeOption) == 7:
    #     # c1, c2 = c_criteria.columns((11,4))
    #     select_pattern = int(c1.selectbox('Select Chart Pattern',
    #                         options = [
    #                             '1 > Bullish Inside Bar (Flag) Pattern',
    #                             '2 > Bearish Inside Bar (Flag) Pattern',
    #                             '3 > Confluence (50 & 200 MA/EMA)',
    #                             '4 > VCP (Experimental)',
    #                             '5 > Buying at Trendline (Ideal for Swing/Mid/Long term)',
    #                         ]
    #                     ).split(' ')[0])
    #     if select_pattern == 1 or select_pattern == 2:
    #         num_candles = c2.number_input('Lookback Candles', min_value=1, max_value=25, value=12, step=1, format="%d")
    #         execute_inputs = [tickerOption, executeOption, select_pattern, int(num_candles), 'N']
    #     elif select_pattern == 3:
    #         confluence_percentage = c2.number_input('MA Confluence %', min_value=0.1, max_value=5.0, value=1.0, step=0.1, format="%1.1f")/100.0
    #         execute_inputs = [tickerOption, executeOption, select_pattern, confluence_percentage, 'N']
    #     else:
    #         execute_inputs = [tickerOption, executeOption, select_pattern, 'N']

def stockScreen(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            c_index = request.POST.get('list_index')
            c_criteria = request.POST.get('list_criteria')
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

            # start_button = c_button_start.button('Start Screening', type='primary', key='start_button', use_container_width=True)

            get_extra_inputs(tickerOption=tickerOption, executeOption=executeOption)

            on_start_button_click()

            res= show_df_as_result_table()
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