from pyramid.view import (
    view_config,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    )
from ..models.base_model import App
############
# APP Main #
############

@view_config(route_name='main', renderer='templates/main-home.pt', permission='view')
def view_app(request):
    
    return dict(project='osipkd', rows=App.get_active())
        