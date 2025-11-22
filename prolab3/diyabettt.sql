SET @aes_key = 'your_secure_key_32_bytes_long!!!';
INSERT INTO Kullanicilar (tc_kimlik, sifre, rol, dogum_tarihi, cinsiyet, eposta)
VALUES ('12345678901', AES_ENCRYPT('doktor123', @aes_key), 'Doktor', '1980-01-01', 'Erkek', 'doktor@example.com');
INSERT INTO Kullanicilar (tc_kimlik, sifre, rol, dogum_tarihi, cinsiyet, eposta)
VALUES ('98765432101', AES_ENCRYPT('hasta123', @aes_key), 'Hasta', '1990-05-15', 'Kadın', 'hasta@example.com');
INSERT INTO Hastalar (doktor_id, tc_kimlik)
VALUES (1, '98765432101');