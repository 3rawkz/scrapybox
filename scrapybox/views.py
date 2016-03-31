# import asyncio
import logging
import logging.handlers
import aiohttp
import aiohttp_jinja2

logger = logging.getLogger(__name__)


@aiohttp_jinja2.template('home.j2.html')
def default(request):
    return {}


@aiohttp_jinja2.template('sockettest.j2.html')
def sockettest(request):
    return {}


class SocketStream():
    def __init__(self, socket):
        self.socket = socket

    def write(self, message):
        if message:
            message = message.replace('\n', '')  # debug
            self.socket.send_str('_.-~+=>^ ({})'.format(message[:99]))


async def socketconn(request):

    ws = aiohttp.web.WebSocketResponse()
    logger.debug('WebSocket opened {}'.format(ws))
    await ws.prepare(request)
    logger.debug('WebSocket prepared {}'.format(ws))

    formatter = logging.Formatter('[%(name)s.%(funcName)s] %(levelname)s: %(message)s')
    handler = logging.StreamHandler(SocketStream(ws))
    handler.terminator = ''
    handler.setFormatter(formatter)
    socket_logger = logging.getLogger(str(id(object())))
    # socket_logger.propagate = False
    socket_logger.setLevel(logging.DEBUG)
    socket_logger.addHandler(handler)
    # logging.root.addHandler(handler)

    import scrapybox.api
    class Request():
        POST = None
        async def post(self):
            self.POST = {'yield_item': True, 'settings.HTTPCACHE_ENABLED': True}
    response = await scrapybox.api.parse_post(Request())
    logger.debug('Response {} keys: {}'.format(len(response), str(response)[:200]))

    socket_logger.removeHandler(handler)
    # logging.root.removeHandler(handler)
    ws.send_str('close')

    async for msg in ws:
        logger.debug('WebSocket received {}'.format(msg))
        if msg.tp == aiohttp.MsgType.text:
            if msg.data == 'close':
                await ws.close()
            else:
                ws.send_str(msg.data + '/answer')
        elif msg.tp == aiohttp.MsgType.error:
            logger.warning('WebSocket error: {}'.format(ws.exception()))

    logger.debug('WebSocket closed {}'.format(ws))

    return ws

# @asyncio.coroutine
# def handler(request):
#     context = {'name': 'Andrew', 'surname': 'Svetlov'}
#     response = aiohttp_jinja2.render_template(
#         'tmpl.j2.html', request, context)
#     response.headers['Content-Language'] = 'ru'
#     return response
