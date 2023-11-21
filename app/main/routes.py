from os import path
from random import sample
from threading import Thread

from flask_login import login_required, login_user, logout_user, current_user
from flask_mail import Message
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from app import app, mail
from app.extensions import create_session
from app.forms import LoginForm, ProductForm, EditProductForm, FilterForm, ChooseProductForm, OrderForm
from app.main import bp
from flask import render_template, redirect, url_for, session, current_app
from app.models.product import Product
from app.models.user import User


@bp.app_errorhandler(404)
def page_not_found(e):
    return redirect('/')


@bp.app_errorhandler(401)
def page_not_found(e):
    return redirect('/')


@bp.route('/')
def index():
    #session.clear()
    if 'count' in session:
        count_products = session['count']
    else:
        count_products = 0

    db_session = create_session()
    products_top = db_session.query(Product).filter(Product.sections.contains("Топ продаж")).order_by(Product.id).all()
    products_new_collection = db_session.query(Product).filter(Product.sections.contains("Новая коллекция")).order_by(
        Product.id).all()
    products_stock = db_session.query(Product).filter(Product.sections.contains("Акции")).order_by(Product.id).all()
    return render_template('index.html', title="Главная страница", products_top=products_top,
                           products_new_collection=products_new_collection, products_stock=products_stock,
                           count_products=count_products)


@bp.route('/catalog_filters/<filters>', methods=['GET', 'POST'])
def catalog_filters(filters):
    if 'count' in session:
        count_products = session['count']
    else:
        count_products = 0
    db_session = create_session()
    products = db_session.query(Product)

    filter_list = [i.split('#') for i in filters.split('&')]
    if len(filter_list) < 3:
        return redirect('/catalog')
    if filter_list[0][0] != '':
        categories_filter_list = [Product.categories.contains(x) for x in filter_list[0]]
        products = products.filter(or_(*categories_filter_list))
    if filter_list[1][0] != '':
        colors_filter_list = [Product.colors.contains(x) for x in filter_list[1]]
        products = products.filter(or_(*colors_filter_list))
    if filter_list[2][0] != '':
        sizes_filter_list = [Product.sizes.contains(x) for x in filter_list[2]]
        products = products.filter(or_(*sizes_filter_list))

    products = products.order_by(Product.id).all()
    products.reverse()
    db_session.close()

    form = FilterForm()
    form.categories.default = filter_list[0]
    form.colors.default = filter_list[1]
    form.sizes.default = filter_list[2]

    if form.validate_on_submit():
        if form.categories.data or form.colors.data or form.sizes.data:
            filters = '&'.join(['#'.join(form.categories.data), '#'.join(form.colors.data), '#'.join(form.sizes.data)])
            return redirect(url_for('main.catalog_filters', filters=filters))

        return redirect('/catalog')

    return render_template('catalog.html', title="Каталог", products=products, form=form, count_products=count_products)


@bp.route('/catalog', methods=['GET', 'POST'])
def catalog():
    if 'count' in session:
        count_products = session['count']
    else:
        count_products = 0
    db_session = create_session()
    products = db_session.query(Product).order_by(Product.id).all()
    products.reverse()
    db_session.close()
    form = FilterForm()
    form.categories.default = []
    form.colors.default = []
    form.sizes.default = []

    if form.validate_on_submit():
        if form.categories.data or form.colors.data or form.sizes.data:
            filters = '&'.join(['#'.join(form.categories.data), '#'.join(form.colors.data), '#'.join(form.sizes.data)])
            return redirect(url_for('main.catalog_filters', filters=filters))

    return render_template('catalog.html', title="Каталог", products=products, form=form, count_products=count_products)


@bp.route('/sales')
def sales():
    if 'count' in session:
        count_products = session['count']
    else:
        count_products = 0
    db_session = create_session()
    products_sales = db_session.query(Product).filter(Product.sections.contains("Распродажи")).order_by(
        Product.id).all()
    return render_template('sales.html', title="Главная страница", products_sales=products_sales, count_products=count_products)


@bp.route('/about')
def about():
    if 'count' in session:
        count_products = session['count']
    else:
        count_products = 0
    return render_template('about.html', title="О нас", count_products=count_products)


@bp.route('/policy-refund')
def policy_refund_page():
    if 'count' in session:
        count_products = session['count']
    else:
        count_products = 0
    return render_template('policy_refund.html', title="Хранилище политик", count_products=count_products)


@bp.route('/contact')
def contact_page():
    if 'count' in session:
        count_products = session['count']
    else:
        count_products = 0
    return render_template('contact.html', title="Контакты", count_products=count_products)


@bp.route('/auth', methods=['get', 'post'])
def auth():
    form = LoginForm()
    db_session = create_session()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        user = db_session.query(User).filter(User.login == login).first()
        if user and user.check_password(password):
            login_user(user, remember=False)
            db_session.close()
            return redirect('/products_list')
        return redirect('/auth')
    db_session.close()
    return render_template('auth.html', title="Войти в аккаунт", form=form)


@bp.route('/products_list')
@login_required
def products_list():
    if current_user.status != 'superuser':
        return redirect('/')
    db_session = create_session()
    products = db_session.query(Product).order_by(Product.id).all()
    products.reverse()
    db_session.close()
    return render_template('products_list.html', title="Список товаров", products=products)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@bp.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.status != 'superuser':
        return redirect('/')

    form = ProductForm()
    if form.validate_on_submit():
        main_filename = secure_filename(form.main_photo.data.filename)
        form.main_photo.data.save(path.join('app\static\photos', main_filename))
        for file in form.photos.data:
            if file:
                filename = secure_filename(file.filename)
                file.save(path.join('app\static\photos', filename))

        product = Product(name=form.name.data, description=form.description.data,
                          categories=', '.join(form.categories.data), sizes=', '.join(form.sizes.data),
                          colors=', '.join(form.colors.data), sections=', '.join(form.sections.data),
                          price=form.price.data, old_price=form.old_price.data, main_photo=main_filename,
                          photos=", ".join([secure_filename(file.filename) for file in form.photos.data]))
        db_session = create_session()
        db_session.add(product)
        db_session.commit()
        db_session.close()
        return redirect('/products_list')

    return render_template('add_or_edit_product.html', title="Добавить товар", form=form)


@bp.route('/<product_id>/delete')
@login_required
def delete_product(product_id):
    if current_user.status != 'superuser':
        return redirect('/')
    db_session = create_session()
    product = db_session.query(Product).filter(Product.id == product_id).first()
    if product:
        db_session.delete(product)
        db_session.commit()
    db_session.close()
    return redirect('/products_list')


@bp.route('/<product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if current_user.status != 'superuser':
        return redirect('/')
    db_session = create_session()
    product = db_session.query(Product).filter(Product.id == product_id).first()
    db_session.close()
    if not product:
        return redirect('/products_list')
    form = EditProductForm(data={'name': product.name, 'description': product.description, 'price': product.price,
                                 'old_price': product.old_price})

    if form.validate_on_submit():
        if form.main_photo.data:
            main_filename = secure_filename(form.main_photo.data.filename)
            form.main_photo.data.save(path.join('app\static\photos', main_filename))
            product.main_photo = main_filename

        for file in form.photos.data:
            if file:
                filename = secure_filename(file.filename)
                file.save(path.join('app\static\photos', filename))

        product.name = form.name.data
        product.description = form.description.data
        product.categories = ', '.join(form.categories.data)
        product.sizes = ', '.join(form.sizes.data)
        product.colors = ', '.join(form.colors.data)
        product.sections = ', '.join(form.sections.data)
        product.price = form.price.data
        product.old_price = form.old_price.data
        product.photos = ", ".join([secure_filename(file.filename) for file in form.photos.data])

        db_session.add(product)
        db_session.commit()
        db_session.close()

        return redirect('/products_list')

    form.categories.process_data(product.categories.split(', '))
    form.sizes.process_data(product.sizes.split(', '))
    form.colors.process_data(product.colors.split(', '))
    form.sections.process_data(product.sections.split(', '))
    return render_template('add_or_edit_product.html', title="Редактировать товар", form=form)


@bp.route('/product/<product_id>', methods=['GET', 'POST'])
def product(product_id):
    if 'count' in session:
        count_products = session['count']
    else:
        count_products = 0
    db_session = create_session()
    product = db_session.query(Product).filter(Product.id == product_id).first()
    if not product:
        db_session.close()
        return redirect('/catalog')
    ids = list(range(1, db_session.query(Product).count() + 1))
    ids.remove(int(product_id))
    if len(ids) > 7:
        ids = sample(ids, 8)
    other_products = [db_session.query(Product).filter(Product.id == i).first() for i in ids]
    db_session.close()
    form = ChooseProductForm()
    form.sizes.choices = [(c, c) for c in product.sizes.split(', ')]
    form.colors.choices = [(c, c) for c in product.colors.split(', ')]

    if form.validate_on_submit():
        if 'count' in session:
            session['count'] += 1
        else:
            session['count'] = 1

        if 'products' in session and len(session['products']) > 0:
            session['products'].append([session['products'][-1][0] + 1, product.id, product.main_photo, product.name,
                                        form.colors.data, form.sizes.data, product.price * form.count.data,
                                        product.price, form.count.data])
        else:
            session['products'] = [[0, product.id, product.main_photo, product.name, form.colors.data, form.sizes.data,
                                    product.price * form.count.data, product.price, form.count.data]]

        if 'total' in session:
            session['total'] += product.price * form.count.data
        else:
            session['total'] = product.price * form.count.data

        if 'total_count_products' in session:
            session['total_count_products'] += form.count.data
        else:
            session['total_count_products'] = form.count.data

        if form.submit_add_to_cart.data:
            return redirect('/catalog')
        if form.submit_buy_one_click.data:
            return redirect('/cart')

    product_photos = (product.main_photo + ', ' + product.photos).split(', ')
    return render_template('product.html', title=product.name, product=product, product_sizes=product.sizes.split(', '),
                           product_colors=product.colors.split(', '), product_photos=product_photos,
                           product_n=len(product_photos), products=other_products, form=form, count_products=count_products)


@bp.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'count' in session:
        count_products = session['count']
    else:
        count_products = 0

    if 'products' in session:
        products = session['products']
    else:
        products = []

    if 'total' in session:
        total = session['total']
    else:
        total = 0

    if 'total_count_products' in session:
        total_count_products = session['total_count_products']
    else:
        total_count_products = 0

    return render_template('cart.html', count_products=count_products, title='Корзина', products=products, total=total,
                           total_count_products=total_count_products)


@bp.route('/delete_chosen_product/<note_id>', methods=['GET', 'POST'])
def delete_chosen_product(note_id):
    if 'products' not in session:
        return redirect('/')

    note_id = int(note_id)

    if len(session['products']) <= note_id:
        return redirect('/')

    session['count'] -= 1
    session['total'] -= session['products'][note_id][6]
    session['total_count_products'] -= session['products'][note_id][8]
    session['products'] = session['products'][:note_id] + session['products'][note_id+1:]

    for i in range(len(session['products'])):
        session['products'][i][0] = i

    session.modified = True
    return redirect('/cart')


@bp.route('/plus_count_product/<note_id>', methods=['GET', 'POST'])
def plus_count_product(note_id):
    if 'products' not in session:
        return redirect('/')

    note_id = int(note_id)

    if len(session['products']) <= note_id:
        return redirect('/')

    if session['products'][note_id][8] < 99:
        session['products'][note_id][8] += 1
        session['total_count_products'] += 1
        session['total'] += session['products'][note_id][7]
        session['products'][note_id][6] += session['products'][note_id][7]
        session.modified = True

    return redirect('/cart')


@bp.route('/minus_count_product/<note_id>', methods=['GET', 'POST'])
def minus_count_product(note_id):
    if 'products' not in session:
        return redirect('/')

    note_id = int(note_id)

    if len(session['products']) <= note_id:
        return redirect('/')

    if session['products'][note_id][8] > 1:
        session['products'][note_id][8] -= 1
        session['total_count_products'] -= 1
        session['total'] -= session['products'][note_id][7]
        session['products'][note_id][6] -= session['products'][note_id][7]
        session.modified = True

    return redirect('/cart')


@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'count' in session and session['count'] > 0:
        count_products = session['count']
    else:
        return redirect('/cart')

    products = session['products']
    total = session['total']
    form = OrderForm()

    if form.validate_on_submit():
        session['order'] = True

        def send_async_email(msg):
            with app.app_context():
                mail.send(msg)

        msg1 = Message("Заказ", sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[current_app.config['MAIL_USERNAME']])
        msg1.html = render_template('mail.html', products=products, total=total, name=form.name.data,
                                   number=form.number.data, email=form.email.data, comment=form.comment.data)
        thr1 = Thread(target=send_async_email, args=[msg1])
        thr1.start()

        msg2 = Message("714 Street Заказ", sender=app.config['MAIL_DEFAULT_SENDER'],
                       recipients=[form.email.data])
        msg2.html = render_template('thanks_email.html')
        thr2 = Thread(target=send_async_email, args=[msg2])
        thr2.start()

        return redirect('/thanks')

    return render_template('checkout.html', title="Оформление заказа", count_products=count_products, products=products,
                           total=total, form=form)


@bp.route('/thanks')
def thanks():
    if 'order' not in session:
        return redirect('/')
    session.clear()

    return render_template('thanks.html', title="Заказ успешно оформлен", count_products=0)
