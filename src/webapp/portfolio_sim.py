from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import current_user

from datetime import datetime
import pytz
import pandas as pd
import yfinance as yf


from . import db
from .data_models import User, Portfolio, Holdings, Transactions

# constants
STARTING_FUNDS = 10000.00

sim = Blueprint('sim', __name__)


# routes
@sim.route('/dashboard', methods=['GET', 'POST'])
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

    portfolio_exists = Portfolio.query.filter_by(user_id=current_user.id).first()

    if portfolio_exists:
        has_holdings = Holdings.query.filter_by(portfolio_id=current_user.portfolio.id).first()
        has_transactions = Transactions.query.filter_by(portfolio_id=current_user.portfolio.id).first()

        transactions, holdings, history = [], [], []

        if has_transactions:
            transactions = get_portfolio_transactions(current_user.portfolio.id)

        return render_template("portfolio_sim/dashboard.html", 
                        user=current_user, 
                        username=current_user.username, 
                        portfolio_exists=portfolio_exists, 
                        time=datetime.now().strftime('%A, %B %d. %Y %I:%M %p %Z'),
                        portfolio_value=100.02, # placeholder
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
def buy_stock(ticker: str):
    if request.method == 'POST':
        ticker = request.form['ticker']
        shares = int(request.form['shares'])
        name = request.form['name']
        price = float(request.form['price'])
        currency = request.form['currency']
        
        record_buy_transaction(current_user.portfolio.id, ticker, name, shares, price, currency)
        update_holdings(current_user.portfolio.id, ticker, name, shares, price)
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


# functions
def create_portfolio(user_id: int) -> None:
    '''Create a portfolio for a user
        args:
            user_id: int - database id of the user
    '''
    portfolio = Portfolio(user_id=user_id, available_cash=STARTING_FUNDS)

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


def record_buy_transaction(portfolio_id: int, ticker: str, name: str, shares: int, price: float, currency: str) -> None:
    '''Records a buy transaction in the database
        args:
            portfolio_id: int - database id of the portfolio
            ticker: str - stock ticker
            name: str - stock name
            shares: int - number of shares
            price: float - price per share
            currency: str - currency of the transaction
    '''
    transaction = Transactions(portfolio_id=portfolio_id, 
                                status='buy', 
                                name=name, 
                                ticker=ticker, 
                                currency=currency, 
                                shares=shares, 
                                share_price=round(price, 2), 
                                total_value=round(shares*price, 2)
                                )

    db.session.add(transaction)
    db.session.commit()


def update_holdings(portfolio_id: int, ticker: str, name: str, shares: int, price: float) -> None:
    '''Updates the stock holdings for a portfolio
        args:
            portfolio_id: int - database id of the portfolio
            ticker: str - stock ticker
            name: str - stock name
            shares: int - number of shares
            price: float - price per share
    '''
    holding = Holdings.query.filter_by(portfolio_id=portfolio_id, ticker=ticker).first()

    if holding:
        holding.average_price = round((holding.average_price*holding.shares + price*shares) / (holding.shares + shares), 2)
        holding.shares += shares
        holding.updated_price = round(price, 2)
        holding.updated_time = datetime.now()
    else:
        holding = Holdings(portfolio_id=portfolio_id, 
                            name=name, 
                            ticker=ticker, 
                            shares=shares, 
                            average_price=round(price, 2), 
                            updated_price=round(price, 2), 
                            updated_time=datetime.now())

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


def get_portfolio_transactions(portfolio_id: int) -> dict:
    '''Gets all transactions for a portfolio and parses data into dataframe
        args:
            portfolio_id: int - database id of the portfolio
        returns:
            pd.DataFrame - all transactions for a portfolio
    '''
    transactions = Transactions.query.filter_by(portfolio_id=portfolio_id).all()

    df = pd.DataFrame([t.__dict__ for t in transactions])
    # drop unnecessary columns
    df = df.drop(columns=['_sa_instance_state', 'id', 'portfolio_id'])
    # rearrange columns
    df = df[['date', 'status', 'name', 'ticker', 'share_price', 'shares', 'total_value', 'currency']]

    return df.to_json(orient='records')
