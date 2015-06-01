from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.url import resource_url
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
from datetime import datetime 
from sqlalchemy.exc import DBAPIError
import colander
from ..models import (
    DBSession,
    UserResourcePermission,
    Resource,
    User,
    )
from osipkd.models.pemda_model import  STATUS_APBD
from datetime import (datetime, date)

from pyjasper.client import JasperGenerator

class BaseViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = request.session
        self.cust_nm   = "PEMERINTAH KABUPATEN TANGERANG"
        self.datas = {}
        
        cday = datetime.today()    
        if not 'tahun' in self.session:
            self.session['tahun'] =  cday.strftime('%Y')
        #self.session['tahun'] =  cday.strftime('%Y')
        if not 'bulan' in self.session:
            self.session['bulan'] = str(cday.month).zfill(2)
        if not 'tanggal' in self.session:
            self.session['tanggal'] = datetime.date(datetime.now()) 
        if not 'tanggal2' in self.session:
            self.session['tanggal2'] = datetime.date(datetime.now()) 
        #datetime.date(datetime.now().year,
        #                                  datetime.now().month, datetime.now().day)
        #    if cday.month ==12:
        #        self.session['bulan'] = '01'
        #        self.session['tahun'] = str(cday.year + 1)
        #    else:
        

        if not 'unit_id' in self.session:
            self.session['unit_id'] = 0 #No tahun datetime.strftime(datetime.now(),'%Y')
        if not 'all_unit' in self.session:
            self.session['all_unit'] = 0 # no status
        if not 'unit_kd' in self.session:
            self.session['unit_kd'] = ""
        if not 'unit_nm' in self.session:
            self.session['unit_nm'] = ""
        if not 'cust_nm' in self.session:
            self.session['cust_nm'] = self.cust_nm
        # Inisiasi tahun anggaran
        ########################################################################
        #remark in production  
        #self.session['bulan'] =  '01'
        #self.session['unit_id'] = 9
        #self.session['unit_kd'] = '4027.114'
        #self.session['unit_nm'] = 'DINAS DEMO'
        ########################################################################
        self.tahun = self.session['tahun']
        self.bulan = self.session['bulan']
        self.unit_id = self.session['unit_id']
        self.all_unit = self.session['all_unit']
        
        self.d = {}
        self.d['success'] = False        
        self.d['msg']='Hak akses dibatasi'

        self.unit_kd = self.session['unit_kd']
        self.unit_nm = self.session['unit_nm']
        #default datas 
        """self.datas={}
        self.datas['tahun'] = self.tahun
        self.datas['bulan'] = self.bulan
        self.datas['unit_id'] = self.unit_id
        self.datas['all_unit'] = self.all_unit
        self.datas['unit_kd'] = self.session['unit_kd']
        self.datas['unit_nm'] = self.session['unit_nm']
        permission = UserResourcePermission()
        permission.perm_name = "read"
        permission.user_name = "aagusti"
        #resource = DBSession.query(User).filter_by(id=1)
        resource = Resource()
        resource.resource_name = 'GAJI'
        resource.resource_type = '1'
        
        DBSession.add(resource)
        request.user.resources.append(resource)
        """
        
    def _DTstrftime(self, chain):
        ret = chain and datetime.strftime(chain, '%d-%m-%Y')
        if ret:
            return ret
        else:
            return chain
            
    def _number_format(self, chain):
        import locale
        locale.setlocale(locale.LC_ALL, 'id_ID.utf8')
        ret = locale.format("%d", chain, grouping=True)
        if ret:
            return ret
        else:
            return chain
    def _StatusAPBD(self, chain):
        if chain:
            for (id,value) in STATUS_APBD:
                if id==chain:
                    ret = value
        if ret:
            return ret
        else:
            return chain    
@view_config(route_name='change-act', renderer='json', permission='view')
def change_act(request):
    ses = request.session
    req = request
    params = req.params
    url_dict = req.matchdict
    
    if url_dict['act']=='tahun':
        ses['tahun'] = 'tahun' in params and params['tahun'] or '2014'
        ses['bulan'] = 'bulan' in params and params['bulan'] or '12'
        return {'success':True}
    elif url_dict['act']=='tanggal':
        ses['tanggal'] = 'tanggal' in params and datetime.strptime(params['tanggal'],'%Y-%m-%d') or datetime.date(datetime.now())
        ses['tanggal2'] = 'tanggal2' in params and datetime.strptime(params['tanggal2'],'%Y-%m-%d') or ses['tanggal']
        return {'success':True, 'msg':''}
        
        