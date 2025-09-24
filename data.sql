CREATE TABLE tabela1 (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(50));
CREATE TABLE tabela2 (id INT AUTO_INCREMENT PRIMARY KEY, descricao VARCHAR(100));
CREATE TABLE tabela3 (id INT AUTO_INCREMENT PRIMARY KEY, valor INT);
 
INSERT INTO tabela1 (nome) SELECT CONCAT('Nome', FLOOR(RAND() * 100)) FROM information_schema.tables LIMIT 100;
INSERT INTO tabela2 (descricao) SELECT CONCAT('Descricao', FLOOR(RAND() * 100)) FROM information_schema.tables LIMIT 100;
INSERT INTO tabela3 (valor) SELECT FLOOR(RAND() * 1000) FROM information_schema.tables LIMIT 100;