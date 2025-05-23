from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

app = Flask(__name__)
app.secret_key = '16546+9898484*sdaf4as4dasdQAqAS'



EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,   
    'email': 'reservasv39@gmail.com',  
    'password': 'qejd mpsi kcoz nkdd',   
}


def enviar_email(destinatario, asunto, mensaje_html):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = EMAIL_CONFIG['email']
        msg['To'] = destinatario
        
        html_part = MIMEText(mensaje_html, 'html')
        msg.attach(html_part)
        
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls(context=context)
            server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
            text = msg.as_string()
            server.sendmail(EMAIL_CONFIG['email'], destinatario, text)
        
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

# Asegurar que la carpeta de base de datos existe
if not os.path.exists('instance'):
    os.makedirs('instance')


# Asegurar que la carpeta de base de datos existe
if not os.path.exists('instance'):
    os.makedirs('instance')

# Inicializar la base de datos
def init_db():
    conn = sqlite3.connect('instance/reservas.db')
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL  -- cliente, empleado, admin
    )
    ''')
    
    # Tabla de servicios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS servicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        duracion INTEGER NOT NULL,  -- duración en minutos
        precio REAL NOT NULL
    )
    ''')
    
    # Tabla de empleados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS empleados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        especialidad TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
    ''')
    
    # Tabla de horarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS horarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dia_semana INTEGER NOT NULL,  -- 0=Lunes, 1=Martes, etc.
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL
    )
    ''')
    
    # Tabla de reservas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        servicio_id INTEGER NOT NULL,
        empleado_id INTEGER NOT NULL,
        fecha DATE NOT NULL,
        hora_inicio TEXT NOT NULL,
        hora_fin TEXT NOT NULL,
        estado TEXT NOT NULL DEFAULT 'pendiente',  -- pendiente, confirmada, cancelada, completada
        FOREIGN KEY (cliente_id) REFERENCES usuarios (id),
        FOREIGN KEY (servicio_id) REFERENCES servicios (id),
        FOREIGN KEY (empleado_id) REFERENCES empleados (id)
    )
    ''')
    
    # Insertar usuario administrador por defecto
    cursor.execute('''
    INSERT OR IGNORE INTO usuarios (nombre, email, password, rol)
    VALUES (?, ?, ?, ?)
    ''', ('Administrador', 'admin@example.com', generate_password_hash('admin123'), 'admin'))
    
    cursor.execute('''
    INSERT OR IGNORE INTO usuarios (nombre, email, password, rol)
    VALUES (?, ?, ?, ?)
    ''', ('Juan', 'juan@example.com', generate_password_hash('123456'), 'empleado'))
    
    cursor.execute('''
    INSERT OR IGNORE INTO empleados (usuario_id, especialidad)
    VALUES (?, ?)
    ''', (2, 'Asesor'))
    
    # Insertar algunos servicios de ejemplo
    servicios = [
        ('Servicio Básico', 'Descripción del servicio básico', 30, 25.0),
        ('Servicio Premium', 'Descripción del servicio premium', 60, 50.0),
        ('Servicio VIP', 'Descripción del servicio VIP', 90, 100.0)
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO servicios (nombre, descripcion, duracion, precio)
    VALUES (?, ?, ?, ?)
    ''', servicios)
    
    conn.commit()
    conn.close()

# Inicializar la base de datos al iniciar la aplicación
init_db()

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.context_processor
def utility_processor():
    def get_now():
        return datetime.now()
    return dict(now=get_now)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('instance/reservas.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario and check_password_hash(usuario[3], password):
            session['usuario_id'] = usuario[0]
            session['usuario_nombre'] = usuario[1]
            session['usuario_rol'] = usuario[4]
            flash('Inicio de sesión exitoso!', 'success')
            
            if usuario[4] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif usuario[4] == 'empleado':
                return redirect(url_for('empleado_dashboard'))
            else:
                return redirect(url_for('cliente_dashboard'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('instance/reservas.db')
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO usuarios (nombre, email, password, rol)
            VALUES (?, ?, ?, ?)
            ''', (nombre, email, password_hash, 'cliente'))
            conn.commit()
            conn.close()

            mensaje_html = f"""
            <html>
                <body>
                    <h2>¡Bienvenido {nombre}!</h2>
                    <p>Tu cuenta ha sido creada exitosamente.</p>
                    <p>Ya puedes iniciar sesión y hacer tus reservas.</p>
                    <p>Gracias por confiar en nuestros servicios.</p>
                </body>
            </html>
            """
            enviar_email(email, 'Bienvenido - Cuenta Creada', mensaje_html)
            
            flash('Registro exitoso! Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El correo ya está registrado', 'danger')
        
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('index'))

# Rutas protegidas para clientes
@app.route('/cliente/dashboard')
def cliente_dashboard():
    if 'usuario_id' not in session or session['usuario_rol'] != 'cliente':
        flash('Necesitas iniciar sesión como cliente', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('instance/reservas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener las reservas del cliente con información completa
    cursor.execute('''
    SELECT r.id, r.fecha, r.hora_inicio, r.hora_fin, r.estado, 
           s.nombre as servicio_nombre, s.descripcion as servicio_desc,
           u.nombre as empleado_nombre
    FROM reservas r
    JOIN servicios s ON r.servicio_id = s.id
    JOIN empleados e ON r.empleado_id = e.id
    JOIN usuarios u ON e.usuario_id = u.id
    WHERE r.cliente_id = ?
    ORDER BY r.fecha DESC, r.hora_inicio
    ''', (session['usuario_id'],))
    reservas = cursor.fetchall()
    
    conn.close()
    
    return render_template('cliente_dashboard.html', reservas=reservas)

@app.route('/cliente/reservar', methods=['GET', 'POST'])
def nueva_reserva():
    if 'usuario_id' not in session or session['usuario_rol'] != 'cliente':
        flash('Necesitas iniciar sesión como cliente', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('instance/reservas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener todos los servicios disponibles
    cursor.execute('SELECT * FROM servicios')
    servicios = cursor.fetchall()
    
    # Obtener todos los empleados
    cursor.execute('''
    SELECT e.id, u.nombre, e.especialidad
    FROM empleados e
    JOIN usuarios u ON e.usuario_id = u.id
    ''')
    empleados = cursor.fetchall()
    
    if request.method == 'POST':
        servicio_id = request.form['servicio_id']
        empleado_id = request.form['empleado_id']
        fecha = request.form['fecha']
        hora_inicio = request.form['hora_inicio']
        
        # Obtener duración del servicio
        cursor.execute('SELECT duracion FROM servicios WHERE id = ?', (servicio_id,))
        duracion = cursor.fetchone()['duracion']
        
        # Calcular hora de fin
        formato_hora = '%H:%M'
        hora_inicio_dt = datetime.strptime(hora_inicio, formato_hora)
        hora_fin_dt = hora_inicio_dt + timedelta(minutes=duracion)
        hora_fin = hora_fin_dt.strftime(formato_hora)
        
        # Verificar disponibilidad
        cursor.execute('''
        SELECT COUNT(*) as count
        FROM reservas
        WHERE empleado_id = ? AND fecha = ? AND 
              ((hora_inicio <= ? AND hora_fin > ?) OR 
               (hora_inicio < ? AND hora_fin >= ?))
        ''', (empleado_id, fecha, hora_inicio, hora_inicio, hora_fin, hora_fin))
        
        if cursor.fetchone()['count'] == 0:
            # Crear la reserva
            cursor.execute('''
            INSERT INTO reservas (cliente_id, servicio_id, empleado_id, fecha, hora_inicio, hora_fin, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session['usuario_id'], servicio_id, empleado_id, fecha, hora_inicio, hora_fin, 'pendiente'))
            conn.commit()
            flash('Reserva creada con éxito!', 'success')
            return redirect(url_for('cliente_dashboard'))
        else:
            flash('La hora seleccionada no está disponible', 'danger')
    
    conn.close()
    
    return render_template('nueva_reserva.html', servicios=servicios, empleados=empleados)

# Rutas protegidas para admin
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'usuario_id' not in session or session['usuario_rol'] != 'admin':
        flash('Necesitas iniciar sesión como administrador', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('instance/reservas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener las últimas 10 reservas con información completa
    cursor.execute('''
    SELECT r.id, r.fecha, r.hora_inicio, r.estado, 
           u.nombre as cliente, s.nombre as servicio,
           emp.nombre as empleado
    FROM reservas r
    JOIN usuarios u ON r.cliente_id = u.id
    JOIN servicios s ON r.servicio_id = s.id
    JOIN empleados e ON r.empleado_id = e.id
    JOIN usuarios emp ON e.usuario_id = emp.id
    ORDER BY r.fecha DESC, r.hora_inicio
    LIMIT 10
    ''')
    reservas = cursor.fetchall()
    
    # Estadísticas básicas
    cursor.execute('SELECT COUNT(*) as total FROM usuarios WHERE rol = "cliente"')
    total_clientes = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM reservas')
    total_reservas = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM servicios')
    total_servicios = cursor.fetchone()['total']
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                          reservas=reservas, 
                          total_clientes=total_clientes,
                          total_reservas=total_reservas,
                          total_servicios=total_servicios)

# Ruta para gestionar servicios
@app.route('/admin/servicios', methods=['GET', 'POST'])
def admin_servicios():
    if 'usuario_id' not in session or session['usuario_rol'] != 'admin':
        flash('Necesitas iniciar sesión como administrador', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('instance/reservas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        duracion = request.form['duracion']
        precio = request.form['precio']
        
        cursor.execute('''
        INSERT INTO servicios (nombre, descripcion, duracion, precio)
        VALUES (?, ?, ?, ?)
        ''', (nombre, descripcion, duracion, precio))
        conn.commit()
        flash('Servicio agregado correctamente', 'success')
    
    # Listar todos los servicios
    cursor.execute('SELECT * FROM servicios')
    servicios = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_servicios.html', servicios=servicios)

@app.route('/admin/reserva/<int:reserva_id>/confirmar', methods=['POST'])
def confirmar_reserva(reserva_id):
    if 'usuario_rol' not in session or session['usuario_rol'] != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('instance/reservas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener información de la reserva
    cursor.execute('''
    SELECT r.*, u.nombre as cliente_nombre, u.email as cliente_email,
           s.nombre as servicio_nombre, emp.nombre as empleado_nombre
    FROM reservas r
    JOIN usuarios u ON r.cliente_id = u.id
    JOIN servicios s ON r.servicio_id = s.id
    JOIN empleados e ON r.empleado_id = e.id
    JOIN usuarios emp ON e.usuario_id = emp.id
    WHERE r.id = ?
    ''', (reserva_id,))
    reserva = cursor.fetchone()
    
    if reserva:
        cursor.execute('UPDATE reservas SET estado = ? WHERE id = ?', ('confirmada', reserva_id))
        conn.commit()
        
        # Enviar email de confirmación
        mensaje_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #28a745;">¡Reserva Confirmada!</h2>
                    <p>Hola {reserva['cliente_nombre']},</p>
                    <p>Tu reserva ha sido <strong>confirmada</strong> por nuestro equipo:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #495057; margin-top: 0;">Detalles de la Reserva</h3>
                        <p><strong>Servicio:</strong> {reserva['servicio_nombre']}</p>
                        <p><strong>Fecha:</strong> {reserva['fecha']}</p>
                        <p><strong>Hora:</strong> {reserva['hora_inicio']} - {reserva['hora_fin']}</p>
                        <p><strong>Empleado asignado:</strong> {reserva['empleado_nombre']}</p>
                        <p><strong>Estado:</strong> <span style="color: #28a745; font-weight: bold;">CONFIRMADA</span></p>
                    </div>
                    
                    <p>Por favor, llegue 10 minutos antes de su cita.</p>
                    <p>Si necesita reprogramar o cancelar, contáctenos con al menos 24 horas de anticipación.</p>
                    
                    <p style="margin-top: 30px;">
                        ¡Gracias por confiar en nuestros servicios!<br>
                        <em>El equipo de administración</em>
                    </p>
                </div>
            </body>
        </html>
        """
        
        if enviar_email(reserva['cliente_email'], '✅ Reserva Confirmada', mensaje_html):
            flash('Reserva confirmada y email enviado al cliente.', 'success')
        else:
            flash('Reserva confirmada, pero hubo un error enviando el email.', 'warning')
    
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reserva/<int:reserva_id>/cancelar', methods=['POST'])
def cancelar_reserva(reserva_id):
    if 'usuario_rol' not in session or session['usuario_rol'] != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('instance/reservas.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE reservas SET estado = ? WHERE id = ?', ('cancelada', reserva_id))
    conn.commit()
    conn.close()
    
    flash('Reserva cancelada.', 'success')
    return redirect(url_for('admin_dashboard'))

# RUTA CORREGIDA PARA VER DETALLES DE RESERVA
@app.route('/reserva/<int:reserva_id>')
def ver_reserva(reserva_id):
    # Verificar que el usuario esté logueado
    if 'usuario_id' not in session:
        flash('Necesitas iniciar sesión', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('instance/reservas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Consulta completa con JOIN para obtener toda la información
    cursor.execute('''
    SELECT r.id, r.fecha, r.hora_inicio, r.hora_fin, r.estado,
           cliente.nombre as cliente_nombre,
           s.nombre as servicio_nombre, s.descripcion as servicio_desc,
           empleado.nombre as empleado_nombre, e.especialidad
    FROM reservas r
    JOIN usuarios cliente ON r.cliente_id = cliente.id
    JOIN servicios s ON r.servicio_id = s.id
    JOIN empleados e ON r.empleado_id = e.id
    JOIN usuarios empleado ON e.usuario_id = empleado.id
    WHERE r.id = ?
    ''', (reserva_id,))
    
    reserva = cursor.fetchone()
    conn.close()

    if reserva is None:
        flash('Reserva no encontrada', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Verificar permisos: admin puede ver todas, cliente solo las suyas
    if session['usuario_rol'] == 'cliente' and reserva['cliente_nombre'] != session['usuario_nombre']:
        flash('No tienes permisos para ver esta reserva', 'danger')
        return redirect(url_for('cliente_dashboard'))

    return render_template('ver_reserva.html', reserva=reserva)

# RUTAS CORREGIDAS PARA EDITAR Y ELIMINAR SERVICIOS
@app.route('/admin/servicio/<int:servicio_id>/editar', methods=['POST'])
def editar_servicio(servicio_id):
    if 'usuario_id' not in session or session['usuario_rol'] != 'admin':
        flash('Necesitas iniciar sesión como administrador', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('instance/reservas.db')
    cursor = conn.cursor()
    
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    duracion = request.form['duracion']
    precio = request.form['precio']
    
    cursor.execute('''
    UPDATE servicios 
    SET nombre = ?, descripcion = ?, duracion = ?, precio = ?
    WHERE id = ?
    ''', (nombre, descripcion, duracion, precio, servicio_id))
    
    conn.commit()
    conn.close()
    
    flash('Servicio actualizado correctamente.', 'success')
    return redirect(url_for('admin_servicios'))

@app.route('/admin/servicio/<int:servicio_id>/eliminar', methods=['POST'])
def eliminar_servicio(servicio_id):
    if 'usuario_id' not in session or session['usuario_rol'] != 'admin':
        flash('Necesitas iniciar sesión como administrador', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('instance/reservas.db')
    cursor = conn.cursor()
    
    # Verificar si hay reservas asociadas a este servicio
    cursor.execute('SELECT COUNT(*) as count FROM reservas WHERE servicio_id = ?', (servicio_id,))
    reservas_count = cursor.fetchone()[0]
    
    if reservas_count > 0:
        flash('No se puede eliminar el servicio porque tiene reservas asociadas.', 'danger')
    else:
        cursor.execute('DELETE FROM servicios WHERE id = ?', (servicio_id,))
        conn.commit()
        flash('Servicio eliminado correctamente.', 'success')
    
    conn.close()
    return redirect(url_for('admin_servicios'))

# Ruta para dashboard de empleados
@app.route('/empleado/dashboard')
def empleado_dashboard():
    if 'usuario_id' not in session or session['usuario_rol'] != 'empleado':
        flash('Necesitas iniciar sesión como empleado', 'warning')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('instance/reservas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener el ID del empleado
    cursor.execute('SELECT id FROM empleados WHERE usuario_id = ?', (session['usuario_id'],))
    empleado = cursor.fetchone()
    
    if empleado:
        # Obtener las reservas del empleado
        cursor.execute('''
        SELECT r.id, r.fecha, r.hora_inicio, r.hora_fin, r.estado,
               u.nombre as cliente_nombre, s.nombre as servicio_nombre
        FROM reservas r
        JOIN usuarios u ON r.cliente_id = u.id
        JOIN servicios s ON r.servicio_id = s.id
        WHERE r.empleado_id = ?
        ORDER BY r.fecha DESC, r.hora_inicio
        ''', (empleado['id'],))
        reservas = cursor.fetchall()
    else:
        reservas = []
    
    conn.close()
    
    return render_template('empleado_dashboard.html', reservas=reservas)

# Punto de entrada
if __name__ == '__main__':
    app.run(debug=True)