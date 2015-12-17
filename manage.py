from flask import Flask, render_template, redirect, url_for, flash, send_file
from flask.ext.wtf import Form
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager, Shell, Server
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
import os
from random import randint
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__name__))

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'hard-to-guess-im-code-kun'
app.config['app.config[SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(basedir, 'data-dev.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
manager = Manager(app)


class CodeItem(db.Model):
    __tablename__ = 'codes'
    id = db.Column(db.Integer, primary_key=True)
    poster = db.Column(db.String(64), index=True)
    syntax = db.Column(db.String(32))
    time = db.Column(db.DateTime())
    content = db.Column(db.Text())

choices=[('Plain', 'Plain'), ('C', 'C'), ('C++', 'C++'),  ('Java', 'Java'), ('Python', 'Python'),
         ('C#', 'C#'), ('PHP', 'PHP'), ('Ruby', 'Ruby'), ('Matlab', 'Matlab'), ('Bash', 'Bash'),
         ('Html', 'Html'), ('CSS', 'CSS'), ('Javascript', 'Javascript'), ('XML', 'XML'), ('Perl', 'Perl'),
         ('R', 'R'), ('Swift', 'Swift'), ('SQL', 'SQL'), ('Delphi', 'Delphi'), ('Lisp', 'Lisp'),
         ('Pascal', 'Pascal'), ('Ada', 'Ada')
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
        item.time = datetime.now()
        item.id = randint(10**6, 10**7)
        while CodeItem.query.filter_by(id=item.id).first() is not None:
            item.id = randint(10**6, 10**7)
        db.session.add(item)
        db.session.commit()
        print(item.id)
        flash('提交成功，代码分享号为：' + str(item.id))
        return redirect(url_for('show', codeid=item.id))
    return render_template('index.html', form=form)


@app.route('/download/<int:codeid>')
def download(codeid):
    if CodeItem.query.filter_by(id=codeid).first() is None:
        flash('下载错误～')
        return redirect(url_for('index'))
    fdir = basedir + '/static/' + str(codeid) + '.txt'
    with open(fdir, 'w') as f:
        f.write(CodeItem.query.filter_by(id=codeid).first().content)
    return send_file(fdir, as_attachment=True)


@app.route('/p/<int:codeid>', methods=['POST', 'GET'])
def show(codeid):
    item = CodeItem.query.filter_by(id=codeid).first()
    fmt = "%Y年%m月%d日 %H:%M"
    return render_template('show.html', item=item, timestr=item.time.strftime(fmt))


def make_shell_context():
    return dict(app=app, CodeItem=CodeItem)

manager.add_command("shell", Shell(make_context=make_shell_context))
# manager.add_command("runserver", Server(host='0.0.0.0', port=80))


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    manager.run()
