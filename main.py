from flask import Flask, render_template, request, redirect
from flask_wtf.csrf import CSRFProtect
import forms
from config import DevelopmentConfig
from datetime import datetime
from models import db, Empleados, Pedido, Venta
from sqlalchemy import func

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

@app.route("/pedido", methods=["GET", "POST"])
def agregar_pedido():
    pedido_form = forms.PedidoForm()
    if request.method == "POST" and pedido_form.validate():

        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        tamano = request.form['tamano']
        ingredientes = ', '.join(request.form.getlist('ingredientes'))  
        no_pizzas = int(request.form['no_pizzas'])
        
        costo_por_ingredientes = len(request.form.getlist('ingredientes')) * 10

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
            'subtotal': subtotal
        })

        return redirect("/pedido")
    else:
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
        for p in pedidos:
            ped = Pedido(
            nombre = p['nombre'],
            direccion = p['direccion'],
            telefono = p['telefono'],
            tamano = p['tamano'],
            ingredientes = p['ingredientes'],
            no_pizzas = p['no_pizzas']
            )
            db.session.add(ped)
            db.session.commit()

        total_venta = sum(pedido['subtotal'] for pedido in pedidos) 
        venta = Venta(
            nombre = pedidos[0]['nombre'],
            total = total_venta
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
        dia_seleccionado = request.form.get('dia')
        mes_seleccionado = request.form.get('mes')

        if dia_seleccionado:
            fecha_dia = datetime.strptime(dia_seleccionado, '%Y-%m-%d').date()
            ventas = Venta.query.filter(func.date(Venta.fechaVenta) == fecha_dia).all()
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