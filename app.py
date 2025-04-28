from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import json
import random
import os

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
app.secret_key = os.getenv("SECRET_KEY")

class Data (db.Model):
    id = db.Column(db.Integer, primary_key =True)
    username = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(20), nullable = False)
    gems = db.Column(db.Integer)
    coins = db.Column(db.Integer)
    inventory = db.Column(db.Text)

@app.route('/login', methods=['POST', 'GET'])
def login ():
    if request.method == "POST":
        user = request.form['username']
        password = request.form['password']
        player_content = Data.query.filter_by(username= user).first()
        if player_content:
            if password == player_content.password:
                id = player_content.id
                try:
                    session[f'is_login{id}'] = True
                    return redirect(f'/mainGame/{id}')
                except:
                    return "Some thing went wronge while login"
            else:
                return render_template('login.html', context='your password is incorrect ')
        else:
            return render_template('login.html', context='you didnt have an account please signup ')
    else:
        return render_template('login.html', context='')

@app.route('/signup', methods=['POST', 'GET'])
def signup ():
    if request.method == "POST":
        datas = Data.query.order_by(Data.id).all()
        username = request.form['username']
        password = request.form['password']
        data_name = [data.username for data in datas]
        if username in data_name :
             return render_template('signup.html', context='already have this name')
        else:
            new_content = Data(
                
                username = username,
                password = password,
                gems = 500,
                coins = 1000,
                inventory = json.dumps([])
            )
            try:
                db.session.add(new_content)
                db.session.commit()
                return render_template('login.html', context="Signup is succesefuly")
            except:
                return "Some thing went wronge while Singup"
    else:
        return render_template('signup.html')
    

@app.route('/admin/login', methods=['POST', 'GET'])
def admin_login ():
    if request.method == "POST":
        user_admin = "Pat"
        password_admin = "1010"

        user = request.form['admin_username']
        password = request.form['admin_password']

        if user == user_admin and password == password_admin:
            session['is_admin'] = True
            return redirect('/admin/dashboard')
        else:
             return render_template('admin_login.html', context='Something was incorrect')
    else:
        return render_template('admin_login.html', context='')
    
@app.route('/admin/dashboard')
def admin_dashboard():
   if session['is_admin'] :
        datas = Data.query.order_by(Data.id).all()
        return render_template('admin_dashboard.html', datas=datas)
   else:
       return redirect('/admin/login')

@app.route('/admin/dashboard/delete/<int:id>')
def delete(id):
    data_delete = Data.query.get_or_404(id)
    try:
        db.session.delete(data_delete)
        db.session.commit()
        return redirect('/admin/dashboard')
    except:
        return "something went wrong while delete a data"
    
@app.route('/admin/dashboard/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    data_updated = Data.query.get_or_404(id)
    if request.method == 'POST':
        data_updated.username = request.form['username']
        data_updated.password = request.form['password']
        data_updated.coins = request.form['coins']
        data_updated.gems = request.form['gems']

        try:
            db.session.commit()
            return redirect('/admin/dashboard')
        except:
            return 'something went wrong while update data'

    else:
        return render_template('update_user.html', user=data_updated)

@app.route('/admin/dashboard/logout')
def admin_logout():
    session['is_admin'] = False
    return redirect('/admin/login')


@app.route('/mainGame/<int:id>')
def mainGame (id):
    user_content = Data.query.get_or_404(id)
    try:
        if user_content.username and session[f'is_login{id}']:
        
            return render_template('maingame.html', id = id, data= user_content)  
    except:
        return "something went wrong"

@app.route('/mainGame/<int:id>/logout')
def Logout (id):
    user_content = Data.query.get_or_404(id)
    try:
        if user_content.username and session[f'is_login{id}']:
            session[f'is_login{id}'] = False
            return redirect('/login')  
    except:
        return "something went wrong"


@app.route('/mainGame/<int:id>/gacha')
def gacha (id):
    user_content = Data.query.get_or_404(id)

    try:
         warnsuc = request.args.get('warnsuc')
         warnfail = request.args.get('warnfail')
    except:
        pass

    try:
        if session[f'is_login{id}']:
            return render_template('gacha.html', id= id, data= user_content, warnsuc = warnsuc, warnfail=warnfail)  
    
    except:
        return "something went wrong"
    
@app.route('/mainGame/<int:id>/gacha/roll<int:amound>')
def roll (id,amound):
    user_content = Data.query.get_or_404(id)
    try:


        if session[f'is_login{id}']:
            if amound == 10 :
                use_gams = 900
            else:
                use_gams = 100

            if user_content.gems < use_gams:
                warnfail = "not enought gems"
                return redirect(url_for(f'gacha',id=id, warnfail=warnfail))  
            else:
                user_content.gems -= use_gams
                items = [ 'Legend sword','Epic sword' , 'Rare sword','Commond sword']
                rates = [2,11,32,55]
                one_roll_item = random.choices(items, weights=rates, k=amound)
                items = json.loads(user_content.inventory)
                for i in range(amound):
                    items.append(one_roll_item[i])
                user_content.inventory = json.dumps(items)
                db.session.commit()
                warnsuc = " roll succesefuly"
            
                return redirect(url_for(f'gacha',id=id, warnsuc=warnsuc))  
            
    
    except:
        return "something went wrong"



@app.route('/mainGame/<int:id>/shop')
def shop (id):
    user_content = Data.query.get_or_404(id)
    try:
        if session[f'is_login{id}']:
            try:
                warnfail = request.args.get('warnfail')
                warnsuc = request.args.get('warnsuc')
            except:
                pass

            return render_template('shop.html', id= id, data= user_content, warnfail = warnfail, warnsuc = warnsuc)  
    
    except:
        return "something went wrong"
    
@app.route('/mainGame/<int:id>/shop/Exclusive Sword', methods=['GET', 'POST'])
def buy(id):
    user_content = Data.query.get_or_404(id)
    if session[f'is_login{id}']:
        warnsuc = " buying succese"
        warnfail = "not enoght coins"
        if user_content.coins < 300:
            return redirect(url_for(f'shop',id=id, warnfail=warnfail)) 
        else:
            user_content.coins -= 300
            inventory_data = json.loads(user_content.inventory)
            inventory_data.append("Exclusive Sword")
            user_content.inventory = json.dumps(inventory_data)
            db.session.commit()
            return  redirect(url_for(f'shop',id=id, warnsuc=warnsuc))
    
@app.route('/mainGame/<int:id>/shop/Exchange', methods=['GET', 'POST'])
def Exchange(id):
    user_content = Data.query.get_or_404(id)
    if session[f'is_login{id}']:
        warnsuc = " Exchange succese"
        warnfail = "not enoght coins"
        if user_content.coins < 500:
            return redirect(url_for(f'shop',id=id, warnfail=warnfail)) 
        else:
            user_content.coins -= 500
            user_content.gems += 100
            db.session.commit()
            return  redirect(url_for(f'shop',id=id, warnsuc=warnsuc))

@app.route('/mainGame/<int:id>/inventory')
def user_inv (id):
    user_content = Data.query.get_or_404(id)
   
    items = json.loads(user_content.inventory)
    index = range(len(items))
    if session[f'is_login{id}']:
        return render_template('inventory.html', id= id, data= user_content, items = items, index=index)

@app.route('/mainGame/<int:id>/inventory/sell/<int:index>')
def sell (id, index):
    user_content = Data.query.get_or_404(id)
   
    if session[f'is_login{id}']:
        user_content.coins += 50
        items = json.loads(user_content.inventory)
        del items[index]
        user_content.inventory = json.dumps(items)
        db.session.commit()
        return redirect(f'/mainGame/{id}/inventory')    


if __name__ == "__main__":
    app.run(debug=True)