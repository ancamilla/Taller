create database correo_yury;
use correo_yury;
CREATE TABLE Usuario (
    RUT INT PRIMARY KEY,
    DV VARCHAR(1) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL,
    CONSTRAINT chk_role CHECK (role IN ('Trabajador', 'JefeRRHH', 'PersonalRRHH'))
);
CREATE TABLE DatosPersonales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    sexo VARCHAR(10) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    RUT INT NOT NULL,
    FOREIGN KEY (RUT) REFERENCES Usuario(RUT) ON DELETE CASCADE
);
CREATE TABLE DatosLaborales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cargo VARCHAR(50) NOT NULL,
    fecha_ingreso DATE NOT NULL,
    area VARCHAR(50) NOT NULL,
    departamento VARCHAR(50) NOT NULL,
    RUT INT NOT NULL,
    FOREIGN KEY (RUT) REFERENCES Usuario(RUT) ON DELETE CASCADE
);
CREATE TABLE ContactoEmergencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    relacion VARCHAR(50) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    RUT INT NOT NULL,
    FOREIGN KEY (RUT) REFERENCES Usuario(RUT) ON DELETE CASCADE
);
CREATE TABLE CargasFamiliares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    parentesco VARCHAR(50) NOT NULL,
    sexo VARCHAR(10) NOT NULL,
    rut_familiar VARCHAR(12) NOT NULL UNIQUE,
    RUT INT NOT NULL,
    FOREIGN KEY (RUT) REFERENCES Usuario(RUT) ON DELETE CASCADE
);
CREATE TABLE ListadoTrabajadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    RUT INT NOT NULL,
    jefeRRHH_RUT INT NOT NULL,
    FOREIGN KEY (RUT) REFERENCES Usuario(RUT) ON DELETE NO ACTION,
    FOREIGN KEY (jefeRRHH_RUT) REFERENCES Usuario(RUT) ON DELETE NO ACTION
);
CREATE TABLE ModificarDatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    RUT INT NOT NULL,
    modificacion VARCHAR(255) NOT NULL,
    fecha_modificacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (RUT) REFERENCES Usuario(RUT) ON DELETE NO ACTION
);
INSERT INTO Usuario (RUT, DV, username, password, role) VALUES 
(12345678, '9', 'trabajador1', 'password1', 'Trabajador'),
(87654321, 'K', 'jefeRRHH1', 'password2', 'JefeRRHH'),
(11223344, '5', 'personalRRHH1', 'password3', 'PersonalRRHH');
-- Insert initial data into DatosPersonales table
INSERT INTO DatosPersonales (nombre_completo, sexo, direccion, telefono, RUT) VALUES 
('Juan Perez', 'Masculino', 'Direccion 123', '987654321', 12345678);

-- Insert initial data into DatosLaborales table
INSERT INTO DatosLaborales (cargo, fecha_ingreso, area, departamento, RUT) VALUES 
('Analista', '2020-01-01', 'IT', 'Desarrollo', 12345678);

-- Insert initial data into ContactoEmergencia table
INSERT INTO ContactoEmergencia (nombre, relacion, telefono, RUT) VALUES 
('Maria Lopez', 'Esposa', '987654321', 12345678);

-- Insert initial data into CargasFamiliares table
INSERT INTO CargasFamiliares (nombre, parentesco, sexo, rut_familiar, RUT) VALUES 
('Pedro Perez', 'Hijo', 'Masculino', '23456789-0', 12345678);
commit;
update Usuario set password = 'password4' where RUT = 12345678;
update Usuario set password = '6cb75f652a9b52798eb6cf2201057c73' where RUT = 87654321;
select * from usuario;
select * from listadotrabajadores;
drop table listadotrabajadores;
SELECT * FROM usuario where RUT=87654321 AND password='6cb75f652a9b52798eb6cf2201057c73';
INSERT INTO Usuario (RUT, DV, username, password, role) VALUES 
(99, '5', 'personalRRHH2', 'ac627ab1ccbdb62ec96e702f07f6425b', 'PersonalRRHH');