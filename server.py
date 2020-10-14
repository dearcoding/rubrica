import webhelpers2.text
import json
from formencode.validators import NotEmpty
from tg import expose, TGController, validate
from tg import redirect
from tg import MinimalApplicationConfigurator
from wsgiref.simple_server import make_server
from tg.configurator.components.statics import StaticsConfigurationComponent
from tg.configurator.components.sqlalchemy import SQLAlchemyConfigurationComponent
from tg.util import Bunch
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime
import random

DeclarativeBase = declarative_base()

def test_add_contact():
    nome = "".join(random.choice("abcdefghilmnopqrstuvz") for x in range(8))
    telefono = "".join(random.choice("123456789") for x in range(8))
    RootController.aggiungi_contatto(nome, telefono);
    print("test add")


class Log(DeclarativeBase):
    __tablename__ = 'logs'

    uid = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    person = Column(String(50), nullable=False)

class Contact(DeclarativeBase):
    __tablename__ = 'contacts'

    uid = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    name = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)

DBSession = scoped_session(sessionmaker(autoflush=True, autocommit=False))

def init_model(engine):
    DBSession.configure(bind=engine)
    DeclarativeBase.metadata.create_all(engine)

class RootController(TGController):

    @expose('contacts.xhtml')
    def index(self):
        contacts = DBSession.query(Contact).all();
        return dict(contacts=contacts)

    @validate({'name': NotEmpty,
               'phone': NotEmpty})
    @expose()
    def process_add(self, name=None, phone=None):
        DBSession.add(Contact(name=name, phone=phone))
        DBSession.commit()
        redirect('./')

    @expose('json')
    def export_json(self):
        json_contacts = []
        contacts = DBSession.query(Contact).all();
        for contact in contacts:
            to_append = {
                        'uid' : contact.uid,
                        'name' : contact.name,
                        'phone' : contact.phone
                }
            json_contacts.append(to_append)

        return json.dumps(json_contacts, indent=4, sort_keys=True)


    @validate({'uid': NotEmpty})
    @expose()
    def process_delete(self, uid=None):
        contact = DBSession.query(Contact).get(uid)
        DBSession.delete(contact)
        DBSession.commit()
        redirect('./')

    @expose('aggiungi_contatto.xhtml')
    def aggiungi_contatto(self, person=None):
        DBSession.add(Log(person=person or ''))
        DBSession.commit()
        return dict(person=person)

config = MinimalApplicationConfigurator()
config.update_blueprint({
    'root_controller': RootController(),
    'renderers': ['kajiki']
})

config.update_blueprint({
    'helpers': webhelpers2
})

config.register(StaticsConfigurationComponent)
config.update_blueprint({
    'serve_static': True,
    'paths': {
        'static_files': 'public'
    }
})

config.register(SQLAlchemyConfigurationComponent)
config.update_blueprint({
    'use_sqlalchemy': True,
    'sqlalchemy.url': 'sqlite:///data.db'
})

config.update_blueprint({'model': Bunch(
    DBSession=DBSession,
    init_model=init_model
)})

application = config.make_wsgi_app()

print("Serving on port 8080...")
httpd = make_server('', 8080, application)
httpd.serve_forever()