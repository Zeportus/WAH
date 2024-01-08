from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import db
from threading import Thread
import waha

app = FastAPI()

app.mount("/static", StaticFiles(directory="styles"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get('/')
def main(request: Request):
    cookies = request.cookies
    if 'auth' not in cookies: return RedirectResponse('/login', status_code=302)
    
    auth = cookies['auth']
    if auth == 'admin': return RedirectResponse('/admin', status_code=302)
    elif auth: return RedirectResponse(f'/manager/{auth}', status_code=302)

@app.get('/login', response_class=HTMLResponse)
def get_login_page(request: Request):
    template_response = templates.TemplateResponse('login_panel.html', {'request' : request})
    template_response.delete_cookie('auth')
    return template_response

@app.get('/admin')
def get_admin_panel(request: Request):
    cookies = request.cookies
    if 'auth' in cookies and cookies['auth'] == 'admin':
        users = db.get_users()
        return templates.TemplateResponse('admin_panel.html', {'request' : request, 'users' : users})
    return 'Вы не авторизованы'        

@app.get('/manager/{login}')
def get_manager_panel(request: Request, login):
    cookies = request.cookies
    if 'auth' in cookies and cookies['auth'] == login:
        user_settings = db.get_user_seetings(login)
        user_autoanswers = db.get_user_auto_answers(login)
        user_phone = db.get_user_phone(login)

        return templates.TemplateResponse('manager_panel.html', {'request' : request, 'name' : login, 'phones' : user_settings[0], 'message' : user_settings[1],
                                                                'delay' : user_settings[2], 'auto_answers' : user_autoanswers, 'manager_phone' : user_phone
                                                                })
    return 'Вы не авторизованы'

@app.post('/auth')
def auth(login = Form(), password = Form()):
    if login == 'admin' and password == 'treg23':
        redirect_response = RedirectResponse('/admin', status_code=302)
        redirect_response.set_cookie('auth', 'admin')
        return redirect_response

    if db.check_user(login, password):
        redirect_response = RedirectResponse(f'/manager/{login}', status_code=302)
        redirect_response.set_cookie('auth', login)
        return redirect_response


@app.post('/admin_action')
def add_user(action = Form(), login = Form(), password = Form(default=None)):
    if action == 'Добавить' and login and password:
        db.add_user(login, password)
    elif action == 'Удалить' and login:
        db.del_user(login)
    
    return RedirectResponse('/admin', status_code=302)

@app.post('/manager_action/{login}')
def manager_action(login, action = Form(), phones = Form(), message = Form(), delay = Form(), trigger: list = Form(default=[]), answer: list = Form(default=[]), manager_phone = Form()):
    if action == 'Сохранить':
        db.save_user(login, phones, message, delay, trigger, answer, manager_phone)
    elif action == 'Добавить':
        db.add_empty_auto_answer(login)
    elif action == 'Отправить':
        phones = db.get_phones(login)
        thread = Thread(target=waha.start_spam, args=(phones, message, int(delay)))
        thread.run()
    else:
        db.del_auto_answer(action)
    return RedirectResponse(f'/manager/{login}', status_code=302)


@app.post('/waha_getter')
def waha_getter(request: dict):
    payload = request['payload']

    manager_phone = payload['to'][:-5]
    userId = payload['from']
    #userName = payload['_data']['notifyName']
    userMsg = payload['body']

    if db.check_phone(userId[:-5]):
        #db.stop_phone(userId[:-5])
        auto_info = db.get_auto_info(manager_phone)
        thread = Thread(target=waha.main, args=(userId, userMsg, auto_info))
        thread.run()


uvicorn.run(app, host='0.0.0.0', port=8008)