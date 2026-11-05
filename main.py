from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

# Enable CORS so your Netlify dashboard can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scan")
def run_quant_scan():
    tickers = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
        "SBIN.NS", "AXISBANK.NS", "POWERGRID.NS", "BPCL.NS", "ONGC.NS"
        # Add your full Nifty 50 ticker list here
    ]
    
    results = []
    for symbol in tickers:
        try:
            tk = yf.Ticker(symbol)
            df = tk.history(period="6mo")
            if len(df) < 50:
                continue
                
            latest_close = df.iloc[-1]['Close']
            info = tk.info
            
            # Fundamentals
            trailing_pe = info.get('trailingPE')
            roe = info.get('returnOnEquity')
            market_cap = tk.fast_info.market_cap or info.get('marketCap', 0)
            
            # Technicals
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['RSI_14'] = 100 - (100 / (1 + rs))
            
            latest = df.iloc[-1]
            
            results.append({
                'Ticker': symbol.replace('.NS', ''),
                'Trailing_PE': trailing_pe,
                'Close': float(latest_close),
                'SMA_50': float(latest['SMA_50']),
                'RSI_14': float(latest['RSI_14']),
                'MACD_Bullish': True,
                'Vol_Breakout': True,
                'ROE': float(roe * 100) if roe else None,
                'Market_Cap_B': float(market_cap / 1e9) if market_cap else 0
            })
        except Exception:
            continue
            
    df_res = pd.DataFrame(results)
    df_res['Trailing_PE'] = pd.to_numeric(df_res['Trailing_PE'], errors='coerce')
    
    filtered = df_res[
        (df_res['Trailing_PE'] > 0) & 
        (df_res['Trailing_PE'] < 50) & 
        (df_res['RSI_14'] < 70) &
        (df_res['Close'] > df_res['SMA_50'])
    ].copy()
    
    ranked = filtered.sort_values(by='Trailing_PE', ascending=True).reset_index(drop=True)
    ranked.insert(0, 'Rank', ranked.index + 1)
    
    return ranked.to_dict(orient='records')
