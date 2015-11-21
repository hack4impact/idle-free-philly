#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Agency, Permission, IncidentReport
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

# Import settings from .env file. Must define FLASK_CONFIG
if os.path.exists('.env'):
    print('Importing environment from .env file')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.option('-nu',
                '--number-users',
                default=10,
                type=int,
                help='Number of users to create',
                dest='number_users')
@manager.option('-nr',
                '--number-reports',
                default=100,
                type=int,
                help='Number of reports to create',
                dest='number_reports')
def add_fake_data(number_users, number_reports):
    """
    Adds fake data to the database.
    """
    User.generate_fake(count=number_users)
    IncidentReport.generate_fake(count=number_reports)


@manager.command
def setup_dev():
    """Runs the set-up needed for local development."""
    setup_general()

    # Create a default admin user
    admin = User(email='admin@user.com',
                 password='password',
                 first_name='Admin',
                 last_name='User',
                 role=Role.query.filter_by(permissions=Permission.ADMINISTER)
                 .first(),
                 confirmed=True)

    # Create a default agency worker user
    worker = User(email='agency@user.com',
                  password='password',
                  first_name='AgencyWorker',
                  last_name='User',
                  role=Role.query
                  .filter_by(permissions=Permission.AGENCY_WORKER)
                  .first(),
                  confirmed=True)
    worker.agencies = [Agency.query.filter_by(name='SEPTA').first()]

    # Create a default general user
    general = User(email='general@user.com',
                   password='password',
                   first_name='General',
                   last_name='User',
                   role=Role.query.filter_by(permissions=Permission.GENERAL)
                   .first(),
                   confirmed=True)

    db.session.add(admin)
    db.session.add(worker)
    db.session.add(general)

    db.session.commit()


@manager.command
def setup_prod():
    """Runs the set-up needed for production."""
    setup_general()


def setup_general():
    """Runs the set-up needed for both local development and production."""
    Role.insert_roles()
    Agency.insert_agencies()

if __name__ == '__main__':
    manager.run()
