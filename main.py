from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect
import forms
from config import DevelopmentConfig
from models import db, Empleados

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
crsf = CSRFProtect()

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

if __name__ == "__main__":
    crsf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()