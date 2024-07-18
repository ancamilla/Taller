from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from models import Usuario
from hashlib import md5


auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    print('login del auth.py')
    return render_template('login.html')

@auth.route('/login', methods=['GET', 'POST'])
def login_post():
    # login code goes here
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    hashed_password = md5(password.encode('utf-8')).hexdigest()
    usuario = Usuario.query.filter_by(rut=int(username)).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not usuario or not (usuario.password == hashed_password):
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    session['loggedin']=True
    session['user_id'] = usuario.rut
    session['username'] = usuario.username
    print(f"Usuario {username} logueado exitosamente. este mensaje es del auth.py")
    login_user(usuario, remember=remember)
                # Ejemplo de redirección basada en el rol del usuario
    if usuario.role == 'Trabajador':
                    return redirect(url_for('perfil'))
    elif usuario.role == 'JefeRRHH':
                    return redirect(url_for('bp.filtrar_usuarios'))
    elif usuario.role == 'PersonalRRHH':
                    return redirect(url_for('perfil_personal_rrhh'))
    
    
   # next_page = request.args.get('next')
    return redirect(url_for('perfil'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))