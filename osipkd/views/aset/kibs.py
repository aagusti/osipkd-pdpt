import colander
from deform import widget
from datetime import datetime

        
def deferred_kondisi(node, kw):
    values = kw.get('kondisi', [])
    return widget.SelectWidget(values=values)
    
kondisi = (
    ('B', 'Baik'),
    ('KB', 'Kurang Baik'),
    ('RB', 'Rusak Berat'),
    )
    
def deferred_cara(node, kw):
    values = kw.get('cara', [])
    return widget.SelectWidget(values=values)
    
cara = (
    ('Pembelian', 'Pembelian'),
    ('Hibah', 'Hibah'),
    ('Mutasi', 'Mutasi'),
    ('Lainnya', 'Lainnya'),
    )
    
class KibSchema(colander.Schema):
    """kat_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/aset/kategori/headofnama/act',
        min_length=1)
    katkode_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/aset/kategori/headofkode/act',
        min_length=1)
    pemilik_widget = widget.AutocompleteInputWidget(
        size=60,
        values = '/aset/pemilik/headofnama/act',
        min_length=1)"""
    unit_nm_widget = widget.AutocompleteInputWidget(
        values = '/unit/act/headofnama',
        min_length=1)
    unit_kd_widget = widget.AutocompleteInputWidget(
        values = '/unit/act/headofkode',
        min_length=1)
        
    tahun           = colander.SchemaNode(
                        colander.Integer(),
                        default = datetime.now().year)
    unit_id         = colander.SchemaNode(
                        colander.Integer(),
                        widget = widget.HiddenWidget(),
                        oid = "unit_id")
    unit_kd         = colander.SchemaNode(
                        colander.String(),
                        widget = unit_kd_widget,
                        oid = "unit_kd",
                        title = "SKPD")
    unit_nm         = colander.SchemaNode(
                        colander.String(),
                        widget = unit_nm_widget,
                        oid = "unit_nm",
                        title = "SKPD Uraian")
    kategori_id     = colander.SchemaNode(
                        colander.Integer(),
                        widget = widget.HiddenWidget(),
                        oid = "kategori_id")
    kategori_kd     = colander.SchemaNode(
                        colander.String(),
                        #widget = katkode_widget,
                        oid = "kategori_kd",
                        title = "Kategori")
    kategori_nm     = colander.SchemaNode(
                        colander.String(),
                        #widget = kat_widget,
                        oid = "kategori_nm",
                        title = "Kategori Uraian")
    no_register     = colander.SchemaNode(
                        colander.Integer(),
                        missing = colander.drop,
                        oid = "no_register",)
    pemilik_id      = colander.SchemaNode(
                        colander.Integer(),
                        widget = widget.HiddenWidget(),
                        oid = "pemilik_id",)
    pemilik_nm      = colander.SchemaNode(
                        colander.String(),
                        #widget = pemilik_widget,
                        oid = "pemilik_nm",
                        title = "Pemilik")                      
    uraian          = colander.SchemaNode(
                        colander.String())
    tgl_perolehan   = colander.SchemaNode(
                        colander.Date(),
                        title="Tanggal")
    cara_perolehan  = colander.SchemaNode(
                        colander.String(),
                        widget=widget.SelectWidget(values=cara),
                        title="Perolehan")
    th_beli         = colander.SchemaNode(
                        colander.Integer(),
                        title="Thn. Beli")
    asal_usul       = colander.SchemaNode(
                        colander.String(),
                        title="Asal-usul")
    harga           = colander.SchemaNode(
                        colander.Integer())
    jumlah          = colander.SchemaNode(
                        colander.Integer())
    satuan          = colander.SchemaNode(
                        colander.String())
    kondisi         = colander.SchemaNode(
                        colander.String(),
                        widget=widget.SelectWidget(values=kondisi),)
    keterangan      = colander.SchemaNode(
                        colander.String())



