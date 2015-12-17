from flask import Flask, render_template, redirect, url_for, flash
from flask.ext.wtf import Form
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
import os

basedir = os.path.abspath(os.path.dirname(__name__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard-to-guess-im-code-kun'
app.config['app.config[SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


class CodeItem(db.Model):
    __tablename__ = 'codes'
    id = db.Column(db.Integer, primary_key=True)
    poster = db.Column(db.String(64), index=True)
    syntax = db.Column(db.String(32))
    content = db.Column(db.Text())

choices=[('Plain', 'Plain'), ('C', 'C'), ('C++', 'C++'),  ('Java', 'Java'), ('Python', 'Python'),
         ('C#', 'C#'), ('PHP', 'PHP'), ('Ruby', 'Ruby'), ('Matlab', 'Matlab')
]

class CodeForm(Form):
    poster = StringField('昵称', validators=[Length(1, 60, '请输入昵称')])
    syntax = SelectField('语言', choices=choices)
    content = TextAreaField('代码', validators=[DataRequired()], id='contentcode')
    submit = SubmitField('提交')


@app.route('/', methods=['POST', 'GET'])
def index():
    form = CodeForm()
    if form.validate_on_submit():
        item = CodeItem(poster=form.poster.data, syntax=form.syntax.data, content=form.content.data)
        db.session.add(item)
        db.session.commit()
        print(item.id)
        flash('提交成功，编号为：' + str(item.id))
        return redirect(url_for('show', codeid=item.id))
    return render_template('index.html', form=form)


@app.route('/show/<int:codeid>', methods=['POST', 'GET'])
def show(codeid):
    item = CodeItem.query.filter_by(id=codeid).first()
    return render_template('show.html', item=item)


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    app.run(debug=True)
