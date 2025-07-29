from arabic_reshaper.arabic_reshaper import auto_config
from flask import Flask, request, render_template, redirect, session, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from pandas.core import methods
from werkzeug.security import check_password_hash, generate_password_hash
from xhtml2pdf import pisa
from io import BytesIO
import os
from sqlalchemy import create_engine,text
from datetime import timedelta
db_path="C:\\Users\\Hedi Moalla\\Desktop\\Stage Juillet 2025\\instance\\users_data.db"
if not os.path.exists(db_path):
    engine=create_engine("sqlite:///instance/users_data.db")
    with engine.begin() as connection:
        connection.execute(text("Create table division ( Id_division number(1) primary key, nom varchar(20) NOT NULL)"))
        connection.execute(text("Create table service ( Id_service number(2) primary key, nom varchar(20) NOT NULL, Id_division number(1) references division(Id_division))"))
        connection.execute(text("Create table user ( matricule number(5) primary key,nom varchar(40) NOT NULL,tel number(8) NOT NULL,password varchar(128) NOT NULL,acces varchar(5) NOT NULL,Id_service number(2)  references service(Id_service))"))
        connection.execute(text("Create table demande ( Id number(5) primary key,tel number(8) NOT NULL,status varchar(10) NOT NULL,matricule number(5)  references user(matricule))"))
        params=[{'Id_division':1, 'nom': 'Software'},{'Id_division':2, 'nom': 'Télécommunications'},{'Id_division':3, 'nom':'Hardware'},{'Id_division':4, 'nom':'Direction'}]
        connection.execute(text("Insert into division (Id_division, nom) values(:Id_division, :nom)"),params)
        params=[{'Id_service':1, 'nom': 'Web', 'Id_division':1},{'Id_service':2, 'nom': 'App', 'Id_division':1},{'Id_service':3, 'nom': 'IA', 'Id_division':1},{'Id_service':4, 'nom': 'Réseau', 'Id_division':2},{'Id_service':5, 'nom': 'Communication', 'Id_division':2},{'Id_service':6, 'nom': 'Cybersécurité', 'Id_division':2},{'Id_service':7, 'nom': 'CPU', 'Id_division':3},{'Id_service':8, 'nom': 'GPU', 'Id_division':3},{'Id_service':9, 'nom': 'TTL', 'Id_division':3},{'Id_service':10, 'nom': 'Gestion', 'Id_division':4},{'Id_service':11, 'nom': 'RH', 'Id_division':4},{'Id_service':12, 'nom': 'Relations externes', 'Id_division':4}]
        connection.execute(text("Insert into service (Id_service, nom, Id_division) values(:Id_service, :nom, :Id_division)"),params)
        pwrd=generate_password_hash('Mhedi.56')
        params={'matricule':10000,'nom':'Hedi','tel':56443199,'password':pwrd, 'acces':'Administrateur', 'Id_service':4}
        connection.execute(text("Insert into user (matricule, nom, tel, password, acces, Id_service) values(:matricule,:nom,:tel,:password,:acces,:Id_service)"),params)
        connection.execute(text("Insert into demande (Id, tel, status, matricule) values(1,97966166,'refused',1)"))
#with engine.connect("sqlite:///instance/users_data.db") as connection:
    #connection.execute(text("Update table division set nom='maintenance informatique et réseau' where nom"))

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users_data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class Demande(db.Model):
    __tablename__ = 'demande'
    Id = db.Column(db.Integer, primary_key=True)
    tel = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False)
    matricule = db.Column('matricule', db.Integer, db.ForeignKey('user.matricule'))
    user = db.relationship('User', backref='demandes')

class User(db.Model):
    __tablename__ = 'user'
    matricule = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(40), nullable=False)
    tel = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    acces = db.Column(db.String(5), nullable=False)
    Id_service = db.Column('Id_service', db.Integer, db.ForeignKey('service.Id_service'))
    service = db.relationship('Service', backref='users')

class Service(db.Model):
    __tablename__ = 'service'
    Id_service = db.Column('Id_service', db.Integer, primary_key=True)
    nom = db.Column('nom', db.String(40), nullable=False)
    Id_division = db.Column('Id_division', db.Integer, db.ForeignKey('division.Id_division'))
    division = db.relationship('Division', backref='services')

class Division(db.Model):
    __tablename__ = 'division'
    Id_division = db.Column('Id_division', db.Integer, primary_key=True)
    nom = db.Column('nom', db.String(40), nullable=False)
def verify_tel(tel):
    test=0
    if(tel.isdigit()==False):
        return "Le numéro doit être composé de chiffres uniquement."
    elif(len(tel)!=8):
        if(len(tel)==7):
            return "Le numéro manque un chiffre."
        elif(len(tel)<7):
            return f"Le numéro manque {8-len(tel)} chiffres."
        elif(len(tel)==9):
            return "Le numéro contient un chiffre extra."
        else:
            return f"Le numéro contient {len(tel)-8} chiffres extras."
    elif (int(tel[0]) not in [2,3,4,5,7,9]):
        return f"Un numéro de téléphone ne commence pas par {tel[0]}."
    return test
def verify_pwrd(pwrd):
    test=0
    if(len(pwrd)<8):
        if(len(pwrd)==7):
            return 'Ajouter un caractére au minimum.'
        else:
            return f'Ajouter {8-len(pwrd)} caractéres au minimum.'
    i=0
    while(i<len(pwrd)):
        if(pwrd[i].isdigit()==True):
            i=len(pwrd)+10
        else:
            i=i+1
    if(i<=len(pwrd)):
        return "Le mot de passe ne contient aucun chiffre."
    i=0
    while(i<len(pwrd)):
        if('a'<=pwrd[i]<='z'):
            i=len(pwrd)+10
        else:
            i=i+1
    if(i<=len(pwrd)):
        return 'Le mot de passe ne contient aucun caractère minuscule.'
    i=0
    while(i<len(pwrd)):
        if('A'<=pwrd[i]<='Z'):
            i=len(pwrd)+10
        else:
            i=i+1
    if(i<=len(pwrd)):
        return 'Le mot de passe ne contient aucun caractère majuscule.'
    i=0
    while(i<len(pwrd)):
        if not('A'<=pwrd[i]<='Z' or 'a'<=pwrd[i]<='z' or (pwrd[i].isdigit()==True and 0<=int(pwrd[i])<=9)):
            i=len(pwrd)+10
        else:
            i=i+1
    if(i<=len(pwrd)):
        return 'Le mot de passe ne contient aucun symbôle.'
    return test
@app.route('/')
def hello_world():
    if session:
        matricule = session.get('matricule')
        if not matricule:
            return render_template('dashboard.html', user=None, nouveau=1)
        user = User.query.get(matricule)
        return render_template("dashboard.html",user=user, matricule=matricule, session=session)
    return render_template('dashboard.html', user=None, nouveau=1)
@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method=='POST':
        return render_template('auth.html')
    return request.url
@app.route('/login', methods=['POST', 'GET'])
def login():
    matricule = session.get('matricule')
    if matricule:
        user = User.query.get(matricule)
        matricule=user.matricule
        return render_template('dashboard.html', user=user, matricule=matricule, session=session)
    else:
        matricule = request.form.get('matricule')
        pwrd = request.form['mot de passe']
        user = User.query.filter_by(matricule=matricule).first()
        if not user:
            return render_template('auth.html', info="Utilisateur introuvable")
        if not check_password_hash(user.password, pwrd):
            return render_template('auth.html', info="Mot de passe incorrect")
        else:
            session.permanent = True
            session['matricule']=user.matricule
            return render_template('dashboard.html', user=user, matricule=matricule, session=session)
@app.before_request
def make_session_permanent():
    session.permanent = True
@app.route('/add', methods=['GET', 'POST'])
def add():
    if not session:
        return render_template('dashboard.html', user=None)
    if 'matricule' in session:
        matricule = session.get('matricule')
        if not matricule:
            return render_template('dashboard.html', user=None)
        user = User.query.get(matricule)
        if user.acces == 'Agent':
            return render_template('acces-error.html')
        else:
            return render_template('ajout.html')
    return render_template('dashboard.html', user=None)
@app.route('/request-tel', methods=['GET', 'POST'])
def request_tel():
    if not session:
        return render_template('dashboard.html', user=None)
    if 'matricule' in session:
        matricule = session.get('matricule')
        if not matricule:
            return render_template('dashboard.html', user=None)
        user = User.query.get(matricule)
        if user.acces == 'Agent':
            return render_template('acces-error.html')
    else:
        return render_template('dashboard.html', user=None)
    requests=Demande.query.filter_by(status='pending')
    if requests.count()==0:
        requests=0
    return render_template('demande.html',requests=requests)
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return render_template("dashboard.html", user=None)
@app.route('/return-dashboard', methods=['GET', 'POST'])
def return_dashboard():
    matricule = session.get('matricule')
    if not matricule:
        return render_template('dashboard.html', user=None)
    user = User.query.get(matricule)
    return render_template('dashboard.html', user=user, matricule=user.matricule, session=session)
@app.route('/return-profil', methods=['GET', 'POST'])
def return_profil():
    matricule = session.get('matricule')
    if not matricule:
        return render_template('dashboard.html', user=None)
    user = User.query.get(matricule)
    return render_template('profil.html',user=user)
@app.route('/return-search', methods=['GET', 'POST'])
def return_search():
    if not session:
        return render_template('dashboard.html', user=None)
    if 'matricule' in session:
        matricule = session.get('matricule')
        if not matricule:
            return render_template('dashboard.html', user=None)
        user = User.query.get(matricule)
        if user.acces == 'Agent':
            return render_template('acces-error.html')
        return redirect(url_for('search_admin'))
    return render_template('dashboard.html', user=None)
@app.route('/consult/<int:matricule>', methods=['GET', 'POST'])
def consult(matricule):
    matri=session.get('matricule')
    if matri:
        if matricule==matri:
            user=User.query.filter_by(matricule=matricule).first()
            return render_template('profil.html',user=user)
        else:
            return render_template('profil.html',user=None)
    return render_template('dashboard.html', user=None)
@app.route('/attribute', methods=['POST', 'GET'])
def attribute():
    if request.method == "POST":
        matricule = request.form['matricule']
        nom = request.form['nom']
        tel = request.form['tel']
        service = request.form['service']
        acces = request.form['type']
        pwrd = request.form['pwrd']
        test_pwrd = verify_pwrd(pwrd)
        test_tel =verify_tel(tel)
        test_user=User.query.get(matricule)
        if (test_user):
             return render_template('ajout.html',info_tel=f"Matricule {matricule} existe déjà, elle est attribuée à {test_user.nom}")
        if (test_pwrd != 0 and test_tel != 0):
            return render_template('ajout.html',info_tel=test_tel,info_pwrd=f"Ce mot de passe n'est pas fort! {test_pwrd}")
        elif (test_tel != 0):
            return render_template('ajout.html',info_tel=test_tel)
        elif (test_pwrd != 0):
            return render_template('ajout.html',info_pwrd=f"Ce mot de passe n'est pas fort! {test_pwrd}")
        service_obj = Service.query.filter_by(Id_service=service).first()
        if not service_obj:
            return render_template('ajout.html', user=user, info_service="Service introuvable")
        hashed_pwrd = generate_password_hash(pwrd)
        newUser = User(matricule=matricule, nom=nom, tel=tel,password=hashed_pwrd, Id_service=service_obj.Id_service, acces=acces)
        try:
            db.session.add(newUser)
            db.session.commit()
            return render_template("ajout.html",info_ajout="Ajout effectué avec succès")
        except Exception as e:
            print(f"ERROR {e}")
            return f"ERROR {e}"
    else:
        return render_template('ajout.html')
@app.route('/search-admin', methods=['POST', 'GET'])
def search_admin():
    if session:
        matricule = session.get('matricule')
        if not matricule:
            return render_template('dashboard.html', user=None)
        user = User.query.get(matricule)
    else:
        return render_template("dashboard.html", user=None)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    if request.method == "POST":
        search = request.form.get('search', '')
        service = request.form.get('service', '')
        page = 1
    else:
        search = request.args.get('search', '')
        service = request.args.get('service', '')
    query_obj = query(search, service)
    results = query_obj.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('search-admin.html',user=user, results=results, search=search)

def query(q, service):
    query_obj = User.query.join(Service).join(Division)
    if service:
        try:
            service_id = int(service)
            query_obj = query_obj.filter(Service.Id_service == service_id)
        except ValueError:
            pass
    if q:
        query_obj = query_obj.filter(
            (User.nom.ilike(f"%{q}%")) | (User.tel.cast(db.String).ilike(f"%{q}%"))
        )
    query_obj = query_obj.order_by(Division.nom).order_by(Service.nom).order_by(User.matricule)
    return query_obj

@app.route('/search-agent', methods=['POST', 'GET'])
def search():
    if session:
        matricule = session.get('matricule')
        if not matricule:
            return render_template('dashboard.html', user=None)
        user = User.query.get(matricule)
    else:
        return render_template("dashboard.html", user=None)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    if request.method == "POST":
        search = request.form.get('search', '')
        service = request.form.get('service', '')
        page = 1
    else:
        search = request.args.get('search', '')
        service = request.args.get('service', '')
    query_obj = query(search, service)
    results = query_obj.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('search-agent.html', results=results, search=search, user=user)
@app.route('/edit-all/<int:matricule>', methods=['POST', 'GET'])
def edit_all(matricule):
    matri=session.get('matricule')
    if matri:
        if matricule == matri:
            user=User.query.filter_by(matricule=matricule).first()
            return render_template('edit.html', user=user, matricule=matricule, profil=1)
        return render_template('acces-error.html')
    return render_template('dashboard.html',user=None)
@app.route('/edit-agent/<int:matricule>', methods=['POST', 'GET'])
def edit_agent(matricule):
    user=User.query.filter_by(matricule=matricule).first()
    matri=session.get('matricule')
    if matri:
        if matricule==matri:
            return render_template('edit-agent.html', user=user, matricule=matricule)
        else:
            return render_template('acces-error.html')
    return render_template('dashboard.html', user=None)
@app.route('/edit-pwrd/<int:matricule>', methods=['POST', 'GET'])
def edit_pwrd(matricule):
    if (matricule==session['matricule']):
        user = User.query.get(matricule)
        if request.method == "POST":
            pwrd = request.form.get('pwrd')
            test=verify_pwrd(pwrd)
            if (test!=0):
                return render_template('edit-agent.html', user=user, info_pwrd=f"Ce mot de passe n'est pas fort! {test}")
            hpwrd=generate_password_hash(pwrd)
            update_data = {'password': hpwrd}
            try:
                User.query.filter_by(matricule=matricule).update(update_data)
                db.session.commit()
                return render_template("profil.html", user=user, info_pwrd="Mot de passe modifié avec succès")
            except Exception as e:
                print(f"ERROR {e}")
                return render_template('edit-agent.html', user=user, info_pwrd=f"Erreur lors de la modification: {e}")
        else:
            return render_template('edit-agent.html', user=user)
    return("acces-error.html")
@app.route('/edit/<int:matricule>', methods=['POST', 'GET'])
def edit(matricule):
    print(f"Edit called for {matricule}, method: {request.method}")
    if session and 'matricule' in session:
        matri=session['matricule']
        user = User.query.get(matri)
        ag=User.query.get(matricule)
        if not ag:
            return render_template('edit.html', info_edit="Utilisateur introuvable.")
        if matri==matricule:
            profil=1
        else:
            profil=0
        if request.method == "POST":
            nom = request.form.get('nom')
            tel = request.form.get('tel')
            service = request.form.get('service')
            acces = request.form.get('type')
            pwrd = request.form.get('pwrd')
            test_pwrd = verify_pwrd(pwrd)
            test_tel = verify_tel(tel)
            if (test_pwrd != 0 and test_tel != 0):
                return render_template('edit.html', profil=profil, info_tel=test_tel, info_pwrd=f"Ce mot de passe n'est pas fort! {test_pwrd}", user=ag)
            elif (test_tel != 0):
                return render_template('edit.html', profil=profil, info_tel=test_tel, user=ag)
            elif (test_pwrd != 0):
                return render_template('edit.html', profil=profil, info_pwrd=f"Ce mot de passe n'est pas fort! {test_pwrd}", user=ag)
            service_obj = Service.query.filter_by(nom=service).first()
            if not service_obj:
                print(f"[DEBUG] Service introuvable: {service}")
                return render_template('edit.html', profil=profil, user=ag, info_edit="Service introuvable")
            s = service_obj.Id_service
            update_data = {'nom': nom, 'tel': tel, 'Id_service': s, 'acces': acces}
            if pwrd:
                update_data['password'] = generate_password_hash(pwrd)
            try:
                User.query.filter_by(matricule=matricule).update(update_data)
                db.session.commit()
                return render_template("edit.html", profil=profil, user=ag, info_edit=f"{acces} modifié avec succès")
            except Exception as e:
                print(f"[ERROR] Exception lors de la modification: {e}")
                return render_template('edit.html', profil=profil, user=ag, info_edit=f"Erreur lors de la modification: {e}")
        else:
            return render_template('edit.html',profil=profil, user=ag)
    return render_template('acces-error.html')
@app.route('/delete/<int:matricule>', methods=['POST', 'GET'])
def delete(matricule):
    if session and "matricule" in session:
        user = User.query.get(matricule)
        matri=session['matricule']
        admin=User.query.get(matri)
        query_obj = query('', '')
        results = query_obj.paginate(page=1, per_page=10, error_out=False)
        if not user:
            return render_template("search-admin.html", info_delete="Utilisateur introuvable ou déjà supprimé.", user=admin, results=results)
        try:
            db.session.delete(user)
            db.session.commit()
            query_obj = query('', '')
            results = query_obj.paginate(page=1, per_page=10, error_out=False)
            return render_template("search-admin.html", info_delete="Utilisateur supprimé de la base de données", user=admin, results=results)
        except Exception as e:
            print(f"ERROR {e}")
            return render_template("search-admin.html", info_delete=f"Erreur lors de la suppression: {e}", user=admin, results=results)
    return render_template("acces-error.html")
@app.route('/edit-tel', methods=['POST', 'GET'])
def edit_tel():
    matricule = session.get('matricule')
    if not matricule:
        return render_template("acces-error.html")
    user= User.query.get(matricule)
    if request.method == "POST":
        tel=request.form['tel']
        test_tel =verify_tel(tel)
        if (test_tel != 0):
            return render_template('edit-agent.html',info_tel=test_tel)
        last_demande=db.session.query(Demande).order_by(Demande.Id.desc()).first()
        id=int(last_demande.Id)+1
        try:
            new_demande=Demande(matricule=matricule, tel=tel, status='pending', Id=id)
            db.session.add(new_demande)
            db.session.commit()
            return render_template("profil.html", user=user, info_tel="Votre demande est en cours, acceptation d'un administrateur requis")
        except Exception as e:
            return f"ERROR {e}"
    else:
        return render_template("profil.html", user=user)
@app.route('/download', methods=['POST'])
def download_pdf():
    search = request.form.get('search', '')
    division = request.form.get('division', '')
    query_obj = query(search, division)
    results = query_obj
    html = render_template('pdf.html', results=results)
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=pdf)

    if pisa_status.err:
        return "Erreur lors de la création du PDF"

    pdf.seek(0)
    response = make_response(pdf.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=results.pdf'
    return response
@app.route('/handle-request/<int:Id>/<string:action>', methods=['GET','POST'])
def handle_request(Id, action):
    req = Demande.query.get(Id)
    if action == 'Acceptation':
        agent = User.query.get(req.matricule)
        agent.tel = req.tel
        req.status = 'accepted'
    elif action == 'Refus':
        req.status = 'refused'
    db.session.commit()
    requests=Demande.query.filter_by(status='pending')
    return render_template("demande.html", info_tel=f"Décision prise: {action}", requests=requests)

if __name__ == "__main__":
    app.run(debug=True)


