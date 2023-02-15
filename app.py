from enum import unique
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login.utils import login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_login import LoginManager, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

#configuration
app = Flask (__name__)
app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/almacenes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)


#El modelo User que permite crear la tabla usuario y guardar los datos
class User (db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column (db.Integer, primary_key = True)
    nombre = db.Column (db.String(), nullable = False)
    apellido = db.Column (db.String(), nullable = False)
    edad = db.Column (db.Integer, nullable = False)
    sexo = db.Column (db.String(), nullable = False)
    usuario= db.Column (db.String(), unique = True, nullable = False)
    contraseña = db.Column (db.String(), nullable = False)
    date_created = db.Column (db.Date, nullable = False)
    #date_modified = db.Column(db.String(), nullable = False)
    almacenes = db.relationship('Almacen', backref='usuario')

    def __repr__(self):
        return f'Usuario: id = {self.id}, nombre = {self.nombre}, apellido = {self.apellido}, edad = {self.edad}'

    #Set_password hashea la contraseña dada por el usuario.
    def set_password(self, contraseña):
        self.contraseña = generate_password_hash(contraseña)

    #Check_password compara la contraseña dada con la contraseña haseada y guardada en la base de datos
    def check_password (self, contraseña):
        return check_password_hash(self.contraseña, contraseña)

    @staticmethod
    def get_by_id(id):
        return User.query.get(id)

    @staticmethod
    def get_by_usuario(usuario):
        return User.query.filter_by(usuario=usuario).first()


#Entidad de los alamcenes
class Almacen(db.Model):
    __tablename__ = 'almacenes'
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    nombre= db.Column(db.String(), unique=True, nullable=False)
    date_created=db.Column(db.String(), nullable=False)
    date_modified=db.Column(db.String(), nullable=False)
    productos=db.relationship('Producto', backref='almacen')

    def __repr__(self) -> str:
        return f'id: {self.id}, Nombre: {self.nombre}, Dueño:{self.user_id}'

    #Método para obtener el almacén
    @staticmethod
    def get_almacen_by_id(user_id):
        return Almacen.query.filter_by(user_id=user_id).first()

#Entidad de los Productos
class Producto(db.Model):
    __tablename__='productos'
    id=db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(), nullable=False)
    almacen_id = db.Column(db.Integer, db.ForeignKey('almacenes.id', ondelete='CASCADE'), nullable=False)
    descripción = db.Column(db.Text, nullable=False)
    tipo= db.Column(db.String(), nullable=False)
    cantidad=db.Column(db.Integer, nullable=False)
    fecha_ingreso=db.Column(db.Date, nullable=False)
    
    def __repr__(self) -> str:
        return f'id: {self.id}, nombre: {self.nombre}, tipo_ {self.tipo}, almacen_id: {self.almacen_id}'

    @staticmethod
    def get_producto_by_nombre(nombre):
        return Producto.query.filter_by(nombre=nombre).first()

db.create_all()

#controlles
@app.route('/')
def index ():
    return render_template('index.html' , usuarios = User.query.all())

#Se genera la calse load_user que manejará los logins de los usuarios
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@app.route("/registro", methods=['GET', 'POST'])
def registro():
    if request.method =='POST':
        response={}
        vacios=False #variable que nos permite saber si se han dejado inputs vacíos en el formulario
        user_id=None
        try:
            #Se obtienen los datos ingresados por el usuario
            registro=request.get_json()
            nombre=registro['nombre']
            apellido=registro['apellido']
            edad=registro['edad']
            sexo=registro['sexo']
            usuario=registro['usuario']
            contraseña=registro['contraseña']
            date_created = datetime.date.today()
            nombre_almacen=registro['nombre_almacen']
            #Se revisa si hay inputs vacíos
            i=0
            for k in registro:
                if registro[k]=='':
                    print(i)
                    response['casilla'+str(i)]=k
                    vacios=True
                    print('vacios', vacios)
                    i+=1
                    
            #En caso de no haber vacíos se manda la información a la base de datos para que lo guarde
            if not vacios:
                usuario = User(nombre=nombre, apellido=apellido, edad=edad, sexo=sexo, usuario=usuario, date_created=date_created)
                usuario.set_password(contraseña)
                db.session.add(usuario)
                db.session.commit()
                almacen=Almacen(user_id=usuario.id,nombre=nombre_almacen,date_created=date_created, date_modified=date_created)
                db.session.add(almacen)
                db.session.commit()
                user_id=usuario.id
                login_user(usuario, remember=True)

        except Exception as e:
            #En caso de haber algún espacio vacío se le asigna True a vacios y se hace un rollback
            print(e)
            vacios=True
            db.session.rollback()
            print(response)

        finally:
            db.session.close()
        
        
        if vacios:
            #En caso de haber vacíos se envía una respuesta json al front-end
            return jsonify(response)
        else:
            #En caso de no haber vacíos se le dice al front-end que debe haber una redirección.
            return redirect(url_for('operarios', user_id=user_id))

    #En caso la solicitud que se haga sea de tipo GET sólo pedimos que se renderice el html de la vista.
    return render_template('registro.html')


@app.route("/login/", methods=['GET', 'POST'])
def login():
    datos={}
    user_id=None
    #Con current_user se verifica si ya hay un usuario logueado.
    if current_user.is_authenticated:
        user_str=str(current_user)
        index=user_str.find(',')
        user_id=int(user_str[14:index])
        #Se le dice al front-end que debe haber una redirección y se la manda la nueva url.
        return redirect(url_for('operarios', user_id=user_id))

    if request.method=='POST':
        data = request.get_json()
        usuario=data['usuario']
        contraseña=data['contraseña']
        remember_me=data['remember_me']
        recordar=False
        
        if remember_me == 'recordarme':
            recordar = True
        
        #Se busca al usuario que quiere loguearse
        user = User.get_by_usuario(usuario)
        if user is not None:
            #Si existe dicho usuario se checkea el password
            if user.check_password(contraseña):
                user_id=user.id
                #Se loguea al usuario
                login_user(user, recordar)
                #Se le dice al front-end que debe haber una redirección
                return redirect(url_for('operarios', user_id=user_id))
            else:
                #En caso la contraseña no sea correcta se le devuelve al front-end una respuesta en json que contiene el error.
                datos['error']='contraseña_incorrecta'
                return jsonify(datos)
        else:
            #En caso el usuario no exista se le devuelve al front-end una respuesta en json que contiene el error.
            datos['error']='usuario_incorrecto'
            return jsonify(datos)

    #En caso la solicitud sea de tipo GET sólo pedimos que se renderice el html de la vista.
    return render_template('login.html')

#Creamos el controlador que nos muestra la página principal para cada usuario y que le permite crear nuevos almacenes
@app.route('/operario/<int:user_id>/creacion/', methods=['GET', 'POST'])
@login_required
def operarios(user_id):
    #Se obtiene el usuario que está en sesión
    user=User.get_id(user_id)
    response={}
    if request.method == 'POST':
        try:
            vacios=False
            data=request.get_json()
            nombre_almacen=data['nombre_almacen']
            date_created=datetime.date.today()
            #Se genera el objeto almacen 
            almacen=Almacen(user_id=user_id,nombre=nombre_almacen,date_created=date_created, date_modified=date_created)

            for k in data:
                if data[k] == '':
                    vacios=True
                    response['vacios']=vacios
                    break

            if not vacios:
                db.session.add(almacen)
                db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify(response)
    return render_template('operario.html', user=user)

@app.route('/operario/almacen/<int:almacen_id>/direccionar/')
def direccionar_operario_almacen(almacen_id):
    return redirect(url_for('almacenes_admin', almacen_id=almacen_id))

@app.route('/operario/almacen/<almacen_id>/delete_almacen', methods = ['DELETE'])
def delete_almacen(almacen_id):
    response = {}
    try:
        almacen = Almacen.query.get(almacen_id)
        db.session.delete(almacen)
        db.session.commit()
        response['success']=True
    except:
        db.session.rollback()
        response['success']=False
        
    finally:
        db.session.close()
    return jsonify(response)

@app.route("/operario/almacen/", methods=['GET', 'POST'], defaults={'almacen_id':None})
@app.route("/operario/almacen/<int:almacen_id>/", methods=['GET', 'POST'])
@login_required
def almacenes_admin(almacen_id):
    #Se obtiene el almacen del usuario logueado
    almacen=Almacen.query.get(almacen_id)
    if request.method =='POST':
        response={}
        vacios = False
        try:
            datos=request.get_json()
            nombre=datos['nombre']
            descripción=datos['descripción']
            tipo=datos['tipo']
            cantidad=datos['cantidad']
            fecha_ingreso=datetime.date.today()
            print(fecha_ingreso)
            producto=Producto(nombre=nombre, almacen=almacen, tipo=tipo, descripción=descripción, cantidad=cantidad, fecha_ingreso=fecha_ingreso)
            date_modified=fecha_ingreso
            almacen.date_modified=date_modified
            for k in datos:
                if datos[k] == '':
                    vacios=True
                    response['vacios']=vacios
                    break
            if not vacios:
                db.session.add(producto)
                producto = Producto.get_producto_by_nombre(nombre)
                response['id']=producto.id
                db.session.commit()

        except Exception as e:
            print(e)
            db.session.rollback()

        finally:
            db.session.close()
        
        return jsonify(response)
    return render_template('almacen.html', almacen=almacen)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#run
if __name__ == '__main__':
    app.run(debug = True, port = 5000)


