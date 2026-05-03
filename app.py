from flask import Flask,render_template,request,url_for,session,redirect
import hashlib
from dotenv import load_dotenv
import os
from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, StringField, SelectField, SubmitField,PasswordField,RadioField
from wtforms.validators import DataRequired, Length,ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError


load_dotenv()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marcet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    login = db.Column(db.String(80), unique = True, nullable = False)
    Password = db.Column(db.String(120), nullable = False)
    is_admin = db.Column(db.Integer, default = 0)
    balance = db.Column(db.Integer, default = 0)
    image = db.Column(db.String(150),nullable = False)

class Cartss(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    product_id = db.Column(db.Integer,nullable = False)
    user_id = db.Column(db.Integer, nullable = False)
    quantity = db.Column(db.Integer)

class Product(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(15), unique = True, nullable = False)
    price = db.Column(db.Integer)
    image = db.Column(db.String(150), nullable = False)

app.secret_key = os.getenv('SECRET_KEY')

class RegForm(FlaskForm):
    login = StringField('login',validators=[DataRequired(),Length(min=4, message='min lenght 4 simvols!')])
    password = PasswordField('password', validators=[DataRequired(),Length(min=6,message='min lenght 6 simvols!')])
    submit = SubmitField('registration')

    def validate_login(self, field):
        user = User.query.filter_by(login = field.data).first()
        if user:
            raise ValidationError('this login in base!!')

class LoginForm(FlaskForm):
    login = StringField('login',validators=[DataRequired()])
    password = PasswordField('password',validators=[DataRequired()])
    submit = SubmitField('sign in')

class Photos(FlaskForm):
    change = RadioField('change',choices=[('default.png','dog'),('cat.png','cat'),('parrot.png','parrot')],default='default.png', validators=[DataRequired()])
    submit = SubmitField('submit')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/registration',methods=['GET','POST'])
def reg():
    form = RegForm()
    try:
        if request.method == "POST" and form.validate_on_submit():
            login = form.login.data
            password = form.password.data
            hashs = hashlib.sha256(password.encode()).hexdigest()
            is_admin = 0
            balance = 0
            new_user = User(login = login, Password = hashs, is_admin = is_admin, balance = balance,image = 'default.png')
            db.session.add(new_user)
            db.session.commit()
            return "<h1>you registr</h1><a href='/login'>sign in</a>"
        else:
            return render_template('reg.html',form = form)
    except IntegrityError:
        db.session.rollback()
        return '<h1>login in base</h1><a href="/">home</a>'
    
@app.route('/login',methods =["GET","POST"])
def login():
    form = LoginForm()
    try:
        if request.method == "POST" and form.validate_on_submit():
            login = form.login.data
            password = form.password.data
            hashs = hashlib.sha256(password.encode()).hexdigest()
            user = User.query.filter_by(login = login, Password = hashs).first()
            if user:
                session['user'] = user.login
                return redirect(url_for('home'))
            else:
                return '<h1>bad password or login</h1><a href"/">home</a>'
        else:
            return render_template('login.html',form = form)
    except Exception as e:
        return str(e)

@app.route('/catalog')
def cataloge():
    products = Product.query.all()
    if products:
        return render_template('cataloge.html',products = products )

@app.route('/add_cart/<int:product_id>')
def add_cart(product_id):
    if 'user' not in session:
        return redirect(url_for('home'))
    user = User.query.filter_by(login = session['user']).first()
    if not user:
        return redirect(url_for('login'))
    cart_item = Cartss.query.filter_by(user_id =user.id,product_id = product_id).first()
    if cart_item:
        cart_item.quantity += 1
        db.session.add(cart_item)
        db.session.commit()
        return redirect(url_for('cataloge'))
    else:
        cart_item = Cartss(user_id =user.id,product_id = product_id, quantity = 1)
        db.session.add(cart_item)
        db.session.commit()
        return redirect(url_for('cataloge'))
    
@app.route('/cart')
def cart():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(login = session['user']).first()
    if not user:
        return redirect(url_for('login'))
    user_id = User.query.filter_by(login = session['user']).first()
    items = db.session.query(Product.name, Product.price, Product.image, Cartss.quantity, Product.id).join( Cartss, Product.id == Cartss.product_id).filter(Cartss.user_id == User.id).all()
    return render_template('cart.html', items=items)

@app.route('/remove_cart/<int:product_id>')
def remove_cart(product_id):
    if 'user' not in session:
        return redirect(url_for('home'))
    user = User.query.filter_by(login = session['user']).first()
    if not user:
        return redirect(url_for('home'))
    result = Cartss.query.filter_by(user_id = user.id, product_id = product_id).first()
    if result:
        d = Cartss.query.filter_by(user_id = user.id,product_id = product_id).delete()
        db.session.commit()
        return redirect(url_for('cart'))
    else:
        return redirect(url_for('cart'))

@app.route('/delete_one/<int:product_id>')
def delete_one(product_id):
    if 'user' not in session:
        return redirect(url_for('home'))
    user = User.query.filter_by(login = session['user']).first()
    if not user:
        return redirect(url_for('home'))
    q = Cartss.query.filter_by(user_id = user.id, product_id = product_id).first()
    if q:
        if q.quantity > 0:
            q.quantity -=1
            db.session.add(q)
            db.session.commit()
            return redirect(url_for('cart'))
        else:
            d = Cartss.query.filter_by(user_id = user.id,product_id = product_id).delete()
            db.session.commit()
            return redirect(url_for('cart'))

@app.route('/sprite')
def sprite():
    return render_template('sprite.html')

@app.route('/exit')
def exits():
    session.pop('user',None)
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('home'))
    user = User.query.filter_by(login = session['user']).first()
    if not user:
        return redirect(url_for('home'))
    return render_template('profile.html',user = user, name = user.login,balance = user.balance,image = user.image)

@app.route('/change_avatar',methods = ["GET","POST"])
def change_avatar():
    form = Photos()
    if 'user' not in session:
        return redirect(url_for('home'))
    user = User.query.filter_by(login = session['user']).first()
    if not user:
        return redirect(url_for('home'))
    if request.method == "POST" and form.validate_on_submit():
        avatar = form.change.data
        user.image = avatar
        db.session.commit()
        return redirect(url_for('change_avatar'))
    else:
        return render_template('change.html',form = form,image = user.image)

@app.route('/add_balance')
def add_balance():
    if 'user' not in session:
        return redirect(url_for('home'))
    user = User.query.filter_by(login = session['user']).first()
    if not user:
        return redirect(url_for('home'))
    user.balance +=10
    db.session.commit()
    return redirect(url_for('profile'))

@app.errorhandler(404)
def error404(e):
    return '<title>Oops</title><style>h1{color:red;} body{ background-color:gray}</style><h1>Oops! error 404</h1><a href="/">home</a>',404

@app.errorhandler(500)
def error500(e):
    return '<title>Oops</title><style>h1{color:red;} body{ background-color:gray}</style><h1>Oops! error 500</h1><a href="/">home</a>',500

if __name__ == '__main__':
    app.run(debug= True)
    