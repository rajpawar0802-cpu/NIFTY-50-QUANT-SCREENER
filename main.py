from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def calculate_macd(series, span1=12, span2=26, signal=9):
    exp1 = series.ewm(span=span1, adjust=False).mean()
    exp2 = series.ewm(span=span2, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

@app.get("/scan")
def run_quant_scan():
    tickers = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
        "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "HINDUNILVR.NS", "LT.NS",
        "BAJFINANCE.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "AXISBANK.NS",
        "KOTAKBANK.NS", "TATASTEEL.NS", "NTPC.NS", "POWERGRID.NS", "M&M.NS",
        "HCLTECH.NS", "ASIANPAINT.NS", "ADANIENT.NS", "BAJAJFINSV.NS", "GRASIM.NS",
        "INDUSINDBK.NS", "TECHM.NS", "WIPRO.NS", "ONGC.NS", "COALINDIA.NS",
        "HINDALCO.NS", "DIVISLAB.NS", "BPCL.NS", "DRREDDY.NS", "CIPLA.NS",
        "EICHERMOT.NS", "SBILIFE.NS", "TATACONSUM.NS", "BRITANNIA.NS", "HEROMOTOCO.NS",
        "APOLLOHOSP.NS", "ADANIPORTS.NS", "BAJAJ-AUTO.NS", "NESTLEIND.NS", "BEL.NS",
        "SHRIRAMFIN.NS", "TORNTPHARM.NS", "SBICARD.NS"
    ]
    
    results = []
    for symbol in tickers:
        try:
            tk = yf.Ticker(symbol)
            df = tk.history(period="6mo")
            if len(df) < 50:
                continue
                
            latest_close = df.iloc[-1]['Close']
            info = tk.info or {}
            
            # Fundamentals
            trailing_pe = info.get('trailingPE')
            roe = info.get('returnOnEquity')
            
            market_cap = None
            try:
                market_cap = tk.fast_info.market_cap
            except Exception:
                pass
            if not market_cap:
                market_cap = info.get('marketCap', 0)
            
            # Technical Indicators
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['RSI_14'] = calculate_rsi(df['Close'])
            df['MACD'], df['MACD_Signal'] = calculate_macd(df['Close'])
            df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
            
            latest = df.iloc[-1]
            macd_bullish = bool(latest['MACD'] > latest['MACD_Signal'])
            vol_breakout = bool(latest['Volume'] > (1.2 * latest['Vol_SMA_20']))
            
            results.append({
                'Ticker': symbol.replace('.NS', ''),
                'Trailing_PE': float(trailing_pe) if trailing_pe else None,
                'Close': float(latest_close),
                'SMA_50': float(latest['SMA_50']) if not pd.isna(latest['SMA_50']) else float(latest_close),
                'RSI_14': float(latest['RSI_14']) if not pd.isna(latest['RSI_14']) else 50.0,
                'MACD_Bullish': macd_bullish,
                'Vol_Breakout': vol_breakout,
                'ROE': float(roe * 100) if roe else None,
                'Market_Cap_B': float(market_cap / 1e9) if market_cap else 0.0
            })
        except Exception:
            continue
            
    df_res = pd.DataFrame(results)
    if df_res.empty:
        return []

    df_res['Trailing_PE'] = pd.to_numeric(df_res['Trailing_PE'], errors='coerce')
    
    # Filter valid P/E values
    valid_pe = df_res[df_res['Trailing_PE'] > 0].copy()
    
    # Strict screener criteria
    filtered = valid_pe[
        (valid_pe['Trailing_PE'] < 50) & 
        (valid_pe['Close'] >= valid_pe['SMA_50'] * 0.95)
    ].copy()
    
    # Fallback to valid PE if criteria is too strict
    final_df = filtered if not filtered.empty else valid_pe
    
    ranked = final_df.sort_values(by='Trailing_PE', ascending=True).reset_index(drop=True)
    ranked.insert(0, 'Rank', ranked.index + 1)
    
    return ranked.to_dict(orient='records')
   
       
    
 
