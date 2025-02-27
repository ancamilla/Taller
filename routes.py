from flask import render_template, request, session, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user
from sqlalchemy import text
from hashlib import md5
from app import cursor
from models import Usuario, DatosLaborales, DatosPersonales, ContactoEmergencia, CargasFamiliares
import hashlib

bp = Blueprint('bp', __name__)
bp_jefe_rrhh = Blueprint('jefe_rrhh', __name__)
routes = Blueprint('routes', __name__)

def register_routes(app, db):
# Ruta para la página de inicio
    @app.route('/')
    def index():
        return render_template('index.html')

    
    @app.route('/logout')
    def logout():
    # Eliminar la sesión del usuario
        session.pop('username', None)  # Elimina el valor de 'username' de la sesión
    # O cualquier otra limpieza de sesión que necesites hacer
        return redirect(url_for('index'))  # Redirige al inicio de sesión o a la página principal
    
    @app.route('/personal_rrhh')
    @login_required
    def perfil_personal_rrhh():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        cargas_familiares = usuario.cargas_familiares
        contactos_emergencias = usuario.contacto_emergencia
        datos_personales = usuario.datos_personales
        return render_template('perfil_personal_rrhh.html', usuario=usuario, cargas_familiares=cargas_familiares, contactos_emergencias = contactos_emergencias, datos_personales = datos_personales)

        # Ruta para el perfil del trabajador
    @app.route('/perfil')
    @login_required
    def perfil():
        # Lógica para obtener y mostrar el perfil del trabajador
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('auth.login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        cargas_familiares = usuario.cargas_familiares
        contactos_emergencias = usuario.contacto_emergencia
        datos_personales = usuario.datos_personales
        return render_template('perfil.html', usuario=usuario, cargas_familiares=cargas_familiares, contactos_emergencias = contactos_emergencias, datos_personales = datos_personales)

 # Ruta para los datos personales
    @app.route('/datos_personales', methods=['GET', 'POST','DELETE'])
    @login_required
    def datos_personales():
        # Lógica para obtener y mostrar el perfil del trabajador
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        return render_template('datos_personales.html', usuario=usuario )

    @app.route('/datos_personales/actualizar/<int:rut>', methods=['GET', 'POST'])
    def actualizar_datos_personales(rut):
        # Lógica para obtener y mostrar el perfil del trabajador
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        datos_personales = DatosPersonales.query.filter_by(rut=user_id) #Como uselist:False, se debe llamar a los datos personales como usuario.datos_personales.telefono 
        if request.method == 'POST':
            usuario.datos_personales.nombre_completo = request.form.get('nombre') #Captura dato name="" desde forma en html
            usuario.datos_personales.sexo = request.form.get('sexo')
            usuario.datos_personales.direccion = request.form.get('direccion')
            usuario.datos_personales.telefono = int(request.form.get('telefono')) 
            usuario.datos_personales.RUT = int(usuario.rut)
            try:
                db.session.commit()
                flash('Datos actualizados exitosamente', 'success')
                return redirect(url_for('datos_personales'))
            except:
                db.session.rollback()
                flash('Hubo un problema actualizando los datos', 'danger')
                return "Hubo un problema actualizando los datos"
        else:
            return render_template('actualizar_datos_personales.html', usuario=usuario, datos = datos_personales )
    

    @app.route('/cargas', methods=['GET', 'POST','DELETE'])
    def listar_cargas(): #Este metodo se comunica con las plantillas html al usar (url_for{{''}} en html), en el caso de esta ruta, se comunica con agregar_cargas.html 
        user_id = session.get('user_id') #Confirma si la sesion está iniciada
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first() #Selecciona el usuario desde la base de datos filtrando por el rut
        cargas_familiares = usuario.cargas_familiares #Asigna las cargas [El contenido de la tabla CargasFamiliares cuya columna rut (es el rut del usuario/trabajador) es llave foranea con tabla Usuario] del usuario seleccionado en la linea anterio a la variable cargas_familiares
        if request.method =='GET':
            return render_template('listar_cargas.html', usuario=usuario,cargas_familiares=cargas_familiares, id_carga=CargasFamiliares.id) #Exporta estas variables al documento html
        
        elif request.method == 'POST': 
            nombre = request.form.get('nombre') #Captura dato name="" desde forma en html
            parentesco = request.form.get('parentesco')
            sexo = request.form.get('sexo')
            rut_familiar = int(request.form.get('rut')) 
            RUT = int(usuario.rut) #Como el RUT del trabajador es la llave foranea el usuario no tiene acceso a modificarlo, entonces lo exportamos directamente de la base de datos.
            carga = CargasFamiliares(nombre=nombre,parentesco=parentesco,sexo=sexo,rut_familiar=rut_familiar,rut=RUT) #Crea una nueva instancia del objeto CargasFamiliares() 
            db.session.add(carga) #dicha instancia se carga en la base datos
            db.session.commit() #commit;
            flash('Carga añadida exitosamente', 'success')
            cargas_familiares = usuario.cargas_familiares #al haber una nueva carga actualiza la variable (en caso de (?) )
# (!) Hace falta agregar un metodo de validacion, especialmente rut
#(!) Tambien hace falta un metodo para manejar los errores al agregar una carga.
            return render_template('listar_cargas.html', usuario=usuario,cargas_familiares=cargas_familiares) #Carga plantilla listar_cargas.html 
        
    @app.route('/cargas/agregar', methods=['GET', 'POST']) #El navbar en base.html llama a la funcion agregar_cargas() la cual carga el archivo agregar_cargas.html y dicho archivo se comunica con la funcion listar_cargas() (Elif 'POST')
    def agregar_cargas(): #Funcion que despues de ser llamada desde el navbar instancia los datos de la sesion y carga el html con el formulario para agregar cargas
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        cargas_familiares = usuario.cargas_familiares
        return render_template('agregar_cargas.html', usuario=usuario,cargas_familiares=cargas_familiares)
    
    @app.route('/perfil/cargas/actualizar/<int:id_carga>', methods=['GET', 'POST'])
    def actualizar_cargas(id_carga):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first() #Busca al usuario basado en la carga
        carga = CargasFamiliares.query.get(id_carga) #Se instancia dicha carga
        if request.method == 'POST': #actualizar_cargas.html se comunica con la funcion actualizar_cargas con un metodo 'POST'
            carga.nombre = request.form.get('nombre') #Captura dato name="" desde forma en html
            carga.parentesco = request.form.get('parentesco')
            carga.sexo = request.form.get('sexo')
            carga.rut_familiar = int(request.form.get('rut')) 
            carga.RUT = int(usuario.rut)
            try:
                db.session.commit()
                flash('Carga actualizada exitosamente', 'success')
                return redirect(url_for('listar_cargas'))
            except:
                flash('Hubo un problema actualizando la carga', 'danger')
                return "Hubo un problema actualizando la carga."
        else: #Si no se envia un metodo 'POST' se carga el html para llenar formulario, junto a instancias de usuario y carga.
            return render_template('actualizar_carga.html', usuario=usuario,carga = carga)
    

    @app.route('/cargas/eliminar/confirmar/<int:id_carga>', methods=['GET']) #Esta es la pagina de confirmacion
    def confirmar_eliminar_carga(id_carga): #(!) Renombrar metodo por algo que suene mas "definitivo" de confirmacion. (solo recomendacion)
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        carga = CargasFamiliares.query.get(id_carga)
        if carga and (int(carga.rut) == int(user_id)):
            return render_template('eliminar_carga.html', id_carga=carga.id, carga = carga)
        return redirect(url_for('listar_cargas')) #El url_for('') carga la url donde esta el metodo '' (argumento del url_for('') )
        
    @app.route('/eliminar_carga/confirmar/<int:id>', methods=['POST', 'DELETE'])  #Actualmente este esta borrando, el argumento de @app.route() es la url, referenciada directamente en los fetch de javascript
    def eliminar_carga(id): #La plantilla html se comunica con este metodo desde el fetch que hace en javascript y se deberia cargar una plantilla que carga los datos del momento para borrarlos definitivamente.
        carga = CargasFamiliares.query.get(id) #Cargamos las cargas 
        if carga:
            db.session.delete(carga)
            db.session.commit()
            flash('Carga eliminada exitosamente', 'success')
            return redirect(url_for('listar_cargas'))





#Aqui comienza la logica para los contactos de emergencias, imitando a cargas familiares
    @app.route('/contactos_emergencias', methods=['GET', 'POST','DELETE'])
    def listar_contactos(): #Este metodo se comunica con las plantillas html al usar (url_for{{''}} en html), en el caso de esta ruta, se comunica con agregar_cargas.html 
        user_id = session.get('user_id') #Confirma si la sesion está iniciada
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first() #Selecciona el usuario desde la base de datos filtrando por el rut
        contactos_emergencias = usuario.contacto_emergencia #Asigna las cargas [El contenido de la tabla CargasFamiliares cuya columna rut (es el rut del usuario/trabajador) es llave foranea con tabla Usuario] del usuario seleccionado en la linea anterio a la variable contactos_emergencias
        #contactos_emergencias = ContactoEmergencia.query.filter_by(rut=usuario.rut).all()  #Esta linea es util cuando el modelo esta configurado en uselist=False
        if request.method =='GET':
            return render_template('listar_contactos.html', usuario=usuario,contactos_emergencias=contactos_emergencias, id_contacto=ContactoEmergencia.id) #Exporta estas variables al documento html
        
        elif request.method == 'POST': 
            nombre = request.form.get('nombre') #Captura dato name="" desde forma en html
            relacion = request.form.get('relacion')
            telefono = request.form.get('telefono')
            RUT = int(usuario.rut) #Como el RUT del trabajador es la llave foranea el usuario no tiene acceso a modificarlo, entonces lo exportamos directamente de la base de datos.
            contacto = ContactoEmergencia(nombre=nombre,relacion=relacion,telefono=telefono,rut=RUT) #Crea una nueva instancia del objeto ContactoEmergencia() 
            db.session.add(contacto) #dicha instancia se carga en la base datos
            db.session.commit() #commit;
            flash('Contacto añadido exitosamente', 'success')
            contactos_emergencias = usuario.contacto_emergencia #al haber una nueva carga actualiza la variable (en caso de (?) )
# (!) Hace falta agregar un metodo de validacion, especialmente rut
            return render_template('listar_contactos.html', usuario=usuario,contactos_emergencias=contactos_emergencias) #Carga plantilla listar_cargas.html 
    @app.route('/contactos_emergencias/agregar', methods=['GET', 'POST']) #El navbar en base.html llama a la funcion agregar_cargas() la cual carga el archivo agregar_cargas.html y dicho archivo se comunica con la funcion listar_cargas() (Elif 'POST')
    def agregar_contactos():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        contactos_emergencias = usuario.contacto_emergencia
        return render_template('agregar_contactos.html', usuario=usuario,contactos_emergencias=contactos_emergencias)
    
    @app.route('/contactos_emergencias/actualizar/<int:id_contacto>', methods=['GET', 'POST'])
    def actualizar_contactos(id_contacto):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        contacto = ContactoEmergencia.query.get(id_contacto)
        if request.method == 'POST':
            contacto.nombre = request.form.get('nombre') #Captura dato name="" desde forma en html
            contacto.relacion = request.form.get('relacion')
            contacto.telefono = request.form.get('telefono') 
            contacto.RUT = int(usuario.rut)
            try:
                db.session.commit()
                flash('Contacto actualizado exitosamente', 'success')
                return redirect(url_for('listar_contactos'))
            except:
                flash('Hubo un problema actualizando el contacto', 'danger')
                return "Hubo un problema actualizando el contacto."
        else:
            return render_template('actualizar_contacto.html', usuario=usuario,contacto = contacto)
        
    @app.route('/contactos_emergencias/eliminar/confirmar/<int:id_contacto>', methods=['GET']) #Esta es la pagina de confirmacion
    def confirmar_eliminar_contacto(id_contacto): #(!) Renombrar metodo por algo que suene mas "definitivo" de confirmacion. (solo recomendacion)
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        contacto = ContactoEmergencia.query.get(id_contacto)
        usuario = Usuario.query.filter_by(rut = user_id)
        if contacto and (int(contacto.rut) == int(user_id)):
            return render_template('eliminar_contacto.html', id_contacto=contacto.id, contacto = contacto, usuario = usuario)
        return redirect(url_for('listar_contactos')) #El url_for('') contacto la url donde esta el metodo '' (argumento del url_for('') )
    
    @app.route('/eliminar_contacto/confirmar/<int:id>', methods=['POST', 'DELETE'])  #Actualmente este esta borrando, el argumento de @app.route() es la url, referenciada directamente en los fetch de javascript
    def eliminar_contacto(id): #La plantilla html se comunica con este metodo desde el fetch que hace en javascript y se deberia contactor una plantilla que contacto los datos del momento para borrarlos definitivamente.
        contacto = ContactoEmergencia.query.get(id) #Cargamos las cargas 
        if contacto:
            db.session.delete(contacto)
            db.session.commit()
            flash('contacto eliminado exitosamente', 'success')
            return redirect(url_for('listar_contactos'))
        

    ######################################################################

        
    @bp.route('/Personal_rrhh/agregar', methods=['GET', 'POST'])
    @login_required
    def agregar_usuario():
        user_id = session.get('user_id') #Confirma si la sesion está iniciada
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        if request.method == 'POST':
            rut = request.form.get('rut')
            dv = request.form.get('dv')
            username = request.form.get('username')
            password = request.form.get('password')  # Recuerda que debes hashear la contraseña antes de guardarla
            # Hashear la contraseña
            password_hashed = hashlib.md5(password.encode()).hexdigest()
            role = request.form.get('role')
            
            nombre_completo = request.form.get('nombre_completo')
            sexo = request.form.get('sexo')
            direccion = request.form.get('direccion')
            telefono = request.form.get('telefono')

            cargo = request.form.get('cargo')
            fecha_ingreso = request.form.get('fecha_ingreso')
            area = request.form.get('area')
            departamento = request.form.get('departamento')

            nombre_contacto = request.form.get('nombre_contacto')
            relacion_contacto = request.form.get('relacion_contacto')
            telefono_contacto = request.form.get('telefono_contacto')

            nombre_carga = request.form.get('nombre_carga')
            parentesco = request.form.get('parentesco')
            sexo_carga = request.form.get('sexo_carga')
            rut_carga = request.form.get('rut_carga')

            # Crear las instancias de los modelos
            usuario = Usuario(rut=rut, dv=dv, username=username, password=password_hashed, role=role)
            datos_personales = DatosPersonales(nombre_completo=nombre_completo, sexo=sexo, direccion=direccion, telefono=telefono, rut=rut)
            datos_laborales = DatosLaborales(cargo=cargo, fecha_ingreso=fecha_ingreso, area=area, departamento=departamento, rut=rut)

            usuario.datos_personales = datos_personales
            usuario.datos_laborales = datos_laborales

            if nombre_contacto and relacion_contacto and telefono_contacto:
                contacto_emergencia = ContactoEmergencia(nombre=nombre_contacto, relacion=relacion_contacto, telefono=telefono_contacto, rut=rut)
                usuario.contacto_emergencia = contacto_emergencia

            if nombre_carga and parentesco and sexo_carga and rut_carga:
                cargas_familiares = CargasFamiliares(nombre=nombre_carga, parentesco=parentesco, sexo=sexo_carga, rut=rut_carga, usuario_rut=rut)
                usuario.cargas_familiares.append(cargas_familiares)

            try:
                db.session.add(usuario)
                db.session.commit()
                flash('Usuario agregado exitosamente')
                return redirect(url_for('bp.listar_usuarios'))
            except Exception as e:
                db.session.rollback()
                flash('Error al agregar el usuario: ' + str(e))

        return render_template('agregar_usuario.html', usuario=usuario) #usuario para mantener la sesion iniciada. corresponde al del personal de rrhh

    @bp.route('/Personal_rrhh/actualizar/<int:rut>', methods=['GET', 'POST'])
    @login_required
    def actualizar_usuario(rut):
        usuario = Usuario.query.filter_by(rut=rut).first()
        if request.method == 'POST':
            usuario.dv = request.form.get('dv')
            usuario.username = request.form.get('username')
            usuario.password = request.form.get('password')  # Recuerda que debes hashear la contraseña antes de guardarla
            usuario.role = request.form.get('role')

            usuario.datos_personales.nombre_completo = request.form.get('nombre_completo')
            usuario.datos_personales.sexo = request.form.get('sexo')
            usuario.datos_personales.direccion = request.form.get('direccion')
            usuario.datos_personales.telefono = request.form.get('telefono')

            usuario.datos_laborales.cargo = request.form.get('cargo')
            usuario.datos_laborales.fecha_ingreso = request.form.get('fecha_ingreso')
            usuario.datos_laborales.area = request.form.get('area')
            usuario.datos_laborales.departamento = request.form.get('departamento')

            usuario.contacto_emergencia.nombre = request.form.get('nombre_contacto')
            usuario.contacto_emergencia.relacion = request.form.get('relacion_contacto')
            usuario.contacto_emergencia.telefono = request.form.get('telefono_contacto')

            usuario.cargas_familiares.nombre = request.form.get('nombre_carga')
            usuario.cargas_familiares.parentesco = request.form.get('parentesco')
            usuario.cargas_familiares.sexo = request.form.get('sexo_carga')
            usuario.cargas_familiares.rut = request.form.get('rut_carga')

            try:
                db.session.commit()
                flash('Usuario actualizado exitosamente')
                return redirect(url_for('bp.listar_usuarios'))
            except Exception as e:
                db.session.rollback()
                flash('Error al actualizar el usuario: ' + str(e))

        return render_template('actualizar_usuario.html', usuario=usuario)

    @bp.route('/Personal_rrhh/listar', methods=['GET'])
    @login_required
    def listar_usuarios():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        usuarios = Usuario.query.all()
        return render_template('listar_usuarios.html', usuarios=usuarios, usuario = usuario)
    
##############################################################3
    
    @bp.route('/jefe_rrhh/filtrar_usuarios', methods=['GET', 'POST'])
    @login_required
    def filtrar_usuarios():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        usuarios = []
         # Obtener todos los cargos, áreas y departamentos únicos de la base de datos
        cargos = db.session.query(DatosLaborales.cargo).distinct().all()
        areas = db.session.query(DatosLaborales.area).distinct().all()
        departamentos = db.session.query(DatosLaborales.departamento).distinct().all()

        # Convertir los resultados de las consultas en listas simples
        lista_cargos = [cargo[0] for cargo in cargos]
        lista_areas = [area[0] for area in areas]
        lista_departamentos = [departamento[0] for departamento in departamentos]
        if request.method == 'POST':
            sexo = request.form.get('sexo')
            cargo = request.form.get('cargo')
            area = request.form.get('area')
            departamento = request.form.get('departamento')
            buscador = request.form.get('buscador')
            query = Usuario.query.join(DatosPersonales).join(DatosLaborales)
            
            if sexo:
                query = query.filter(DatosPersonales.sexo == sexo)
            if cargo:
                query = query.filter(DatosLaborales.cargo == cargo)
            if area:
                query = query.filter(DatosLaborales.area == area)
            if departamento:
                query = query.filter(DatosLaborales.departamento == departamento)
            
            if buscador:
                query = query.filter(
                    (Usuario.rut.like(f"%{buscador}%")) |
                    (DatosPersonales.nombre_completo.like(f"%{buscador}%")) |
                    (DatosLaborales.cargo.like(f"%{buscador}%")) |
                    (DatosLaborales.area.like(f"%{buscador}%")) |
                    (DatosLaborales.departamento.like(f"%{buscador}%"))
            )
            print(query)
            usuarios = query.all()
        if request.method == 'GET' or not request.form:
            usuarios = Usuario.query.join(DatosPersonales).join(DatosLaborales).all()    

        return render_template('jefe_rrhh.html',usuario = usuario, usuarios=usuarios, lista_cargos=lista_cargos, lista_areas=lista_areas, lista_departamentos=lista_departamentos)
