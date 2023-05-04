from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
import hashlib, datetime, os, shutil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db = SQLAlchemy(app)
HOST = '0.0.0.0'
PORT = 1000
DEBUG = False


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    surname = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_super_user = db.Column(db.Boolean, default=False, nullable=False)
    dateR = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Users %r>' % self.id


class Pizzas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    ingredients = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    path = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Pizzas %r>' % self.id


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(150), nullable=False)
    pizza_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Pizzas %r>' % self.id


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(150), nullable=False)
    pizza_id = db.Column(db.Integer)
    address = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(150), nullable=False, default='В обработке')

    def __repr__(self):
        return '<Orders %r>' % self.id


@app.route('/')
def main():
    name = request.cookies.get('user')
    search = request.args.get('search')
    if name is None:
        return redirect('/login')
    user = Users.query.filter_by(login=name).first()
    try:
        if search is not None:
            pizzas = []
            for i in list(Pizzas.query.all()):
                if i.name.lower() in search.lower() or search.lower() in i.name.lower():
                    pizzas.append(i)
        else:
            search = ''
            pizzas = list(Pizzas.query.all())
        if len(pizzas) == 2:
            pizzas[0], pizzas[1] = pizzas[1], pizzas[0]
        if len(pizzas) >= 3:
            pizzas.reverse()
        cart_volume = len(list(Cart.query.filter_by(author=name).all()))
    except:
        pizzas = ''
        cart_volume = 0
    cart_ = list(Cart.query.filter_by(author=name).all())
    pizzas_in_cart = []
    for i in cart_:
        pizzas_in_cart.append(Pizzas.query.filter_by(id=i.pizza_id).first())
    return render_template("index.html", user=user, pizzas=pizzas, cart_volume=cart_volume, pizzas_in_cart=pizzas_in_cart, search=search)


@app.route('/register', methods=['POST', 'GET'])
def register():
    name = request.cookies.get('user')
    if request.method == "POST":
        login = request.form['login']
        email = request.form['email']
        name = request.form['name']
        surname = request.form['surname']
        passw1 = request.form['passw1']
        password = hashlib.md5(passw1.encode("utf-8")).hexdigest()
        exists = db.session.query(Users.id).filter_by(login=login).first() is not None
        if not exists:
            if Users.query.first() is None:
                is_super_user = True
            else:
                is_super_user = False
            user = Users(login=login, password=password, name=name, surname=surname, email=email, is_super_user=is_super_user)
            try:
                db.session.add(user)
                db.session.commit()
                resp = make_response(redirect("/"))
                resp.set_cookie('user', user.login)
                return resp
            except Exception as ex:
                print(ex)
                return redirect("/register")
        else:
            return redirect("/register")
    else:
        if name is None:
            cart_volume = 0
        else:
            cart_volume = len(list(Cart.query.filter_by(author=name).all()))
        return render_template("register.html", cart_volume=cart_volume)


@app.route('/login', methods=['POST', "GET"])
def login():
    name = request.cookies.get('user')
    if request.method == "POST":
        email = request.form['email']
        passw1 = request.form['passw1']
        password = hashlib.md5(passw1.encode("utf-8")).hexdigest()
        exists = db.session.query(Users.id).filter_by(email=email, password=password).first() is not None
        user = db.session.query(Users.login).filter_by(email=email, password=password).first()
        if exists:
            resp = make_response(redirect("/"))
            resp.set_cookie('user', user[0])
            return resp
        else:
            return redirect("/login")
    else:
        if name is None:
            cart_volume = 0
        else:
            cart_volume = len(list(Cart.query.filter_by(author=name).all()))
        return render_template("login.html", cart_volume=cart_volume)


@app.route('/logout')
def logout():
    resp = make_response(redirect("/login"))
    resp.set_cookie('user', '', expires=0)
    return resp


@app.route('/admin/add_pizza', methods=['GET', 'POST'])
def add():
    name = request.cookies.get('user')
    user = Users.query.filter_by(login=name).first()
    if not user.is_super_user or name is None:
        return redirect('/login')
    if request.method == 'POST':
        pizza_name = request.form['name']
        ingredients = request.form['ingrs']
        price = float(request.form['price'])
        image = request.files['file[]']
        try:
            path = f'static/pizzas_images/{pizza_name}'
            os.makedirs(path)
            path += '/image.png'
            image.save(path)
            pizza = Pizzas(name=pizza_name, path=path, ingredients=ingredients, price=price)
            db.session.add(pizza)
            db.session.commit()
            return redirect('/')
        except Exception as ex:
            print(ex)
            return redirect('/admin/add_pizza')

    else:
        cart_volume = len(list(Cart.query.filter_by(author=name).all()))
        return render_template('add.html', cart_volume=cart_volume)


@app.route('/add2cart')
def add2cart():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    try:
        _id = int(request.args.get('id'))
        cart_obj = Cart(pizza_id=_id, author=name)
        exists = db.session.query(Cart.id).filter_by(pizza_id=_id, author=name).first() is not None
        if not exists:
            db.session.add(cart_obj)
            db.session.commit()
        else:
            return redirect('/')
        return redirect('/cart')
    except:
        return redirect('/')


@app.route('/del_from_cart')
def del_from_cart():
    name = request.cookies.get('user')
    try:
        _id = int(request.args.get('id'))
        Cart.query.filter_by(author=name, pizza_id=_id).delete()
        db.session.commit()
        return redirect('/cart')
    except Exception as _ex:
        print(_ex)
        return redirect('/')


@app.route('/cart')
def cart():
    name = request.cookies.get('user')
    cart_ = list(Cart.query.filter_by(author=name).all())
    pizzas_in_cart = []
    for i in cart_:
        pizzas_in_cart.append(Pizzas.query.filter_by(id=i.pizza_id).first())
    cart_volume = len(list(Cart.query.filter_by(author=name).all()))
    all_price = 0
    for i in pizzas_in_cart:
        if i is not None:
            all_price += i.price

    all_price = round(all_price, 2)
    return render_template('cart.html', cart_volume=cart_volume, pizzas=pizzas_in_cart, all_price=all_price)


@app.route('/view')
def view():
    name = request.cookies.get('user')
    _id = request.args.get('id')
    red_from = request.args.get('red_from')
    if red_from is None:
        red_from = ''
    pizza = Pizzas.query.filter_by(id=_id).first()
    cart_volume = len(list(Cart.query.filter_by(author=name).all()))
    in_cart = Cart.query.filter_by(pizza_id=_id, author=name).first() is not None
    return render_template('view.html', pizza=pizza, cart_volume=cart_volume, red_from=red_from, in_cart=in_cart)


@app.route('/profile')
def profile():
    name = request.cookies.get('user')
    cart_volume = len(list(Cart.query.filter_by(author=name).all()))
    user = Users.query.filter_by(login=name).first()
    orders = list(Orders.query.filter_by(author=name).all())
    pizzas = []
    if len(orders) == 2:
        orders[0], orders[1] = orders[1], orders[0]
    if len(orders) >= 3:
        orders.reverse()
    orders_copy = orders
    orders = []
    for i in orders_copy:
        if i.status != 'Доставлен':
            orders.append(i)
    try:
        for i in range(len(orders)):
            obj = Pizzas.query.filter_by(id=orders[i].pizza_id).first()
            if obj is not None:
                pizzas.append(obj)
    except:
        pizzas = []
    return render_template('profile.html', cart_volume=cart_volume, user=user, orders=orders, pizzas=pizzas)


@app.route('/admin')
def admin():
    name = request.cookies.get('user')
    user = Users.query.filter_by(login=name).first()
    if not user.is_super_user:
        return redirect('/login')
    search = request.args.get('search')
    if name is None:
        return redirect('/login')

    try:
        if search is not None:
            pizzas = []
            for i in list(Pizzas.query.all()):
                if i.name.lower() in search.lower() or search.lower() in i.name.lower():
                    pizzas.append(i)
        else:
            pizzas = list(Pizzas.query.all())
        if len(pizzas) == 2:
            pizzas[0], pizzas[1] = pizzas[1], pizzas[0]
        if len(pizzas) >= 3:
            pizzas.reverse()
        cart_volume = len(list(Cart.query.filter_by(author=name).all()))
    except:
        pizzas = ''
        cart_volume = 0
    if user is None:
        user = ''
    return render_template("admin.html", user=user, pizzas=pizzas, cart_volume=cart_volume)


@app.route('/admin/del_pizza')
def admin_del_pizza():
    name = request.cookies.get('user')
    user = Users.query.filter_by(login=name).first()
    if not user.is_super_user:
        return redirect('/login')
    try:
        _id = int(request.args.get('id'))
        split = Pizzas.query.filter_by(id=_id).first().path.split('/')
        path = ''
        for i in range(len(split)-1):
            path += split[i] + '/'
        print(path)
        shutil.rmtree(path)
        Pizzas.query.filter_by(id=_id).delete()
        db.session.commit()
        return redirect('/admin')
    except:
        return redirect('/admin')


@app.route('/admin/edit_pizza', methods=['POST', 'GET'])
def admin_edit_pizza():
    name = request.cookies.get('user')
    user = Users.query.filter_by(login=name).first()
    if not user.is_super_user:
        return redirect('/login')
    _id = int(request.args.get('id'))
    pizza = Pizzas.query.filter_by(id=_id).first()
    if request.method == 'POST':
        pizza_name = request.form['name']
        price = float(request.form['price'])
        ingredients = request.form['ingrs']
        image = request.files['file[]']
        if pizza_name != pizza.name:
            if image:
                shutil.rmtree(f'static/pizzas_images/{pizza.name}')
                os.mkdir(f'static/pizzas_images/{pizza_name}')
                image.save(f'static/pizzas_images/{pizza_name}/image.png')
            else:
                try:
                    os.mkdir(f'static/pizzas_images/cache/{pizza.name}')
                except:
                    pass
                os.rename(pizza.path, f'static/pizzas_images/cache/{pizza.name}/image.png')
                shutil.rmtree(f'static/pizzas_images/{pizza.name}')
                os.mkdir(f'static/pizzas_images/{pizza_name}')
                os.rename(f'static/pizzas_images/cache/{pizza.name}/image.png', f'static/pizzas_images/{pizza_name}/image.png')
                os.rmdir(f'static/pizzas_images/cache/{pizza.name}')
            pizza.path = f'static/pizzas_images/{pizza_name}/image.png'
        else:
            if image:
                shutil.rmtree(f'static/pizzas_images/{pizza_name}')
                os.mkdir(f'static/pizzas_images/{pizza_name}')
                image.save(f'static/pizzas_images/{pizza_name}/image.png')
            else:
                try:
                    os.mkdir(f'static/pizzas_images/cache/{pizza_name}')
                except:
                    pass
                os.rename(pizza.path, f'static/pizzas_images/cache/{pizza_name}/image.png')
                shutil.rmtree(f'static/pizzas_images/{pizza_name}')
                os.mkdir(f'static/pizzas_images/{pizza_name}')
                os.rename(f'static/pizzas_images/cache/{pizza_name}/image.png',
                          f'static/pizzas_images/{pizza_name}/image.png')
                os.rmdir(f'static/pizzas_images/cache/{pizza_name}')

        pizza.name = pizza_name
        pizza.price = price
        pizza.ingredients = ingredients
        db.session.commit()
        return redirect('/admin')
    else:
        try:
            return render_template('edit.html', pizza=pizza)
        except:
            return redirect('/admin')


@app.route('/admin/all_users')
def admin_all_users():
    name = request.cookies.get('user')
    user = Users.query.filter_by(login=name).first()
    if not user.is_super_user:
        return redirect('/login')
    name = request.cookies.get('user')
    users = list(Users.query.all())
    cart_volume = len(list(Cart.query.filter_by(author=name).all()))
    return render_template('users.html', users=users, cart_volume=cart_volume, name=name)


@app.route('/admin/del_account')
def admin_del_account():
    name = request.cookies.get('user')
    user = Users.query.filter_by(login=name).first()
    if not user.is_super_user:
        return redirect('/login')

    try:
        _id = int(request.args.get('id'))
        user = Users.query.filter_by(id=_id).first()
        if user.login == name:
            return redirect('/admin/all_users')
        db.session.delete(user)
        db.session.commit()
    except:
        pass
    return redirect('/admin/all_users')


@app.route('/admin/gimme_admin')
def gimme_admin():
    try:
        name = request.cookies.get('user')
        _id = int(request.args.get('id'))
    except Exception as _ex:
        print(_ex)
        return redirect('/admin/all_users')
    user = Users.query.filter_by(login=name).first()
    if not user.is_super_user:
        return redirect('/login')
    try:
        user = Users.query.filter_by(id=_id).first()
        user.is_super_user = True
        db.session.commit()
    except:
        pass
    return redirect('/admin/all_users')


@app.route('/admin/steal_admin')
def steal_admin():
    try:
        name = request.cookies.get('user')
        _id = int(request.args.get('id'))
    except:
        return redirect('/admin/all_users')
    user = Users.query.filter_by(login=name).first()
    if not user.is_super_user:
        return redirect('/login')
    try:
        user = Users.query.filter_by(id=_id).first()
        user.is_super_user = False
        db.session.commit()
    except:
        pass
    return redirect('/admin/all_users')


@app.route('/buy', methods=['GET', 'POST'])
def buy():
    try:
        name = request.cookies.get('user')
        _id = int(request.args.get('id'))
        pizza = Pizzas.query.filter_by(id=_id).first()
        cart_volume = len(list(Cart.query.filter_by(author=name).all()))
        user = Users.query.filter_by(login=name).first()
        card_ns = f"{user.name[0]}. {user.surname}".upper()
        years = []
        for i in range(int(datetime.datetime.now().year), int(datetime.datetime.now().year)+4):
            years.append(i)
    except:
        return redirect('/')
    if request.method == 'POST':
        address = request.form['pizza_address']
        try:
            order = Orders(address=address, author=name, pizza_id=_id)
            db.session.add(order)
            db.session.commit()
            return redirect('/profile#orders')
        except Exception as ex:
            print(ex)
            return redirect(f'/buy?id={_id}')
    else:
        return render_template('buy.html', cart_volume=cart_volume, card_ns=card_ns, pizza=pizza, years=years)


@app.route('/buyallcart', methods=['GET', 'POST'])
def buy_all_cart():
    try:
        name = request.cookies.get('user')
        user = Users.query.filter_by(login=name).first()
        card_ns = f"{user.name[0]}. {user.surname}".upper()
        years = []
        for i in range(int(datetime.datetime.now().year), int(datetime.datetime.now().year) + 4):
            years.append(i)
        cart_ = list(Cart.query.filter_by(author=name).all())
        pizzas_in_cart = []
        for i in cart_:
            pizzas_in_cart.append(Pizzas.query.filter_by(id=i.pizza_id).first())
        cart_volume = len(list(Cart.query.filter_by(author=name).all()))
        all_price = 0
        for i in pizzas_in_cart:
            if i is not None:
                all_price += i.price

        all_price = round(all_price, 2)
    except:
        return redirect('/')
    if request.method == 'POST':
        address = request.form['pizza_address']
        try:
            for i in cart_:
                order = Orders(address=address, author=name, pizza_id=i.pizza_id)
                db.session.add(order)
            db.session.commit()
            return redirect('/profile#orders')
        except Exception as ex:
            print(ex)
            return redirect(f'/buyallcart')
    else:
        return render_template('buyallcart.html', cart_volume=cart_volume, card_ns=card_ns, years=years, all_price=all_price)


@app.route('/admin/orders')
def admin_orders():
    try:
        name = request.cookies.get('user')
        cart_volume = len(list(Cart.query.filter_by(author=name).all()))
        user = Users.query.filter_by(login=name).first()
        if not user.is_super_user:
            return redirect('/login')
        orders = list(Orders.query.filter_by(author=name).all())
        pizzas = []
        if len(orders) == 2:
            orders[0], orders[1] = orders[1], orders[0]
        if len(orders) >= 3:
            orders.reverse()
        try:
            for i in range(len(orders)):
                obj = Pizzas.query.filter_by(id=orders[i].pizza_id).first()
                if obj is not None:
                    pizzas.append(obj)
        except:
            pizzas = []
        return render_template('orders.html', cart_volume=cart_volume, orders=orders, pizzas=pizzas)
    except:
        return redirect('/admin')


@app.route('/admin/delete_order')
def admin_delete_order():
    name = request.cookies.get('user')
    user = Users.query.filter_by(login=name).first()
    if not user.is_super_user:
        return redirect('/login')
    try:
        _id = int(request.args.get('id'))
        order = Orders.query.filter_by(id=_id).first()
        db.session.delete(order)
        db.session.commit()
        return redirect('/admin/orders')
    except:
        return redirect('/admin/orders')


@app.route('/admin/orders/set_status')
def admin_order_set_status():
    name = request.cookies.get('user')
    user = Users.query.filter_by(login=name).first()
    if not user.is_super_user:
        return redirect('/login')
    try:
        _id = int(request.args.get('id'))
        _status = request.args.get('status')
        order = Orders.query.filter_by(id=_id).first()
        order.status = _status
        db.session.commit()
        return redirect('/admin/orders')
    except:
        return redirect('/admin/orders')


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    name = request.cookies.get('user')
    if name is None:
        return redirect('/login')
    user = Users.query.filter_by(login=name).first()
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        surname = request.form['surname']
        passw1 = request.form['passw1']
        if passw1 != '':
            user.password = hashlib.md5(passw1.encode("utf-8")).hexdigest()
        user.email = email
        user.name = name
        user.surname = surname
        db.session.commit()
        return redirect('/profile')
    else:
        return render_template('edit_profile.html', user=user)


if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)
