from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///telefonos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'H1q2w3e4r.'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable = False)

    def __repr__(self):
        return f'<User {self.name} {self.email}>'

class Repuestos(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    marca = db.Column(db.String(100), nullable = False)
    modelo = db.Column(db.String(100), nullable = False)
    repuesto = db.Column(db.String(100), nullable = False)
    precio = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f'<Repuestos {self.marca} {self.modelo} {self.repuesto} {self.precio}>'
    

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/resultado', methods=['GET', 'POST'])
def resultado():
    if request.method == 'POST':
        busqueda = request.form['buscar']
        resultado = Repuestos.query.filter(Repuestos.modelo.like('%' + busqueda + '%' )).all() 
        if resultado:
            return render_template('resultado.html', resultado=resultado)
        else:
            return render_template('resultado.html', mensaje='No se encontraron resultados')
    return redirect(url_for('index'))


@app.route('/iniciar_sesion')
def v_inicio():
    return render_template('login.html')

@app.route('/iniciar_sesion', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'
            return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('index'))
    user_count = db.session.query(User).count()
    cantidad_repuestos = db.session.query(Repuestos).count()
    return render_template('dashboard.html', user_count = user_count, cantidad_repuestos = cantidad_repuestos)

# crud usuarios y telefonos creadas

@app.route('/usuarios')
def v_usuarios():
    if not session.get('user_id'):
        return redirect(url_for('index'))
    user = User.query.all()
    return render_template('usuarios.html', user = user)

@app.route('/add', methods=['POST'])
def add_user():
    if not session.get('user_id'):
        return redirect(url_for('index'))
    name = request.form['name'].strip()
    email = request.form['email'].strip()
    password = request.form['password'].strip()
    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('v_usuarios'))

@app.route('/editar_user/<int:id>')
def editar_user(id):
    if not session.get('user_id'):
        return redirect(url_for('index'))
    user = User.query.get(id)
    return render_template('editar_usuario.html', user = user)


@app.route('/editar_usuario/<int:id>', methods=['GET','POST'])
def editar_usuario(id):
    if not session.get('user_id'):
        return redirect(url_for('index'))
    user = User.query.get(id)
    if request.method == 'POST':
        user.name = request.form.get('name').strip()
        user.email = request.form.get('email').strip()
        user.password = request.form.get('password').strip()
        db.session.commit()
        return redirect(url_for('v_usuarios'))
    return render_template('editar_usuario.html')

@app.route('/eliminar_usuario/<int:id>')
def eliminar_usuario(id):
    if not session.get('user_id'):
        return redirect(url_for('index'))
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('v_usuarios'))


@app.route('/repuestos')
def repuestos():
    if not session.get('user_id'):
        return redirect(url_for('index'))
    repuestos = Repuestos.query.all()
    return render_template('rep/repuestos.html', repuestos = repuestos)

@app.route('/agregar_repuesto', methods=['GE', 'POST'])
def agregar_repuesto():
    if not session.get('user_id'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        modelo = request.form['modelo'].strip()
        marca = request.form['marca'].strip()
        repuesto = request.form['repuesto'].strip()
        precio = request.form['precio'].strip()
        new_repuesto = Repuestos(modelo=modelo, marca=marca, repuesto=repuesto, precio=precio)
        db.session.add(new_repuesto)
        db.session.commit()
        return redirect(url_for('repuestos'))
    return render_template('rep/agregar_repuesto.html')


@app.route('/v_editar/<int:id>')
def v_editar(id):
    if not session.get('user_id'):
        return redirect(url_for('index'))
    repuesto = Repuestos.query.get(id)
    return render_template('rep/editar_repuestos.html', repuesto = repuesto)

@app.route('/editar_repuesto/<int:id>', methods=['GET', 'POST'])
def editar_repuesto(id):
    if not session.get('user_id'):
        return redirect(url_for('index'))
    repuesto = Repuestos.query.get(id)
    if request.method == 'POST':
        repuesto.modelo = request.form.get('modelo').strip()
        repuesto.marca = request.form.get('marca').strip()
        repuesto.repuesto = request.form.get('repuesto').strip()
        repuesto.precio = request.form.get('precio').strip()
        db.session.commit()
        return redirect(url_for('repuestos'))
    return render_template('rep/editar_repuestos.html', repuesto = repuesto)

@app.route('/eliminar_repuesto/<int:id>')
def eliminar_repuesto(id):
    if not session.get('user_id'):
        return redirect(url_for('index'))
    repuesto = Repuestos.query.get(id)
    db.session.delete(repuesto)
    db.session.commit()
    return redirect(url_for('repuestos'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))





    