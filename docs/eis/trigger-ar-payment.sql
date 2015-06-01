-------------------------------------------------------------
-- PAYMENT
-------------------------------------------------------------

CREATE OR REPLACE FUNCTION eis.f_ar_payment_detail_biu()
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


CREATE TRIGGER t_ar_payment_detail_biu
  BEFORE INSERT OR UPDATE
  ON eis.ar_payment_detail
  FOR EACH ROW
  EXECUTE PROCEDURE eis.f_ar_payment_detail_biu();

-------------------------------------------------------------
-- INVOICE
-------------------------------------------------------------
CREATE OR REPLACE FUNCTION eis.f_ar_invoice_detail_biu()
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


CREATE TRIGGER t_ar_invoice_detail_biu
  BEFORE INSERT OR UPDATE
  ON eis.ar_invoice_detail
  FOR EACH ROW
  EXECUTE PROCEDURE eis.f_ar_invoice_detail_biu();

