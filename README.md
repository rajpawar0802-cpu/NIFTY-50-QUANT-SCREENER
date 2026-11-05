# 🚀 Nifty 50 Quantitative Screener & Portfolio Allocator

An end-to-end quantitative equity screening pipeline and responsive web dashboard built with Python, Pandas, and Tailwind CSS. The system automates factor-based stock selection across the Nifty 50 universe, combining valuation, quality, and momentum metrics with dynamic portfolio capital allocation.

👉 **[Live Demo Dashboard](https://your-project-name.netlify.app)** *(Replace with your Netlify URL)*

---

## 🛠️ Key Features

* **Multi-Factor Quantitative Scoring:** Automatically filters and ranks stocks using a robust factor model:
  * **Value:** Trailing P/E and Forward P/E multiples.
  * **Quality:** Return on Equity (ROE) to ensure fundamental profitability.
  * **Momentum & Trend:** 50-day Simple Moving Average (SMA) price confirmation, 14-period RSI, MACD bullish crossovers, and institutional volume breakout surges.
* **Fault-Tolerant Data Pipeline:** Leverages `yfinance` with multi-layered fallback mechanisms (utilizing `fast_info` and share count/close price recalculations) to guarantee 100% data coverage for index heavyweights like Reliance and TCS.
* **Automated Portfolio Construction:** Allocates a target capital pool across the top high-conviction picks using both **Equal-Weighted** and **Market-Cap Weighted** strategies, calculating aggregate portfolio risk-return metrics (Average P/E & ROE).
* **Static Web Hosting:** Decoupled architecture that exports processed screener data into a lightweight JavaScript payload (`stocks.js`), enabling fast, serverless deployment on Netlify.

---

## 🏗️ Architecture & Tech Stack

* **Data Pipeline & Analytics:** Python, Pandas, NumPy, `yfinance`, Tabulate (executed in Google Colab)
* **Frontend Dashboard:** HTML5, JavaScript, Tailwind CSS (Responsive dark-mode UI)
* **Hosting & CI/CD:** GitHub, Netlify (Automated static deployment)

---

## 📊 Pipeline Workflow

1. **Data Ingestion:** Scrapes live historical price action and fundamental indicators for the Nifty 50 index constituents.
2. **Data Cleaning & Fallbacks:** Handles missing data points and API rate limits gracefully.
3. **Technical Calculation:** Computes rolling SMAs, RSI, MACD, and volume averages.
4. **Factor Filtering:** Filters out overextended assets (RSI < 70, Price > 50 SMA, P/E < 50) and ranks candidates by valuation.
5. **Portfolio Allocation:** Generates capital weights, share quantities, and summary metrics.
6. **Frontend Export:** Dumps data into `stocks.js` to instantly update the live web interface.

---

## 🚀 Getting Started Locally

If you want to run the pipeline yourself:
1. Clone this repository.
2. Open the Python script in Google Colab or your local Jupyter environment.
3. Run the script to generate an updated `stocks.js` file.
4. Preview `index.html` locally or push changes to GitHub to update your live Netlify deployment.