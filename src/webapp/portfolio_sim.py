from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import current_user, login_required

import json
from datetime import datetime
import pytz
import pandas as pd
import yfinance as yf


from . import db
from .data_models import Portfolio, Holdings, Transactions, History

# constants
STARTING_FUNDS = 10000.00

sim = Blueprint('sim', __name__)


# routes
@sim.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # create portfolio form
        if 'create_portfolio' in request.form:
            create_portfolio(current_user.id)
        # buy stock form
        elif 'ticker' in request.form:
            ticker = request.form['ticker'].upper()
            try:
                ticker_info = yf.Ticker(ticker).info
                
                if 'currentPrice' in ticker_info:
                    return redirect(url_for('sim.buy_stock', ticker=ticker))
                else:
                    flash(f'Cannot find ticker {ticker}', category='error')
            except:
                flash(f'Cannot find ticker {ticker}', category='error')
        # sell stock form
        elif 'sellDropdown' in request.form:
            ticker = request.form['sellDropdown']
            if ticker:
                return redirect(url_for('sim.sell_stock', ticker=ticker))
            else:
                flash(f'Please select a stock to sell', category='error')
        # search stock form
        elif 'searchTicker' in request.form:
            ticker = request.form['searchTicker'].upper()
            try:
                ticker_info = yf.Ticker(ticker).info
                
                if 'currentPrice' in ticker_info:
                    return redirect(url_for('sim.search_stock', ticker=ticker))
                else:
                    flash(f'Cannot find ticker {ticker}', category='error')
            except:
                flash(f'Cannot find ticker {ticker}', category='error')

    portfolio_exists = current_user.portfolio

    if portfolio_exists:
        has_holdings = current_user.portfolio.holdings
        has_transactions = current_user.portfolio.transactions
        transactions, holdings = [], []
        history = get_portfolio_history(current_user.portfolio.id)

        if has_holdings:
            holdings = get_portfolio_holdings(current_user.portfolio.id)

        if has_transactions:
            transactions = get_portfolio_transactions(current_user.portfolio.id)

        return render_template("portfolio_sim/dashboard.html", 
                        user=current_user, 
                        username=current_user.username, 
                        portfolio_exists=portfolio_exists, 
                        update_time=current_user.portfolio.updated_time.strftime('%A, %B %d. %Y %I:%M %p %Z') + ' EST',
                        portfolio_value=current_user.portfolio.updated_value,
                        has_holdings=has_holdings, 
                        has_transactions=has_transactions, 
                        available_cash=current_user.portfolio.available_cash,
                        transactions=transactions,
                        holdings=holdings,
                        history=history,
                        cash_available=current_user.portfolio.available_cash,
                        )

    return render_template("portfolio_sim/dashboard.html", 
                        user=current_user, 
                        username=current_user.username, 
                        portfolio_exists=portfolio_exists,
                        )


@sim.route('/rules', methods=['GET'])
def rules():

    return render_template("portfolio_sim/rules.html", user=current_user, starting_funds=STARTING_FUNDS)


@sim.route('/buy_stock/<ticker>', methods=['GET', 'POST'])
@login_required
def buy_stock(ticker: str):
    if request.method == 'POST':
        ticker = request.form['ticker']
        shares = int(request.form['shares'])
        name = request.form['name']
        price = float(request.form['price'])
        currency = request.form['currency']
        open = float(request.form['open'])
        
        update_holding(current_user.portfolio.id, ticker, name, shares, price, currency)
        record_transaction(current_user.portfolio.id, ticker, 'buy', name, shares, price, currency)
        update_portfolio_cash(current_user.portfolio.id, shares*price)

        flash(f'Transaction complete!', category='success')

        return redirect(url_for('sim.dashboard'))

    info = get_stock_info(ticker)

    stock_info = {
        'price': info['price'],
        'industry': info['industry'],
        'company_summary': info['company_summary'],
        'currency': info['currency'],
        'company_name': info['company_name'],
        'open': info['open']
    }

    est_time = get_est_time().strftime('%A, %B %d. %Y %I:%M %p %Z')
    available_cash = get_available_cash(current_user.id)
    max_shares = int(available_cash / stock_info['price'])

    return render_template("portfolio_sim/buy.html",
                            user=current_user, 
                            ticker=ticker, 
                            info=stock_info, 
                            time=est_time, 
                            available_cash=available_cash,
                            max_shares=max_shares)


@sim.route('/sell_stock/<ticker>', methods=['GET', 'POST'])
@login_required
def sell_stock(ticker: str):
    if request.method == 'POST':
        ticker = request.form['ticker']
        shares = int(request.form['shares'])
        name = request.form['name']
        price = float(request.form['price'])
        currency = request.form['currency']

        update_holding(current_user.portfolio.id, ticker, name, -1*shares, price, currency) # 0 is a placeholder (not used for sell)
        record_transaction(current_user.portfolio.id, ticker, 'sell', name, shares, price, currency)
        update_portfolio_cash(current_user.portfolio.id, -1*shares*price)

        flash(f'Transaction complete!', category='success')

        return redirect(url_for('sim.dashboard'))

    current_price = get_current_price(ticker)
    info = get_holding(current_user.portfolio.id, ticker)
    details = calculate_holding_value(info['average_price'], current_price, info['shares'], info['open'])

    return render_template("portfolio_sim/sell.html", 
                           user=current_user, 
                           info=info,
                           details=details, 
                           current_price=current_price,
                           time=get_est_time().strftime('%A, %B %d. %Y %I:%M %p %Z'))


@sim.route('/search_stock/<ticker>', methods=['GET', 'POST'])
@login_required
def search_stock(ticker: str):
    if request.method == 'POST':
        if 'searchTicker' in request.form:
            ticker = request.form['searchTicker'].upper()
            og_ticker = request.form['originalTicker'].upper()
            try:
                ticker_info = yf.Ticker(ticker).info
                
                if 'currentPrice' in ticker_info:
                    return redirect(url_for('sim.search_stock', ticker=ticker))
                else:
                    flash(f'Cannot find ticker {ticker}', category='error')
                    return redirect(url_for('sim.search_stock', ticker=og_ticker))

            except:
                flash(f'Cannot find ticker {ticker}', category='error')
                return redirect(url_for('sim.search_stock', ticker=og_ticker))
        elif 'buyTicker' in request.form:
            ticker = request.form['buyTicker']
            return redirect(url_for('sim.buy_stock', ticker=ticker))
    
    info = get_stock_info(ticker)
    stock_info = {
        'price': info['price'],
        'industry': info['industry'],
        'company_summary': info['company_summary'],
        'currency': info['currency'],
        'company_name': info['company_name'],
    }
    performance_info = {
        'Current Price': f"${info['price']}",
        'Open Price': f"${info['open']}",
        'Day Change': f"${info['day_change']}",
        '% Day Change': f"{info['%_day_change']}%",
        '52 Week Returns': f"{info['52_week_returns']}%",
        '52 Week High': f"${info['52_week_high']}",
        '52 Week Low': f"${info['52_week_low']}"
    }

    history = get_stock_history(ticker)
    news = get_ticker_news(ticker)

    return render_template("portfolio_sim/search.html", 
                           user=current_user, 
                           info=stock_info, 
                           performance=performance_info,
                           ticker=ticker, 
                           time=get_est_time().strftime('%A, %B %d. %Y %I:%M %p %Z'),
                           history=history,
                           news=news)


@sim.route('/leaderboard', methods=['GET'])
def leaderboard():
    try:
        top_performers = get_top_performers()
        top_daily_performers = get_top_daily_performers()
        performance_history = get_performance_history()
        update_time = get_update_time() + ' EST'

        return render_template("portfolio_sim/leaderboard.html",
                            user=current_user,
                            top_performers=top_performers,
                            top_daily_performers=top_daily_performers,
                            performance_history=performance_history,
                            update_time=update_time)
    except:
        flash(f'There is no leaderboard yet', category='error')
        return redirect(url_for('views.home'))


# functions
def get_est_time() -> datetime:
    '''Gets the current time in EST
        returns:
            datetime - current time in EST
    '''
    est = pytz.timezone('US/Eastern')

    return datetime.now(est)


def create_portfolio(user_id: int) -> None:
    '''Create a portfolio for a user
        args:
            user_id: int - database id of the user
    '''
    portfolio = Portfolio(user_id=user_id, 
                          available_cash=STARTING_FUNDS,
                          creation_date=datetime.today().date(), 
                          updated_value=STARTING_FUNDS, 
                          updated_time=get_est_time(), 
                          last_close_value=STARTING_FUNDS)

    db.session.add(portfolio)
    db.session.commit()

    history = History(portfolio_id=portfolio.id, record_time=get_est_time(), portfolio_value=STARTING_FUNDS)
    db.session.add(history)
    db.session.commit()

def get_stock_info(ticker: str) -> dict:
    '''Gets custom stock information from yfinance
        args:
            ticker: str - stock ticker
        returns:
            dict - stock information
    '''
    stock_info = yf.Ticker(ticker).info

    return {
        'price': round(float(stock_info.get('currentPrice', 0)), 2),
        'industry': stock_info.get('industry', 'n/a'),
        'company_summary': stock_info.get('longBusinessSummary', 'n/a'),
        'currency': stock_info.get('currency', 'n/a'),
        'company_name': stock_info.get('longName', 'n/a'),
        'open': stock_info.get('open', 'n/a'),
        'day_change': round(float(stock_info.get('currentPrice', 0))-float(stock_info.get('open', 1)), 2),
        '%_day_change': round((float(stock_info.get('currentPrice', 0))/float(stock_info.get('open', 1)) - 1)*100, 2),
        '52_week_returns': round(float(stock_info.get('52WeekChange', 0))*100, 2),
        '52_week_high': round(float(stock_info.get('fiftyTwoWeekHigh', 0)), 2),
        '52_week_low': round(float(stock_info.get('fiftyTwoWeekLow', 0)), 2)
    }


def get_available_cash(user_id: int) -> float:
    '''Gets the available cash in a users portfolio. Assumes portfolio exists
        args:
            user_id: int - database id of the user
        returns:
            float - available cash
    '''
    portfolio = Portfolio.query.filter_by(user_id=user_id).first()

    return portfolio.available_cash


def record_transaction(portfolio_id: int, ticker: str, status: str, name: str, shares: int, price: float, currency: str) -> None:
    '''Records a transaction in the database
        args:
            portfolio_id: int - database id of the portfolio
            ticker: str - stock ticker
            status: str - buy/sell
            name: str - stock name
            shares: int - number of shares
            price: float - price per share
            currency: str - currency of the transaction
    '''
    transaction = Transactions(portfolio_id=portfolio_id,
                               transaction_date=get_est_time(), 
                               status=status, 
                               company_name=name, 
                               ticker=ticker, 
                               currency=currency, 
                               number_of_shares=shares, 
                               price_per_share=round(price, 2), 
                               total_value=round(shares*price, 2))

    db.session.add(transaction)
    db.session.commit()


def update_holding(portfolio_id: int, ticker: str, name: str, shares: int, price: float, currency: str) -> None:
    '''Updates a stock holding in a portfolio after a transaction
        If its a sell transaction (shares<0), assumes that the holding exists
        args:
            portfolio_id: int - database id of the portfolio
            ticker: str - stock ticker
            name: str - stock name
            shares: int - number of shares
            price: float - price per share
            currency: str - currency of the stock
            open_price: float - opening price of the stock for the day
    '''
    holding = Holdings.query.filter_by(portfolio_id=portfolio_id, ticker=ticker).first()

    # sell transaction
    if shares < 0:
        if holding.number_of_shares == -1*shares:
            db.session.delete(holding)
        else: 
            holding.number_of_shares += shares
    # buy transaction
    else:
        # holding already exists in portfolio
        if holding:
            holding.average_price = round((holding.average_price*holding.number_of_shares + price*shares) / (holding.number_of_shares + shares), 2)
            holding.number_of_shares += shares
            holding.updated_price = round(price, 2)
            
        # holding is new to portfolio
        else:
            holding = Holdings(portfolio_id=portfolio_id, 
                               company_name=name, 
                               ticker=ticker, 
                               number_of_shares=shares, 
                               average_price=round(price, 2), 
                               updated_price=round(price, 2),
                               currency=currency, 
                               opening_price=round(price, 2))

            db.session.add(holding)
    
    db.session.commit()


def update_portfolio_cash(portfolio_id: int, transaction_cost: float) -> None:
    '''Updates the available cash for a portfolio 
    (subtracts the transaction cost from the available cash)
        args:
            portfolio_id: int - database id of the portfolio
            transaction_cost: float - total value of the transaction
    '''
    portfolio = Portfolio.query.filter_by(id=portfolio_id).first()

    portfolio.available_cash = round(portfolio.available_cash - transaction_cost, 2)

    db.session.commit()


def get_portfolio_transactions(portfolio_id: int) -> str:
    '''Gets all transactions in a portfolio and parses data into a json string
        args:
            portfolio_id: int - database id of the portfolio
        returns:
            str - json string of transaction history of a portfolio
    '''
    transactions = Transactions.query.filter_by(portfolio_id=portfolio_id).all()

    df = pd.DataFrame([t.__dict__ for t in transactions])

    # rearrange and rename columns
    df['transaction_date'] = df['transaction_date'].dt.strftime('%H:%M:%S %m-%d-%Y')    
    df = df[['ticker', 'company_name', 'status', 'number_of_shares', 'price_per_share', 'total_value', 'currency', 'transaction_date']]
    df = df.rename(columns={'ticker': 'Ticker',
                            'company_name': 'Company Name',
                            'status': 'Buy/Sell',
                            'number_of_shares': 'Shares',
                            'price_per_share': 'Price per Share',
                            'total_value': 'Total Value',
                            'currency': 'Currency',
                            'transaction_date': 'Date'})

    return df.to_json(orient='records')


def get_portfolio_holdings(portfolio_id: int) -> str:
    '''Gets all holdings in a portfolio and parses data a json string
            portfolio_id: int - database id of the portfolio
        returns:
            str - json string of all holdings in a portfolio
    '''
    holdings = Holdings.query.filter_by(portfolio_id=portfolio_id).all()

    df = pd.DataFrame([h.__dict__ for h in holdings])

    df['Day Change'] = round((df['updated_price'] - df['opening_price']), 2)
    df['Total Day Change'] = round((df['Day Change'] * df['number_of_shares']), 2)
    df['% Day Change'] = round((df['Day Change'] / df['opening_price']) * 100, 2)
    df['Change'] = round((df['updated_price'] - df['average_price']), 2)
    df['Total Change'] = round((df['Change'] * df['number_of_shares']), 2)
    df['% Change'] = round((df['Change'] / df['average_price']) * 100, 2)
    df['Market Value'] = round((df['updated_price'] * df['number_of_shares']), 2)

    # rearrange and rename columns
    df = df[['ticker', 'number_of_shares', 'average_price', 'updated_price', 'Day Change', '% Day Change', 'Total Change', '% Change', 'Market Value', 'currency']]
    df = df.rename(columns={'ticker': 'Ticker',
                            'number_of_shares': 'Shares Owned',
                            'average_price': 'Average Price',
                            'updated_price': 'Current Price',
                            'currency': 'Currency'})

    return df.to_json(orient='records')


def update_prices() -> None:
    '''Updates the prices of all holdings in the database
    Also updates the open price of the stock for the day if not already done
    this is intended to run once an hour
    '''
    holdings = Holdings.query.all()
    updated_prices = {}

    for holding in holdings:
        ticker = holding.ticker

        if ticker not in updated_prices:
            updated_prices[ticker] = yf.Ticker(ticker).info.get('currentPrice', holding.updated_price)

        holding.updated_price = updated_prices[ticker]

    db.session.commit()


def update_portfolio_value() -> None:
    '''Updates the total value of all portfolios in the database
    '''
    portfolios = Portfolio.query.all()

    for portfolio in portfolios:
        holdings = portfolio.holdings
        updated_value = portfolio.available_cash

        for holding in holdings:
            updated_value += holding.updated_price * holding.number_of_shares

        portfolio.updated_value = round(updated_value, 2)
        portfolio.updated_time = get_est_time()

    db.session.commit()


def save_history() -> None:
    '''Saves the value of all portfolios in the database under the history table
    '''
    portfolios = Portfolio.query.all()

    for portfolio in portfolios:
        history = History(portfolio_id=portfolio.id, record_time=get_est_time(), portfolio_value=portfolio.updated_value)

        db.session.add(history)

    db.session.commit()


def update_opening_prices() -> None:
    '''Updates the opening price of all holdings in the database
    '''
    holdings = Holdings.query.all()
    open_prices = {}

    for holding in holdings:
        ticker = holding.ticker

        if ticker not in open_prices:
            open_prices[ticker] = yf.Ticker(ticker).info.get('open', holding.opening_price)
        
        holding.opening_price = open_prices[ticker]

    db.session.commit()


def update_last_close_value() -> None:
    '''Updates the last close value of all portfolios in the database
    '''
    portfolios = Portfolio.query.all()

    for portfolio in portfolios:
        portfolio.last_close_value = portfolio.updated_value

    db.session.commit()


def get_portfolio_history(portfolio_id: int) -> str:
    '''Gets the history of a portfolio and parses data into a json string
        args:
            portfolio_id: int - database id of the portfolio
        returns:
            str - json string of the history of a portfolio
    '''
    history = History.query.filter_by(portfolio_id=portfolio_id).all()

    portfolio_history = {
        'Date': [h.record_time.strftime('%Y-%m-%d %H:%M') for h in history],
        'Value': [h.portfolio_value for h in history]
    }

    return json.dumps(portfolio_history)


def get_holding(portfolio_id: int, ticker: str) -> dict:
    '''Gets a specific holding from a portfolio. Assumes holding exists
        args:
            portfolio_id: int - database id of the portfolio
            ticker: str - stock ticker
        returns:
            dict - holding information
    '''
    holding = Holdings.query.filter_by(portfolio_id=portfolio_id, ticker=ticker).first()

    return {
        'ticker': holding.ticker,
        'name': holding.company_name,
        'shares': holding.number_of_shares,
        'average_price': holding.average_price,
        'updated_price': holding.updated_price,
        'currency': holding.currency,
        'open': holding.opening_price
    }


def get_current_price(ticker: str) -> float:
    '''Gets the current price of a stock
        args:
            ticker: str - stock ticker
        returns:
            float - current price of the stock
    '''
    return yf.Ticker(ticker).info.get('currentPrice', 'n/a')


def calculate_holding_value(average_price: float, current_price: float, shares: int, open: float) -> dict:
    '''Calculates the current value of a stock holding and other metrics
        args:
            average_price: float - average price of the stock
            current_price: float - current price of the stock
            shares: int - number of shares owned
        returns:
            dict - holding value and metrics
    '''
    return {
        'Shares Owned': shares,
        'Average Price per Share': f'${round(average_price, 2)}',
        'Total Purchase Value': f'${round(average_price * shares, 2)}',
        'Current Price per Share': f'${round(current_price, 2)}',
        'Current Market Value': f'${round(current_price * shares, 2)}',
        'Day Change per Share': f'${round(current_price - open, 2)}',
        'Total Day Change': f'${round((current_price - open) * shares, 2)}',
        '% Day Change': f'{round(((current_price - open) / open) * 100, 2)}%',
        'Change per Share': f'${round(current_price - average_price, 2)}',
        'Total Change': f'${round((current_price - average_price) * shares, 2)}',
        '% Change': f'{round(((current_price - average_price) / average_price) * 100, 2)}%'
    }


def get_stock_history(ticker: str, period='5y') -> str:
    '''Gets the historical price of a stock
        args:
            ticker: str - stock ticker
            period: str - time period for the historical data
        returns:
            str - json string of the historical price of a stock
    '''
    stock = yf.Ticker(ticker).history(period=period).dropna()

    history = {
        'Date': [d.strftime('%Y-%m-%d') for d in stock.index],
        'Price': [p for p in round(stock['Close'], 2)]
    }

    return json.dumps(history)


def get_top_performers() -> str:
    '''Gets the top performing portfolios ordered
        returns:
            str - json string of top performing portfolios
    '''
    portfolios = Portfolio.query.all()
    ranked_portfolios = sorted(portfolios, key=lambda p: p.updated_value, reverse=True)

    top_performers = []
    count = 0
    prev = None

    for portfolio in ranked_portfolios:
        count += 1
        updated_val = portfolio.updated_value
        portfolio_change =  round((updated_val/STARTING_FUNDS - 1) * 100, 2)
        portfolio_age = (get_est_time().date() - portfolio.creation_date).days

        rank = count
        if updated_val == prev:
            rank = '-'
        
        if portfolio_age == 0:
            daily_change = 'n/a'
        else:
            daily_change = round(portfolio_change/portfolio_age, 2)
        
        top_performers.append({
            'Rank': rank,
            'Username': portfolio.user.username,
            'Portfolio Value': portfolio.updated_value,
            'Change (%)': portfolio_change,
            'Portfolio Age (days)': portfolio_age,
            'Average Daily Change (%)': daily_change
        })

        prev = updated_val


    return json.dumps(top_performers)


def get_top_daily_performers() -> str:
    '''Gets the top daily performers ordered
        returns:
            str - json string of top daily performers
    '''
    portfolios = Portfolio.query.all()
    ranked_portfolios = sorted(portfolios, key=lambda p: (p.updated_value / p.last_close_value), reverse=True)

    top_performers = []
    count = 0
    prev = None

    for portfolio in ranked_portfolios:
        count += 1
        day_change =  round(portfolio.updated_value - portfolio.last_close_value, 2)
        day_change_percent = round(day_change/portfolio.last_close_value, 2)

        rank = count
        if day_change_percent == prev:
            rank = '-'

        top_performers.append({
            'Rank': rank,
            'Username': portfolio.user.username,
            'Change (%)': day_change_percent,
            'Change ($)': day_change,
            'Total Portfolio Value': portfolio.updated_value
        })

        prev = day_change_percent



    return json.dumps(top_performers)


def get_performance_history() -> str:
    '''Gets the performance history of all portfolios
        returns:
            str - json string of the performance history of all portfolios
    '''
    portfolios = Portfolio.query.all()
    history = []

    for portfolio in portfolios:
        history.append({
            'x': [h.record_time.strftime('%Y-%m-%d %H:%M') for h in portfolio.history],
            'y': [h.portfolio_value for h in portfolio.history],
            'name': portfolio.user.username
        })

    return json.dumps(history)


def get_update_time() -> str:
    '''Gets the last time the portfolios were updated
        returns:
            str - last update time
    '''
    return Portfolio.query.first().updated_time.strftime('%A, %B %d. %Y %I:%M %p %Z')


def get_ticker_news(ticker: str) -> list:
    '''Gets the related news articles for a stock
        args:
            ticker: str - stock ticker
        returns:
            list - news articles for the stock
    '''
    news = yf.Ticker(ticker).news
    articles = []

    for n in news:
        articles.append({
            'name': n['title'],
            'url': n['link']
        })

    return articles