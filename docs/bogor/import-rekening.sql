/*INSERT INTO admin.rekenings(
            id, )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 
            ?, ?, ?);
*/
COPY admin.rekenings (kode, nama, level_id, tahun, disabled, created, updated, 
           create_uid) FROM '/tmp/rekening_bogor1.csv' DELIMITER ',' HEADER CSV;
