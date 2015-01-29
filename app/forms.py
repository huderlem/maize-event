from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class TrainerIdForm(Form):
    trainer_id = StringField('trainer_id', validators=[DataRequired()])

