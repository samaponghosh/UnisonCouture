from django import forms

class ScreeningForm(forms.Form):
    ticker_option = forms.ChoiceField(choices=['All Stocks (Default)',
    '0 > By Stock Names (NSE Stock Code)',
    '1 > Nifty 50',
    '2 > Nifty Next 50',
    '3 > Nifty 100',
    '4 > Nifty 200',
    '5 > Nifty 500',
    '6 > Nifty Smallcap 50',
    '7 > Nifty Smallcap 100',
    '8 > Nifty Smallcap 250',
    '9 > Nifty Midcap 50',
    '10 > Nifty Midcap 100',
    '11 > Nifty Midcap 150',
    '13 > Newly Listed (IPOs in last 2 Year)',
    '14 > F&O Stocks Only',
    '15 > US S&P 500',
    '16 > Sectoral Indices (NSE)'])
    backtest_date = forms.DateField()
    execute_option = forms.ChoiceField(choices=['0 > Full Screening (Shows Technical Parameters without Any Criteria)',
      '1 > Screen stocks for Breakout or Consolidation',
      '2 > Screen for the stocks with recent Breakout & Volume',
      '3 > Screen for the Consolidating stocks',
      '4 > Screen for the stocks with Lowest Volume in last N-days (Early Breakout Detection)',
      '5 > Screen for the stocks with RSI',
      '6 > Screen for the stocks showing Reversal Signals',
      '7 > Screen for the stocks making Chart Patterns'])