import os
from pyramid.renderers import render_to_response
from pyramid.view import view_config
@view_config(route_name="aset", renderer="templates/home.pt",
             permission="read")
def home(self):
    #params = self.request.params
    return {}