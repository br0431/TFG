# Asistente conversacional para Teamfight Tactics

Asistente conversacional para el set 16 del videojuego Teamfight Tactics, construido
sobre una arquitectura de Generación Aumentada por Recuperación (RAG) y ejecutado
íntegramente en local, sin dependencia de servicios externos.

El sistema ofrece dos modos de interacción. Un chat en lenguaje natural, que responde
consultas sobre campeones, objetos y composiciones en castellano y en inglés, y un
módulo de asesoramiento estratégico, que elabora una recomendación a partir de los
elementos que el jugador selecciona y del estado de su partida.

Trabajo de Fin de Grado del Grado en Tecnologías para la Sociedad de la Información,
Escuela Técnica Superior de Ingeniería de Sistemas Informáticos, Universidad
Politécnica de Madrid.

## Requisitos previos

- **Python 3.11**
- **Ollama** instalado en el equipo, con el modelo de lenguaje descargado:
  ```
  ollama pull llama3.1:8b
  ```
  La aplicación de Ollama debe estar en ejecución antes de arrancar el sistema, ya que
  la generación de respuestas se delega en el modelo servido por ella.
- **Google Chrome**, necesario únicamente para los scripts de recopilación de datos.

El sistema se ha desarrollado y probado sobre un equipo con procesador Intel Core i7 de
duodécima generación, 16 GB de memoria y tarjeta gráfica NVIDIA GeForce RTX 3050 Ti.

## Instalación

```
git clone https://github.com/br0431/TFG.git
cd TFG
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

En Linux o macOS, la activación del entorno virtual es `source .venv/bin/activate`.

La primera instalación descarga los modelos de embeddings y de BERTScore desde
Hugging Face, por lo que requiere conexión a internet y puede tardar varios minutos.

## Construcción de la base de conocimiento

La base vectorial no se versiona en el repositorio y debe generarse antes del primer
arranque. El proceso lee los ficheros JSON de `scrapping/data`, los serializa a texto
plano, los convierte en representaciones vectoriales y los almacena en tres colecciones
independientes:

```
python rag/embedding.py
```

El script crea el directorio `rag/chroma_db` e informa por consola del número de
documentos indexados en cada colección: 51 campeones, 36 objetos y 8 composiciones.

## Ejecución

Con Ollama en marcha y la base vectorial construida:

```
python UI/app.py
```

La interfaz queda disponible en `http://localhost:5000`.

## Uso

El panel izquierdo permite desplegar las secciones de campeones, objetos y componentes
y seleccionar los elementos de que se dispone en la partida, junto a los campos de fase,
nivel, oro y puntos de vida. El botón **Send Context** envía esa situación al módulo de
asesoramiento, que devuelve las acciones recomendadas por el motor de reglas y una
recomendación de composición elaborada por el modelo.

El panel derecho contiene el chat, que atiende consultas directas sobre el contenido del
juego con independencia de la selección realizada en el panel izquierdo. Ambos modos
funcionan por separado.

La primera consulta posterior al arranque tarda en torno a veinticinco segundos, ya que
en ella se cargan en memoria el modelo de embeddings, las colecciones y el modelo de
lenguaje. Las consultas sucesivas se resuelven en unos pocos segundos.

## Actualización del contenido ante un nuevo set

La renovación del contenido del juego se resuelve reejecutando las dos primeras fases,
sin intervenir sobre el modelo de lenguaje ni sobre la lógica de recuperación y
generación:

1. Ejecutar los scripts de recopilación para obtener los nuevos ficheros JSON. Los de
   campeones y objetos operan sobre la URL del elemento indicada en el propio script,
   mientras que el de composiciones recorre el listado de la fuente.
2. Volver a ejecutar `rag/embedding.py` para reconstruir las colecciones vectoriales.

La actualización requiere además dos tareas complementarias: incorporar a
`UI/static/images` las imágenes de los elementos nuevos y revisar los diccionarios de
equivalencias de `rag/translations.py`, de los que depende el tratamiento de las
consultas formuladas en castellano.

## Estructura del proyecto

```
TFG/
├── rag/
│   ├── search.py                      Clasificación de consultas, recuperación y generación
│   ├── embedding.py                   Serialización e indexación en ChromaDB
│   ├── translations.py                Diccionarios de equivalencias castellano-inglés
│   └── gameContext/
│       └── decision_engine.py         Motor de reglas sobre el estado de la partida
├── scrapping/
│   ├── scrapping_champions.py         Recopilación de campeones
│   ├── scrapping_items.py             Recopilación de objetos
│   ├── scrapping_comps.py             Recopilación de composiciones
│   └── data/                          Base documental en formato JSON
├── UI/
│   ├── app.py                         Aplicación Flask
│   ├── templates/                     Plantillas HTML con HTMX
│   └── static/                        Hoja de estilos e imágenes de los elementos
├── results/
│   └── bertscore_evaluation.py        Cálculo del valor F1 de BERTScore
├── testing/                           Pruebas exploratorias de la fase inicial
└── requirements.txt
```

## Evaluación

El script de evaluación automática calcula el valor F1 de BERTScore sobre los treinta
pares de respuesta esperada y respuesta obtenida que componen el conjunto de
evaluación, desglosado por nivel de dificultad e idioma:

```
python results/bertscore_evaluation.py
```

Los resultados completos, junto a la valoración manual de cada respuesta, se recogen en
los anexos de la memoria.

La carpeta `testing` contiene las pruebas exploratorias realizadas al inicio del
desarrollo para evaluar distintas tecnologías. No forman parte del sistema y sus
dependencias no se incluyen en `requirements.txt`.

## Sobre los datos

La base documental se ha obtenido mediante técnicas de *web scraping* sobre MetaTFT y
recoge información del set 16 del videojuego. Los datos se emplean con fines
exclusivamente educativos, en el marco de este Trabajo de Fin de Grado. Teamfight
Tactics es propiedad de Riot Games.

## Autor

Rodrigo Valiente Pérez
