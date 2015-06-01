-- Function: eis.f_ar_payment_detail_aiu()

-- DROP FUNCTION eis.f_ar_payment_detail_aiu();

CREATE OR REPLACE FUNCTION eis.f_ar_payment_detail_aiu()
  RETURNS trigger AS
$BODY$

BEGIN
  IF TG_OP='INSERT' OR TG_OP='UPDATE' THEN
     new.tahun  = EXTRACT(YEAR FROM new.tanggal);
     new.bulan  = EXTRACT(MONTH FROM new.tanggal);
     new.hari   = EXTRACT(DAY FROM new.tanggal);
     new.minggu = EXTRACT(week FROM new.tanggal);
  END IF;
  return new;
END
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
--ALTER FUNCTION eis.f_ar_payment_detail_aiu()
--  OWNER TO aagusti;

/*
update eis.ar_payment_detail 
   set bulan = extract(month from tanggal),
       tahun = extract(year from tanggal),
       hari = extract(day from tanggal),
       minggu = extract(week from tanggal)
       */
