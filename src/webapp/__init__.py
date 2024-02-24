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
    def run_hourly():
        from .portfolio_sim import update_prices, update_portfolio_value

        with app.app_context():
            update_prices()
            update_portfolio_value()
            print('Prices updated at ', datetime.now().strftime('%H:%M:%S')) #TODO temp for testing

    def run_daily():
        from .portfolio_sim import save_portfolio_value

        with app.app_context():
            save_portfolio_value()
            print('Portfolio value saved at ', datetime.now().strftime('%H:%M:%S')) #TODO temp for testing

    # add jobs
    scheduler.add_job(id='Hourly task', func=run_hourly, trigger='interval', hours=1)
    scheduler.add_job(id='Daily task', func=run_daily, trigger='cron', hour=17, minute=0)

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