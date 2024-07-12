from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from aplicacion.app.modelsssss import Usuario, DatosPersonales, DatosLaborales, ContactoEmergencia, CargasFamiliares, ListadoTrabajadores, ModificarDatos

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/usuarios')
def usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@bp.route('/add_usuario', methods=['GET', 'POST'])
def add_usuario():
    if request.method == 'POST':
        RUT = request.form['RUT']
        DV = request.form['DV']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        new_usuario = Usuario(RUT=RUT, DV=DV, username=username, password=password, role=role)
        db.session.add(new_usuario)
        db.session.commit()
        return redirect(url_for('main.usuarios'))
    return render_template('add_usuario.html')

# Add similar routes for DatosPersonales, DatosLaborales, etc.
