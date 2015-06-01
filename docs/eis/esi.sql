-- Function: eis.f_ar_payment_detail_aiu()

--DROP FUNCTION eis.f_ar_payment_detail_aiu();

CREATE OR REPLACE FUNCTION eis.f_ar_payment_detail_aiu()
  RETURNS trigger AS
$BODY$
declare dlast_date date;
declare ntahun integer;
BEGIN
  SELECT wells::date FROM eis.last_update limit 1 INTO dlast_date;
  IF TG_OP='INSERT' THEN
    --INISIASI TAHUN DATA YANG AKAN DIUPDATE
    ntahun = EXTRACT(year from new.tanggal);
    IF dlast_date < new.tanggal::date THEN
      update eis.last_update set wells = new.tanggal;
      -- JIKA BERGANTI BULANAN UBAH DATA BULANAN 
      IF EXTRACT(MONTH from new.tanggal)>EXTRACT(MONTH from dlast_date) OR 
        (EXTRACT(MONTH from new.tanggal)=1 AND EXTRACT(YEAR FROM new.tanggal)<EXTRACT(YEAR FROM dlast_date))THEN --Jika Tanggal 1 Januari Closing Data Tahun Lalu
          -- JIKA BERGANTI TAHUN TAHUN DI SET DULU TAHUN SEBELUMNYA 
          IF EXTRACT(MONTH from new.tanggal)=1 THEN
            ntahun = ntahun-1;
            --BUAT RECORD BARU TAHUN BERIKUTNYA
            INSERT INTO eis.wells (tahun, kode, uraian, amt_tahun, amt_bulan, amt_minggu, amt_hari, 
                   order_id, is_aktif)
            SELECT tahun+1, kode, uraian, 0, 0, 0, 0, 
                   order_id, is_aktif
            FROM eis.wells
            WHERE tahun = ntahun;

            UPDATE eis.wells set is_aktif=0, disabled=1
            WHERE tahun = ntahun;
            ntahun = ntahun+1;
          END IF; --end of tahun
          -- LAKUKAN UPDATE DATA   
          UPDATE eis.wells SET amt_tahun=amt_tahun+amt_bulan+amt_hari, amt_bulan=0, amt_hari=0
          WHERE tahun = ntahun;
        --END OF BULAN             
      ELSE  
      --UPDATE perpindahan hari
        UPDATE eis.wells SET amt_bulan=amt_bulan+amt_hari, amt_minggu=amt_minggu+amt_hari, amt_hari=0
        WHERE tahun = ntahun;
      END IF;
      
      --JIKA BERGANTI MINGGU (HARI SENIN) DATA MINGGUAN DIHAPUS
      IF EXTRACT(week FROM new.tanggal)<>EXTRACT(week FROM dlast_date) THEN
        UPDATE eis.wells SET amt_minggu=0
        WHERE tahun=ntahun;
      END IF; -- end ganti minggu
    END IF; --ganti hari
    --update data harian
    UPDATE eis.wells SET amt_hari=amt_hari+new.amount
    WHERE tahun = ntahun AND new.kode ilike kode||'%';
  END IF;  
  return new;
END
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION eis.f_ar_payment_detail_aiu()
  OWNER TO aagusti;
