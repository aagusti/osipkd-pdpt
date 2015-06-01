UPDATE admin.rekenings set parent_id=(select id from admin.rekenings b
        where b.level_id=rekenings.level_id-1 and rekenings.kode like b.kode||'%');
/*
SELECT id, kode, created, updated, create_uid, update_uid, nama, tahun, 
       level_id, parent_id, disabled, 
       (select id from admin.rekenings b
        where b.level_id=rekenings.level_id-1 and rekenings.kode like b.kode||'%')
  FROM admin.rekenings
  order by rekenings.kode;
||'%' like 
s
osipkd(>     where b.level_id=rekenings.level_id-1 and b.kode||'' like admin.rekenings.kode);
*/