tu_route = (
    ('b100', '/b100'),
    
    #Invoice/Tagihan/SPJ/Per Kegiatan
    ('b103_001',    '/b103/001'),
    ('b103_001_frm','/b103/001/frm/{id}'), #0 tambah selain itu edit
    ('b103_001_act','/b103/001/{act}'), #grid, delete?id
    ('b103_r001_act','/b103/r001/{act}'), #cetak?id

    #Invoice/Tagihan/SPJ/Per Item
    ('b103_997',    '/b103/997'),
    ('b103_997_frm','/b103/997/frm/{id}'), #0 tambah selain itu edit
    ('b103_997_act','/b103/997/{act}'), #grid, delete?id

    #SPP
    ('b103_002',    '/b103/002'),
    ('b103_002_frm','/b103/002/frm/{id}'), #0 tambah selain itu edit
    ('b103_002_act','/b103/002/{act}'), #grid, delete?id
    ('b103_r002_act','/b103/r002/{act}'), #cetak?id

    #SPM
    ('b103_003',    '/b103/003'),
    ('b103_003_frm','/b103/003/frm/{id}'), #0 tambah selain itu edit
    ('b103_003_act','/b103/003/{act}'), #grid, delete?id
    ('b103_r003_act','/b103/r003/{act}'), #cetak?id

    #Ketetapan
    ('b102_001',    '/b102/001'),
    ('b102_001_frm','/b102/001/frm/{id}'), #0 tambah selain itu edit
    ('b102_001_act','/b102/001/{act}'), #grid, delete?id11
    ('b102_r001_act','/b102/r001'), #cetak?id

    #TBP/ ARInvoice
    ('b102_002',    '/b102/002'),
    ('b102_002_frm','/b102/002/frm/{id}'), #0 tambah selain itu edit
    ('b102_002_act','/b102/002/{act}'), #grid, delete?id11
    ('b102_r002_act','/b102/r002'), #cetak?id

    #TBP Item
    ('b102_996',    '/b102/996'),
    ('b102_996_frm','/b102/996/frm/{id}'), #0 tambah selain itu edit
    ('b102_996_act','/b102/996/{act}'), #grid, delete?id11

    #STS
    ('b102_003',    '/b102/003'),
    ('b102_003_frm','/b102/003/frm/{id}'), #0 tambah selain itu edit
    ('b102_003_act','/b102/003/{act}'), #grid, delete?id11
    ('b102_r003_act','/b102/r003'), #cetak?id

    ('b200', '/b200'),
    #SP2D
    ('b203_001',    '/b203/001'),              
    ('b203_001_frm','/b203/001/frm/{id}'), #0 tambah selain itu edit
    ('b203_001_act','/b203/001/{act}'), #grid, delete?id
    ('b203_r001_act','/b203/r001'), #cetak?id

    #SPD
    ('b203_003',    '/b203/003'),              
    ('b203_003_frm','/b203/003/frm/{id}'), #0 tambah selain itu edit
    ('b203_003_act','/b203/003/{act}'), #grid, delete?id
    ('b203_r003_act','/b203/r003'), #cetak?id

    #GIRO
    ('b203_002',    '/b203/002'),              
    ('b203_002_frm','/b203/002/frm/{id}'), #0 tambah selain itu edit
    ('b203_002_act','/b203/002/{act}'), #grid, delete?id
    ('b203_r002_act','/b203/r002'), #cetak?id

    # LAPORAN  SKPD

    #Laporan ARInvoice
    ('b104_r000',  '/b104/r000'),
    ('b104_r000_act',  '/b104/r000/{act}'),

    #Laporan SPP
    ('b104_r100',  '/b104/r100'),
    ('b104_r100_act',  '/b104/r100/{act}'),

    #Laporan SPM
    ('b104_r200',  '/b104/r200'),
    ('b104_r200_act',  '/b104/r200/{act}'),

    #Laporan SPJ Fungsional
    ('b104_r300',  '/b104/r300'),
    ('b104_r300_act',  '/b104/r300/{act}'),
    
    #Laporan SPJ Administratif
    ('b104_r400',  '/b104/r400'),
    ('b104_r400_act',  '/b104/r400/{act}'),

    #Laporan SP2D
    ('b204_r000',  '/b204/r000'),
    ('b204_r000_act',  '/b204/r000/{act}'),

    #Laporan Realisasi Anggaran
    ('b204_r100',  '/b204/r100'),
    ('b204_r100_act',  '/b204/r100/{act}'),

    #Laporan Realisasi Anggaran/SKPD
    ('b204_r300',  '/b204/r300'),
    ('b204_r300_act',  '/b204/r300/{act}'),

    #Laporan Realisasi Anggaran/SKPD/Kegiatan
    ('b204_r200',  '/b204/r200'),
    ('b204_r200_act',  '/b204/r200/{act}'),

    )
