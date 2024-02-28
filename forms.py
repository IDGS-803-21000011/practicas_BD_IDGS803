from wtforms import Form
from wtforms import StringField, SelectField, RadioField, EmailField, IntegerField
from wtforms import validators

class EmpleadoForm(Form):
    id = IntegerField('id')
    nombre = StringField('nombre', [
        validators.DataRequired(message='El campo es requerido.'),
        validators.length(min=4, max=10, message='Ingresa un nombre válido.')
    ])
    correo = EmailField('correo', [
        validators.Email(message='Ingrese un correo válido.')
    ])
    telefono = IntegerField('telefono', [
        validators.DataRequired(message='El campo es requerido.'),
        # validators.number_range(min=1, max=7, message='Ingresa una cantidad válida.')
    ])
    direccion = StringField('direccion', [
        validators.DataRequired(message='El campo es requerido.'),
        validators.length(min=10, max=100, message='Ingresa una dirección válida.')
    ])
    sueldo = IntegerField('sueldo', [
        validators.DataRequired(message='El campo es requerido.'),
        # validators.number_range(min=1, max=10, message='Valor no válido.')
    ])
    