from app import app, db, lm
from flask import render_template, request, g, redirect, url_for, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from .forms import SignupForm, LoginForm
from .models import User, File
from .authMethods import get_auth_flow, get_gd_auth_flow
import pickle
import httplib2
from googleapiclient.discovery import build
from datetime import datetime
from dropbox.client import DropboxClient, DropboxOAuth2Flow

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title = 'Home')

@app.route('/signup', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def signup():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    else:
        return render_template("signup.html", title = "Sign Up", form = form)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username = form.username.data).first()
        print User.query.limit(100).all()
        if user is not None and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('index'))
    return render_template("login.html", title = "Log In", form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def before_request():
    g.user = current_user

@login_required
@app.route('/dropbox-auth-start')
def dropbox_auth_start():
    return redirect(get_auth_flow().start())

@app.route('/user/<username>', methods = ['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username = username).first()
    if user == None or not username == current_user.username:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if request.form.get('db_in') == "Log In":
            return redirect(url_for('dropbox_auth_start'))
        elif request.form.get('db_in') == "Log Out":
            return redirect(url_for('account_logout', source = "db"))
        if request.form.get('gd_in') == "Log In":
            return google_auth_start()
        elif request.form.get('gd_in') == "Log Out":
            return redirect(url_for('account_logout', source = "gd"))
    return render_template('user.html', user = user)

@login_required
def google_auth_start():
    return redirect(get_gd_auth_flow().step1_get_authorize_url())

@login_required
def dropbox_auth_start():
    return redirect(get_auth_flow().start())

@login_required
@app.route("/google-auth-finish")
def google_auth_finish():
    username = current_user.username
    code = request.args.get('code')
    access_credential = get_gd_auth_flow().step2_exchange(code)
    user = User.query.filter_by(username = current_user.username).first()
    user.gd_access_token = pickle.dumps(access_credential)
    db.session.commit()
    user = User.query.filter_by(username = current_user.username).first()
    return redirect(url_for("user", username = username))

@app.route('/dropbox-auth-finish')
def dropbox_auth_finish():
    username = current_user.username
    access_token, user_id, url_state = get_auth_flow().finish(request.args)
    user = User.query.filter_by(username = username).first()
    user.db_access_token = access_token
    db.session.commit()
    return redirect(url_for("user", username = username))

@login_required
@app.route('/account-logout/<source>')
def account_logout(source):
    username = current_user.username
    user = User.query.filter_by(username = username).first()
    if source == "gd":
        user.gd_access_token = None
    elif source == "db":
        user.db_access_token = None
    db.session.commit()
    return redirect(url_for("user", username = username))

@login_required
@app.route('/list-files')
def list_files(path = ""):
    user = current_user
    parent = File.query.filter_by(owner_id = user.id, path = path).first()
    if parent:
        print parent.last_updated
    elif path == 'root':
        getFile('root', False)
    elif path == '/':
        getFile('/', True)
    elif path == "":
        getFile("",False )
    return redirect(url_for("user", username = user.username))

@login_required
def getFile(path, dropbox):
    user = current_user
    if dropbox:
        getDropbox(path)
    elif path == "" and not dropbox:
        pass
    return redirect(url_for("user", username = user.username))

def getDropbox(path):
    db_access_token = user.db_access_token
    client = DropboxClient(str(db_access_token))
    metadata = client.metadata(path)
    for content in metadata['contents']:
        title = content['path'][content['path'].rfind('/')+1:]
        modified = content['modified'][:-6]
        datetime_modified = datetime.strptime(modified, "%a, %d %b %Y %X")
        name = File(current_user.id, title, content['path'], dropbox, content['is_dir'], datetime_modified, None)
        db.session.add(name)
        db.session.commit()
    for f in current_user.files:
        print f


def getDrive(path):
    user = current_user
    if user.gd_access_token is None:
        return redirect(url_for("user", username = user.username))
    credential = user.gd_access_token
    credential = pickle.loads(credential)
    http = httplib2.Http()
    if credential.access_token_expired:
        credential.refresh(http)
    http = httplib2.Http()
    http = credential.authorize(http)
    drive_service = build('drive', 'v2', http = http)
    results =  drive_service.children().list(folderId = path).execute()

    opening_file = get_file(path, user.get("username"))
    if (not opening_file.get('last_updated') is None):
        if (datetime.now()- datetime.strptime(str(opening_file['last_updated'])[:18], "%Y-%m-%dT%H:%M:%S")).seconds<3600:
            cur2 = list(g.db.execute('SELECT * from file WHERE parent = ? and owner = ? and dropbox = ? ', [path, user.get('username'), False]))
            return json.dumps(cur2)
    g.db.execute('UPDATE file SET last_updated = ? WHERE owner = ? and content_path = ?', [str(datetime.now().isoformat()), user.get("username"), path])
    g.db.commit()
    credential = user['gd_access_token']
    credential = pickle.loads(credential)
    http = httplib2.Http()
    if credential.access_token_expired:
        credential.refresh(http)
    http = httplib2.Http()
    http = credential.authorize(http)
    drive_service = build('drive', 'v2', http = http)
    results =  drive_service.children().list(folderId = path).execute()
    print "Google API REQUEST"
    for child in results.get('items', []):
        metadata = drive_service.files().get(fileId = child['id']).execute()
        folder = metadata.get('mimeType') == 'application/vnd.google-apps.folder'
        g.db.execute('INSERT or REPLACE into file (ID, owner, name, parent, content_path, dropbox, folder) values ((SELECT ID FROM file WHERE content_path = ? and owner = ?),?,?,?,?,?,?)', [ metadata.get('id'), user.get("username"), user.get("username"), metadata.get('title'), path, metadata.get('id'), False, folder])
    g.db.execute('UPDATE file SET last_updated = ? WHERE owner = ? and content_path = ?', [str(datetime.now().isoformat()), user.get("username"), path])
    g.db.commit()
    cur3 = list(g.db.execute('SELECT * from file WHERE owner = ? and parent = ? and dropbox = ?', [user.get("username"), path, False]))
    return json.dumps(cur3)

