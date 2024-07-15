from app import db
db.create_all()

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
                    return redirect(url_for('perfil'))
                elif usuario.role == 'JefeRRHH':
                    return redirect(url_for('bp.filtrar_usuarios'))
                elif usuario.role == 'PersonalRRHH':
                    return redirect(url_for('perfil_personal_rrhh'))
            else:
         
                return render_template('errores.html', usuario = usuario, username=username, password=password, tests = tests )
        
        return render_template('login.html', alerta=alerta)