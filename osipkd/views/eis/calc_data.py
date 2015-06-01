#!/usr/bin/python

import json
from datetime import datetime, date
from pyramid.view import (view_config,)
from pyramid.httpexceptions import (HTTPFound,)
from osipkd.views.base_view import BaseViews
from osipkd.models import DBSession
from osipkd.models.eis import Eis, Chart, ChartItem, Slide,ARPaymentDetail as AR
from osipkd.models.pemda_model import Rekening as R

from osipkd.tools import row2dict
from sqlalchemy import func

"""    tahun = Column(Integer)
    amount = Column(BigInteger)
    ref_kode = Column(String(32))
    ref_nama = Column(String(64))
    tanggal = Column(DateTime(timezone=True), nullable=True)
    kecamatan_kd = Column(String(32))
    kecamatan_nm = Column(String(64))
    kelurahan_kd = Column(String(32))
    kelurahan_nm = Column(String(64))
    is_kota      = Column(SmallInteger)
    sumber_data  = Column(String(32)) #Manual, PBB, BPHTB, PAD
    sumber_id    = Column(SmallInteger)#1, 2, 3, 4
"""
def eis_update_grid(row):
    pass
    
def eis_update_chart_item(row):
    pass
    
class eis_calc(BaseViews):
    @view_config(route_name='eis-calc-all', renderer='json')
    def eis_all(self):
        #UPDATE GRID
        req = self.request
        ses = self.session
        tahun = ses['tahun']
        
        eis_date  = datetime.now()
        eis_year  = eis_date.year
        eis_month = eis_date.month
        eis_day   = eis_date.day

        eis_date  = date(eis_year,eis_month,eis_day) 
        eis_week   = eis_date.isocalendar()[1]
        
        #UPDATE DATA wells
        rows = DBSession.query(Eis).filter(Eis.tahun==tahun).all()
        for row in rows:
            row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                          filter(AR.tahun==tahun, AR.bulan < eis_month,
                                 AR.kode.ilike("%s%%" % row.kode)).scalar()
            if row_data:
                row.amt_tahun = row_data

            row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                          filter(AR.tahun==tahun, AR.bulan == eis_month,
                                 AR.hari < eis_day,
                                 AR.kode.ilike("%s%%" % row.kode)).scalar()
            if row_data:
                row.amt_bulan = row_data

            row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                          filter(AR.tahun==tahun, AR.bulan == eis_month,
                                 AR.hari == eis_day,
                                 AR.kode.ilike("%s%%" % row.kode)).scalar()
            if row_data:
                row.amt_hari = row_data
            #update mingguan
            row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                          filter(AR.tahun==tahun, AR.bulan == eis_month,
                                 AR.minggu == eis_week,
                                 AR.kode.ilike("%s%%" % row.kode)).scalar()
            if row_data:
                row.amt_minggu = row_data - row.amt_hari
        DBSession.flush()
        #UPDATE DATA Chart Item Untuk Realisasi
        rows = DBSession.query(ChartItem).filter(ChartItem.source_type=='realisasi').all()
        for row in rows:
            #JIKA PIE hanya 1 kolom yang di update
            row_dict = row2dict(row)
            tupKode = row.rekening_kd.split(',') # split dulu kode rekening yang digunakan
            if row.chart.chart_type=='pie': 
                row_sum = 0
                for tup in tupKode:
                    row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                          filter(AR.tahun==tahun,
                                 AR.kode.ilike("%s%%" % tup.strip())).scalar()
                    if row_data:
                        row_sum += row_data
                row.value_1 = row_sum
            elif row.is_sum:
                if row.chart.label[:3]=='JAN':
                    row_sum = 0
                    for i in range(1,7):
                        tupKode = row.rekening_kd.split(',')
                        for tup in tupKode:
                            row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                                  filter(AR.tahun==tahun,
                                         AR.bulan == i,
                                         AR.kode.ilike("%s%%" % tup.strip())).scalar()
                            if row_data:
                                row_sum = row_sum+row_data
                        row_dict['value_%s' %i] = row_sum
                    print row_dict
                    row.from_dict(row_dict)
                    
                elif row.chart.label[:3]=='JUL':
                    row_sum = 0
                    for i in range(7,13):
                        tupKode = row.rekening_kd.split(',')
                        for tup in tupKode:
                            row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                                  filter(AR.tahun==tahun,
                                         AR.bulan == i,
                                         AR.kode.ilike("%s%%" % tup.strip())).scalar()
                            if row_data:
                                row_sum += row_data
                        row_dict['value_%s' % str(i-6)] = row_sum
                    row.from_dict(row_dict)
       
            else:
                if row.chart.label[:3]=='JAN':
                    for i in range(1,7):
                        tupKode = row.rekening_kd.split(',')
                        row_sum = 0
                        for tup in tupKode:
                            row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                                  filter(AR.tahun==tahun,
                                         AR.bulan == i,
                                         AR.kode.ilike("%s%%" % tup.strip())).scalar()
                            if row_data:
                                row_sum += row_data
                        row_dict['value_%s' %i] = row_sum
                    row.from_dict(row_dict)
                elif row.chart.label[:3]=='JUL':
                    for i in range(7,13):
                        tupKode = row.rekening_kd.split(',')
                        row_sum = 0
                        for tup in tupKode:
                            row_data = DBSession.query(func.sum(AR.amount).label('s')).\
                                  filter(AR.tahun==tahun,
                                         AR.bulan == i,
                                         AR.kode.ilike("%s%%" % tup.strip())).scalar()
                            if row_data:
                                row_sum += row_data
                        row_dict['value_%s' % str(i-6)] = row_sum
                    row.from_dict(row_dict)
        DBSession.flush()
        return {"minggu":eis_week}
        