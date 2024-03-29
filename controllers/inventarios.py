# -*- coding: utf-8 -*-
# tente algo como


# < -------- Funciones privadas de SMDYP ------------>

import datetime

# Verifica si el usuario que intenta acceder al controlador tiene alguno de los
# roles necesarios
def __check_role():

    roles_permitidos = ['WEBMASTER', 'DIRECTOR', 'ASISTENTE DEL DIRECTOR', 
                        'JEFE DE LABORATORIO', 'JEFE DE SECCIÓN', 'TÉCNICO', 
                        'GESTOR DE SMyDP']
    return True in map(lambda x: auth.has_membership(x), roles_permitidos)

# Determina si el id de la dependencia es valido. Retorna False si el id no existe
# o es de un tipo incorrecto
def __is_valid_id(id_, tabla):
    try:
        int(id_)
    except:
        return False
    # Si el id recibido tiene el tipo correcto pero no existe en la base de datos
    if not db(tabla.id == int(id_)).select():
        return False

    return True

# Determina si una variable "booleana" pasada como parametro con GET es realmente
# 'True' o 'False' (request.vars almacena todo como strings)
def __is_bool(bool_var):
    if not bool_var in ['True', 'False']:
        return False
    else:
        return True

# Dado el nombre de una dependencia, retorna el id de esta si la encuentra o
# None si no lo hace
def __find_dep_id(nombre):

    dep_id = db(db.dependencias.nombre == nombre).select()[0].id    
    return dep_id

# Dado el id de un espacio fisico, retorna las sustancias que componen el inventario
# de ese espacio.
def __get_inventario_espacio(espacio_id=None):
    return db(db.bien_mueble.bm_espacio_fisico == espacio_id).select()

# Retorna las hojas o dependencias que no tienen hijos (posiblemente secciones) y
# que estan por debajo de la dependencia dada.
# "jerarquia" tiene la forma: 
#       {'dependencia1': [dep_hija1,
#                        .
#                        .
#                         dep_hijan]
#        'dependencia2': [dep_hija1,
#                         .
#                         .
#                         dep_hijam]
#     }
# Si una dependencia no tiene otras adscritas, entonces no aparece en "jerarquia"
def __get_leaves(dep_id, jerarquia):

    if not dep_id in jerarquia:
        return [dep_id]
    else:
        l = []
        for d in jerarquia[dep_id]:
            l = l + __get_leaves(d, jerarquia) 
        return l


# Dada una lista de ids de dependencias que no poseen otras adscritas a ellas,
# retorna los ids de espacios fisicos en la base de datos que tienen a estas 
# dependencias como secciones
def __filtrar_espacios(hojas):

    espacios = []
    for dep_id in hojas:
        nuevos_espacios = [esp.id for esp in db(db.espacios_fisicos.dependencia == dep_id).select()]
        if nuevos_espacios:
            espacios = espacios + nuevos_espacios
    return espacios

# Dado el id de una dependencia, retorna una lista con los ids de todos los
# espacios fisicos que pertenecen a esta. Si el id es de la ULAB, retorna
# todos los espacios fisicos
def __get_espacios(dep_id):
    espacios = []

    secciones = []
    dependencias = db(db.dependencias.id > 0).select()
    
    # Creando lista de adyacencias
    lista_adyacencias = {dep.id: dep.unidad_de_adscripcion for dep in dependencias}

    # Representando la jerarquia con la forma {'dependencia': [dep_hija1, dep_hija2]}
    jerarquia = {}

    for hijo, padre in lista_adyacencias.iteritems():
        # Si el padre es None, es porque se trata de la unidad de laboratorios
        # que no tiene padre (nivel mas alto de la jerarquia)
        if padre is not None:
            if padre in jerarquia:
                jerarquia[padre].append(hijo)
            else:
                jerarquia[padre] = [hijo]

    hojas = __get_leaves(int(dep_id), jerarquia)

    espacios = __filtrar_espacios(hojas)

    return espacios

# Agrega los inventarios de los espacios en la lista "espacios"
def __sumar_inventarios(espacios):

    inventario_total = []
    for esp_id in espacios:
        inventario_total += __get_inventario_espacio(esp_id)
                       
    return inventario_total


# Dado el id de una dependencia, retorna una lista con el agregado de los bm
# que existen en los espacios fisicos que pertenecen a esta. 
def __get_inventario_dep(dep_id):

    inventario = {}

    # Obteniendo lista de espacios bajo la dependencia con id dep_id
    espacios = __get_espacios(dep_id)

    # Agrega los inventarios de los espacios en la lista "espacios"
    inventario = __sumar_inventarios(espacios)

    return inventario
# Registra un nueva bm en el espacio fisico indicado. Si el bm ya
# existe en el inventario, genera un mensaje con flash y no anade de nuevo 
# el bm. 
def __agregar_bm(nombre, no_bien, no_placa, marca, modelo, serial,
                descripcion, material, color, calibrar, fecha_calibracion,
                unidad_med, ancho, largo, alto, diametro, movilidad, uso, 
                estatus, nombre_cat, subcategoria, cod_loc, localizacion, espacio, unidad_ad, 
                dependencia, user, clasificacion):

    # Si ya existe el BM en el inventario
    if (db(db.bien_mueble.bm_num == no_bien).select()):
        bm = db(db.bien_mueble.bm_num == no_bien).select()[0]

        response.flash = "El BM \"{0}\" ya ha sido ingresado anteriormente \
                          al espacio \"{1}\".".format(bm.bm_nombre, bm.bm_espacio_fisico)
        return False
    # Si no, se agrega al inventario del espacio fisico la nueva sustancia
    else:
        inv_id = db.bien_mueble.insert(
            bm_nombre = nombre, 
            bm_num = no_bien, 
            bm_placa = no_placa, 
            bm_marca = marca, 
            bm_modelo = modelo, 
            bm_serial = serial,
            bm_descripcion = descripcion, 
            bm_material = material, 
            bm_color = color,
            bm_calibrar =  calibrar,
            bm_fecha_calibracion = fecha_calibracion,
            bm_unidad = unidad_med, 
            bm_ancho = ancho, 
            bm_largo = largo,
            bm_alto = alto, 
            bm_diametro = diametro, 
            bm_movilidad = movilidad, 
            bm_uso = uso,
            bm_estatus = estatus, 
            bm_categoria = nombre_cat,
            bm_subcategoria = subcategoria, 
            bm_codigo_localizacion = cod_loc,
            bm_localizacion = localizacion, 
            bm_espacio_fisico = espacio,
            bm_unidad_de_adscripcion = unidad_ad, 
            bm_depedencia = dependencia, 
            bm_crea_ficha = user,
            bm_clasificacion = clasificacion
        )
    return redirect(URL(args=request.args, vars=request.get_vars, host=True)) 

"""         concepto = 'Ingreso'
        tipo_ing = 'Ingreso inicial'
        # Agregando la primera entrada de la sustancia en la bitacora
        db.t_Bitacora.insert(
                                f_cantidad=cantidad,
                                f_cantidad_total=cantidad,
                                f_concepto=concepto,
                                f_tipo_ingreso=tipo_ing,
                                f_medida=unidad_id,
                                f_inventario=inv_id,
                                f_sustancia=sustancia_id) """

# Dado el id de una depencia y conociendo si es un espacio fisico o una dependencia
# comun, determina si el usuario tiene privilegios suficientes para obtener informacion
# de esta
def __acceso_permitido(user, dep_id, es_espacio):
    """
    Args:
        * user_id (str): id del usuario en la tabla t_Personal (diferente de auth.user.id)
        * dep_id (str): id de la dependencia a la cual pertenece el recurso que se 
            desea acceder
        * es_espacio (str): 'True' si el usuario viene de seleccionar un espacio 
            fisico
    """
    # Valor a retornar que determina si el usuario tiene o no acceso al recurso
    permitido = False

    # dep_actual es un apuntador que permitira recorrer la jerarquia de dependencias
    # desde dep_id hasta usuario_dep. Si dep_actual no encuentra usuario_dep 
    # entonces se esta tratando de acceder a una dependencia sin permisos suficientes
    dep_actual = dep_id

    # Si el usuario es tecnico se busca en la tabla de es_encargado si el usuario 
    # es encargado del espacio con id dep_id
    if auth.has_membership("TÉCNICO"):
        encargado = db(db.es_encargado.espacio_fisico == dep_id).select().first()
        if encargado:
            permitido = encargado.tecnico == user.id

    else:
        # Dependencia a la que pertenece el usuario o que tiene a cargo
        usuario_dep = user.f_dependencia

        # Buscando todas las dependencias para conocer la lista de adyacencias con
        # la jerarquia de la ULAB
        dependencias = db(db.dependencias.id > 0).select(
                                db.dependencias.nombre,
                                db.dependencias.id,
                                db.dependencias.unidad_de_adscripcion)

        # Creando lista de adyacencias
        lista_adyacencias = {dep.id: dep.unidad_de_adscripcion for dep in dependencias}

        # Buscando el id de la direccion para saber si ya se llego a la raiz
        direccion_id = __find_dep_id('DIRECCIÓN')

        # Si dep_id es un espacio fisico, se sube un nivel en la jerarquia (hasta
        # las secciones) ya que los espacios fisicos no aparecen en la lista de 
        # adyacencias pero si las secciones a las que pertenecen
        if es_espacio == "True":
            dep_actual = db(db.espacios_fisicos.id == dep_id).select().first().dependencia

        while dep_actual is not None:

            # Si en el camino hacia la raiz se encontro la dependencia a la que
            # pertenece el usuario, entonces si hay privilegios suficientes
            if dep_actual == usuario_dep:
                permitido = True
                break
            # Si ya se llego a la raiz, terminar el while
            if dep_actual == direccion_id:
                break
            else:
                dep_actual = lista_adyacencias[dep_actual] 

    return permitido

# Retorna un string con la descripcion de un registro de la bitacora de acuerdo 
# a si es un ingreso (sompra, suministro almacen u otorgado por otra seccion) 
# o un egreso (docencia, invenstigacion o extension)
def __get_descripcion(registro):
    descripcion = ""

    if registro.f_concepto[0] == "Ingreso":
        # Si es un ingreso por compra, se muestra el 
        # Compra a "Proveedor" según Factura No. "No. Factura" de fecha "Fecha de compra"
        if registro.f_tipo_ingreso[0] == "Compra":
            compra = db(db.t_Compra.id == registro.f_compra).select()[0]
            
            # Datos de la compra
            proveedor = compra.f_institucion
            nro_factura = compra.f_nro_factura
            fecha_compra = compra.f_fecha

            fecha = fecha_compra

            descripcion = "Compra a \"{0}\" según Factura No. \"{1}\" con fecha"\
                         " \"{2}\"".format(proveedor, nro_factura, fecha)

        # Si es un ingreso por almacen
        # Suministro por el almacén del Laboratorio "X" 
        elif registro.f_tipo_ingreso[0] == "Almacén":
            almacen = db(db.espacios_fisicos.id == registro.f_almacen).select()[0]
            dep_id = almacen.dependencia
            dep = db(db.dependencias.id == dep_id).select()[0]

            # Asumiendo que siempre habra un laboratorio sobre la seccion a la que
            descripcion = "Suministrado por el almacén de la dependencia "\
                          "\"{0}\"".format(dep.nombre)

        elif registro.f_tipo_ingreso[0] == "Solicitud":
            # Respuesta a la solicitud en la que se otorgo la sustancia
            respuesta = db(db.t_Respuesta.id == registro.f_respuesta_solicitud
                          ).select()[0]

            # Espacio desde el que se acepto proveer la sustancia
            espacio = db(db.espacios_fisicos.id == respuesta.f_espacio).select()[0]

            # Seccion a la que pertenece ese espacio
            seccion = db(db.dependencias.id == espacio.dependencia).select()[0]

            # Laboratorio al que pertenece esa seccion
            lab = db(db.dependencias.id == seccion.unidad_de_adscripcion).select()[0]

            descripcion = "Otorgado por la Sección \"{0}\" del \"{1}\" "\
                          "en calidad de \"{2}\"".format(seccion.nombre,
                          lab.nombre, respuesta.f_calidad[0])
        elif registro.f_tipo_ingreso[0] == "Ingreso inicial":
            descripcion = "Ingreso inicial de la sustancia al inventario"

    else:
        # Si es un consumo por Docencia
        if registro.f_tipo_egreso[0] == "Docencia":
            servicio = db(db.servicios.id == registro.f_servicio).select()[0] 

            nombre = servicio.nombre

            descripcion = "Ejecución de la práctica \"{0}\"".format(nombre)
        elif registro.f_tipo_egreso[0] == "Investigación":
            servicio = db(db.servicios.id == registro.f_servicio).select()[0] 

            nombre = servicio.nombre

            descripcion = "Ejecución del proyecto de investigación \"{0}\"".format(nombre)
            
        elif registro.f_tipo_egreso[0] == "Extensión":
            servicio = db(db.servicios.id == registro.f_servicio).select()[0] 

            nombre = servicio.nombre

            descripcion = "Ejecución del servicio \"{0}\"".format(nombre)
            
        # Cuando es un egreso en respuesta a una solicitud
        else:
            
            # Respuesta a la solicitud en la que se solicito la sustancia
            respuesta = db(db.t_Respuesta.id == registro.f_respuesta_solicitud
                          ).select()[0]

            # Solicitud que hizo que por aceptarla se sacara material
            solicitud = db(db.t_Solicitud_smydp.id == respuesta.f_solicitud
                          ).select()[0]

            # Espacio desde el que se solicito la sustancia
            espacio = db(db.espacios_fisicos.id == solicitud.f_espacio).select()[0]

            # Seccion a la que pertenece ese espacio
            seccion = db(db.dependencias.id == espacio.dependencia).select()[0]

            # Laboratorio al que pertenece esa seccion
            lab = db(db.dependencias.id == seccion.unidad_de_adscripcion).select()[0]

            descripcion = "Otorgado a la Sección \"{0}\" del \"{1}\" "\
                          "en calidad de \"{2}\"".format(seccion.nombre,
                          lab.nombre, respuesta.f_calidad[0])
        

    return descripcion

# Agrega un nuevo registro a la bitacora de una sustancia
def __agregar_registro(concepto):

    cantidad = float(request.vars.cantidad)

    # Operaciones comunes a todos los casos: actualizacion del inventario

    # ID de la unidad en la que el usuario registro la cantidad ingresada
    unidad_id = request.vars.unidad

    # Inventario al cual pertenece la bitacora consultada
    inv = db(db.t_Inventario.id == request.get_vars.inv).select()[0]

    # Unidad indicada por el usuario
    unidad = db(db.t_Unidad_de_medida.id == unidad_id
                   ).select()[0].f_nombre

    # Unidad de medida en la que se encuentra el inventario de la sustancia
    unidad_inventario = db(db.t_Unidad_de_medida.id == inv.f_medida
                          ).select()[0].f_nombre

    # Transformando las cantidades de acuerdo a la unidad utilizada en
    # el inventario de la sustancia
    cantidad = __transformar_cantidad(cantidad, unidad, unidad_inventario)

    # Cantidades total y de uso interno antes del ingreso o consumo
    total_viejo = inv.f_existencia
    uso_interno_viejo = inv.f_uso_interno

    if concepto == 'Ingreso':
        tipo_ing = request.vars.tipo_ingreso

        # Nueva cantidad total y nueva cantidad para uso interno
        total_nuevo = total_viejo + cantidad
        uso_interno_nuevo = uso_interno_viejo + cantidad

        # Actualizando cantidad total con la nueva 
        inv.update_record(
            f_existencia=total_nuevo,
            f_uso_interno=uso_interno_nuevo)

        if tipo_ing == 'Almacén':

            almacen = int(request.vars.almacen)

            db.t_Bitacora.insert(
                f_cantidad=cantidad,
                f_cantidad_total=total_nuevo,
                f_concepto=concepto,
                f_tipo_ingreso=tipo_ing,
                f_medida=inv.f_medida,
                f_inventario=inv.id,
                f_sustancia=inv.sustancia,
                f_almacen=almacen)

        # Tipo ingreso es compra
        else:

            # Datos de la nueva compra
            nro_factura = request.vars.nro_factura
            institucion = request.vars.institucion
            rif = request.vars.rif

            # Fecha de la compra en formato "%m/%d/%Y"
            fecha_compra = request.vars.fecha_compra
            
            # Se registra la nueva compra en la tabla t_Compra
            compra_id = db.t_Compra.insert(
                f_cantidad=cantidad,
                f_nro_factura=nro_factura,
                f_institucion=institucion,
                f_rif=rif,
                f_fecha=fecha_compra,
                f_sustancia=inv.sustancia,
                f_medida=unidad_id)

            db.t_Bitacora.insert(
                f_cantidad=cantidad,
                f_cantidad_total=total_nuevo,
                f_concepto=concepto,
                f_tipo_ingreso=tipo_ing,
                f_medida=inv.f_medida,
                f_compra=compra_id,
                f_inventario=inv.id,
                f_sustancia=inv.sustancia)

    else:
        tipo_eg = request.vars.tipo_egreso            
        
        # Nueva cantidad total luego del consumo
        total_nuevo = total_viejo - cantidad
        if total_nuevo < 0:
            response.flash = "La cantidad total luego del consumo no puede ser "\
                             "negativa"
            redirect(URL(args=request.args, vars=request.get_vars, host=True))
        
        # Nueva cantidad de uso interno nueva puede ser maximo lo que era antes
        # (si hay material suficiente) o el nuevo total
        uso_interno_nuevo = min(uso_interno_viejo, total_nuevo)

        # Actualizando cantidad total con la nueva 
        inv.update_record(
            f_existencia=total_nuevo,
            f_uso_interno=uso_interno_nuevo)

        servicio_id = request.vars.servicio

        db.t_Bitacora.insert(
            f_cantidad=cantidad,
            f_cantidad_total=total_nuevo,
            f_concepto=concepto,
            f_tipo_egreso=tipo_eg,
            f_medida=inv.f_medida,
            f_servicio=servicio_id,
            f_inventario=inv.id,
            f_sustancia=inv.sustancia)

    # Se redirije para evitar mensaje de revisita con metodo POST
    return redirect(URL(args=request.args, vars=request.get_vars, host=True))

# < -------- Final Funciones privadas de SMDYP ------------>

# < ------- Vistas del modulo de inventario -------->
def index(): return locals()

@auth.requires(lambda: __check_role())
@auth.requires_login(otherwise=URL('modulos', 'login'))
def detalles():
    bm = request.vars['bm']
    bien = db(db.bien_mueble.bm_num == bm).select()[0]
    return dict(bien = bien)

# Muestra el inventario de acuerdo al cargo del usuario y la dependencia que tiene
# a cargo
@auth.requires(lambda: __check_role())
@auth.requires_login(otherwise=URL('modulos', 'login'))
def bienes_muebles():
# Inicializando listas de espacios fisicos y dependencias

    # OJO: Espacios debe ser [] siempre que no se este visitando un espacio fisico
    espacios = []
    dependencias = []
    dep_nombre = ""
    dep_padre_id = ""
    dep_padre_nombre = ""

    # Lista de BM en el inventario de un espacio fisico o que componen 
    # el inventario agregado de una dependencia
    inventario = []
    
    # Elementos que deben ser mostrados como una lista en el modal
    # de agregar BM
    material_pred = []
    color = []
    unidad_med = []
    movilidad = []
    uso = []
    nombre_cat = []
    cod_localizacion = []
    localizacion = []
    nombre_espaciof = []
    unidad_adscripcion = []
    
    # Esta variable es enviada a la vista para que cuando el usuario seleccione 
    # un espacio fisico, se pase por GET es_espacio = "True". No quiere decir
    # que la dependencia seleccionada sea un espacio, sino que la siguiente
    # dependencia visitada sera un espacio fisico
    es_espacio = False

    # Permite saber si actualmente se esta visitando un espacio fisico (True)
    # o una dependencia (False)
    espacio_visitado = False
    
    # Indica si se debe seguir mostrando la flecha para seguir retrocediendo 
    retroceder = True

    es_tecnico = auth.has_membership("TÉCNICO")
    direccion_id = __find_dep_id('DIRECCIÓN')

    # Obteniendo la entrada en t_Personal del usuario conectado
    user = db(db.t_Personal.f_usuario == auth.user.id).select()[0]
    user_id = user.id
    user_dep_id = user.f_dependencia

    if auth.has_membership("TÉCNICO"):
        # Si el tecnico ha seleccionado un espacio fisico
        if request.vars.dependencia:
            if request.vars.es_espacio == "True":
                # Evaluando la correctitud de los parametros del GET 
                if not (__is_valid_id(request.vars.dependencia, db.espacios_fisicos) and
                        __is_bool(request.vars.es_espacio)):
                    redirect(URL('bienes_muebles'))

                # Determinando si el usuario tiene privilegios suficientes para
                # consultar la dependencia en request.vars.dependencia
                if not __acceso_permitido(user, 
                                    int(request.vars.dependencia), 
                                        request.vars.es_espacio):
                    redirect(URL('bienes_muebles'))

                espacio_id = request.vars.dependencia
                espacio = db(db.espacios_fisicos.id == espacio_id).select()[0]
                dep_nombre = espacio.nombre

                # Guardando el ID y nombre de la dependencia padre para el link 
                # de navegacion de retorno
                dep_padre_id = espacio.dependencia
                dep_padre_nombre = db(db.dependencias.id == dep_padre_id
                                    ).select().first().nombre
                # Guardando la unidad de adscripcion
                dep_padre_unid_ads = db(db.dependencias.id == dep_padre_id
                                    ).select().first().unidad_de_adscripcion

                espacio_visitado = True

                # Busca el inventario del espacio
                inventario = __get_inventario_espacio(espacio_id)

                material_pred = ['Acero','Acrílico','Madera','Metal','Plástico','Tela','Vidrio', 'Otro']
                color = ['Amarillo','Azul','Beige','Blanco','Dorado','Gris','Madera','Marrón','Mostaza','Naranja',
                'Negro','Plateado','Rojo','Rosado','Verde','Vinotinto','Otro color']
                unidad_med = ['cm','m']
                movilidad = ['Fijo','Portátil']
                uso = ['Docencia','Investigación','Extensión','Apoyo administrativo']
                nombre_cat = ['Maquinaria Construcción', 'Equipo Transporte', 'Equipo Comunicaciones', 
                'Equipo Médico', 'Equipo Científico Religioso', 'Equipo Oficina']
                cod_localizacion = ['150301','240107']
                localizacion = ['Edo Miranda, Municipio Baruta, Parroquia Baruta',
                'Edo Vargas, Municipio Vargas, Parroquia Macuto']

                # Si se esta agregando un nuevo BM, se registra en la DB
                if request.vars.nombre: # Verifico si me pasan como argumento el nombre del BM.
                    __agregar_bm(
                        request.vars.nombre,request.vars.no_bien,request.vars.no_placa, 
                        request.vars.marca, request.vars.modelo, request.vars.serial,
                        request.vars.descripcion, request.vars.material, request.vars.color,
                        request.vars.calibrar, request.vars.fecha_calibracion, request.vars.unidad, 
                        request.vars.ancho, request.vars.largo, request.vars.alto,
                        request.vars.diametro, request.vars.movilidad, request.vars.tipo_uso, request.vars.estatus, 
                        request.vars.nombre_cat, request.vars.subcategoria, request.vars.cod_loc, request.vars.localizacion, espacio, dep_padre_unid_ads, 
                        dep_padre_id, user_id, request.vars.clasificacion)
            else:
                # Espacios a cargo del usuario user_id que pertenecen a la seccion
                # en request.vars.dependencia
                espacios = [row.espacios_fisicos for row in db(
                    (db.es_encargado.espacio_fisico == db.espacios_fisicos.id) & 
                    (db.espacios_fisicos.dependencia == int(request.vars.dependencia)) & 
                    (db.es_encargado.tecnico == user_id)).select()]

                espacios_ids = [e.id for e in espacios]

                dep_id = int(request.vars.dependencia)
                dep_nombre = db(db.dependencias.id == dep_id).select()[0].nombre

                dep_padre_nombre = "Secciones"

                # Se muestra el inventarios de los espacios que tiene a cargo el usuario en la
                # seccion actual
                inventario = __sumar_inventarios(espacios_ids)

                es_espacio = True

        # Si el tecnico o jefe no ha seleccionado un espacio sino que acaba de 
        # entrar a la opcion de inventarios
        else:
            # Se buscan las secciones a las que pertenecen los espacios que
            # tiene a cargo el usuario
            espacios_a_cargo = db(
                (db.es_encargado.tecnico == user_id) & 
                (db.espacios_fisicos.id == db.es_encargado.espacio_fisico)
                                 ).select()

            secciones_ids = {e.espacios_fisicos.dependencia for e in espacios_a_cargo}

            dependencias = map(lambda x: db(db.dependencias.id == x).select()[0], 
                               secciones_ids)

            dep_nombre = "Secciones"

            espacios_ids = [e.espacios_fisicos.id for e in espacios_a_cargo]

            inventario = __sumar_inventarios(espacios_ids)

    elif auth.has_membership("JEFE DE SECCIÓN"):
        # Si el jefe de seccion ha seleccionado un espacio fisico
        if request.vars.es_espacio == 'True':
            # Determinando si el usuario tiene privilegios suficientes para
            # consultar la dependencia en request.vars.dependencia
            if not __acceso_permitido(user, 
                                int(request.vars.dependencia), 
                                    request.vars.es_espacio):
                redirect(URL('bienes_muebles'))

            # Evaluando la correctitud de los parametros del GET 
            if not (__is_valid_id(request.vars.dependencia, db.espacios_fisicos) and
                    __is_bool(request.vars.es_espacio)):
                redirect(URL('bienes_muebles'))


                espacio_id = request.vars.dependencia
                espacio = db(db.espacios_fisicos.id == espacio_id).select()[0]
                dep_nombre = espacio.nombre

                # Guardando el ID y nombre de la dependencia padre para el link 
                # de navegacion de retorno
                dep_padre_id = espacio.dependencia
                dep_padre_nombre = db(db.dependencias.id == dep_padre_id
                                    ).select().first().nombre
                # Guardando la unidad de adscripcion
                dep_padre_unid_ads = db(db.dependencias.id == dep_padre_id
                                    ).select().first().unidad_de_adscripcion

                espacio_visitado = True

                # Busca el inventario del espacio
                inventario = __get_inventario_espacio(espacio_id)

                material_pred = ['Acero','Acrílico','Madera','Metal','Plástico','Tela','Vidrio', 'Otro']
                color = ['Amarillo','Azul','Beige','Blanco','Dorado','Gris','Madera','Marrón','Mostaza','Naranja',
                'Negro','Plateado','Rojo','Rosado','Verde','Vinotinto','Otro color']
                unidad_med = ['cm','m']
                movilidad = ['Fijo','Portátil']
                uso = ['Docencia','Investigación','Extensión','Apoyo administrativo']
                nombre_cat = ['Maquinaria Construcción', 'Equipo Transporte', 'Equipo Comunicaciones', 
                'Equipo Médico', 'Equipo Científico Religioso', 'Equipo Oficina']
                cod_localizacion = ['150301','240107']
                localizacion = ['Edo Miranda, Municipio Baruta, Parroquia Baruta',
                'Edo Vargas, Municipio Vargas, Parroquia Macuto']

                # Si se esta agregando un nuevo BM, se registra en la DB
                if request.vars.nombre: # Verifico si me pasan como argumento el nombre del BM.
                    __agregar_bm(
                        request.vars.nombre,request.vars.no_bien,request.vars.no_placa, 
                        request.vars.marca, request.vars.modelo, request.vars.serial,
                        request.vars.descripcion, request.vars.material, request.vars.color,
                        request.vars.calibrar, request.vars.fecha_calibracion, request.vars.unidad, 
                        request.vars.ancho, request.vars.largo, request.vars.alto,
                        request.vars.diametro, request.vars.movilidad, request.vars.tipo_uso, request.vars.estatus, 
                        request.vars.nombre_cat, request.vars.subcategoria, request.vars.cod_loc, request.vars.localizacion, espacio, dep_padre_unid_ads, 
                        dep_padre_id, user_id, request.vars.clasificacion)


        # Si el jefe de seccion no ha seleccionado un espacio sino que acaba de 
        # regresar a la vista inicial de inventarios
        elif request.vars.es_espacio == 'False':
            if not (__is_valid_id(request.vars.dependencia, db.espacios_fisicos) and
                    __is_bool(request.vars.es_espacio)):
                    redirect(URL('bienes_muebles'))
            # Determinando si el usuario tiene privilegios suficientes para
            # consultar la dependencia en request.vars.dependencia
            if not __acceso_permitido(user, 
                                int(request.vars.dependencia), 
                                    request.vars.es_espacio):
                redirect(URL('bienes_muebles'))
            espacios = list(db(
                              db.espacios_fisicos.dependencia == user_dep_id
                              ).select(db.espacios_fisicos.ALL))
            dep_nombre = db(db.dependencias.id == user_dep_id
                           ).select().first().nombre

            es_espacio = True                        
        # Si el jefe de seccion no ha seleccionado un espacio sino que acaba de 
        # entrar a la vista inicial de inventarios
        else:
            espacios = list(db(
                              db.espacios_fisicos.dependencia == user_dep_id
                              ).select(db.espacios_fisicos.ALL))
            dep_nombre = db(db.dependencias.id == user_dep_id
                           ).select().first().nombre

            es_espacio = True

            # Se muestra como inventario el egregado de los inventarios que
            # pertenecen a la seccion del jefe
            inventario = __get_inventario_dep(user_dep_id)

    # Si el usuario no es tecnico, para la base de datos es indiferente su ROL
    # pues la jerarquia de dependencias esta almacenada en la misma tabla
    # con una lista de adyacencias
    else:
        # Si el usuario ha seleccionado una dependencia o un espacio fisico
        if request.vars.dependencia:

            # Evaluando la correctitud de los parametros del GET 
            if not (__is_valid_id(request.vars.dependencia, db.dependencias) and
                    __is_bool(request.vars.es_espacio)):
                redirect(URL('bienes_muebles'))

            # Determinando si el usuario tiene privilegios suficientes para
            # consultar la dependencia en request.vars.dependencia
            if not __acceso_permitido(user, 
                                int(request.vars.dependencia), 
                                    request.vars.es_espacio):
                redirect(URL('bienes_muebles'))

            if request.vars.es_espacio == "True":
        
                # Se muestra el inventario del espacio
                espacio_id = request.vars.dependencia
                espacio = db(db.espacios_fisicos.id == espacio_id).select()[0]
                dep_nombre = espacio.nombre

                # Guardando el ID y nombre de la dependencia padre para el link 
                # de navegacion de retorno
                dep_padre_id = espacio.dependencia
                dep_padre_nombre = db(db.dependencias.id == dep_padre_id
                                    ).select().first().nombre
                # Guardando la unidad de adscripcion
                dep_padre_unid_ads = db(db.dependencias.id == dep_padre_id
                                    ).select().first().unidad_de_adscripcion

                espacio_visitado = True

                # Busca el inventario del espacio
                inventario = __get_inventario_espacio(espacio_id)

                material_pred = ['Acero','Acrílico','Madera','Metal','Plástico','Tela','Vidrio', 'Otro']
                color = ['Amarillo','Azul','Beige','Blanco','Dorado','Gris','Madera','Marrón','Mostaza','Naranja',
                'Negro','Plateado','Rojo','Rosado','Verde','Vinotinto','Otro color']
                unidad_med = ['cm','m']
                movilidad = ['Fijo','Portátil']
                uso = ['Docencia','Investigación','Extensión','Apoyo administrativo']
                nombre_cat = ['Maquinaria Construcción', 'Equipo Transporte', 'Equipo Comunicaciones', 
                'Equipo Médico', 'Equipo Científico Religioso', 'Equipo Oficina']
                cod_localizacion = ['150301','240107']
                localizacion = ['Edo Miranda, Municipio Baruta, Parroquia Baruta',
                'Edo Vargas, Municipio Vargas, Parroquia Macuto']

                # Si se esta agregando un nuevo BM, se registra en la DB
                if request.vars.nombre: # Verifico si me pasan como argumento el nombre del BM.
                    __agregar_bm(
                        request.vars.nombre,request.vars.no_bien,request.vars.no_placa, 
                        request.vars.marca, request.vars.modelo, request.vars.serial,
                        request.vars.descripcion, request.vars.material, request.vars.color,
                        request.vars.calibrar, request.vars.fecha_calibracion, request.vars.unidad, 
                        request.vars.ancho, request.vars.largo, request.vars.alto,
                        request.vars.diametro, request.vars.movilidad, request.vars.tipo_uso, request.vars.estatus, 
                        request.vars.nombre_cat, request.vars.subcategoria, request.vars.cod_loc, request.vars.localizacion, espacio, dep_padre_unid_ads, 
                        dep_padre_id, user_id, request.vars.clasificacion)

            else:
                # Se muestran las dependencias que componen a esta dependencia padre
                # y se lista el inventario agregado
                dep_id = request.vars.dependencia
                dep_nombre = db.dependencias(db.dependencias.id == dep_id).nombre
                dependencias = list(db(db.dependencias.unidad_de_adscripcion == dep_id
                                      ).select(db.dependencias.ALL))
                # Si la lista de dependencias es vacia, entonces la dependencia no 
                # tiene otras dependencias por debajo (podria tener espacios fisicos
                # o estar vacia)
                if len(dependencias) == 0:
                    # Buscando espacios fisicos que apunten a la dependencia escogida
                    espacios = list(db(db.espacios_fisicos.dependencia == dep_id
                                      ).select(db.espacios_fisicos.ALL))
                    es_espacio = True

                # Guardando el ID y nombre de la dependencia padre para el link 
                # de navegacion de retorno
                dep_padre_id = db(db.dependencias.id == request.vars.dependencia
                                 ).select().first().unidad_de_adscripcion
                # Si dep_padre_id es None, se ha llegado al tope de la jerarquia
                # y no hay un padre de este nodo
                if dep_padre_id:
                    dep_padre_nombre = db(db.dependencias.id == dep_padre_id
                                         ).select().first().nombre
                # Se muestra como inventario el egregado de los inventarios que
                # pertenecen a la dependencia del usuario
                inventario = __get_inventario_dep(dep_id)

        else:
            # Dependencia a la que pertenece el usuario o que tiene a cargo
            dep_id = user.f_dependencia
            dep_nombre = db.dependencias(db.dependencias.id == dep_id).nombre

            # Se muestran las dependencias que componen a la dependencia que
            # tiene a cargo el usuario y el inventario agregado de esta
            dependencias = list(db(db.dependencias.unidad_de_adscripcion == dep_id
                                  ).select(db.dependencias.ALL))

            # Se muestra como inventario el egregado de los inventarios que
            # pertenecen a la dependencia del usuario
            inventario = __get_inventario_dep(dep_id)

    return dict(dep_nombre=dep_nombre, 
                dependencias=dependencias, 
                espacios=espacios, 
                es_espacio=es_espacio,
                espacio_visitado=espacio_visitado,
                dep_padre_id=dep_padre_id,
                dep_padre_nombre=dep_padre_nombre,
                direccion_id=direccion_id,
                es_tecnico=es_tecnico,
                inventario=inventario,
                retroceder=retroceder,
                material_pred = material_pred,
                color_list = color,
                unidad_med = unidad_med,
                movilidad_list = movilidad,
                uso_list = uso,
                nombre_cat = nombre_cat,
                cod_localizacion = cod_localizacion,
                localizacion = localizacion,
                ) 


# Muestra un crud para añadir bienes muebles
def entrega0():
    grid_bm = SQLFORM.grid(db.bien_mueble)
    return locals()