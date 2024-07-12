from app import db

class Usuario(db.Model):
    __tablename__ = 'Usuario'

    rut = db.Column(db.Integer, primary_key=True)
    dv = db.Column(db.String(1), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    datos_personales = db.relationship("DatosPersonales", back_populates="usuario", uselist=False,
                                    primaryjoin="Usuario.rut == DatosPersonales.rut")
    datos_laborales = db.relationship("DatosLaborales", back_populates="usuario", uselist=False)
    contacto_emergencia = db.relationship("ContactoEmergencia", back_populates="usuario", uselist=False)
    cargas_familiares = db.relationship("CargasFamiliares", back_populates="usuario", uselist=True)


    __table_args__ = (
        db.CheckConstraint("role IN ('Trabajador', 'JefeRRHH', 'PersonalRRHH')"),
    )
    def __repr__(self):
        return f'<Usuario {self.rut} - {self.username} - {self.role}>'

class DatosPersonales(db.Model):
    __tablename__ = 'DatosPersonales'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    sexo = db.Column(db.String(10), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    rut = db.Column(db.Integer, db.ForeignKey('Usuario.rut'), nullable=False)

    usuario = db.relationship("Usuario", back_populates="datos_personales")
    def __repr__(self):
        return f'<DatosPersonales {self.id} - {self.nombre_completo}>'

class DatosLaborales(db.Model):
    __tablename__ = 'DatosLaborales'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cargo = db.Column(db.String(50), nullable=False)
    fecha_ingreso = db.Column(db.String, nullable=False)
    area = db.Column(db.String(50), nullable=False)
    departamento = db.Column(db.String(50), nullable=False)
    rut = db.Column(db.Integer, db.ForeignKey('Usuario.rut'), nullable=False)

    usuario = db.relationship("Usuario", back_populates="datos_laborales")
    def __repr__(self):
        return f'<DatosLaborales {self.id} - {self.cargo}>'
class ContactoEmergencia(db.Model):
    __tablename__ = 'ContactoEmergencia'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    relacion = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    rut = db.Column(db.Integer, db.ForeignKey('Usuario.rut'), nullable=False)

    usuario = db.relationship("Usuario", back_populates="contacto_emergencia")

    def __repr__(self):
        return f'<ContactoEmergencia {self.id} - {self.nombre}>'
class CargasFamiliares(db.Model):
    __tablename__ = 'CargasFamiliares'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    parentesco = db.Column(db.String(50), nullable=False)
    sexo = db.Column(db.String(10), nullable=False)
    rut_familiar = db.Column(db.String(12), nullable=False, unique=True)
    rut = db.Column(db.Integer, db.ForeignKey('Usuario.rut'), nullable=False)

    usuario = db.relationship("Usuario", back_populates="cargas_familiares")
    def __repr__(self):
        return f'<CargasFamiliares {self.id} - {self.nombre}>'