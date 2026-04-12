import os
import re
import json
import glob
from flask import Flask, render_template, session, request, send_from_directory

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

    if message and context:
        bot_response = f"[MOCK] Pregunta: «{message}» con contexto de {len(json.loads(context) if context else {})} elementos seleccionados."
    elif message:
        bot_response = f"[MOCK] Pregunta recibida: «{message}». Aquí iría la respuesta del modelo local."
    elif context:
        bot_response = "[MOCK] He analizado tu selección actual. Aquí iría el consejo del asistente TFT."
    else:
        bot_response = "[MOCK] No he recibido ni pregunta ni contexto. ¡Selecciona algo o escribe una pregunta!"

    # --- Integración RAG (descomenta para activar) ---
    # import sys
    # sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    # from rag.search import classify_query
    # full_query = message
    # if context:
    #     ctx_dict = json.loads(context)
    #     ctx_str = ", ".join(f"{k} (x{v['qty']}, {v['type']})" for k, v in ctx_dict.items())
    #     full_query = f"Contexto actual: {ctx_str}. Pregunta: {message}"
    # collections = classify_query(full_query)
    # bot_response = llm.invoke(prompt)
    # ---

    display_message = message if message else "(sin mensaje — contexto enviado)"
    return render_template('partials/chat_message.html',
                           user_message=display_message,
                           bot_response=bot_response)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
