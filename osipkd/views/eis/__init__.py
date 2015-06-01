import json
from pyramid.view import (
    view_config,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    )
from osipkd.views.base_view import BaseViews
from osipkd.models import DBSession
from osipkd.models.eis import Eis, Chart, ChartItem, Slide
from osipkd.tools import row2dict
########
# APP Home #
########
class eis(BaseViews):
    def cek_value(self,value,devider,simbol):
        if value<devider:
            return "{0:,.0f}".format(value)
        else:
            return "{0:,.2f} {1}".format(value/devider,simbol) 
        
    @view_config(route_name='eis', renderer='templates/home.pt')
    def view_app(self):
        tahun = self.session['tahun']
        datas = DBSession.query(Slide).filter(Slide.disabled==0).order_by(Slide.order_id)
        if not datas:
            datas = {}
        return dict(project='EIS', datas=datas)#, datas=Eis.sum_order_id('2014'))

    @view_config(route_name='eis-act', renderer='json')
    def view_app_act(self):
        tahun = self.session['tahun']
        req    =  self.request
        params =  req.params
        id = 'id' in params and params['id'] or 0
        json_data = {}
        json_data['success']=False
        
        if req.matchdict['act']=='grid':
            rows = DBSession.query(Eis).filter(Eis.id==id)
            if not rows:
                return json_data
                
            for row in rows:
                row_dicted = row2dict(row)
                amt_hari   =  float(row_dicted['amt_hari'])
                amt_minggu =  float(row_dicted['amt_minggu'])+amt_hari
                amt_bulan  =  float(row_dicted['amt_bulan'])+amt_hari
                amt_tahun  =  float(row_dicted['amt_tahun'])+amt_bulan
                json_data['success']= True
                json_data['tahun']  = self.cek_value(amt_tahun,1000000000, 'M')
                json_data['bulan']  = self.cek_value(amt_bulan,1000000000, 'M')
                json_data['minggu'] = self.cek_value(amt_minggu,1000000000, 'M')
                json_data['hari']   = self.cek_value(amt_hari,1000000000, 'M')
                
            return json_data

        #######################################################################
        # GRAFIK LINE/BAR
        #######################################################################        
        elif req.matchdict['act']=='linebar':
            rows = DBSession.query(Chart).filter(Chart.id==id).first()
            if not rows:
                return json_data
            
            json_data['label'] = rows.label.split(',')
            rows = DBSession.query(ChartItem).filter(ChartItem.chart_id==id).\
                      order_by(ChartItem.id)
            for row in rows:
                json_data[row.source_type] = [row.value_1/row.chart.devider,row.value_2/row.chart.devider,row.value_3/row.chart.devider,
                                              row.value_4/row.chart.devider,row.value_5/row.chart.devider,row.value_6/row.chart.devider, 
                                              row.value_7/row.chart.devider,row.value_8/row.chart.devider,row.value_9/row.chart.devider,
                                              row.value10/row.chart.devider,row.value11/row.chart.devider,row.value12/row.chart.devider,]
            
            
            json_data['success']= True
            return json_data
            
        #######################################################################
        # GRAFIK LINGKARAN
        #######################################################################        
        elif req.matchdict['act']=='pie':
            rows = DBSession.query(Chart).filter(Chart.id==id).first()
            if not rows:
                return json_data
            
            json_data['label'] = rows.label.split(',')
            rows = DBSession.query(ChartItem).filter(ChartItem.chart_id==id).\
                      order_by(ChartItem.id)
            json_data['rows'] = {}
            for row in rows:
                anama = {}
                anama['nama']       = row.nama
                anama['color']      = row.color
                anama ['highlight'] = row.highlight
                anama ['value']     = row.value_1/row.chart.devider
                json_data['rows'][row.nama] =anama 
                
            json_data['success']= True
            return json_data

        