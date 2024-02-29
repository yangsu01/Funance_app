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
        elif 'sellDropdown' in request.form:
            ticker = request.form['sellDropdown']
            if ticker:
                return redirect(url_for('sim.sell_stock', ticker=ticker))
            else:
                flash(f'Please select a stock to sell', category='error')

    portfolio_exists = current_user.portfolio

    if portfolio_exists:
        has_holdings = current_user.portfolio.holdings
        has_transactions = current_user.portfolio.transactions
        transactions, holdings = [], []
        history = get_portfolio_history(current_user.portfolio.id)

        # save_portfolio_value()

        if has_holdings:
            holdings = get_portfolio_holdings(current_user.portfolio.id)

        if has_transactions:
            transactions = get_portfolio_transactions(current_user.portfolio.id)

        return render_template("portfolio_sim/dashboard.html", 
                        user=current_user, 
                        username=current_user.username, 
                        portfolio_exists=portfolio_exists, 
                        update_time=current_user.portfolio.updated_time.strftime('%A, %B %d. %Y %I:%M %p %Z'),
                        portfolio_value=current_user.portfolio.updated_value,
                        has_holdings=has_holdings, 
                        has_transactions=has_transactions, 
                        available_cash=current_user.portfolio.available_cash,
                        transactions=transactions,
                        holdings=holdings,
                        history=history
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
        
        record_transaction(current_user.portfolio.id, ticker, 'buy', name, shares, price, currency)
        update_holdings(current_user.portfolio.id, ticker, name, shares, price, currency, open)
        update_portfolio_cash(current_user.portfolio.id, shares*price)

        flash(f'Transaction complete!', category='success')

        return redirect(url_for('sim.dashboard'))

    stock_info = get_stock_info(ticker)
    est_time = get_est_time()
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

        record_transaction(current_user.portfolio.id, ticker, 'sell', name, shares, price, currency)
        delete_holdings(current_user.portfolio.id, ticker, shares)
        update_portfolio_cash(current_user.portfolio.id, -1*shares*price)

        flash(f'Transaction complete!', category='success')

        return redirect(url_for('sim.dashboard'))

    current_price = get_current_price(ticker)
    info = get_holding(current_user.portfolio.id, ticker)
    details = calculate_holding_value(info['average_price'], current_price, info['shares'])

    return render_template("portfolio_sim/sell.html", 
                           user=current_user, 
                           info=info,
                           details=details, 
                           current_price=current_price,
                           time=get_est_time())


# functions
def create_portfolio(user_id: int) -> None:
    '''Create a portfolio for a user
        args:
            user_id: int - database id of the user
    '''
    portfolio = Portfolio(user_id=user_id, available_cash=STARTING_FUNDS, updated_value=STARTING_FUNDS, updated_time=datetime.now())

    db.session.add(portfolio)
    db.session.commit()

    return portfolio


def get_stock_info(ticker: str) -> dict:
    '''Gets custom stock information from yfinance
        args:
            ticker: str - stock ticker
        returns:
            dict - stock information
    '''
    stock_info = yf.Ticker(ticker).info

    parced_info = {
        'price': round(float(stock_info.get('currentPrice', 'n/a')), 2),
        'industry': stock_info.get('industry', 'n/a'),
        'company_summary': stock_info.get('longBusinessSummary', 'n/a'),
        'currency': stock_info.get('currency', 'n/a'),
        'company_name': stock_info.get('longName', 'n/a'),
        'open': stock_info.get('open', 'n/a')
    }

    return parced_info


def get_est_time() -> str:
    '''Gets the current time in EST
        returns:
            str - current time in EST
    '''
    est = pytz.timezone('US/Eastern')
    est_time = datetime.now(est).strftime('%A, %B %d. %Y %I:%M %p %Z')

    return est_time


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
                                status=status, 
                                name=name, 
                                ticker=ticker, 
                                currency=currency, 
                                shares=shares, 
                                share_price=round(price, 2), 
                                total_value=round(shares*price, 2),
                                date=datetime.now()
                                )

    db.session.add(transaction)
    db.session.commit()


def update_holdings(portfolio_id: int, ticker: str, name: str, shares: int, price: float, currency: str, open_price: float) -> None:
    '''Updates the stock holdings for a portfolio
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

    if holding:
        holding.average_price = round((holding.average_price*holding.shares + price*shares) / (holding.shares + shares), 2)
        holding.shares += shares
        holding.updated_price = round(price, 2)
    else:
        holding = Holdings(portfolio_id=portfolio_id, 
                            name=name, 
                            ticker=ticker, 
                            shares=shares, 
                            average_price=round(price, 2), 
                            updated_price=round(price, 2),
                            currency=currency, 
                            open_price=round(open_price, 2),
                            open_price_date=datetime.today().date())

        db.session.add(holding)
    
    db.session.commit()


def update_portfolio_cash(portfolio_id: int, transaction_cost: float) -> None:
    '''Updates the available cash for a portfolio 
    (subtracts the transaction cost from the available cash)
        args:
            portfolio_id: int - database id of the portfolio
            transaction_cost: float - total value of the buy transaction
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
    df['date'] = df['date'].dt.strftime('%H:%M:%S %m-%d-%Y')    
    df = df[['ticker', 'name', 'status', 'shares', 'share_price', 'total_value', 'currency', 'date']]
    df = df.rename(columns={'ticker': 'Ticker',
                            'name': 'Company Name',
                            'status': 'Buy/Sell',
                            'shares': 'Shares',
                            'share_price': 'Price per Share',
                            'total_value': 'Total Value',
                            'currency': 'Currency',
                            'date': 'Date'})

    return df.to_json(orient='records')


def get_portfolio_holdings(portfolio_id: int) -> str:
    '''Gets all holdings in a portfolio and parses data a json string
            portfolio_id: int - database id of the portfolio
        returns:
            str - json string of all holdings in a portfolio
    '''
    holdings = Holdings.query.filter_by(portfolio_id=portfolio_id).all()

    df = pd.DataFrame([h.__dict__ for h in holdings])

    df['Change'] = round((df['updated_price'] - df['average_price']), 2)
    df['Total Change'] = round((df['Change'] * df['shares']), 2)
    df['% Change'] = round((df['Change'] / df['average_price']) * 100, 2)
    df['Market Value'] = round((df['updated_price'] * df['shares']), 2)

    # rearrange and rename columns
    df = df[['ticker', 'name', 'shares', 'average_price', 'updated_price', 'Change', 'Total Change', '% Change', 'Market Value', 'currency']]
    df = df.rename(columns={'ticker': 'Ticker',
                            'name': 'Company Name',
                            'shares': 'Shares',
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
    update_open = False
    
    # check if open price hasnt been updated for today
    open_date = holdings[0].open_price_date
    if open_date != datetime.today().date():
        open_prices = {}
        update_open = True

    for holding in holdings:
        ticker = holding.ticker
        if ticker not in updated_prices:
            updated_prices[ticker] = yf.Ticker(ticker).info.get('currentPrice', holding.updated_price)

            if update_open:
                open_prices[ticker] = yf.Ticker(ticker).info.get('open', holding.open_price)

        holding.updated_price = updated_prices[ticker]
        if update_open:
            holding.open_price = open_prices[ticker]
            holding.open_price_date = datetime.today().date()

    db.session.commit()


def update_portfolio_value() -> None:
    '''Updates the total value of all portfolios in the database
    this is intended to run once an hour
    '''
    portfolios = Portfolio.query.all()

    for portfolio in portfolios:
        holdings = portfolio.holdings
        updated_value = portfolio.available_cash

        for holding in holdings:
            updated_value += holding.updated_price * holding.shares

        portfolio.updated_value = round(updated_value, 2)
        portfolio.updated_time = datetime.now()

    db.session.commit()


def save_portfolio_value() -> None:
    '''Saves the value of all portfolios in the database under the history table
    this is intended to run at the end of each day
    '''
    portfolios = Portfolio.query.all()
    value_updated = History.query.filter_by(date=datetime.today().date()).first()

    if not value_updated:
        for portfolio in portfolios:
            history = History(portfolio_id=portfolio.id, date=datetime.today().date(), portfolio_value=portfolio.updated_value)

            db.session.add(history)

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
        'Date': [h.date.strftime('%Y-%m-%d') for h in history],
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
        'name': holding.name,
        'shares': holding.shares,
        'average_price': holding.average_price,
        'updated_price': holding.updated_price,
        'currency': holding.currency
    }


def get_current_price(ticker: str) -> float:
    '''Gets the current price of a stock
        args:
            ticker: str - stock ticker
        returns:
            float - current price of the stock
    '''
    return yf.Ticker(ticker).info.get('currentPrice', 'n/a')


def calculate_holding_value(average_price: float, current_price: float, shares: int) -> dict:
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
        'Market Value': f'${round(current_price * shares, 2)}',
        'Change per Share': f'${round(current_price - average_price, 2)}',
        'Total Change': f'${round((current_price - average_price) * shares, 2)}',
        '% Change': f'{round(((current_price - average_price) / average_price) * 100, 2)}%'
    }


def delete_holdings(portfolio_id: int, ticker: str, shares_sold: int, ) -> None:
    '''deletes a holding from a portfolio. if not all shares are sold, updates the holding
        args:
            portfolio_id: int - database id of the portfolio
            ticker: str - stock ticker
    '''
    holding = Holdings.query.filter_by(portfolio_id=portfolio_id, ticker=ticker).first()

    if holding.shares == shares_sold:
        db.session.delete(holding)
    else: 
        holding.shares -= shares_sold

    db.session.commit()