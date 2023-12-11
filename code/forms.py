from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField

class Recipe(FlaskForm):
    name = StringField("Type in name of a recipe", validators=[DataRequired()])
    author = StringField("What's your name?", validators=[DataRequired()])
    description = StringField("Tell the world how to make this wonderful recipe!", validators=[DataRequired()])
    submit = SubmitField("Submit")