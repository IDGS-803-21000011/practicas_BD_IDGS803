from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class Empleados(db.Model):
    __tablename__ = 'empleados'
    id= db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    correo = db.Column(db.String(50))
    telefono = db.Column(db.String(50))
    direccion = db.Column(db.String(100))
    sueldo = db.Column(db.Integer)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    direccion = db.Column(db.String(50))
    telefono = db.Column(db.String(50))
    fechaCompra = db.Column(db.Date)
    tamano = db.Column(db.String(50))
    ingredientes = db.Column(db.String(50))
    no_pizzas = db.Column(db.Integer)

class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    total = db.Column(db.Integer)
    fechaVenta = db.Column(db.Date)
    diaVenta = db.Column(db.String(15))