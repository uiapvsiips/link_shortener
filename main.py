import json
import uuid

from aiohttp import web


async def show_form(request):
    with open('form.html', 'r') as f:
        html = f.read()
    return web.Response(text=html, content_type='text/html')


async def create_link(request):
    data = await request.post()
    original_link = data.get('link')
    link_id = str(uuid.uuid4())[:6]
    links = read_links_from_file('links.json')
    links[link_id] = original_link
    write_links_to_file('links.json', links)
    return web.json_response({'id': link_id})


async def get_link(request):
    link_id = request.match_info.get('id')
    links = read_links_from_file('links.json')
    original_link = links.get(link_id)
    if original_link:
        return web.HTTPFound(original_link)
    else:
        return web.json_response({'error': 'Link not found'}, status=404)


def read_links_from_file(file_path):
    with open(file_path, 'r') as f:
        links = json.load(f)
    return links.get('links', {})


def write_links_to_file(file_path, links):
    with open(file_path, 'w') as f:
        json.dump({'links': links}, f)


app = web.Application()
app.add_routes([
    web.get('/', show_form),
    web.post('/', create_link),
    web.get('/{id}', get_link),
])

if __name__ == '__main__':
    web.run_app(app)
