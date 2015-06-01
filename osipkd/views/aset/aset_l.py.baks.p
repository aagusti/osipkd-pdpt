from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
from sqlalchemy import *
from sqlalchemy.exc import DBAPIError
from osipkd.views.views import *
from osipkd.models.model_base import *
from osipkd.models.aset_models import *

import os
from pyramid.renderers import render_to_response
from asets_lap import *

def _upper(chain):
    ret = chain.upper()
    if ret:
        return ret
    else:
        return chain
        
class ViewAsetLap(BaseViews):
    @view_config(route_name="aset_lap_01", renderer="../../templates/aset/lap_skpd.pt")
    def aset(self):
        params = self.request.params
        self.app='aset'
        if self.logged:
            if self.session["unit_id"]:
                row = UnitModel.get_by_id(self.session['unit_id'])
            else:
                row = DBSession.query(UnitModel).\
                      order_by(UnitModel.kode).limit(1).one()
            return dict(datas=self.datas, rows=row)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="aset_lap_01_act")
    def aset_lap_01_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        uid = self.session["unit_id"] and self.session["unit_id"]>0 or params and params['uid']  or 0
        tahun = params and params['tahun']  or self.session["tahun"] or 0

        if self.logged :
            if url_dict['act']=='r001' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register, AsetKibModel.a_luas_m2, 
                        AsetKibModel.th_beli, AsetKibModel.a_alamat, AsetKibModel.a_hak_tanah, AsetKibModel.a_sertifikat_tanggal, AsetKibModel.a_sertifikat_nomor, 
                        AsetKibModel.a_penggunaan, AsetKibModel.asal_usul, AsetKibModel.harga, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,\
                                 AsetKibModel.kib=="A",AsetKibModel.unit_id==uid, AsetKibModel.tahun<=tahun)\
                        .order_by(AsetKategoriModel.kode).all()
                generator = r001Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
                
            elif url_dict['act']=='r002' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register, AsetKibModel.b_merk, 
                        AsetKibModel.b_type, AsetKibModel.b_cc, AsetKibModel.b_bahan, AsetKibModel.tahun, AsetKibModel.b_nomor_pabrik, 
                        AsetKibModel.b_nomor_rangka, AsetKibModel.b_nomor_mesin, AsetKibModel.b_nomor_polisi, AsetKibModel.b_nomor_bpkb, AsetKibModel.asal_usul, AsetKibModel.harga, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                 AsetKibModel.kib=="B",AsetKibModel.unit_id==uid, AsetKibModel.tahun<=tahun)\
                        .order_by(AsetKategoriModel.kode).all()
                generator = r002Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r003' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register, AsetKibModel.kondisi, 
                        AsetKibModel.c_bertingkat_tidak, AsetKibModel.c_beton_tidak, AsetKibModel.c_luas_lantai, AsetKibModel.c_lokasi, AsetKibModel.c_dokumen_tanggal, 
                        AsetKibModel.c_dokumen_nomor, AsetKibModel.c_luas_bangunan, AsetKibModel.c_status_tanah, AsetKibModel.c_kode_tanah, AsetKibModel.asal_usul, AsetKibModel.harga, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                 AsetKibModel.kib=="C",AsetKibModel.unit_id==uid, AsetKibModel.tahun<=tahun)\
                        .order_by(AsetKategoriModel.kode).all()
                generator = r003Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r004' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register, AsetKibModel.d_konstruksi, 
                        AsetKibModel.d_panjang, AsetKibModel.d_lebar, AsetKibModel.d_luas, AsetKibModel.d_lokasi, AsetKibModel.d_dokumen_tanggal, 
                        AsetKibModel.d_dokumen_nomor, AsetKibModel.d_status_tanah, AsetKibModel.d_kode_tanah, AsetKibModel.asal_usul, AsetKibModel.harga, AsetKibModel.kondisi, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                 AsetKibModel.kib=="D",AsetKibModel.unit_id==uid, AsetKibModel.tahun<=tahun)\
                        .order_by(AsetKategoriModel.kode).all()
                generator = r004Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r005' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register,  
                        AsetKibModel.e_judul, AsetKibModel.e_spek, AsetKibModel.e_asal, AsetKibModel.e_pencipta, AsetKibModel.e_bahan, 
                        AsetKibModel.e_jenis, AsetKibModel.e_ukuran, AsetKibModel.jumlah, AsetKibModel.asal_usul, AsetKibModel.b_thbuat, AsetKibModel.harga, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                 AsetKibModel.kib=="E",AsetKibModel.unit_id==uid, AsetKibModel.tahun<=tahun)\
                        .order_by(AsetKategoriModel.kode).all()
                generator = r005Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r006' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"),  
                        AsetKibModel.kondisi, AsetKibModel.f_bertingkat_tidak, AsetKibModel.f_beton_tidak, AsetKibModel.f_luas_lantai, AsetKibModel.f_lokasi, 
                        AsetKibModel.f_dokumen_tanggal, AsetKibModel.f_dokumen_nomor, AsetKibModel.tgl_perolehan, AsetKibModel.f_status_tanah, AsetKibModel.f_kode_tanah, AsetKibModel.asal_usul, AsetKibModel.harga, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                 AsetKibModel.kib=="F",AsetKibModel.unit_id==uid, AsetKibModel.tahun<=tahun)\
                        .order_by(AsetKategoriModel.kode).all()
                generator = r006Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r008' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register, AsetKategoriModel.uraian.label("katnm"),   
                        AsetKibModel.b_merk, AsetKibModel.b_type, AsetKibModel.a_sertifikat_nomor, AsetKibModel.b_nomor_pabrik, 
                        AsetKibModel.b_nomor_rangka, AsetKibModel.b_nomor_mesin, AsetKibModel.b_bahan, AsetKibModel.asal_usul, AsetKibModel.th_beli, AsetKibModel.e_ukuran, AsetKibModel.d_konstruksi, AsetKibModel.kondisi,
                        AsetKibModel.jumlah, AsetKibModel.harga, AsetKibModel.keterangan, AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                AsetKibModel.unit_id==uid, AsetKibModel.tahun<=tahun)\
                        .order_by(AsetKategoriModel.kode).all()
                generator = r008Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r010' and self.is_akses_mod('read'):
                subq = DBSession.query(AsetKategoriModel.kode, AsetKategoriModel.uraian).filter(AsetKategoriModel.level_id==1).subquery()
                query = DBSession.query(AsetKibModel.tahun.label("tahun"), UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"),  
                        subq.c.kode, subq.c.uraian, func.sum(AsetKibModel.harga*AsetKibModel.jumlah).label("nilai")).\
                        filter(AsetKibModel.kategori_id==AsetKategoriModel.id, subq.c.kode==func.substr(AsetKategoriModel.kode,1,5),
						AsetKibModel.unit_id==UnitModel.id, AsetKibModel.unit_id==uid, AsetKibModel.tahun==tahun).\
						group_by(AsetKibModel.tahun, UnitModel.kode, UnitModel.nama, subq.c.kode, subq.c.uraian).\
						order_by(subq.c.kode).all()
                generator = r010Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="aset_lap_02", renderer="../../templates/aset/lap_ppkd.pt")
    def aset_lap_02(self):
        params = self.request.params
        self.app='aset'
        if self.logged:
            return dict(datas=self.datas)
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)

    @view_config(route_name="aset_lap_02_act")
    def aset_lap_02_act(self):
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        tahun = params and params['tahun']  or self.session["tahun"] or 0

        if self.logged :
            if url_dict['act']=='r101' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register, AsetKibModel.a_luas_m2, 
                        AsetKibModel.th_beli, AsetKibModel.a_alamat, AsetKibModel.a_hak_tanah, AsetKibModel.a_sertifikat_tanggal, AsetKibModel.a_sertifikat_nomor, 
                        AsetKibModel.a_penggunaan, AsetKibModel.asal_usul, AsetKibModel.harga, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,\
                                 AsetKibModel.kib=="A", AsetKibModel.tahun<=tahun)\
                        .order_by(UnitModel.kode,AsetKategoriModel.kode,AsetKibModel.no_register).all()
                generator = r101Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
                
            elif url_dict['act']=='r102' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register, AsetKibModel.b_merk, 
                        AsetKibModel.b_type, AsetKibModel.b_cc, AsetKibModel.b_bahan, AsetKibModel.tahun, AsetKibModel.b_nomor_pabrik, 
                        AsetKibModel.b_nomor_rangka, AsetKibModel.b_nomor_mesin, AsetKibModel.b_nomor_polisi, AsetKibModel.b_nomor_bpkb, AsetKibModel.asal_usul, AsetKibModel.harga, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                 AsetKibModel.kib=="B", AsetKibModel.tahun<=tahun)\
                        .order_by(UnitModel.kode,AsetKategoriModel.kode,AsetKibModel.no_register).all()
                generator = r102Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r103' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register, AsetKibModel.kondisi, 
                        AsetKibModel.c_bertingkat_tidak, AsetKibModel.c_beton_tidak, AsetKibModel.c_luas_lantai, AsetKibModel.c_lokasi, AsetKibModel.c_dokumen_tanggal, 
                        AsetKibModel.c_dokumen_nomor, AsetKibModel.c_luas_bangunan, AsetKibModel.c_status_tanah, AsetKibModel.c_kode_tanah, AsetKibModel.asal_usul, AsetKibModel.harga, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                 AsetKibModel.kib=="C", AsetKibModel.tahun<=tahun)\
                        .order_by(UnitModel.kode,AsetKategoriModel.kode,AsetKibModel.no_register).all()
                generator = r103Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r104' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register, AsetKibModel.d_konstruksi, 
                        AsetKibModel.d_panjang, AsetKibModel.d_lebar, AsetKibModel.d_luas, AsetKibModel.d_lokasi, AsetKibModel.d_dokumen_tanggal, 
                        AsetKibModel.d_dokumen_nomor, AsetKibModel.d_status_tanah, AsetKibModel.d_kode_tanah, AsetKibModel.asal_usul, AsetKibModel.harga, AsetKibModel.kondisi, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                 AsetKibModel.kib=="D", AsetKibModel.tahun<=tahun)\
                        .order_by(UnitModel.kode,AsetKategoriModel.kode,AsetKibModel.no_register).all()
                generator = r104Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r105' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register,  
                        AsetKibModel.e_judul, AsetKibModel.e_spek, AsetKibModel.e_asal, AsetKibModel.e_pencipta, AsetKibModel.e_bahan, 
                        AsetKibModel.e_jenis, AsetKibModel.e_ukuran, AsetKibModel.jumlah, AsetKibModel.asal_usul, AsetKibModel.b_thbuat, AsetKibModel.harga, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                 AsetKibModel.kib=="E", AsetKibModel.tahun<=tahun)\
                        .order_by(UnitModel.kode,AsetKategoriModel.kode,AsetKibModel.no_register).all()
                generator = r105Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r106' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.uraian.label("katnm"), AsetKategoriModel.kode.label("katkd"),  
                        AsetKibModel.kondisi, AsetKibModel.f_bertingkat_tidak, AsetKibModel.f_beton_tidak, AsetKibModel.f_luas_lantai, AsetKibModel.f_lokasi, 
                        AsetKibModel.f_dokumen_tanggal, AsetKibModel.f_dokumen_nomor, AsetKibModel.tgl_perolehan, AsetKibModel.f_status_tanah, AsetKibModel.f_kode_tanah, AsetKibModel.asal_usul, AsetKibModel.harga, AsetKibModel.keterangan,
                        AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                 AsetKibModel.kib=="F", AsetKibModel.tahun<=tahun)\
                        .order_by(UnitModel.kode,AsetKategoriModel.kode,AsetKibModel.no_register).all()
                generator = r106Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r108' and self.is_akses_mod('read'):
                query = DBSession.query(AsetKategoriModel.kode.label("katkd"), AsetKibModel.no_register, AsetKategoriModel.uraian.label("katnm"),   
                        AsetKibModel.b_merk, AsetKibModel.b_type, AsetKibModel.a_sertifikat_nomor, AsetKibModel.b_nomor_pabrik, 
                        AsetKibModel.b_nomor_rangka, AsetKibModel.b_nomor_mesin, AsetKibModel.b_bahan, AsetKibModel.asal_usul, AsetKibModel.th_beli, AsetKibModel.e_ukuran, AsetKibModel.d_konstruksi, AsetKibModel.kondisi,
                        AsetKibModel.jumlah, AsetKibModel.harga, AsetKibModel.keterangan, AsetKibModel.tahun, UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"))\
                        .filter(AsetKibModel.kategori_id==AsetKategoriModel.id, AsetKibModel.unit_id==UnitModel.id,
                                AsetKibModel.tahun<=tahun)\
                        .order_by(UnitModel.kode,AsetKategoriModel.kode,AsetKibModel.no_register).all()
                generator = r108Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            elif url_dict['act']=='r110' and self.is_akses_mod('read'):
                subq = DBSession.query(AsetKategoriModel.kode, AsetKategoriModel.uraian).filter(AsetKategoriModel.level_id==1).subquery()
                query = DBSession.query(AsetKibModel.tahun.label("tahun"), UnitModel.kode.label("unitkd"), UnitModel.nama.label("unitnm"),  
                        subq.c.kode, subq.c.uraian, func.sum(AsetKibModel.harga*AsetKibModel.jumlah).label("nilai")).\
                        filter(AsetKibModel.kategori_id==AsetKategoriModel.id, subq.c.kode==func.substr(AsetKategoriModel.kode,1,5),
						AsetKibModel.unit_id==UnitModel.id, AsetKibModel.tahun==tahun).\
						group_by(AsetKibModel.tahun, UnitModel.kode, UnitModel.nama, subq.c.kode, subq.c.uraian).\
						order_by(UnitModel.kode,subq.c.kode).all()
                generator = r110Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=output.pdf' 
                response.write(pdf)
                return response
            else:
                return HTTPNotFound() 

        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
