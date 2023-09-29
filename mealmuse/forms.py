from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

class AddIngredientListForm(FlaskForm):
    list_of_items = TextAreaField('Enter a list of ingredients to add to your pantry', validators=[DataRequired()])
    submit = SubmitField('Add Ingredients')

class CreateRecipeForm(FlaskForm):
    recipe_details = TextAreaField('Type or paste your recipe details', validators=[DataRequired()])
    submit = SubmitField('Create Recipe')

class BugReportForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired()])
    steps = TextAreaField('Steps to Reproduce (optional)')
    submit = SubmitField('Submit')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

