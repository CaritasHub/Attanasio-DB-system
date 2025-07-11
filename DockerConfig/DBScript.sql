--⚙️ DBscript MySQL – Versione 1.3

-- Rimozione e creazione del database
DROP DATABASE IF EXISTS Attanasio;
CREATE DATABASE Attanasio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE Attanasio;

-- TABELLA Specialista
CREATE TABLE Specialista (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  cognome VARCHAR(100) NOT NULL,
  email VARCHAR(255),
  telefono VARCHAR(20),
  indirizzo VARCHAR(255),
  ruolo VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- TABELLA Utente (con data_arresto)
CREATE TABLE Utente (
  id INT AUTO_INCREMENT PRIMARY KEY,
  operatore_id INT NOT NULL
    REFERENCES Specialista(id),
  data_inserimento DATE NOT NULL,
  riferimento VARCHAR(20) UNIQUE NOT NULL,
  nome VARCHAR(100) NOT NULL,
  cognome VARCHAR(100) NOT NULL,
  codice_fiscale CHAR(16) UNIQUE NOT NULL,
  sesso CHAR(1) CHECK (sesso IN ('M','F','O')),
  data_nascita DATE,
  luogo_nascita VARCHAR(100),
  telefono VARCHAR(20),
  email VARCHAR(255),
  data_arresto DATE,
  cpa VARCHAR(100),
  primo_ascolto DATE,
  consenso_data DATE,
  consenso_operatore_id INT
    REFERENCES Specialista(id),
  consenso_ambito VARCHAR(100),
  note TEXT,
  religione VARCHAR(100),
  stato_civile VARCHAR(50),
  numero_conviventi SMALLINT,
  ha_figli BOOLEAN DEFAULT FALSE,
  cittadinanza VARCHAR(100),
  possesso_permesso BOOLEAN DEFAULT FALSE,
  permesso_scadenza DATE,
  permesso_motivo VARCHAR(255),
  anno_ingresso INT,
  provincia_residenza CHAR(2),
  comune_residenza VARCHAR(100),
  indirizzo_residenza VARCHAR(255),
  cap CHAR(5),
  dimora_tipo VARCHAR(50),
  provincia_domicilio CHAR(2),
  comune_domicilio VARCHAR(100),
  indirizzo_domicilio VARCHAR(255),
  possesso_mezzo BOOLEAN DEFAULT FALSE,
  mezzo VARCHAR(100),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- TABELLA Afferenza (Utente ↔ Specialista)
CREATE TABLE Afferenza (
  utente_id INT NOT NULL
    REFERENCES Utente(id) ON DELETE CASCADE,
  specialista_id INT NOT NULL
    REFERENCES Specialista(id) ON DELETE CASCADE,
  ruolo VARCHAR(100) NOT NULL,
  data_inizio DATE NOT NULL,
  data_fine DATE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (utente_id, specialista_id, data_inizio)
);

-- TABELLA Sede
CREATE TABLE Sede (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  indirizzo VARCHAR(255),
  comune VARCHAR(100),
  provincia CHAR(2),
  cap CHAR(5),
  telefono VARCHAR(20),
  email VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- TABELLA Provvedimento
CREATE TABLE Provvedimento (
  id INT AUTO_INCREMENT PRIMARY KEY,
  utente_id INT NOT NULL
    REFERENCES Utente(id) ON DELETE CASCADE,
  sede_id INT NOT NULL
    REFERENCES Sede(id) ON DELETE RESTRICT,
  tipo ENUM('Volontariato', 'LPU', 'Messa alla prova') NOT NULL,
  data_inizio DATETIME NOT NULL,
  data_fine DATETIME NOT NULL,
  ore_minime INT,
  giorni_minimi INT,
  polizza_inail VARCHAR(50),
  stato ENUM('Attivo','Sospeso','Concluso') NOT NULL DEFAULT 'Attivo',
  note TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Vincolo per polizza INAIL obbligatoria
ALTER TABLE Provvedimento
  ADD CONSTRAINT chk_inail_required
    CHECK (
      (tipo IN ('LPU','Messa alla prova') AND polizza_inail IS NOT NULL)
      OR
      (tipo = 'Volontariato')
    );

-- Table for login
CREATE TABLE Users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email VARCHAR(255),
  role ENUM('founder','editor','viewer') NOT NULL DEFAULT 'viewer'
);

CREATE TABLE AccessLog (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
  ip VARCHAR(45),
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE EventLog (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
  event TEXT,
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ColumnConfig (
  id INT AUTO_INCREMENT PRIMARY KEY,
  table_name VARCHAR(255) NOT NULL,
  column_name VARCHAR(255) NOT NULL,
  highlight BOOLEAN NOT NULL DEFAULT FALSE,
  visible BOOLEAN NOT NULL DEFAULT TRUE,
  display_order INT DEFAULT 0,
  UNIQUE KEY table_col (table_name, column_name)
);

-- Default admin user
INSERT INTO Users (username, password_hash, role) VALUES ('admin', 'scrypt:32768:8:1$NlPZbR5e1kOfJbDC$6540ed8260096c5640a9101e65ecd71639c7d2e83c9ac4059f250e7001a24253074ffdac0ded2c3a805ee07664b771a5016259f84194ddcf825fa9d70c6c2da8', 'founder');

