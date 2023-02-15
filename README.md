# Nombre del Proyecto

<img src="/img/GestionaApp.jpg" alt="Logo"/>

## Integrantes:
- Kevin Abraham Huaman Vega
- Sebastián Loza Mendoza
- Rubén Aaron Coorahua Peña
- Renzo Fernandez
## Descripción del proyecto:

<img src="/img/Gestiona.jpg" alt="Logo"/>

**Gestiona App** consiste en una página web que simule un gestor de almacenes, es decir, que permiteque los usuarios puedan tener un manejo de sus almacenes, lo que tienen allí, lo que sale de allí, lo que ellos ingresan, etc., desde nuestra página web. La página también permite que usuarios que no sean dueños de los alamcenes que se tienen registrados puedan ingresar, pero como clientes, es decir, este tipo de usuarios podrán acceder a los almacenes para comprar o pedir información sobre los materiales o productos que los usuarios dueños tengan en sus alamcenes y que permiten que sean visibles al público general. Para esto la página se encargará de registrar a las personas que ingresen a la misma, ya que deberán que tener una cuenta y dependiendo del tipo de cuenta podrán ingresar con un rol u otro.

### Objetivos Principales:

### Mision:
Hacer sencilla la gestión de almacenes. 

### Vision:
Ser la app más importante y utilizada para la gestión de almacenes a nivel mundial.

## Librerías usadas

### Flask:
**Flask** es un *microframework* que está escrito en python y nos ayuda a poder crear un servidor para páginas web con python. **Flask** funciona bajo el patrón *MVC* (Modelo Vista Controlador) y nos presta muchas funcionalidades para nuestra página web. También te da la opción de agregarle muchas funcionalidades con extensiones o plugins que, si bien no vienen integradas con Flask, las puedes integrar externamente y seguir trabajando con el mismo Flask pero con más funcionalidades.  Una de estas extensiones es SQLAlchemy. Puedes buscar más información acerca de [Flask](https://flask.palletsprojects.com/en/2.1.x/) en su página oficial.
### SQLAlchemy:
Esta es la ORM (*Object Relational Mapper)* que se usa en Python para poder trabajar desde python e interactuar con nuestra base de datos. Es muy flexible con SQL, es decir, que nos permite usar cualquier dialecto de SQL, ya sea **Postgres**, **MySQL**, **SQLLite**, etc. Para más información puedes visitar la página de [SQLAlchemy](https://www.sqlalchemy.org/).
### Werkzeug:
Werkzeug es una colección de librerias que se pueden usar para crear una aplicación web compatible con WSGI (Web Server Gateway Interface) en Python.Se necesita un servidor WSGI (Web Server Gateway Interface) para las aplicaciones web de Python, ya que un servidor web no puede comunicarse directamente con Python. WSGI es una interfaz entre un servidor web y una aplicación web hecha en Python. Werkzeug proporciona la siguiente funcionalidad (que utiliza Flask):
- Procesamiento de solicitudes
- Manejo de respuestas
- Enrutamiento de URL
- software intermedio
- Utilidades HTTP
- Manejo de excepciones
Para más información puede revisar la documentacion de [Werkzeug](https://werkzeug.palletsprojects.com/en/2.1.x/).
### Jinja
Jinja es un motor de plantillas rápido, expresivo y extensible. Los marcadores de posición especiales en la plantilla permiten escribir código similar a la sintaxis de Python. Luego, se pasan datos a la plantilla para renderizar el documento final.Flask utiliza jinja2 para generar documentos HTML válidos de una manera muy sencilla y eficiente. Mayor informacion en [Jinja](https://jinja.palletsprojects.com/en/3.1.x/).
### Api GOOGLE FONTS
Son las fuentes utilizadas para el diseño de letras en las plantillas css.
## Modelos  
### Class User()
El modelo User que permite crear la tabla usuario y guardar los datos(_tablename_="usuarios"), se pasan mediante db=SQLalchemy(app)
La tabla creada cuenta con las siguientes columnas de datos:
- id: integer, primary_key
- nombre: string
- apellido : string
- edad: integer
- sexo: string
- usuario: string, unique
- contraseña: string
- data_created: Date
- almacenes: relationship("Almacen")
### Class Almacen()
El modelo o clase Almacen crea la tabla almacenes(_tablename_="almacenes"), la cual esta relaciona con la primera instancia User()
La tabla creada cuenta con las siguientes columnas de datos:
- id: integer, primary_key
- user_id: integer, foreignKey("usuarios.id")
- nombre: string, unique
- descripcion: text
- capacidad: integer
- data_created: Date
- data_modified: Date
- productos: relationship("Producto")
### Class Producto()
El modelo o clase Producto crea la tabla productos(_tablename_="productos"), la cual tiene una relacion uno a varios con la instancia Almacen()
La tabla creada cuenta con las siguientes columnas de datos:
- id: integer, primary_key
- nombre: string, unique
- almacens_id: integer, foreignKey
- descripcion: text
- tipo: string
- cantidad: integer
- fecha_ingreso: Date.

## Controladores
### @app.route("/")
def index() Nos dirige al index principal o landing page de la pagina
### @login_manger.user_loader
def load_user() Se genera la clase load user la cual maneja los logins de los usuarios
### @app.route("/registro")
def registro() El registro en la pagina web por primera vez, se hace atraves de 2 metodos("GET","POST") 
Si el metodo request es igual a **POST**: 
Se crea el dicc response y la variable vacios=False(variable que nos permite saber si se han dejado inputs vacíos en el formulario)

Empieza con un try: donde se obtienen los datos ingresados por el usuario:

            registro=request.get_json()
            nombre=registro['nombre']
            apellido=registro['apellido']
            edad=registro['edad']
            sexo=registro['sexo']
            usuario=registro['usuario']
            contraseña=registro['contraseña']
            date_created = datetime.date.today()
            
Luego se realiza un "for" dentro de **registro[]** para revisar si existen inputs vacíos.En caso de no haber vacíos se manda la información a la base de datos para que lo guarde.En caso de haber algún espacio vacío se le asigna True a vacios y se hace un rollback. 

En cuanto al front-end, en caso de haber vacíos se envía una respuesta json(return jsonify(response)) y en caso de no haber vacíos se le dice al front-end que debe haber una redirección(**return redirect(url_for('operarios', user_id=user_id))**).

Si el metodo request es igual a **GET**, solo se renderiza el html de la vista.
### @app.route("/login/")
def(login) Para el login, el servidor verificara si ya existe un usuario logueado anteriormente:


            if current_user.is_authenticated:
            user_str = str(current_user)
            index = user_str.find(',')
            user_id = int(user_str[14:index])
            return redirect(url_for('operarios', user_id=user_id))
            
El return le dice al front-end que debe haber una redirección y se la manda la nueva url donde encontrara sus almacenes.

Si el metodo request es igual a Post, se busca al usuario que quiere loguearse:

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
                
Si el metodo request es igual a **GET**, solo se renderiza el html de la vista Login.

### @app.route('/operario/<int:user_id>/creacion/'
Creamos el controlador que nos muestra la página principal para cada usuario y que le permite crear nuevos almacenes

            #Se obtiene el usuario que está en sesión
            user=User.get_by_id(user_id)
            response={}
            if request.method == 'POST':
              try:
                        vacios = False
                        data = request.get_json()
                        nombre_almacen = data['nombre']
                        descripcion = data['descripcion']
                        capacidad = data['capacidad']
                        date_created = datetime.date.today()
                        #Se genera el objeto almacen
                        almacen = Almacen(
                            user_id = user_id,
                            nombre = nombre_almacen,
                            descripcion = descripcion,
                            capacidad = capacidad,
                            date_created = date_created,
                            date_modified = date_created)
                            
                            
El metodo Post obtiene la data por request.get_json() y genera un objeto almacen. Verifica que no haya espacios vacio para agregarlo a la tabla y comitearlo.

### @app.route('/operario/almacen/<int:almacen_id>/direccionar/')
            def direccionar_operario_almacen(almacen_id):
            return redirect(url_for('almacenes_admin', almacen_id=almacen_id))
Es el controlador, para que atraves de un boton en el html, podamos acceder a editar el almacen creado.

##@app.route('/operario/almacen/<almacen_id>/delete_almacen', methods = ['DELETE'])

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
                
Mediante el controlador delete, en el front-end podremos implementar un boton para eliminar de la tabla los almacenes que ya no queramos usar, tambien se eliminan de la base de datos.

### @app.route('/logout')

            def logout():
                logout_user()
                return redirect(url_for('index'))
                
Controlador para que el usuario pueda cerrar sesión.
