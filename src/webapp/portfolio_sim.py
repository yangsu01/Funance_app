from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import current_user, login_required

import yfinance as yf

from .portfolio_sim_functions import *

portfolio_sim = Blueprint('portfolio_sim', __name__)


# routes
@portfolio_sim.route('/dashboard', methods=['GET', 'POST'])
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
                    return redirect(url_for('portfolio_sim.buy_stock', ticker=ticker))
                else:
                    flash(f'Cannot find ticker {ticker}', category='error')
            except:
                flash(f'Cannot find ticker {ticker}', category='error')
        # sell stock form
        elif 'sellDropdown' in request.form:
            ticker = request.form['sellDropdown']
            if ticker:
                return redirect(url_for('portfolio_sim.sell_stock', ticker=ticker))
            else:
                flash(f'Please select a stock to sell', category='error')
        # search stock form
        elif 'searchTicker' in request.form:
            ticker = request.form['searchTicker'].upper()
            try:
                ticker_info = yf.Ticker(ticker).info
                
                if 'currentPrice' in ticker_info:
                    return redirect(url_for('portfolio_sim.search_stock', ticker=ticker))
                else:
                    flash(f'Cannot find ticker {ticker}', category='error')
            except:
                flash(f'Cannot find ticker {ticker}', category='error')

    portfolio_exists = current_user.portfolio

    if portfolio_exists:
        has_holdings = current_user.portfolio.holdings
        has_transactions = current_user.portfolio.transactions
        transactions, holdings = [], []
        holdings_breakdown, sector_breakdown = None, None
        history = get_portfolio_history(current_user.portfolio.id)
        portfolio_value = current_user.portfolio.updated_value
        change = round((portfolio_value/STARTING_FUNDS - 1) * 100, 2)
        profit = round(portfolio_value - STARTING_FUNDS, 2)
        update_time = utc_to_est(current_user.portfolio.updated_time).strftime('%a, %b %d. %Y %I:%M%p') + ' EST'

        if has_holdings:
            holdings = get_portfolio_holdings(current_user.portfolio.id)
            holdings_breakdown = get_holdings_breakdown(current_user.portfolio.id)
            sector_breakdown = get_sector_breakdown(current_user.portfolio.id)


        if has_transactions:
            transactions = get_portfolio_transactions(current_user.portfolio.id)

        return render_template("portfolio_sim/dashboard.html", 
                        user=current_user, 
                        username=current_user.username, 
                        portfolio_exists=portfolio_exists, 
                        update_time=update_time,
                        portfolio_value=portfolio_value,
                        has_holdings=has_holdings, 
                        has_transactions=has_transactions, 
                        transactions=transactions,
                        holdings=holdings,
                        history=history,
                        cash_available=current_user.portfolio.available_cash,
                        holdings_breakdown=holdings_breakdown,
                        sector_breakdown=sector_breakdown,
                        change=change,
                        profit=profit,
                        active_page='dashboard')

    return render_template("portfolio_sim/dashboard.html", 
                        user=current_user, 
                        username=current_user.username, 
                        portfolio_exists=portfolio_exists,
                        active_page='dashboard')


@portfolio_sim.route('/rules', methods=['GET'])
def rules():

    return render_template("portfolio_sim/rules.html", 
                           user=current_user, 
                           starting_funds=STARTING_FUNDS,
                           active_page='rules')


@portfolio_sim.route('/buy_stock/<ticker>', methods=['GET', 'POST'])
@login_required
def buy_stock(ticker: str):
    if request.method == 'POST':
        ticker = request.form['ticker']
        shares = int(request.form['shares'])
        name = request.form['name']
        price = float(request.form['price'])
        currency = request.form['currency']
        industry = request.form['industry']
        sector = request.form['sector']
        
        update_holding(current_user.portfolio.id, ticker, name, shares, price, currency, industry, sector)
        record_transaction(current_user.portfolio.id, ticker, 'buy', name, shares, price, currency)
        update_portfolio_cash(current_user.portfolio.id, shares*price)

        flash(f'Transaction complete!', category='success')

        return redirect(url_for('portfolio_sim.dashboard'))

    info = get_stock_info(ticker)

    stock_info = {
        'price': info['price'],
        'sector': info['sector'],
        'industry': info['industry'],
        'company_summary': info['company_summary'],
        'currency': info['currency'],
        'company_name': info['company_name'],
        'open': info['open']
    }

    performance = {
        'Current Price': f"${info['price']}",
        'Open Price': f"${info['open']}",
        'Day Change': f"${info['day_change']}",
        'Day Change (%)': f"{info['%_day_change']}%",
        '52 Week Returns': f"{info['52_week_returns']}%",
        '52 Week High': f"${info['52_week_high']}",
        '52 Week Low': f"${info['52_week_low']}"
    }

    history = get_stock_history(ticker, '1mo', True)

    est_time = get_est_time().strftime('%a, %b %d. %Y %I:%M%p') + ' EST'
    available_cash = get_available_cash(current_user.id)
    max_shares = int(available_cash / stock_info['price'])

    return render_template("portfolio_sim/buy.html",
                            user=current_user, 
                            ticker=ticker, 
                            info=stock_info, 
                            time=est_time, 
                            available_cash=available_cash,
                            max_shares=max_shares,
                            history=history,
                            performance=performance,
                            active_page='buy')


@portfolio_sim.route('/sell_stock/<ticker>', methods=['GET', 'POST'])
@login_required
def sell_stock(ticker: str):
    if request.method == 'POST':
        ticker = request.form['ticker']
        shares = int(request.form['shares'])
        name = request.form['name']
        price = float(request.form['price'])
        currency = request.form['currency']

        update_holding(current_user.portfolio.id, ticker, name, -1*shares, price, currency)
        record_transaction(current_user.portfolio.id, ticker, 'sell', name, shares, price, currency)
        update_portfolio_cash(current_user.portfolio.id, -1*shares*price)

        flash(f'Transaction complete!', category='success')

        return redirect(url_for('portfolio_sim.dashboard'))

    current_price = get_current_price(ticker)
    info = get_holding(current_user.portfolio.id, ticker)
    details = calculate_holding_value(info['average_price'], current_price, info['shares'], info['open'])

    return render_template("portfolio_sim/sell.html", 
                           user=current_user, 
                           info=info,
                           details=details, 
                           current_price=current_price,
                           time=get_est_time().strftime('%a, %b %d. %Y %I:%M%p') + ' EST',
                           active_page='sell')


@portfolio_sim.route('/search_stock/<ticker>', methods=['GET', 'POST'])
@login_required
def search_stock(ticker: str):
    if request.method == 'POST':
        if 'searchTicker' in request.form:
            ticker = request.form['searchTicker'].upper()
            og_ticker = request.form['originalTicker'].upper()
            try:
                ticker_info = yf.Ticker(ticker).info
                
                if 'currentPrice' in ticker_info:
                    return redirect(url_for('portfolio_sim.search_stock', ticker=ticker))
                else:
                    flash(f'Cannot find ticker {ticker}', category='error')
                    return redirect(url_for('portfolio_sim.search_stock', ticker=og_ticker))

            except:
                flash(f'Cannot find ticker {ticker}', category='error')
                return redirect(url_for('portfolio_sim.search_stock', ticker=og_ticker))
        elif 'buyTicker' in request.form:
            ticker = request.form['buyTicker']
            return redirect(url_for('portfolio_sim.buy_stock', ticker=ticker))
    
    info = get_stock_info(ticker)
    stock_info = {
        'price': info['price'],
        'sector': info['sector'],
        'industry': info['industry'],
        'company_summary': info['company_summary'],
        'currency': info['currency'],
        'company_name': info['company_name'],
    }
    performance = {
        'Current Price': f"${info['price']}",
        'Open Price': f"${info['open']}",
        'Day Change': f"${info['day_change']}",
        'Day Change (%)': f"{info['%_day_change']}%",
        '52 Week Returns': f"{info['52_week_returns']}%",
        '52 Week High': f"${info['52_week_high']}",
        '52 Week Low': f"${info['52_week_low']}"
    }

    history = get_stock_history(ticker)

    news = get_ticker_news(ticker)

    return render_template("portfolio_sim/search.html", 
                           user=current_user, 
                           info=stock_info, 
                           performance=performance,
                           ticker=ticker, 
                           time=get_est_time().strftime('%a, %b %d. %Y %I:%M%p') + ' EST',
                           history=history,
                           news=news,
                           active_page='search')


@portfolio_sim.route('/leaderboard', methods=['GET'])
def leaderboard():
    try:
        top_performers = get_top_performers()
        top_daily_performers = get_top_daily_performers()
        performance_history = get_performance_history()
        update_time = get_update_time()

        return render_template("portfolio_sim/leaderboard.html",
                            user=current_user,
                            top_performers=top_performers,
                            top_daily_performers=top_daily_performers,
                            performance_history=performance_history,
                            update_time=update_time,
                            active_page='leaderboard')
    except:
        flash(f'There is no leaderboard yet', category='error')
        return redirect(url_for('views.home'))