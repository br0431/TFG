import os
import re
import sys
import json
import glob
from flask import Flask, render_template, session, request, send_from_directory

# Añadimos la raíz del proyecto al path para poder importar rag/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rag.gameContext.decision_engine import get_decisions
from rag.search import ask

app = Flask(__name__)
app.secret_key = 'tft-set16-secret-key-2024'

DATA_DIR   = os.path.join(os.path.dirname(__file__), '..', 'scrapping', 'data')
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')


def normalize(text):
    return re.sub(r'[_\-&\s]', '', text).lower()


def resolve_image(slug, folder, prefix):
    filename = f'{prefix}{normalize(slug)}.png'
    full = os.path.join(IMAGES_DIR, folder, filename)
    if os.path.exists(full):
        return f'/static/images/{folder}/{filename}'
    return ''


def load_json_dir(subdir, img_folder, img_prefix):
    pattern = os.path.join(DATA_DIR, subdir, '*.json')
    result = []
    for filepath in sorted(glob.glob(pattern)):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        stem = os.path.splitext(os.path.basename(filepath))[0]
        data['slug'] = stem
        data['image_path'] = resolve_image(stem, img_folder, img_prefix)
        result.append(data)
    return result


def load_components():
    pattern = os.path.join(IMAGES_DIR, 'COMPONENTS', 'tft_item_*.png')
    result = []
    for filepath in sorted(glob.glob(pattern)):
        filename = os.path.basename(filepath)
        slug = filename.replace('tft_item_', '').replace('.png', '')
        result.append({
            'name': slug.capitalize(),
            'slug': slug,
            'image_path': f'/static/images/COMPONENTS/{filename}',
        })
    return result


champions  = load_json_dir('champions', 'CHAMPS',  'tft16_')
items      = load_json_dir('items',     'ITEMS',   'tft_item_')
components = load_components()

DATASETS = {
    'champions':  champions,
    'items':      items,
    'components': components,
}


@app.route('/')
def index():
    return render_template('index.html',
                           champions=champions,
                           items=items,
                           components=components)


@app.route('/api/grid/<tipo>')
def api_grid(tipo):
    selected = session.get('selected', {})
    return render_template('partials/icon_grid.html',
                           items=DATASETS.get(tipo, []),
                           tipo=tipo,
                           selected=selected)


@app.route('/select', methods=['POST'])
def select():
    name  = request.form.get('name', '').strip()
    tipo  = request.form.get('type', '')
    image = request.form.get('image', '')
    if not name:
        selected = session.get('selected', {})
        return render_template('partials/selected_zone.html', selected=selected)
    selected = session.get('selected', {})
    if name in selected:
        if selected[name]['qty'] < 3:
            selected[name]['qty'] += 1
    else:
        selected[name] = {'qty': 1, 'type': tipo, 'image': image}
    session['selected'] = selected
    return render_template('partials/selected_zone.html', selected=selected)


@app.route('/deselect', methods=['POST'])
def deselect():
    name = request.form.get('name', '').strip()
    selected = session.get('selected', {})
    if name in selected:
        selected[name]['qty'] -= 1
        if selected[name]['qty'] <= 0:
            del selected[name]
    session['selected'] = selected
    return render_template('partials/selected_zone.html', selected=selected)


@app.route('/clear', methods=['POST'])
def clear():
    session['selected'] = {}
    return render_template('partials/selected_zone.html', selected={})


@app.route('/chat', methods=['POST'])
def chat():
    message = request.form.get('message', '').strip()
    context = request.form.get('context', '').strip()

    # Construir la query combinando contexto seleccionado + pregunta del usuario
    full_query = message
    if context:
        try:
            ctx_dict = json.loads(context)
            if ctx_dict:
                ctx_str = ", ".join(
                    f"{name} (x{v['qty']}, {v['type']})"
                    for name, v in ctx_dict.items()
                )
                full_query = f"Current board context: {ctx_str}. Question: {message}"
        except (json.JSONDecodeError, KeyError):
            pass

    if not full_query:
        bot_response = "Please write a question or select something from the board first."
    else:
        try:
            bot_response = ask(full_query)
        except Exception as e:
            bot_response = f"Error connecting to the RAG system: {e}"

    display_message = message if message else "(no message — context sent)"
    return render_template('partials/chat_message.html',
                           user_message=display_message,
                           bot_response=bot_response)


@app.route('/advice', methods=['POST'])
def advice():
    # Datos del formulario de situación
    phase = request.form.get('phase', '').strip()
    level = request.form.get('level', '0').strip()
    gold  = request.form.get('gold',  '0').strip()
    hp    = request.form.get('hp',    '100').strip()

    # Validación básica de fase
    if not re.match(r'^[1-7]-[1-7]$', phase):
        return render_template('partials/advice_response.html',
                               error="Formato de fase incorrecto. Usa el formato X-Y (ej. 3-2).")

    level = int(level) if level.isdigit() else 0
    gold  = int(gold)  if gold.isdigit()  else 0
    hp    = int(hp)    if hp.isdigit()    else 100

    # Campeones e ítems vienen del tablero seleccionado en la sesión
    selected   = session.get('selected', {})
    champions  = [name for name, v in selected.items() if v['type'] == 'champions']
    items      = [name for name, v in selected.items() if v['type'] in ('items', 'components')]

    # Motor de decisiones
    result = get_decisions(phase, level, gold, hp, champions, items)

    # El prompt enriquecido va al RAG
    try:
        bot_response = ask(result['prompt'])
    except Exception as e:
        bot_response = f"Error conectando con el sistema RAG: {e}"

    return render_template('partials/advice_response.html',
                           rules=result['rules'],
                           bot_response=bot_response,
                           error=None)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
