import yfinance as yf

from . import db
from .data_models import Holdings, Portfolio, History
from .portfolio_sim_functions import get_est_time

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


