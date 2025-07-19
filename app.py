from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key ="12345"

def connect_to_db():
    return  pymysql.connect(
    host='localhost',
    user='root',
    password='',  
    database='bd_automoviles'
)

@app.route('/')
def inicio():
    return render_template('app.html')

@app.route('/clientes')
def cliente():
    return render_template('cliente.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    nif = request.form['nif']
    nombre = request.form['nombre']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    

    try:
        conexion=connect_to_db()
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO clientes (nif, nombre, direccion, telefono) VALUES (%s, %s, %s, %s)",
                (nif, nombre, direccion, telefono )
            )
        conexion.commit()
        return redirect(url_for('consulta'))
    except Exception as e:
        flash(f"Error al agregar cliente: {e}")
        return redirect(url_for('consulta'))


@app.route('/consulta')
def consulta():
    try:
        conexion = connect_to_db()
        cursor = conexion.cursor()

        cursor.execute("SELECT nif, nombre, direccion, telefono FROM clientes")
        clientes = cursor.fetchall()

       
        cursor.execute("""
            SELECT c.matricula, c.marca, c.modelo, c.color, c.precio, cl.nombre FROM coches c
 LEFT JOIN clientes cl ON c.nif_cliente = cl.nif
        """)
        coches = cursor.fetchall()

        cursor.execute("""
            SELECT r.codigo, r.matricula_coche, c.modelo, r.filtro, r.aceite, r.frenos
            FROM revisiones r
            LEFT JOIN coches c ON r.matricula_coche = c.matricula
        """)
        revisiones = cursor.fetchall()


        conexion.close()

        return render_template("consulta.html", clientes=clientes, coches=coches, revisiones=revisiones)
    except Exception as e:
        return f"Error al consultar base de datos: {e}"


@app.route('/eliminar_clientes/<int:id>')
def eliminar_clientes(id):
    try:
        conexion = connect_to_db()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM clientes WHERE nif = %s", (id,))

        conexion.commit()
        conexion.close()

        flash("Cliente eliminado correctamente.")
    except Exception as e:
        flash(f"Error al eliminar cliente: {e}")
    return redirect(url_for('consulta'))


@app.route('/editar_cliente/<nif>', methods=['GET'])
def editar_cliente(nif):
    try:
        conexion = connect_to_db()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM clientes WHERE nif = %s", (nif,))
            cliente = cursor.fetchone()
        conexion.close()

        if cliente:
            return render_template('editar_cliente.html', cliente=cliente)
        else:
            flash("Cliente no encontrado.")
            return redirect(url_for('consulta'))
    except Exception as e:
        flash(f"Error al cargar el cliente: {e}")
        return redirect(url_for('consulta'))

@app.route('/actualizar_cliente/<nif>', methods=['POST'])
def actualizar_cliente(nif):
    nombre = request.form['nombre']
    direccion = request.form['direccion']
    telefono = request.form['telefono']

    try:
        conexion = connect_to_db()
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE clientes
                SET nombre = %s, direccion = %s, telefono = %s
                WHERE nif = %s
            """, (nombre, direccion, telefono, nif))
        conexion.commit()
        conexion.close()

        flash("Cliente actualizado correctamente.")
        return redirect(url_for('consulta'))
    except Exception as e:
        flash(f"Error al actualizar cliente: {e}")
        return redirect(url_for('consulta'))


@app.route('/registro_coche')
def registro_coche():
    try:
        conexion = connect_to_db()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT nif, nombre FROM clientes")
            clientes = cursor.fetchall()
        conexion.close()
        return render_template('registro_coche.html', clientes=clientes)
    except Exception as e:
        flash(f"Error al cargar clientes: {e}")
        return redirect(url_for('inicio'))


@app.route('/guardar_coche', methods=['POST'])
def guardar_coche():
    matricula = request.form['matricula']
    marca = request.form['marca']
    modelo = request.form['modelo']
    color = request.form['color']
    precio = request.form['precio']
    nif_cliente = request.form['nif_cliente'] or None  # Puede ser NULL

    try:
        conexion = connect_to_db()
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO coches (matricula, marca, modelo, color, precio, nif_cliente)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (matricula, marca, modelo, color, precio, nif_cliente))
        conexion.commit()
        conexion.close()
        flash("Coche registrado correctamente.")
        return redirect(url_for('registro_coche'))
    except Exception as e:
        flash(f"Error al registrar coche: {e}")
        return redirect(url_for('registro_coche'))
    
@app.route('/editar_coche/<matricula>', methods=['GET', 'POST'])
def editar_coche(matricula):
    if request.method == 'GET':
        try:
            conexion = connect_to_db()
            with conexion.cursor() as cursor:
                cursor.execute("SELECT * FROM coches WHERE matricula = %s", (matricula,))
                coche = cursor.fetchone()
                cursor.execute("SELECT nif, nombre FROM clientes")
                clientes = cursor.fetchall()
            conexion.close()
            if coche:
                return render_template('editar_coche.html', coche=coche, clientes=clientes)
            else:
                flash("Coche no encontrado.")
                return redirect(url_for('consulta'))
        except Exception as e:
            flash(f"Error al cargar el coche: {e}")
            return redirect(url_for('consulta'))
    else:
        # POST: actualizar coche
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        precio = request.form['precio']
        nif_cliente = request.form['nif_cliente'] or None
        try:
            conexion = connect_to_db()
            with conexion.cursor() as cursor:
                cursor.execute("""
                    UPDATE coches
                    SET marca=%s, modelo=%s, color=%s, precio=%s, nif_cliente=%s
                    WHERE matricula=%s
                """, (marca, modelo, color, precio, nif_cliente, matricula))
            conexion.commit()
            conexion.close()
            flash("Coche actualizado correctamente.")
            return redirect(url_for('consulta'))
        except Exception as e:
            flash(f"Error al actualizar coche: {e}")
            return redirect(url_for('consulta'))

@app.route('/eliminar_coche/<matricula>')
def eliminar_coche(matricula):
    try:
        conexion = connect_to_db()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM coches WHERE matricula = %s", (matricula,))
        conexion.commit()
        conexion.close()
        flash("Coche eliminado correctamente.")
    except Exception as e:
        flash(f"Error al eliminar coche: {e}")
    return redirect(url_for('consulta'))

@app.route('/registro_revision')
def registro_revision():
    try:
        conexion = connect_to_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT matricula, modelo FROM coches")
        coches = cursor.fetchall()
        conexion.close()
        return render_template('registro_revision.html', coches=coches)
    except Exception as e:
        flash(f"Error al cargar coches: {e}")
        return redirect(url_for('inicio'))
    
@app.route('/guardar_revision', methods=['POST'])
def guardar_revision():
    matricula_coche = request.form['matricula_coche']
    filtro = 1 if 'filtro' in request.form else 0
    aceite = 1 if 'aceite' in request.form else 0
    frenos = 1 if 'frenos' in request.form else 0

    try:
        conexion = connect_to_db()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO revisiones (matricula_coche, filtro, aceite, frenos)
            VALUES (%s, %s, %s, %s)
        """, (matricula_coche, filtro, aceite, frenos))
        conexion.commit()
        conexion.close()
        flash("Revisión registrada correctamente.")
        return redirect(url_for('registro_revision'))
    except Exception as e:
        flash(f"Error al guardar revisión: {e}")
        return redirect(url_for('registro_revision'))

@app.route('/editar_revision/<int:codigo>', methods=['GET', 'POST'])
def editar_revision(codigo):
    if request.method == 'GET':
        try:
            conexion = connect_to_db()
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM revisiones WHERE codigo = %s", (codigo,))
            revision = cursor.fetchone()
            cursor.execute("SELECT matricula, modelo FROM coches")
            coches = cursor.fetchall()
            conexion.close()
            if revision:
                return render_template('editar_revision.html', revision=revision, coches=coches)
            else:
                flash("Revisión no encontrada.")
                return redirect(url_for('consulta'))
        except Exception as e:
            flash(f"Error al cargar la revisión: {e}")
            return redirect(url_for('consulta'))
    else:
        matricula_coche = request.form['matricula_coche']
        filtro = 1 if 'filtro' in request.form else 0
        aceite = 1 if 'aceite' in request.form else 0
        frenos = 1 if 'frenos' in request.form else 0
        try:
            conexion = connect_to_db()
            cursor = conexion.cursor()
            cursor.execute("""
                UPDATE revisiones
                SET matricula_coche=%s, filtro=%s, aceite=%s, frenos=%s
                WHERE codigo=%s
            """, (matricula_coche, filtro, aceite, frenos, codigo))
            conexion.commit()
            conexion.close()
            flash("Revisión actualizada correctamente.")
            return redirect(url_for('consulta'))
        except Exception as e:
            flash(f"Error al actualizar revisión: {e}")
            return redirect(url_for('consulta'))

@app.route('/eliminar_revision/<int:codigo>')
def eliminar_revision(codigo):
    try:
        conexion = connect_to_db()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM revisiones WHERE codigo = %s", (codigo,))
        conexion.commit()
        conexion.close()
        flash("Revisión eliminada correctamente.")
    except Exception as e:
        flash(f"Error al eliminar revisión: {e}")
    return redirect(url_for('consulta'))

if __name__ == '__main__':
    
    app.run(debug=True, port=5020)