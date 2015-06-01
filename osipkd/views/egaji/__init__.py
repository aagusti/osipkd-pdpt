from pyramid.view import (
    view_config,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    )
from osipkd.models.base_model import App
########
# APP Home #
########
@view_config(route_name='gaji', renderer='templates/home.pt', permission='view')
def view_app(request):
    return dict(project='egaji')
        