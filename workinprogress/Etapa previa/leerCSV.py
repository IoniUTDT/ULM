import pandas

'''
Esta funcion lo que hace es interpretar un CSV generado por el programa SPDPS donde se escanean formularios en forma automatica. El programa interpreta una estructura anidada de secciones y preguntas donde (excepto en las preguntas que tienen una unica escala de valores preestablecida) cada casillero marcado se asocia a una variable booleana, bajo un encabezado que es una combinacion de indices de la forma n1_n2_n3_n4 con n1 el numero de seccion, n2 el numero de pregunta, n3 las opciones y n4 las subopciones en caso de que corresponda. A partir de este CSV y con la informacion del pdf original del cuestionario necesitamos reconstruir los titulos originales de las preguntas y las respuestas dadas. 

Para eso construimos un archivo auxiliar (fileCodigos) que tiene la informacion del formulario necesaria estructuada en bloques. Cada bloque corresponde a una pregunta y esta separado del siguiente por una linea en blanco. Cada bloque tiene una primer linea con el texto correspondiente al titulo de la pregunta y un anexo "_M" para indicar que espera opciones multiples si corresponde. Una segunda linea que indica cual es la combinacion de indices que apuntan a la pregunta en cuestion, esta combinacion omite la iteracion sobre el ultimo indice que recorre las opciones de la pregunta en cuestion. Un conjunto arbitrariamente largo de lineas donde cada linea corresponde al titulo de cada una de las opciones incluidas en la pregunta respetando el orden establecido en el formulario. 

El programa tiene que elegir, si se trata de una pregunta de opcion multiple, genera una lista y agrega cada una de las opciones marcadas. Si se trata de una pregunta con escala de valores simplemente reemplaza el titulo de la columna, y si se trata de una pregunta donde debe haber una unica opcion seleccionada, la encuentra y reemplaza el valor por dicho titulo o genera un NS/NC o un Null segun haya 0 o mas de una opcion marcada.

A continuacion se presenta un ejemplo:

JustificacionSecundaria_M
2_3
Calor
Telequinesis
Magnetismo
Cosmica
Cuantica
Presion
Aura
Electricidad
Otra

En este caso se debe generar una lista bajo el encabezado "Justifiacion secundaria" donde la opciones que pueden estar incluidad son las que se mencionan y que se corresponden con los encabezados originales: 2_3_0 , 2_3_1, ... , 2_3_8

Para manipular los datos se utiliza Pandas DataFrame
'''
def leerCSV (fileCSV, fileCodigos):

	data = pandas.read_csv(fileCSV)
	with open(fileCodigos) as f:
		lineas = f.readlines()

	grupos = []
	subGrupo = []

	for linea in lineas:
		if linea == "\n":
			grupos.append(subGrupo)
			subGrupo = []
		else:
			subGrupo.append(linea.split('\n')[0])
	if not subGrupo == []:
		grupos.append(subGrupo)

	for grupo in grupos:
		encabezado = grupo[0]
		multiples = False
		if encabezado[-2:] == '_M':
			multiples=True
			encabezado = encabezado[:-2]
		inicio = grupo[1]
		opciones = grupo[2::]

		if len(opciones)>0:
			titulos = [inicio+'_'+str(indice) for indice in range(len(opciones))]
		else:
			titulos = [grupo[1]]
		mapeo = {x:y for x,y in zip(titulos,opciones)}

		if len(titulos) > 1:
			if not multiples:
				data[encabezado] = data[titulos].idxmax(axis=1)
				data[encabezado].replace(mapeo, inplace=True)
				data.loc[data[titulos].sum(axis=1)<1, encabezado] = 'NS/NC'
				data.loc[data[titulos].sum(axis=1)>1, encabezado] = 'Null'
			else:
				data[encabezado] = [[]] * len(data)
				for titulo in titulos:
					data[encabezado] = [x if y == 0 else x + [mapeo[titulo]] for x,y in zip(data[encabezado],data[titulo])]
		else:
			data[encabezado] = data[titulos]
		data = data.drop(titulos, 1)
	return data
