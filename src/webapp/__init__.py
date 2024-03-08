from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from datetime import datetime #TODO delete later??

db = SQLAlchemy()
DB_NAME = "data.db"


class Config:
    SCHEDULER_API_ENABLED = True


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = 'spooky secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # register blueprints 
    from .views import views
    from .auth import auth
    from .portfolio_sim import sim

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(sim, url_prefix='/')

    # initiate scheduler
    scheduler = APScheduler()
    scheduler.init_app(app)

    # define jobs
    def update_prices():
        from .portfolio_sim import update_prices, update_portfolio_value, save_history

        with app.app_context():
            update_prices()
            update_portfolio_value()
            save_history()

            print('Prices updated at ', datetime.now().strftime('%H:%M:%S')) #TODO temp for testing

    def update_open():
        from .portfolio_sim import update_opening_prices

        with app.app_context():
            update_opening_prices()

            print('Opening prices updated at ', datetime.now().strftime('%H:%M:%S')) #TODO temp for testing

    def update_close():
        from .portfolio_sim import update_last_close_value

        with app.app_context():
            update_last_close_value()

            print('Closing prices updated at ', datetime.now().strftime('%H:%M:%S')) #TODO temp for testing
    
    # run every 30 minutes between 9am and 4pm
    scheduler.add_job(id='update_prices',
                      func=update_prices,
                      trigger='cron',
                      day_of_week='mon-fri', 
                      hour='9-16', 
                      minute='0, 30',
                      second='10', # TODO maybe delete?
                      timezone='EST')
    
    # run once at 9:30am
    scheduler.add_job(id='update_open',
                      func=update_open,
                      trigger='cron', 
                      day_of_week='mon-fri',
                      hour='9', 
                      minute='30',
                      second='10', # TODO maybe delete?
                      timezone='EST')
    
    # run once at 4:00pm
    scheduler.add_job(id='update_close',
                      func=update_close,
                      trigger='cron', 
                      day_of_week='mon-fri',
                      hour='16', 
                      minute='0',
                      second='10', # TODO maybe delete?
                      timezone='EST')


    scheduler.start()
    
    # create db if not already created
    with app.app_context():
        db.create_all()

    from .data_models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app