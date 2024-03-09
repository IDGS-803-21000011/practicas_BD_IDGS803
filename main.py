from flask import Flask, render_template, request, redirect, session
from flask_wtf.csrf import CSRFProtect
import forms
from config import DevelopmentConfig
from datetime import datetime
from models import db, Empleados, Pedido, Venta
from sqlalchemy import func
from forms import PedidoForm

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
crsf = CSRFProtect()
pedidos = []

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/agregarEmpleado", methods=["GET", "POST"])
def agregarEmpleado():
    emp_form = forms.EmpleadoForm(request.form)
    if request.method == "POST":
        emp = Empleados(nombre=emp_form.nombre.data, 
                       correo=emp_form.correo.data,
                       telefono=emp_form.telefono.data,
                       direccion=emp_form.direccion.data,
                       sueldo=emp_form.sueldo.data)
        db.session.add(emp)
        db.session.commit()
    return render_template("vista_agregar_empleado.html", form=emp_form)

@app.route("/vistaEmpleados", methods=["GET", "POST"])
def vistaEmpleados():
    emp_form = forms.EmpleadoForm(request.form)
    empleado = Empleados.query.all()
    return render_template("vista_empleados.html", empleados=empleado)

@app.route("/eliminar", methods=["GET", "POST"])
def eliminar():
    emp_form = forms.EmpleadoForm(request.form)
    if request.method == "GET":
        id = request.args.get('id')
        emp1 = db.session.query(Empleados).filter(Empleados.id == id).first()
        emp_form.id.data = request.args.get('id')
        emp_form.nombre.data = emp1.nombre
        emp_form.correo.data = emp1.correo
        emp_form.telefono.data = emp1.telefono
        emp_form.direccion.data = emp1.direccion
        emp_form.sueldo.data = emp1.sueldo
    elif request.method == 'POST':
        id = emp_form.id.data
        alum = Empleados.query.get(id)
        db.session.delete(alum)
        db.session.commit()
    return render_template('eliminar.html', form=emp_form)

@app.route("/modificar", methods=["GET", "POST"])
def modificar():
    emp_form = forms.EmpleadoForm(request.form)
    if request.method == "GET":
        id = request.args.get('id')
        emp1 = db.session.query(Empleados).filter(Empleados.id == id).first()
        emp_form.id.data = request.args.get('id')
        emp_form.nombre.data = emp1.nombre
        emp_form.correo.data = emp1.correo
        emp_form.telefono.data = emp1.telefono
        emp_form.direccion.data = emp1.direccion
        emp_form.sueldo.data = emp1.sueldo
    elif request.method == 'POST':
        id = emp_form.id.data
        emp1 = db.session.query(Empleados).filter(Empleados.id == id).first()
        emp1.nombre = emp_form.nombre.data
        emp1.correo = emp_form.correo.data
        emp1.telefono = emp_form.telefono.data
        emp1.direccion = emp_form.direccion.data
        emp1.sueldo = emp_form.sueldo.data
        db.session.add(emp1)
        db.session.commit()
    return render_template('modificar.html', form=emp_form)

from flask import session

@app.route("/pedido", methods=["GET", "POST"])
def agregar_pedido():
    if 'nombre' not in session:
        session['nombre'] = ''
    if 'direccion' not in session:
        session['direccion'] = ''
    if 'telefono' not in session:
        session['telefono'] = ''
    if 'fecha' not in session:
        session['fecha'] = ''

    if request.method == "POST":
        pedido_form = PedidoForm(request.form)
        if pedido_form.validate():
            # Obtener los datos del formulario
            nombre = request.form['nombre']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            tamano = request.form['tamano']
            ingredientes = ', '.join(request.form.getlist('ingredientes'))
            no_pizzas = int(request.form['no_pizzas'])
            fecha = request.form['fecha']

            # Almacenar los datos en la sesión
            session['nombre'] = nombre
            session['direccion'] = direccion
            session['telefono'] = telefono
            session['fecha'] = fecha

            # Resto del código para procesar el pedido...
            costo_por_ingredientes = len(request.form.getlist('ingredientes')) * 10

            # Obtener el día de la semana a partir de la fecha
            fecha_datetime = datetime.strptime(fecha, '%Y-%m-%d')
            dia_semana = fecha_datetime.strftime('%A')

            if tamano == 'chica':
                subtotal = no_pizzas * 40 + costo_por_ingredientes
            elif tamano == 'mediana':
                subtotal = no_pizzas * 80 + costo_por_ingredientes
            else:
                subtotal = no_pizzas * 120 + costo_por_ingredientes

            idsugerido = len(pedidos) + 1
            while idsugerido in [pedido['id'] for pedido in pedidos]:
                idsugerido += 1

            pedidos.append({
                'id': idsugerido,
                'nombre': nombre,
                'direccion': direccion,
                'telefono': telefono,
                'tamano': tamano,
                'ingredientes': ingredientes,
                'no_pizzas': no_pizzas,
                'subtotal': subtotal,
                'fecha': fecha,
                'dia_semana': dia_semana
            })

            return redirect("/pedido")
    else:
        nombre = session.get('nombre', '')
        direccion = session.get('direccion', '')
        telefono = session.get('telefono', '')
        fecha = session.get('fecha', '')

        pedido_form = PedidoForm(nombre=nombre, direccion=direccion, telefono=telefono, fecha=fecha)

    return render_template("vista_pedidos.html", form=pedido_form, pedidos1=pedidos)

@app.route("/quitar_pedido", methods=["POST"])
def quitar_pedido():
    global pedidos

    pedido_id = int(request.form["pedido_id"])

    pedidos = [pedido for pedido in pedidos if pedido["id"] != pedido_id]

    return redirect('/pedido')

@app.route("/alerta", methods=["POST"])
def guardar_pedido():
    total_pedido = sum(pedido['subtotal'] for pedido in pedidos) 

    return render_template("confirmar_pedido.html", total_pedido=total_pedido)

@app.route("/confirmar_pedido", methods=["POST"])
def confirmar_pedido():
    global pedidos
    decision = request.form.get('decision')
    
    if decision == 'si':
        total_venta = 0
        nombre = pedidos[0]['nombre']
        direccion = pedidos[0]['direccion']
        telefono = pedidos[0]['telefono']
        fechaCompra = pedidos[0]['fecha']
        for p in pedidos:
            ped = Pedido(
            nombre = nombre,
            direccion = direccion,
            telefono = telefono,
            fechaCompra = fechaCompra,
            tamano = p['tamano'],
            ingredientes = p['ingredientes'],
            no_pizzas = p['no_pizzas'],
            )
            db.session.add(ped)
            db.session.commit()
        
        # Obtener el día de la semana correspondiente a la fecha de compra
        dia_semana = datetime.strptime(pedidos[0]['fecha'], '%Y-%m-%d').strftime('%A')
        total_venta = sum(pedido['subtotal'] for pedido in pedidos) 
        venta = Venta(
            nombre = pedidos[0]['nombre'],
            total = total_venta,
            fechaVenta = pedidos[0]['fecha'],
            diaVenta = dia_semana
        )
        db.session.add(venta)
        db.session.commit()
        pedidos = []
        return redirect("/ventas")
    else:
        return redirect("/pedido")

@app.route("/ventas", methods=["GET", "POST"])
def mostrar_ventas():
    ventas = []
    total_ventas = 0 

    if request.method == "POST":
        dia_seleccionado = request.form.get('dia_semana')
        mes_seleccionado = request.form.get('mes')

        if dia_seleccionado and mes_seleccionado:
            print("Por favor, seleccione solo una opción: por día o por mes.")
            return redirect("/ventas")
        elif dia_seleccionado:
            dia_semana = dia_seleccionado 
            ventas = Venta.query.filter(Venta.diaVenta == dia_semana).all()
        elif mes_seleccionado:
            mes_numero = int(mes_seleccionado)
            ventas = Venta.query.filter(func.extract('month', Venta.fechaVenta) == mes_numero).all()
        else:
            ventas = Venta.query.all()

        total_ventas = sum(venta.total for venta in ventas)

    return render_template("ventas.html", ventas=ventas, total_ventas=total_ventas)


if __name__ == "__main__":
    crsf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()