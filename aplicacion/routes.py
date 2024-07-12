from flask import render_template, request, session, redirect, url_for
from sqlalchemy import text
from hashlib import md5
from app import cursor
from models import Usuario, DatosLaborales, DatosPersonales, ContactoEmergencia, CargasFamiliares

def register_routes(app, db):
# Ruta para la página de inicio
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Ruta y vista para el login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        alerta =''
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Encriptación de la contraseña con MD5
            hashed_password = md5(password.encode('utf-8')).hexdigest()
            #cursor.execute('SELECT * FROM usuario where RUT=%s AND password=%s',(username,hashed_password))
            usuario = Usuario.query.filter_by(rut=username, password=hashed_password).first()
            tests = db.session.execute(text("SELECT username FROM usuario where RUT = 12345678"))
           # usuario = cursor.fetchall()
           # usuario = Usuario.query.filter_by(username=username).first()
            if usuario:
                session['loggedin']=True
                session['user_id'] = usuario.rut
                session['username'] = usuario.username
                print(f"Usuario {username} logueado exitosamente.")
                # Ejemplo de redirección basada en el rol del usuario
                if usuario.role == 'Trabajador':
                    return redirect(url_for('perfil_trabajador'))
                elif usuario.role == 'JefeRRHH':
                    return redirect(url_for('perfil_jefe_rrhh', next=request.endpoint))
                elif usuario.role == 'PersonalRRHH':
                    return redirect(url_for('perfil_personal_rrhh'))
            else:
         
                return render_template('errores.html', usuario = usuario, username=username, password=password, tests = tests )
        
        return render_template('login.html', alerta=alerta)
    
    @app.route('/personal_rrhh')
    def perfil_personal_rrhh():
        # Lógica para rellenar datos por PersonalRRHH
        return render_template('perfil_personal_rrhh.html')
    
        # Ruta para el perfil del trabajador
    @app.route('/perfil_trabajador')
    def perfil_trabajador():
        # Lógica para obtener y mostrar el perfil del trabajador
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        cargas_familiares = usuario.cargas_familiares
        return render_template('perfil_trabajador.html', usuario=usuario, cargas_familiares=cargas_familiares)

    @app.route('/perfil_trabajador/cargas', methods=['GET', 'POST','DELETE'])
    def listar_cargas():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        cargas_familiares = usuario.cargas_familiares
        if request.method =='GET':
            return render_template('listar_cargas.html', usuario=usuario,cargas_familiares=cargas_familiares, id=CargasFamiliares.id)
        
        elif request.method == 'POST':
            nombre = request.form.get('nombre')
            parentesco = request.form.get('parentesco')
            sexo = request.form.get('sexo')
            rut_familiar = int(request.form.get('rut'))
            RUT = int(usuario.rut)
            carga = CargasFamiliares(nombre=nombre,parentesco=parentesco,sexo=sexo,rut_familiar=rut_familiar,rut=RUT)
            db.session.add(carga)
            db.session.commit()
            cargas_familiares = usuario.cargas_familiares

            return render_template('listar_cargas.html', usuario=usuario,cargas_familiares=cargas_familiares)
        
    @app.route('/perfil_trabajador/cargas/agregar', methods=['GET', 'POST'])
    def agregar_cargas():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        cargas_familiares = usuario.cargas_familiares
        return render_template('agregar_cargas.html', usuario=usuario,cargas_familiares=cargas_familiares)
    
    @app.route('/eliminar_carga/<int:id>', methods=['DELETE'])
    def eliminar_carga(id):
        carga = CargasFamiliares.query.get(id)
        if carga:
            db.session.delete(carga)
            db.session.commit()
            return render_template('listar_cargas.html', id=carga.id)



    @app.route('/jefe_rrhh')
    def perfil_jefe_rrhh():
        # Lógica para listar trabajadores filtrados
        return render_template('perfil_jefe.html')

