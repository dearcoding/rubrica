from tg import expose, TGController

class Controller(TGController):
    @expose(content_type='text/plain')
    def index(self):
        logs = DBSession.query(Log).order_by(Log.timestamp.desc()).all()
        return 'Past Greetings\n' + '\n'.join(['%s - %s' % (l.timestamp, l.person) for l in logs])

    @expose('hello.xhtml')
    def hello(self, person=None):
        DBSession.add(Log(person=person or ''))
        DBSession.commit()
        return dict(person=person)