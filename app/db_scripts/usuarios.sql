CREATE TABLE usuarios(
    user_name VARCHAR(255) PRIMARY KEY NOT NULL,
    nombre BLOB NOT NULL,
    apellidos BLOB NOT NULL,
    email BLOB NOT NULL,
    telefono BLOB NOT NULL,
    salt BLOB NOT NULL,
    encryped_pass BLOB NOT NULL,
    permiso CHAR(1) NOT NULL,
    public_key BLOB
);


CREATE TABLE papers(
    user_name VARCHAR(255) NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    cuerpo BLOB NOT NULL,
    salt BLOB NOT NULL,
    nonce BLOB NOT NULL,
    PRIMARY KEY (user_name, titulo),
    FOREIGN KEY (user_name) REFERENCES usuarios(user_name)
);

CREATE TABLE solicitudes(
    user_name VARCHAR(255) PRIMARY KEY NOT NULL,
    rechazada TINYINT(1) NOT NULL,
    FOREIGN KEY (user_name) REFERENCES usuarios(user_name)
);