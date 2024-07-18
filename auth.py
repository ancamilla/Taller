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

    # Revisa si el usuario existe
    # toma la contraseña ingresada, la hashea y compara con la almacenada en la base datos
    if not usuario or not (usuario.password == hashed_password):
        flash('Hubo un problema con su usuario/contraseña', 'danger')
        return redirect(url_for('auth.login')) # Si el usuario o la contraseña son incorrectos recarga la pagina del login

    # if the above check passes, then we know the user has the right credentials
    session['loggedin']=True
    session['user_id'] = usuario.rut
    session['username'] = usuario.username
    session['role'] = usuario.role
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