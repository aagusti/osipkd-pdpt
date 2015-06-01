\COPY routes(kode,disabled,created,create_uid,nama,path,perm_name) FROM stdin
home	0	2014-12-24 03:04:42.837591	1	Home	/	view
login	0	2014-12-24 03:04:42.837591	1	Login	/login	view
logout	0	2014-12-24 03:04:42.837591	1	Logout	/logout	view
password	0	2014-12-24 03:04:42.837591	1	Change password	/password	view
admin	0	2014-12-24 03:04:42.837591	1	Administrator	/admin	read
apbd-tahun	0	2014-12-24 03:04:42.837591	1	Tahun Anggaran	/apbd-tahun	read
apbd-tahun-act	0	2014-12-24 03:04:42.837591	1	Tahun Anggaran Act	/apbd-tahun/act/{act}	read
apbd-tahun-add	0	2014-12-24 03:04:42.837591	1	Tambah Tahun Anggaran	/apbd-tahun/add	add
apbd-tahun-edit	0	2014-12-24 03:04:42.837591	1	Edit Tahun Anggaran	/apbd-tahun/{id}/edit	edit
apbd-tahun-delete	0	2014-12-24 03:04:42.837591	1	Hapus Tahun Anggaran	/apbd-tahun/{id}/delete	delete
carousel	0	2014-12-24 03:04:42.837591	1	Carousel	/carousel	view
carousel-act	0	2014-12-24 03:04:42.837591	1	Carousel	/carousel/act/{act}	view
carousel-add	0	2014-12-24 03:04:42.837591	1	Tambah Carousel	/carousel/add	add
carousel-edit	0	2014-12-24 03:04:42.837591	1	Edit Carousel	/carousel/{id}/edit	edit
carousel-delete	0	2014-12-24 03:04:42.837591	1	Hapus Carousel	/carousel/{id}/delete	delete
eis-chart	0	2014-12-24 03:04:42.837591	1	eis-chart	/eis-chart	read
eis-chart-act	0	2014-12-24 03:04:42.837591	1	eis-chart	/eis-chart/act/{act}	read
eis-chart-add	0	2014-12-24 03:04:42.837591	1	Edit Tambah eis-chart	/eis-chart/add	add
eis-chart-edit	0	2014-12-24 03:04:42.837591	1	Edit eis-chart	/eis-chart/{id}/edit	edit
eis-chart-delete	0	2014-12-24 03:04:42.837591	1	Hapus eis-chart	/eis-chart/{id}/delete	delete
eis-chart-item	0	2014-12-24 03:04:42.837591	1	EIS-chart-item	/eis-chart-item/{chart_id}	read
eis-chart-item-act	0	2014-12-24 03:04:42.837591	1	eis-chart-item	/eis-chart-item/{chart_id}/act/{act}	read
eis-chart-item-add	0	2014-12-24 03:04:42.837591	1	Tambah eis-chart-item	/eis-chart-item/{chart_id/add	add
eis-chart-item-edit	0	2014-12-24 03:04:42.837591	1	Edit eis-chart-item	/eis-chart-item/{chart_id}/{id}/edit	edit
eis-chart-item-delete	0	2014-12-24 03:04:42.837591	1	Hapus eis-chart-item	/eis-chart-item/{chart_id}/{id}/delete	delete
eis-item	0	2014-12-24 03:04:42.837591	1	EIS item	/eis-item	read
eis-item-act	0	2014-12-24 03:04:42.837591	1	eis-item	/eis-item/act/{act}	read
eis-item-add	0	2014-12-24 03:04:42.837591	1	Tambah eis-item	/eis-item/add	add
eis-item-edit	0	2014-12-24 03:04:42.837591	1	Edit eis-item	/eis-item/{id}/edit	edit
eis-item-delete	0	2014-12-24 03:04:42.837591	1	Hapus eis-item	/eis-item/{id}/delete	delete
eis-slide	0	2014-12-24 03:04:42.837591	1	EIS slide	/eis-slide	read
eis-slide-act	0	2014-12-24 03:04:42.837591	1	eis-slide	/eis-slide/act/{act}	read
eis-slide-add	0	2014-12-24 03:04:42.837591	1	Tambah eis-slide	/eis-slide/add	add
eis-slide-edit	0	2014-12-24 03:04:42.837591	1	Edit eis-slide	/eis-slide/{id}/edit	edit
eis-slide-delete	0	2014-12-24 03:04:42.837591	1	Hapus eis-slide	/eis-slide/{id}/delete	delete
app	0	2014-12-24 03:04:42.837591	1	Aplikasi	/app	read
app-act	0	2014-12-24 03:04:42.837591	1	Aplikasi Act	/app/act/{act}	read
app-add	0	2014-12-24 03:04:42.837591	1	Tambah Aplikasi	/app/add	add
app-edit	0	2014-12-24 03:04:42.837591	1	Edit Aplikasi	/app/{id}/edit	edit
app-delete	0	2014-12-24 03:04:42.837591	1	Hapus Aplikasi	/app/{id}/delete	delete
fungsi	0	2014-12-24 03:04:42.837591	1	Fungsi	/fungsi	read
fungsi-act	0	2014-12-24 03:04:42.837591	1	Fungsi Act	/fungsi/act/{act}	read
fungsi-add	0	2014-12-24 03:04:42.837591	1	Tambah Fungsi	/fungsi/add	add
fungsi-edit	0	2014-12-24 03:04:42.837591	1	Edit Fungsi	/fungsi/{id}/edit	edit
fungsi-delete	0	2014-12-24 03:04:42.837591	1	Hapus Fungsi	/fungsi/{id}/delete	delete
group	0	2014-12-24 03:04:42.837591	1	Groups	/group	read
group-act	0	2014-12-24 03:04:42.837591	1	NULL	/group/act/{act}	read
group-add	0	2014-12-24 03:04:42.837591	1	Tambah group	/group/add	add
group-edit	0	2014-12-24 03:04:42.837591	1	Edit group	/group/{id}/edit	edit
group-delete	0	2014-12-24 03:04:42.837591	1	Hapus group	/group/{id}/delete	delete
group-routes	0	2014-12-24 03:04:42.837591	1	Group Route	/group/routes	read
group-routes-act	0	2014-12-24 03:04:42.837591	1	Group Route Act	/group/routes/act/{act}	read
group-routes-add	0	2014-12-24 03:04:42.837591	1	Tambah Group Route	/group/routes/add	add
group-routes-delete	0	2014-12-24 03:04:42.837591	1	Hapus Group Route	/group/routes/{id}/{id2}/delete	delete
jabatan	0	2014-12-24 03:04:42.837591	1	Jabatan	/jabatan	read
jabatan-act	0	2014-12-24 03:04:42.837591	1	Jabatan Act	/jabatan/act/{act}	read
jabatan-add	0	2014-12-24 03:04:42.837591	1	Tambah Jabatan	/jabatan/add	add
jabatan-edit	0	2014-12-24 03:04:42.837591	1	Edit Jabatan	/jabatan/{id}/edit	edit
jabatan-delete	0	2014-12-24 03:04:42.837591	1	Hapus Jabatan	/jabatan/{id}/delete	delete
kegiatan	0	2014-12-24 03:04:42.837591	1	Kegiatan	/kegiatan	read
kegiatan-act	0	2014-12-24 03:04:42.837591	1	Kegiatan Act	/kegiatan/act/{act}	read
kegiatan-add	0	2014-12-24 03:04:42.837591	1	Tambah Kegiatan	/kegiatan/add	add
kegiatan-edit	0	2014-12-24 03:04:42.837591	1	Edit Kegiatan	/kegiatan/{id}/edit	edit
kegiatan-delete	0	2014-12-24 03:04:42.837591	1	Hapus Kegiatan	/kegiatan/{id}/delete	delete
pegawai	0	2014-12-24 03:04:42.837591	1	Pegawai	/pegawai	read
pegawai-act	0	2014-12-24 03:04:42.837591	1	Pegawai Act	/pegawai/act/{act}	read
pegawai-add	0	2014-12-24 03:04:42.837591	1	Tambah Pegawai	/pegawai/add	add
pegawai-edit	0	2014-12-24 03:04:42.837591	1	Edit Pegawai	/pegawai/{id}/edit	edit
pegawai-delete	0	2014-12-24 03:04:42.837591	1	Hapus Pegawai	/pegawai/{id}/delete	delete
pejabat	0	2014-12-24 03:04:42.837591	1	Pejabat	/pejabat	read
pejabat-act	0	2014-12-24 03:04:42.837591	1	Pejabat Act	/pejabat/act/{act}	read
pejabat-add	0	2014-12-24 03:04:42.837591	1	Tambah Pejabat	/pejabat/add	add
pejabat-edit	0	2014-12-24 03:04:42.837591	1	Edit Pejabat	/pejabat/{id}/edit	edit
pejabat-delete	0	2014-12-24 03:04:42.837591	1	Hapus Pejabat	/pejabat/{id}/delete	delete
program	0	2014-12-24 03:04:42.837591	1	Program	/program	read
program-act	0	2014-12-24 03:04:42.837591	1	Program Act	/program/act/{act}	read
program-add	0	2014-12-24 03:04:42.837591	1	Tambah Program	/program/add	add
program-edit	0	2014-12-24 03:04:42.837591	1	Edit Program	/program/{id}/edit	edit
program-delete	0	2014-12-24 03:04:42.837591	1	Hapus Program	/program/{id}/delete	delete
rekening	0	2014-12-24 03:04:42.837591	1	Rekening	/rekening	read
rekening-act	0	2014-12-24 03:04:42.837591	1	Rekening Act	/rekening/act/{act}	read
rekening-add	0	2014-12-24 03:04:42.837591	1	Tambah Rekening	/rekening/add	add
rekening-edit	0	2014-12-24 03:04:42.837591	1	Edit Rekening	/rekening/{id}/edit	edit
rekening-delete	0	2014-12-24 03:04:42.837591	1	Hapus Rekening	/rekening/{id}/delete	delete
routes	0	2014-12-24 03:04:42.837591	1	Route	/routes	read
routes-act	0	2014-12-24 03:04:42.837591	1	Route Act	/routes/act/{act}	read
routes-add	0	2014-12-24 03:04:42.837591	1	Tambah Route	/routes/add	add
routes-edit	0	2014-12-24 03:04:42.837591	1	Edit Route	/routes/{id}/edit	edit
routes-delete	0	2014-12-24 03:04:42.837591	1	Hapus Route	/routes/{id}/delete	delete
unit	0	2014-12-24 03:04:42.837591	1	units	/unit	read
unit-act	0	2014-12-24 03:04:42.837591	1	AdminFactory	/unit/act/{act}	read
unit-add	0	2014-12-24 03:04:42.837591	1	Tambah unit	/unit/add	add
unit-edit	0	2014-12-24 03:04:42.837591	1	Edit unit	/unit/{id}/edit	edit
unit-delete	0	2014-12-24 03:04:42.837591	1	Hapus unit	/unit/{id}/delete	delete
urusan	0	2014-12-24 03:04:42.837591	1	urusans	/urusan	read
urusan-act	0	2014-12-24 03:04:42.837591	1	Action	/urusan/act/{act}	read
urusan-add	0	2014-12-24 03:04:42.837591	1	Tambah urusan	/urusan/add	add
urusan-edit	0	2014-12-24 03:04:42.837591	1	Edit urusan	/urusan/{id}/edit	edit
urusan-delete	0	2014-12-24 03:04:42.837591	1	Hapus urusan	/urusan/{id}/delete	delete
dasarhukum	0	2014-12-24 03:04:42.837591	1	Dasar Hukum	/dasarhukum	read
dasarhukum-act	0	2014-12-24 03:04:42.837591	1	Dasar Hukum Act	/dasarhukum/act/{act}	read
dasarhukum-add	0	2014-12-24 03:04:42.837591	1	Tambah Dasar Hukum	/dasarhukum/add	add
dasarhukum-edit	0	2014-12-24 03:04:42.837591	1	Edit Dasar Hukum	/dasarhukum/{id}/edit	edit
dasarhukum-delete	0	2014-12-24 03:04:42.837591	1	Hapus Dasar Hukum	/dasarhukum/{id}/delete	delete
user	0	2014-12-24 03:04:42.837591	1	Users	/user	read
user-act	0	2014-12-24 03:04:42.837591	1	Users	/user/act/{act}	read
user-add	0	2014-12-24 03:04:42.837591	1	Tambah user	/user/add	add
user-edit	0	2014-12-24 03:04:42.837591	1	Edit user	/user/{id}/edit	edit
user-delete	0	2014-12-24 03:04:42.837591	1	Hapus user	/user/{id}/delete	delete
user-group	0	2014-12-24 03:04:42.837591	1	Group User	/user/group	read
user-group-act	0	2014-12-24 03:04:42.837591	1	Group User Act	/user/group/act/{act}	read
user-group-add	0	2014-12-24 03:04:42.837591	1	Tambah Group User	/user/group/add	add
user-group-edit	0	2014-12-24 03:04:42.837591	1	Edit Group User	/user/group/{id}/edit	edit
user-group-delete	0	2014-12-24 03:04:42.837591	1	Hapus Group User	/user/group/{id}/delete	delete
user-unit	0	2014-12-24 03:04:42.837591	1	User Unit	/user/unit	read
user-unit-act	0	2014-12-24 03:04:42.837591	1	User Unit Act	/user/unit/act/{act}	read
user-unit-add	0	2014-12-24 03:04:42.837591	1	Tambah User Unit	/user/unit/add	add
user-unit-edit	0	2014-12-24 03:04:42.837591	1	Edit User Unit	/user/unit/{id}/edit	edit
user-unit-delete	0	2014-12-24 03:04:42.837591	1	Hapus User Unit	/user/unit/{id}/delete	delete
skpd	0	2014-12-24 03:04:42.837591	1	Penatausahaan dan Akuntansi SKPD	/skpd	read
ak-jurnal	0	2014-12-24 03:04:42.837591	1	Jurnal	/ak-jurnal	read
ak-jurnal-act	0	2014-12-24 03:04:42.837591	1	ACT Jurnal	/ak-jurnal/act/{act}	read
ak-jurnal-add	0	2014-12-24 03:04:42.837591	1	Tambah Jurnal	/ak-jurnal/add	add
ak-jurnal-edit	0	2014-12-24 03:04:42.837591	1	Edit Jurnal	/ak-jurnal/{id}/edit	edit
ak-jurnal-delete	0	2014-12-24 03:04:42.837591	1	Hapus Jurnal	/ak-jurnal/{id}/delete	delete
ak-jurnal-item	0	2014-12-24 03:04:42.837591	1	Jurnal Item	/ak-jurnal-item	read
ak-jurnal-item-act	0	2014-12-24 03:04:42.837591	1	Jurnal Item Act	/ak-jurnal-item/act/{act}	read
ak-jurnal-item-add	0	2014-12-24 03:04:42.837591	1	Tambah Jurnal Item	/ak-jurnal-item/add	add
ak-jurnal-item-delete	0	2014-12-24 03:04:42.837591	1	Hapus Jurnal Item	/ak-jurnal-item/{id}/delete	delete
ak-report	0	2014-12-24 03:04:42.837591	1	Laporan Akuntansi	/ak-report	read
ak-report-act	0	2014-12-24 03:04:42.837591	1	AK Report ACT	/ak-report/act/{act}	read
ak-report-lkpj	0	2014-12-24 03:04:42.837591	1	Laporan Keuangan dan Pertanggung Jawaban	/ak-report-lkpj	read
ak-report-lkpj-act	0	2014-12-24 03:04:42.837591	1	Laporan Keuangan dan Pertanggung Jawaban	/ak-report-lkpj/act/{act}	read
ar-invoice-item	0	2014-12-24 03:04:42.837591	1	Penetapan/Tagihan	/ar-invoice-item	read
ar-invoice-item-act	0	2014-12-24 03:04:42.837591	1	Penetapan/Tagihan Act	/ar-invoice-item/act/{act}	read
ar-invoice-item-add	0	2014-12-24 03:04:42.837591	1	Tambah Penetapan/Tagihan	/ar-invoice-item/add	add
ar-invoice-item-edit	0	2014-12-24 03:04:42.837591	1	Edit Penetapan/Tagihan	/ar-invoice-item/{id}/edit	edit
ar-invoice-item-delete	0	2014-12-24 03:04:42.837591	1	Hapus Penetapan/Tagihan	/ar-invoice-item/{id}/delete	delete
ar-payment-item	0	2014-12-24 03:04:42.837591	1	Realisasi/STS	/ar-payment-item	read
ar-payment-item-act	0	2014-12-24 03:04:42.837591	1	Realisasi/STS Act	/ar-payment-item/act/{act}	read
ar-payment-item-add	0	2014-12-24 03:04:42.837591	1	Tambah Realisasi/ STS	/ar-payment-item/add	add
ar-payment-item-edit	0	2014-12-24 03:04:42.837591	1	Edit Realisasi/STS	/ar-payment-item/{id}/edit	edit
ar-payment-item-delete	0	2014-12-24 03:04:42.837591	1	Hapus Realisasi/STS	/ar-payment-item/{id}/delete	delete
ar-report-item	0	2014-12-24 03:04:42.837591	1	Laporan Pendapatan	/ar-report-item	read
anggaran	0	2014-12-24 03:04:42.837591	1	Anggaran	/anggaran	read
ag-btl	0	2014-12-24 03:04:42.837591	1	Anggaran Belanja Tidak Langsung	/ag-btl	read
ag-kegiatan-item	0	2014-12-24 03:04:42.837591	1	Kegiatan Item	/ag-kegiatan-item/{kegiatan_sub_id}	read
ag-kegiatan-item-act	0	2014-12-24 03:04:42.837591	1	Anggaran Penerimaan Act	/ag-kegiatan-item/act/{act}	read
ag-kegiatan-item-add-fast	0	2014-12-24 03:04:42.837591	1	Anggaran Penerimaan Act	/ag-kegiatan-item/add/fast	add
ag-kegiatan-item-add	0	2014-12-24 03:04:42.837591	1	Tambah Kegiatan Item	/ag-kegiatan-item/{kegiatan_sub_id}/add	add
ag-kegiatan-item-edit	0	2014-12-24 03:04:42.837591	1	Edit Kegiatan Item	/ag-kegiatan-item/{kegiatan_sub_id}/{id}/edit	edit
ag-kegiatan-item-delete	0	2014-12-24 03:04:42.837591	1	Hapus Kegiatan Item	/ag-kegiatan-item/{kegiatan_sub_id}/{id}/delete	delete
ag-bl	0	2014-12-24 03:04:42.837591	1	Anggaran Belanja  Langsung	/ag-bl	read
ag-bl-act	0	2014-12-24 03:04:42.837591	1	Anggaran Belanja  Langsung Act	/ag-bl/act/{act}	read
ag-bl-add	0	2014-12-24 03:04:42.837591	1	Tambah Anggaran Belanja  Langsung	/ag-bl/add	add
ag-bl-edit	0	2014-12-24 03:04:42.837591	1	Edit Anggaran Belanja  Langsung	/ag-bl/{id}/edit	edit
ag-bl-delete	0	2014-12-24 03:04:42.837591	1	Hapus Anggaran Belanja  Langsung	/ag-bl/{id}/delete	delete
ag-kegiatan-sub-act	0	2014-12-24 03:04:42.837591	1	Anggaran Penerimaan Act	/ag-kegiatan-sub/act/{act}	read
ag-kegiatan-sub-add-fast	0	2014-12-24 03:04:42.837591	1	Anggaran Penerimaan Act	/ag-kegiatan-sub/add/fast	add
ag-pendapatan	0	2014-12-24 03:04:42.837591	1	Anggaran Pendapatan	/ag-pendapatan	read
ag-penerimaan	0	2014-12-24 03:04:42.837591	1	Anggaran Penerimaan	/ag-penerimaan	read
ag-pengeluaran	0	2014-12-24 03:04:42.837591	1	Anggaran Pengeluaran	/ag-pengeluaran	read
ag-indikator	0	2014-12-24 03:04:42.837591	1	Indikator Kegiatan	/ag-indikator/{kegiatan_sub_id}	read
ag-indikator-act	0	2014-12-24 03:04:42.837591	1	Indikator Kegiatan Act	/ag-indikator/act/{act}	read
ag-indikator-add	0	2014-12-24 03:04:42.837591	1	Tambah Indikator Kegiatan	/ag-indikator/{kegiatan_sub_id}/add	add
ag-indikator-edit	0	2014-12-24 03:04:42.837591	1	Edit Indikator Kegiatan	/ag-indikator/{kegiatan_sub_id}/{id}/edit	edit
ag-indikator-delete	0	2014-12-24 03:04:42.837591	1	Hapus Indikator Kegiatan	/ag-indikator/{kegiatan_sub_id}/{id}/delete	delete
ag-indikator-add-fast	0	2014-12-24 03:04:42.837591	1	Tambah Indikator Kegiatan	/ag-indikator/add/fast	add
anggaran_r000	0	2014-12-24 03:04:42.837591	1	Report Master	/ag-report/r000	read
anggaran_r000_act	0	2014-12-24 03:04:42.837591	1	Report Master Act	/ag-report/r000/act/{act}	read
anggaran_r100	0	2014-12-24 03:04:42.837591	1	Report RKA	/ag-report/r100	read
anggaran_r100_act	0	2014-12-24 03:04:42.837591	1	Report RKA Act	/ag-report/r100/act/{act}	read
anggaran_r200	0	2014-12-24 03:04:42.837591	1	Report DPA	/ag-report/r200	read
anggaran_r200_act	0	2014-12-24 03:04:42.837591	1	Report DPA Act	/ag-report/r200/act/{act}	read
anggaran_r300	0	2014-12-24 03:04:42.837591	1	Report RPKA	/ag-report/r300	read
anggaran_r300_act	0	2014-12-24 03:04:42.837591	1	Report RPKA Act	/ag-report/r300/act/{act}	read
anggaran_r400	0	2014-12-24 03:04:42.837591	1	Report DPPA	/ag-report/r400	read
anggaran_r400_act	0	2014-12-24 03:04:42.837591	1	Report DPPA Act	/ag-report/r400/act/{act}	read
anggaran_r500	0	2014-12-24 03:04:42.837591	1	Report Perda	/ag-report/r500	read
anggaran_r500_act	0	2014-12-24 03:04:42.837591	1	Report Perda Act	/ag-report/r500/act/{act}	read
anggaran_r600	0	2014-12-24 03:04:42.837591	1	Report Perbup	/ag-report/r600	read
anggaran_r600_act	0	2014-12-24 03:04:42.837591	1	Report Perbup Act	/ag-report/r600/act/{act}	read
change-act	0	2014-12-24 03:04:42.837591	1	change	/change/{act}	read
gaji	0	2014-12-24 03:04:42.837591	1	Gaji	/gaji	read
gaji-peg	0	2014-12-24 03:04:42.837591	1	Gaji Pegawai	/gaji-peg	read
gaji-peg-act	0	2014-12-24 03:04:42.837591	1	Gaji Pegawai Act	/gaji-peg/act/{act}	read
gaji-peg-csv	0	2014-12-24 03:04:42.837591	1	Gaji Pegawai Act	/gaji-peg/csv	read
gaji-potongan	0	2014-12-24 03:04:42.837591	1	Potongan Gaji	/gaji-potongan	read
gaji-potongan-act	0	2014-12-24 03:04:42.837591	1	Action Potongan Gaji	/gaji-potongan/act/{act}	read
gaji-potongan-add	0	2014-12-24 03:04:42.837591	1	Tambah Potongan	/gaji-potongan/add	add
gaji-potongan-edit	0	2014-12-24 03:04:42.837591	1	Edit Potongan	/gaji-potongan/{id}/edit	edit
gaji-potongan-delete	0	2014-12-24 03:04:42.837591	1	Hapus Potongan	/gaji-potongan/{id}/delete	delete
gaji-potongan-csv	0	2014-12-24 03:04:42.837591	1	Gaji Potongan Act	/gaji-potongan/csv	read
eis	0	2014-12-24 03:04:42.837591	1	Executive Summary	/eis	read
eis-act	0	2014-12-24 03:04:42.837591	1	Executive Summary	/eis/act/{act}	read
eis-calc-all	0	2014-12-24 03:04:42.837591	1	Executive Summary Calc	/eis/calc-all	read
main	0	2014-12-24 03:04:42.837591	1	Main Aplikasi	/main	read
tu-ppkd	0	2014-12-24 03:04:42.837591	1	Penatausahaan PPKD	/tu-ppkd	read
ap-giro	0	2014-12-24 03:04:42.837591	1	Giro	/ap-giro	read
ap-giro-act	0	2014-12-24 03:04:42.837591	1	Giro Act	/ap-giro/act/{act}	read
ap-giro-add	0	2014-12-24 03:04:42.837591	1	Tambah Giro	/ap-giro/add	add
ap-giro-edit	0	2014-12-24 03:04:42.837591	1	Edit Giro	/ap-giro/{id}/edit	edit
ap-giro-delete	0	2014-12-24 03:04:42.837591	1	Hapus Giro	/ap-giro/{id}/delete	delete
ap-giro-item-act	0	2015-01-07 00:29:49.485249	1	Giro Item Act	/ap-giro/item/{ap_giro_id}/act/{act}	read
ap-giro-item-add	0	2015-01-07 00:29:49.485249	1	Tambah Giro Item	/ap-giro/item/{ap_giro_id}/add	add
ap-giro-item-edit	0	2015-01-07 00:29:49.485249	1	Edit GIRO Item	/ap-giro/item/{ap_giro_id}/{id}/edit	edit
ap-giro-item-delete	0	2015-01-07 00:29:49.485249	1	Hapus Giro Item	/ap-giro/item/{ap_giro_id}/{id}/delete	delete
ap-sp2d	0	2014-12-24 03:04:42.837591	1	SP2D	/ap-sp2d	read
ap-sp2d-act	0	2014-12-24 03:04:42.837591	1	SP2D Act	/ap-sp2d/act/{act}	read
ap-sp2d-add	0	2014-12-24 03:04:42.837591	1	Tambah SP2D	/ap-sp2d/add	add
ap-sp2d-edit	0	2014-12-24 03:04:42.837591	1	Edit SP2D	/ap-sp2d/{id}/edit	edit
ap-sp2d-delete	0	2014-12-24 03:04:42.837591	1	Hapus SP2D	/ap-sp2d/{id}/delete	delete
ap-spd	0	2014-12-24 03:04:42.837591	1	SPD	/ap-spd	read
ap-spd-act	0	2014-12-24 03:04:42.837591	1	SPD Act	/ap-spd/act/{act}	read
ap-spd-add	0	2014-12-24 03:04:42.837591	1	Tambah SPD	/ap-spd/add	add
ap-spd-edit	0	2014-12-24 03:04:42.837591	1	Edit SPD	/ap-spd/{id}/edit	edit
ap-spd-delete	0	2014-12-24 03:04:42.837591	1	Hapus SPD	/ap-spd/{id}/delete	delete
ap-spd-item-act	0	2015-01-07 00:29:49.485249	1	SPD Item Act	/ap-spd/item/{ap_spd_id}/act/{act}	read
ap-spd-item-add	0	2015-01-07 00:29:49.485249	1	Tambah SPD Item	/ap-spd/item/{ap_spd_id}/add	add
ap-spd-item-delete	0	2015-01-07 00:29:49.485249	1	Hapus SPD Item	/ap-spd/item/{ap_spd_id}/{id}/delete	delete
ap-report-sp2d	0	2014-12-24 03:04:42.837591	1	Report SP2D	/ap-report-sp2d	read
ap-report-sp2d-act	0	2014-12-24 03:04:42.837591	1	Report SP2D Act	/ap-report-sp2d/act/{act}	read
ap-report-real	0	2014-12-24 03:04:42.837591	1	Report Realisasi	/ap-report-real	read
ap-report-real-act	0	2014-12-24 03:04:42.837591	1	Report Realisasi Act	/ap-report-real/act/{act}	read
tu-skpd	0	2014-12-24 03:04:42.837591	1	Penatausahaan SKPD	/tu-skpd	read
ak-jurnal-skpd	0	2014-12-24 03:04:42.837591	1	JURNAL SKPD	/ak-jurnal-skpd	read
ak-jurnal-skpd-act	0	2014-12-24 03:04:42.837591	1	JURNAL SKPD Act	/ak-jurnal-skpd/act/{act}	read
ak-jurnal-skpd-add	0	2014-12-24 03:04:42.837591	1	Tambah JURNAL SKPD	/ak-jurnal-skpd/add	add
ak-jurnal-skpd-edit	0	2014-12-24 03:04:42.837591	1	Edit JURNAL SKPD	/ak-jurnal-skpd/{id}/edit	edit
ak-jurnal-skpd-delete	0	2014-12-24 03:04:42.837591	1	Hapus JURNAL SKPD	/ak-jurnal-skpd/{id}/delete	delete
ak-jurnal-skpd-item	0	2014-12-24 03:04:42.837591	1	Item Jurnal SKPD	/ak-jurnal-skpd-item	read
ak-jurnal-skpd-item-act	0	2015-01-07 00:29:49.485249	1	Item Jurnal SKPD Act	/ak-jurnal-skpd-item/{ak_jurnal_id}/act/{act}	read
ak-jurnal-skpd-item-add	0	2014-12-24 03:04:42.837591	1	Tambah Item Jurnal SKPD	/ak-jurnal-skpd-item/{ak_jurnal_id}/add	add
ak-jurnal-skpd-item-delete	0	2015-01-07 00:29:49.485249	1	Hapus Item Jurnal SKPD	/ak-jurnal-skpd-item/{ak_jurnal_id}/{id}/delete	delete
ap-invoice-skpd	0	2014-12-24 03:04:42.837591	1	Tagihan/Utang	/ap-invoice-skpd	read
ap-invoice-skpd-act	0	2014-12-24 03:04:42.837591	1	ACT Tagihan/Utang	/ap-invoice-skpd/act/{act}	read
ap-invoice-skpd-add	0	2014-12-24 03:04:42.837591	1	Tambah Tagihan/Utang	/ap-invoice-skpd/add	read
ap-invoice-skpd-edit	0	2014-12-24 03:04:42.837591	1	Edit Tagihan/Utang	/ap-invoice-skpd/{id}/edit	read
ap-invoice-skpd-delete	0	2014-12-24 03:04:42.837591	1	Hapus Tagihan/Utang	/ap-invoice-skpd/{id}/delete	read
ap-invoice-skpd-item-act	0	2014-12-24 03:04:42.837591	1	ACT Item AP Invoice	/ap-invoice-skpd/item/{ap_invoice_id}/act/{act}	read
ap-invoice-skpd-item-add	0	2014-12-24 03:04:42.837591	1	Tambah Item AP Invoice	/ap-invoice-skpd/item/{ap_invoice_id}/add	add
ap-invoice-skpd-item-edit	0	2015-01-07 00:29:49.485249	1	Edit Tagihan Item	/ap-invoice-skpd/item/{ap_invoice_id}/{id}/edit	edit
ap-invoice-skpd-item-delete	0	2014-12-24 03:04:42.837591	1	Hapus Item AP Invoice	/ap-invoice-skpd/item/{ap_invoice_id}/{id}/delete	delete
ap-spm	0	2014-12-24 03:04:42.837591	1	SPM	/ap-spm	read
ap-spm-act	0	2014-12-24 03:04:42.837591	1	SPM Act	/ap-spm/act/{act}	read
ap-spm-add	0	2014-12-24 03:04:42.837591	1	Tambah SPM	/ap-spm/add	add
ap-spm-edit	0	2014-12-24 03:04:42.837591	1	Edit SPM	/ap-spm/{id}/edit	edit
ap-spm-delete	0	2014-12-24 03:04:42.837591	1	Hapus SPM	/ap-spm/{id}/delete	delete
ap-spm-potongan-act	0	2014-12-24 03:04:42.837591	1	SPM Potongan Act	/ap-spm-potongan/act/{act}	read
ap-spm-potongan-add	0	2014-12-24 03:04:42.837591	1	Tambah SPM Potongan	/ap-spm-potongan/{ap_spm_id}/add	add
ap-spm-potongan-edit	0	2014-12-24 03:04:42.837591	1	Edit SPM Potongan	/ap-spm-potongan/{ap_spm_id}/{id}/edit	edit
ap-spm-potongan-delete	0	2014-12-24 03:04:42.837591	1	Hapus SPM Potongan	/ap-spm-potongan/{ap_spm_id}/{id}/delete	delete
ap-spp	0	2014-12-24 03:04:42.837591	1	SPP	/ap-spp	read
ap-spp-act	0	2014-12-24 03:04:42.837591	1	SPP Act	/ap-spp/act/{act}	read
ap-spp-add	0	2014-12-24 03:04:42.837591	1	Tambah SPP	/ap-spp/add	add
ap-spp-edit	0	2014-12-24 03:04:42.837591	1	Edit SPP	/ap-spp/{id}/edit	edit
ap-spp-delete	0	2014-12-24 03:04:42.837591	1	Hapus SPP	/ap-spp/{id}/delete	delete
ap-spp-item-act	0	2014-12-24 03:04:42.837591	1	ACT SPP Item	/ap-spp/item/{ap_spp_id}/act/{act}	read
ap-spp-item-add	0	2014-12-24 03:04:42.837591	1	Tambah Item SPP	/ap-spp/item/{ap_spp_id}/add	add
ap-spp-item-edit	0	2015-01-07 00:29:49.485249	1	Edit SPP Item	/ap-spp/item/{ap_spp_id}/{id}/edit	edit
ap-spp-item-delete	0	2014-12-24 03:04:42.837591	1	Hapus Item SPP	/ap-spp/item/{ap_spp_id}/{id}/delete	delete
ar-invoice-skpd	0	2014-12-24 03:04:42.837591	1	Tagihan/Piutang/Ketetapan	/ar-invoice-skpd	read
ar-invoice-skpd-act	0	2014-12-24 03:04:42.837591	1	Tagihan/Piutang/Ketetapan Act	/ar-invoice-skpd/act/{act}	read
ar-invoice-skpd-add	0	2014-12-24 03:04:42.837591	1	Tambah Tagihan/Piutang/Ketetapan	/ar-invoice-skpd/add	add
ar-invoice-skpd-edit	0	2014-12-24 03:04:42.837591	1	Edit Tagihan/Piutang/Ketetapan	/ar-invoice-skpd/{id}/edit	edit
ar-invoice-skpd-delete	0	2014-12-24 03:04:42.837591	1	Hapus Tagihan/Piutang/Ketetapan	/ar-invoice-skpd/{id}/delete	delete
ar-invoice-skpd-item-act	0	2015-01-07 00:29:49.485249	1	Piutang Item Act	/ar-invoice-skpd/item/{ar_invoice_id}/act/{act}	read
ar-invoice-skpd-item-add	0	2015-01-07 00:29:49.485249	1	Tambah Tagihan/Piutang/Ketetapan Item	/ar-invoice-skpd/item/{ar_invoice_id}/add	add
ar-invoice-skpd-item-edit	0	2015-01-07 00:29:49.485249	1	Edit Tagihan/Piutang/Ketetapan Item	/ar-invoice-skpd/item/{ar_invoice_id}/{id}/edit	edit
ar-invoice-skpd-item-delete	0	2015-01-07 00:29:49.485249	1	Hapus Tagihan/Piutang/Ketetapan Item	/ar-invoice-skpd/item/{ar_invoice_id}/{id}/delete	delete
ar-sts	0	2014-12-24 03:04:42.837591	1	STS	/ar-sts	read
ar-sts-act	0	2014-12-24 03:04:42.837591	1	STS Act	/ar-sts/act/{act}	read
ar-sts-add	0	2014-12-24 03:04:42.837591	1	Tambah STS	/ar-sts/add	add
ar-sts-edit	0	2014-12-24 03:04:42.837591	1	Edit STS	/ar-sts/{id}/edit	edit
ar-sts-delete	0	2014-12-24 03:04:42.837591	1	Hapus STS	/ar-sts/{id}/delete	delete
ar-sts-item-act	0	2015-01-07 00:29:49.485249	1	STS Item Act	/ar-sts/item/{ar_sts_id}/act/{act}	read
ar-sts-item-add	0	2014-12-24 03:04:42.837591	1	Tambah STS Item	/ar-sts/item/{ar_sts_id}/add	add
ar-sts-item-edit	0	2015-01-07 00:29:49.485249	1	Edit STS Item	/ar-sts/item/{ar_sts_id}/{id}/edit	edit
ar-sts-item-delete	0	2015-01-07 00:29:49.485249	1	Hapus STS Item	/ar-sts/item/{ar_sts_id}/{id}/delete	delete
ar-report-skpd	0	2014-12-24 03:04:42.837591	1	Laporan Pendapatan	/ar-report-skpd	read
ar-report-skpd-act	0	2014-12-24 03:04:42.837591	1	Report AR SKPD Act	/ar-report-skpd/act/{act}	read
ap-report-skpd	0	2014-12-24 03:04:42.837591	1	Laporan Belanja	/ap-report-skpd	read
ap-report-skpd-act	0	2014-12-24 03:04:42.837591	1	Report AP SKPD Act	/ap-report-skpd/act/{act}	read
p-ap-invoice-skpd	0	2014-12-24 03:04:42.837591	1	Posting Tagihan/Utang	/p-ap-invoice-skpd	view
p-ap-invoice-skpd-act	0	2014-12-24 03:04:42.837591	1	Posting Tagihan/Utang Act	/p-ap-invoice-skpd/act/{act}	read
p-ap-sp2d-skpd	0	2014-12-24 03:04:42.837591	1	Posting SP2D	/p-ap-sp2d-skpd	view
p-ap-sp2d-skpd-act	0	2014-12-24 03:04:42.837591	1	Posting SP2D Act	/p-ap-sp2d-skpd/act/{act}	read
aset	0	2014-12-24 03:04:42.837591	1	Aset	/aset	read
aset-kategori	0	2014-12-24 03:04:42.837591	1	Kategori Aset	/aset/kategori	read
aset-kategori-add	0	2014-12-24 03:04:42.837591	1	Tambah Kategori Aset	/aset/kategori/add	read
aset-kategori-edit	0	2014-12-24 03:04:42.837591	1	Edit Kategori Aset	/aset/kategori/{id}/edit	edit
aset-kategori-delete	0	2014-12-24 03:04:42.837591	1	Hapus Kategori Aset	/aset/kategori/{id}/delete	delete
aset-kategori-act	0	2014-12-24 03:04:42.837591	1	Kategori Aset Act	/aset/kategori/{act}/act	read
aset-kategori-csv	0	2014-12-24 03:04:42.837591	1	Kategori Aset CSV	/aset/kategori/{csv}/csv	read
aset-kebijakan	0	2014-12-24 03:04:42.837591	1	Kebijakan Aset	/aset/kebijakan	read
aset-kebijakan-add	0	2014-12-24 03:04:42.837591	1	Tambah Kebijakan Aset	/aset/kebijakan/add	read
aset-kebijakan-edit	0	2014-12-24 03:04:42.837591	1	Edit Kebijakan Aset	/aset/kebijakan/{id}/edit	edit
aset-kebijakan-delete	0	2014-12-24 03:04:42.837591	1	Hapus Kebijakan Aset	/aset/kebijakan/{id}/delete	delete
aset-kebijakan-act	0	2014-12-24 03:04:42.837591	1	Kebijakan Aset Act	/aset/kebijakan/{act}/act	read
aset-kebijakan-csv	0	2014-12-24 03:04:42.837591	1	Kebijakan Aset CSV	/aset/kebijakan/{csv}/csv	read
aset-mutasi	0	2014-12-24 03:04:42.837591	1	Mutasi Aset	/aset/mutasi	read
aset-mutasi-add	0	2014-12-24 03:04:42.837591	1	Tambah Mutasi Aset	/aset/mutasi/add	read
aset-mutasi-edit	0	2014-12-24 03:04:42.837591	1	Edit Mutasi Aset	/aset/mutasi/{id}/edit	edit
aset-mutasi-delete	0	2014-12-24 03:04:42.837591	1	Hapus Mutasi Aset	/aset/mutasi/{id}/delete	delete
aset-mutasi-act	0	2014-12-24 03:04:42.837591	1	Mutasi Aset Act	/aset/mutasi/{act}/act	read
aset-mutasi-csv	0	2014-12-24 03:04:42.837591	1	Mutasi Aset CSV	/aset/mutasi/{csv}/csv	read
aset-kiba	0	2014-12-24 03:04:42.837591	1	KIB A (Tanah)	/aset/kiba	read
aset-kiba-add	0	2014-12-24 03:04:42.837591	1	Tambah KIB A (Tanah)	/aset/kiba/add	add
aset-kiba-edit	0	2014-12-24 03:04:42.837591	1	Edit KIB A (Tanah)	/aset/kiba/{id}/edit	edit
aset-kiba-delete	0	2014-12-24 03:04:42.837591	1	Hapus KIB A (Tanah)	/aset/kiba/{id}/delete	delete
aset-kiba-act	0	2014-12-24 03:04:42.837591	1	KIB A (Tanah) Act	/aset/kiba/{act}/act	read
aset-kiba-csv	0	2014-12-24 03:04:42.837591	1	KIB A (Tanah) CSV	/aset/kiba/{csv}/csv	read
aset-kibb	0	2014-12-24 03:04:42.837591	1	KIB KIB B (Peralatan dan Mesin)	/aset/kibb	read
aset-kibb-add	0	2014-12-24 03:04:42.837591	1	Tambah KIB KIB B (Peralatan dan Mesin)	/aset/kibb/add	add
aset-kibb-edit	0	2014-12-24 03:04:42.837591	1	Edit KIB KIB B (Peralatan dan Mesin)	/aset/kibb/{id}/edit	edit
aset-kibb-delete	0	2014-12-24 03:04:42.837591	1	Hapus KIB KIB B (Peralatan dan Mesin)	/aset/kibb/{id}/delete	delete
aset-kibb-act	0	2014-12-24 03:04:42.837591	1	KIB KIB B (Peralatan dan Mesin) Act	/aset/kibb/{act}/act	read
aset-kibb-csv	0	2014-12-24 03:04:42.837591	1	KIB KIB B (Peralatan dan Mesin) CSV	/aset/kibb/{csv}/csv	read
aset-kibc	0	2014-12-24 03:04:42.837591	1	KIB C (Bangunan)	/aset/kibc	read
aset-kibc-add	0	2014-12-24 03:04:42.837591	1	Tambah KIB C (Bangunan)	/aset/kibc/add	add
aset-kibc-edit	0	2014-12-24 03:04:42.837591	1	Edit KIB C (Bangunan)	/aset/kibc/{id}/edit	edit
aset-kibc-delete	0	2014-12-24 03:04:42.837591	1	Hapus KIB C (Bangunan)	/aset/kibc/{id}/delete	delete
aset-kibc-act	0	2014-12-24 03:04:42.837591	1	KIB C (Bangunan) Act	/aset/kibc/{act}/act	read
aset-kibc-csv	0	2014-12-24 03:04:42.837591	1	KIB C (Bangunan) CSV	/aset/kibc/{csv}/csv	read
aset-kibd	0	2014-12-24 03:04:42.837591	1	KIB D (Jalan, jaringan dan Irigasi)	/aset/kibd	read
aset-kibd-add	0	2014-12-24 03:04:42.837591	1	Tambah KIB D (Jalan, jaringan dan Irigasi)	/aset/kibd/add	add
aset-kibd-edit	0	2014-12-24 03:04:42.837591	1	Edit KIB D (Jalan, jaringan dan Irigasi)	/aset/kibd/{id}/edit	edit
aset-kibd-delete	0	2014-12-24 03:04:42.837591	1	Hapus KIB D (Jalan, jaringan dan Irigasi)	/aset/kibd/{id}/delete	delete
aset-kibd-act	0	2014-12-24 03:04:42.837591	1	KIB D (Jalan, jaringan dan Irigasi) Act	/aset/kibd/{act}/act	read
aset-kibd-csv	0	2014-12-24 03:04:42.837591	1	KIB D (Jalan, jaringan dan Irigasi) CSV	/aset/kibd/{csv}/csv	read
aset-kibe	0	2014-12-24 03:04:42.837591	1	KIB E (Aset Lainnya)	/aset/kibe	read
aset-kibe-add	0	2014-12-24 03:04:42.837591	1	Tambah KIB E (Aset Lainnya)	/aset/kibe/add	add
aset-kibe-edit	0	2014-12-24 03:04:42.837591	1	Edit KIB E (Aset Lainnya)	/aset/kibe/{id}/edit	edit
aset-kibe-delete	0	2014-12-24 03:04:42.837591	1	Hapus KIB E (Aset Lainnya)	/aset/kibe/{id}/delete	delete
aset-kibe-act	0	2014-12-24 03:04:42.837591	1	KIB E (Aset Lainnya) Act	/aset/kibe/{act}/act	read
aset-kibe-csv	0	2014-12-24 03:04:42.837591	1	KIB E (Aset Lainnya) CSV	/aset/kibe/{csv}/csv	read
aset-kibf	0	2014-12-24 03:04:42.837591	1	KIB F (Konstruksi dalam Pengerjaan)	/aset/kibf	read
aset-kibf-add	0	2014-12-24 03:04:42.837591	1	Tambah KIB F (Konstruksi dalam Pengerjaan)	/aset/kibf/add	add
aset-kibf-edit	0	2014-12-24 03:04:42.837591	1	Edit KIB F (Konstruksi dalam Pengerjaan)	/aset/kibf/{id}/edit	edit
aset-kibf-delete	0	2014-12-24 03:04:42.837591	1	Hapus KIB F (Konstruksi dalam Pengerjaan)	/aset/kibf/{id}/delete	delete
aset-kibf-act	0	2014-12-24 03:04:42.837591	1	KIB F (Konstruksi dalam Pengerjaan) Act	/aset/kibf/{act}/act	read
aset-kibf-csv	0	2014-12-24 03:04:42.837591	1	KIB F (Konstruksi dalam Pengerjaan) CSV	/aset/kibf/{csv}/csv	read
aset-pemilik	0	2014-12-24 03:04:42.837591	1	Pemilik	/aset/pemilik	read
aset-pemilik-add	0	2014-12-24 03:04:42.837591	1	Tambah Pemilik	/aset/pemilik/add	add
aset-pemilik-edit	0	2014-12-24 03:04:42.837591	1	Edit Pemilik	/aset/pemilik/{id}/edit	edit
aset-pemilik-delete	0	2014-12-24 03:04:42.837591	1	Hapus Pemilik	/aset/pemilik/{id}/delete	delete
aset-pemilik-act	0	2014-12-24 03:04:42.837591	1	Pemilik Act	/aset/pemilik/{act}/act	read
aset-pemilik-csv	0	2014-12-24 03:04:42.837591	1	Pemilik CSV	/aset/pemilik/{csv}/csv	read
efiling	0	2014-12-24 03:04:42.837591	1	Filing	/efiling	read
efiling-admin	0	2014-12-24 03:04:42.837591	1	Admin e-Filling	/efiling/admin	read
efiling-kategori	0	2014-12-24 03:04:42.837591	1	Kategori Filing	/efiling/kategori	read
efiling-kategori-add	0	2014-12-24 03:04:42.837591	1	Tambah Kategori Filing	/efiling/kategori/add	read
efiling-kategori-edit	0	2014-12-24 03:04:42.837591	1	Edit Kategori Filing	/efiling/kategori/{id}/edit	edit
efiling-kategori-delete	0	2014-12-24 03:04:42.837591	1	Hapus Kategori Filing	/efiling/kategori/{id}/delete	delete
efiling-kategori-act	0	2014-12-24 03:04:42.837591	1	Kategori Filing Act	/efiling/kategori/{act}/act	read
efiling-kategori-csv	0	2014-12-24 03:04:42.837591	1	Kategori Filing CSV	/efiling/kategori/{csv}/csv	read
efiling-lokasi	0	2014-12-24 03:04:42.837591	1	Lokasi Filing	/efiling/lokasi	read
efiling-lokasi-add	0	2014-12-24 03:04:42.837591	1	Tambah Lokasi Filing	/efiling/lokasi/add	read
efiling-lokasi-edit	0	2014-12-24 03:04:42.837591	1	Edit Lokasi Filing	/efiling/lokasi/{id}/edit	edit
efiling-lokasi-delete	0	2014-12-24 03:04:42.837591	1	Hapus Lokasi Filing	/efiling/lokasi/{id}/delete	delete
efiling-lokasi-act	0	2014-12-24 03:04:42.837591	1	Lokasi Filing Act	/efiling/lokasi/{act}/act	read
efiling-lokasi-csv	0	2014-12-24 03:04:42.837591	1	Lokasi Filing CSV	/efiling/lokasi/{csv}/csv	read
efiling-filing	0	2014-12-24 03:04:42.837591	1	 Filing	/efiling/filing	read
efiling-filing-add	0	2014-12-24 03:04:42.837591	1	Tambah Filing	/efiling/filing/add	read
efiling-filing-edit	0	2014-12-24 03:04:42.837591	1	Edit Filing	/efiling/filing/{id}/edit	edit
efiling-filing-delete	0	2014-12-24 03:04:42.837591	1	Hapus Filing	/efiling/filing/{id}/delete	delete
efiling-filing-act	0	2014-12-24 03:04:42.837591	1	 Filing Act	/efiling/filing/{act}/act	read
efiling-filing-csv	0	2014-12-24 03:04:42.837591	1	 Filing CSV	/efiling/filing/{csv}/csv	read
efiling-file	0	2014-12-24 03:04:42.837591	1	 Daftar File	/efiling/{id}/file	read
efiling-file-upload	0	2014-12-24 03:04:42.837591	1	 Filing CSV	/efiling/{id}/file/upload	add
efiling-file-delete	0	2014-12-24 03:04:42.837591	1	Tambah Filing	/efiling/file/{id}/delete	delete
