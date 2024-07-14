from flask import render_template, request, session, redirect, url_for, flash
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
            return render_template('listar_cargas.html', usuario=usuario,cargas_familiares=cargas_familiares) #Carga plantilla listar_cargas.html 
        
    @app.route('/cargas/agregar', methods=['GET', 'POST']) #El navbar en base.html llama a la funcion agregar_cargas() la cual carga el archivo agregar_cargas.html y dicho archivo se comunica con la funcion listar_cargas() (Elif 'POST')
    def agregar_cargas():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        cargas_familiares = usuario.cargas_familiares
        return render_template('agregar_cargas.html', usuario=usuario,cargas_familiares=cargas_familiares)
    
    @app.route('/perfil_trabajador/cargas/actualizar/<int:id_carga>', methods=['GET', 'POST'])
    def actualizar_cargas(id_carga):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        carga = CargasFamiliares.query.get(id_carga)
        if request.method == 'POST':
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
        else:
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



    @app.route('/jefe_rrhh')
    def perfil_jefe_rrhh():
        # Lógica para listar trabajadores filtrados
        return render_template('perfil_jefe.html')

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
            flash('Contacto añadida exitosamente', 'success')
            contactos_emergencias = usuario.contactos_emergencias #al haber una nueva carga actualiza la variable (en caso de (?) )
# (!) Hace falta agregar un metodo de validacion, especialmente rut
            return render_template('listar_contactos.html', usuario=usuario,contactos_emergencias=contactos_emergencias) #Carga plantilla listar_cargas.html 
    @app.route('/contactos_emergencias/agregar', methods=['GET', 'POST']) #El navbar en base.html llama a la funcion agregar_cargas() la cual carga el archivo agregar_cargas.html y dicho archivo se comunica con la funcion listar_cargas() (Elif 'POST')
    def agregar_contactos():
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(rut=user_id).first()
        contactos_emergencias = usuario.contactos_emergencias
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
        if contacto and (int(contacto.rut) == int(user_id)):
            return render_template('eliminar_contacto.html', id_contacto=contacto.id, contacto = contacto)
        return redirect(url_for('listar_contactos')) #El url_for('') contacto la url donde esta el metodo '' (argumento del url_for('') )
    
    @app.route('/eliminar_contacto/confirmar/<int:id>', methods=['POST', 'DELETE'])  #Actualmente este esta borrando, el argumento de @app.route() es la url, referenciada directamente en los fetch de javascript
    def eliminar_contacto(id): #La plantilla html se comunica con este metodo desde el fetch que hace en javascript y se deberia contactor una plantilla que contacto los datos del momento para borrarlos definitivamente.
        contacto = ContactoEmergencia.query.get(id) #Cargamos las cargas 
        if contacto:
            db.session.delete(contacto)
            db.session.commit()
            flash('contacto eliminado exitosamente', 'success')
            return redirect(url_for('listar_contactos'))