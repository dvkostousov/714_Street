from os import environ

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectMultipleField, widgets, MultipleFileField, \
    FloatField, TextAreaField, FileField, RadioField, IntegerField, EmailField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


class ChoiceObj(object):
    def __init__(self, name, choices):
        # this is needed so that BaseForm.process will accept the object for the named form,
        # and eventually it will end up in SelectMultipleField.process_data and get assigned
        # to .data
        setattr(self, name, choices)


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.TableWidget()
    option_widget = widgets.CheckboxInput()


class ProductForm(FlaskForm):
    all_categories = environ.get('ALL_CATEGORIES').split(", ")
    all_colors = environ.get('ALL_COLORS').split(", ")
    all_sizes = environ.get('ALL_SIZES').split(", ")
    all_sections = environ.get('ALL_SECTIONS').split(", ")
    name = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    categories = MultiCheckboxField(choices=[(c, c) for c in all_categories])
    sizes = MultiCheckboxField(choices=[(c, c) for c in all_sizes])
    colors = MultiCheckboxField(choices=[(c, c) for c in all_colors])
    sections = MultiCheckboxField(choices=[(c, c) for c in all_sections])
    price = FloatField("Цена", validators=[DataRequired()])
    old_price = FloatField("Старая цена")
    main_photo = FileField("Главное фото", validators=[DataRequired()])
    photos = MultipleFileField("Фото")
    submit = SubmitField("Добавить товар")


class EditProductForm(FlaskForm):
    all_categories = environ.get('ALL_CATEGORIES').split(", ")
    all_colors = environ.get('ALL_COLORS').split(", ")
    all_sizes = environ.get('ALL_SIZES').split(", ")
    all_sections = environ.get('ALL_SECTIONS').split(", ")
    name = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    categories = MultiCheckboxField(choices=[(c, c) for c in all_categories])
    sizes = MultiCheckboxField(choices=[(c, c) for c in all_sizes])
    colors = MultiCheckboxField(choices=[(c, c) for c in all_colors])
    sections = MultiCheckboxField(choices=[(c, c) for c in all_sections])
    price = FloatField("Цена", validators=[DataRequired()])
    old_price = FloatField("Старая цена")
    main_photo = FileField("Главное фото")
    photos = MultipleFileField("Фото")
    submit = SubmitField("Сохранить изменения")


class FilterForm(FlaskForm):
    all_categories = environ.get('ALL_CATEGORIES').split(", ")
    all_colors = environ.get('ALL_COLORS').split(", ")
    all_sizes = environ.get('ALL_SIZES').split(", ")

    categories = MultiCheckboxField(choices=[(c, c) for c in all_categories])
    sizes = MultiCheckboxField(choices=[(c, c) for c in all_sizes])
    colors = MultiCheckboxField(choices=[(c, c) for c in all_colors])
    submit = SubmitField("Применить фильтры")


class ChooseProductForm(FlaskForm):
    colors = RadioField(validators=[DataRequired()])
    sizes = RadioField(validators=[DataRequired()])
    count = IntegerField(validators=[DataRequired()])
    submit_buy_one_click = SubmitField("Купить в один клик")
    submit_add_to_cart = SubmitField("Добавить в корзину")


class OrderForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    number = StringField("Номер телефона", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    comment = StringField("Комментарий к заказу")
    submit = SubmitField("Оформить заказ")
