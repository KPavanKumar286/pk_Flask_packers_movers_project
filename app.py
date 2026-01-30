from flask import Flask, render_template, request, flash, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import re 
from sqlalchemy.orm import aliased
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'pavan'

app.permanent_session_lifetime = timedelta(minutes=30)

# Database connection
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://postgres:1234@localhost/demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users_table'   
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone_number = db.Column(db.BigInteger)
    passwords = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')
    role_id = db.Column(db.Integer, nullable=False)



@app.route('/login', methods= ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user:
            if generate_password_hash(user.passwords):
                session['user_id'] = user.user_id
                session['user_name'] = user.first_name
                session['email'] = user.email
                session['phone_number'] = user.phone_number
                session['role_id'] = user.role_id
                flash('Login Successfull 123', 'success')
                return redirect('homePage')
            else :
                flash('Invalid username or Password', 'danger')
                return 'There are some issue while login'
        else :
            return 'Email not registered'

    return render_template('registration/login.html')


def validate_first_last_name(name, field_name):
    if not name:
        return f'{field_name} cannot be empty'
    if not re.match(r'^[A-Za-z]+$', name):
        return f'{field_name} can only contain letters'
    if len(name) < 2 and len(name) > 30:
        return f'{field_name} must be between 2 and 30 charecters'


def validate_email(email):
    if not email:
        return 'Email cannot be empty'
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        return 'Invalid email format'
    if User.query.filter_by(email=email).first():
        return "Email already registered"
    return None


def validate_phone_number(phone_number):
    if not phone_number:
        return 'Phone number cannot be empty'
    if not re.match(r'^\d{10,15}$', phone_number):
        return 'Phone number must be 10 to 15 digits'
    return None


def validate_password(password):
    if not password:
        return 'Password cannot be empty'
    if len(password) < 8:
        return 'Password must be atleast 8 charecters'
    if not re.search(r'[A-Za-z]', password):
        return 'Password must contain atleast one letter'
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character"
    return None


def validate_confirm_password(password, confirm_password):
    if password != confirm_password:
        return 'Password do not match'
    return None



@app.route('/registration/<int:role_id>', methods= ['GET', 'POST'])
def registration(role_id):
    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        passwords = request.form['password']
        cnfpassword = request.form['confpassword']
       
        hashed_password = generate_password_hash(request.form['password'])
        hashed_conf_password = generate_password_hash(request.form['confpassword'])
        role_id = role_id 


        errors = []

        validators = [(validate_first_last_name, (first_name, 'First Name')),
                      (validate_first_last_name, (last_name, 'Last Name')),
                      (validate_email, (email,)),
                      (validate_phone_number, (phone_number,)),
                      (validate_password, (passwords,)),
                      (validate_confirm_password, (passwords, cnfpassword))
                     ]

        for validator, args in validators:
            error = validator(*args)
            if error:
                errors.append(error)

        if errors:
            for i in errors:
                flash(i)
            return redirect(url_for('registration'))


        user = User( 
            first_name = first_name,
            last_name = last_name,
            email = email,
            phone_number = phone_number,
            passwords = hashed_password,
            role_id = role_id 
        )

        db.session.add(user)
        db.session.commit()
        return 'User Inserted Successfully'
    return render_template('registration/registration.html', role_id=role_id)


class From_adress(db.Model):
    __tablename__ = 'location'
    __table_args__ = {'extend_existing': True}
    location_id = db.Column(db.Integer, primary_key = True)
    location_name = db.Column(db.String)

class Item_size(db.Model):
    __tablename__ = 'estimate_items'
    id = db.Column(db.Integer, primary_key = True)
    estimate_size = db.Column(db.String)
    price = db.Column(db.Float)

class Dash_items(db.Model):
    __tablename__ = 'item_size'
    item_id = db.Column(db.Integer, primary_key = True)
    item_name = db.Column(db.String)
    item_description = db.Column(db.Text)
    item_price = db.Column(db.Float)

class Packers(db.Model):
    __tablename__ = 'packers'
    packer_id = db.Column(db.Integer, primary_key = True)
    packer_name = db.Column(db.String)
    packer_email = db.Column(db.String)
    packer_phone_number = db.Column(db.BigInteger)

class Movers(db.Model):
    __tablename__ = 'movers'
    movers_id = db.Column(db.Integer, primary_key = True)
    movers_name = db.Column(db.String)
    movers_email = db.Column(db.String)
    movers_phone_number = db.Column(db.BigInteger)


class Distance(db.Model):
    __tablename__ = 'distance'
    distance_id = db.Column(db.Integer, primary_key = True)
    from_location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'))
    to_location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'))
    price = db.Column(db.Float)
    distance_km = db.Column(db.Integer)
    from_location = db.relationship('From_adress', foreign_keys=[from_location_id])
    to_location = db.relationship('From_adress', foreign_keys=[to_location_id])

class Bookings(db.Model):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users_table.user_id'))
    from_location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'))
    to_location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'))
    distance_id = db.Column(db.Integer, db.ForeignKey('distance.distance_id'))
    booking_date = db.Column(db.DateTime, default=db.func.now())
    booking_cost = db.Column(db.Numeric(10,2))
    booking_description = db.Column(db.Text)
    booking_status = db.Column(db.String, default='active')


@app.route('/homePage', methods=['GET', 'POST'])
def homePage():

    user_id = session.get('user_id')
    if not user_id:
        return redirect('login')

        

    locations = From_adress.query.with_entities(
        From_adress.location_id,
        From_adress.location_name
    ).all()

    all_items = Item_size.query.with_entities(
        Item_size.id,
        
        Item_size.estimate_size,
        Item_size.price
    ).all()

    lf = aliased(From_adress)
    lt = aliased(From_adress)
    distance_price = db.session.query(
        lf.location_name.label('from_location'),
        lt.location_name.label('to_location'),
        Distance.price.label('distance_price')
    ).select_from(Distance).join(lf, Distance.from_location).join(lt, Distance.to_location).all()
    

    from_address = None
    to_address = None
    selected_item = None
    estimated_cost = None
    if request.method == 'POST':
        from_address_id = request.form['from_address_id']
        to_address_id = request.form['to_address_id']
        selected_item_id  = request.form.get('items_id')
        

        if not from_address_id or not to_address_id or not selected_item_id:
            estimated_cost = "Please select From Location, To Location, and Item Size."
        else:
            from_address_id = int(from_address_id)
            to_address_id = int(to_address_id)
            selected_item_id = int(selected_item_id)

            if from_address_id:
                from_address = From_adress.query.get(from_address_id)
            if to_address_id:
                to_address = From_adress.query.get(to_address_id)
            if selected_item_id :
                selected_item = Item_size.query.get(selected_item_id)


            from_location = From_adress.query.filter_by(location_id = from_address_id).first()
            to_location = From_adress.query.filter_by(location_id = to_address_id).first()
            item = Item_size.query.filter_by(id = selected_item_id).first()
            
            if not from_location or not to_location or not item:
                estimated_cost = 'Invalid locations'
            else :
                distance = Distance.query.filter(
                    ((Distance.from_location_id == from_location.location_id) &
                    (Distance.to_location_id == to_location.location_id)) |
                    ((Distance.from_location_id == to_location.location_id) &
                    (Distance.to_location_id == from_location.location_id))
                ).first()

                if distance :
                    estimated_cost = distance.price + item.price 
                else :
                    estimated_cost = 'No select'

        flash(f'From ID: {from_address_id}, To ID: {to_address_id}, Selected Items: {selected_item}')

    return render_template('registration/homePage.html',locations=locations,items=all_items,from_address=from_address,
        to_address=to_address,selected_item=selected_item, estimated_cost= estimated_cost)


@app.route('/dashboard', methods=['GET'])
def dashboard():

    user_id = session.get('user_id')
    if not user_id:
        return redirect('login')


    items = Dash_items.query.all()   
    locations = From_adress.query.all()
    if session.get("role_id") == 1:
        booking_map = text("""
        SELECT 
            ut.first_name,
            ut.phone_number,
            b.booking_date,
            lf.location_name AS from_location,
            lt.location_name AS to_location,
            b.booking_description,
            b.booking_cost,
            b.booking_status
        FROM bookings b
        LEFT JOIN users_table ut ON b.user_id = ut.user_id
        LEFT JOIN location lf ON b.from_location_id = lf.location_id
        LEFT JOIN location lt ON b.to_location_id = lt.location_id
        ORDER BY b.booking_date DESC
        """)

        bookings = db.session.execute(booking_map).fetchall()

    else :
        booking_map  = text(
            """
            select ut.first_name, 
                ut.phone_number, 
                b.booking_date, 
                lf.location_name as from_location, 
                lt.location_name as to_location, 
                b.booking_description, 
                b.booking_cost, 
                b.booking_status 
            from bookings b
            left join users_table ut on b.user_id = ut.user_id
            left join location lf on b.from_location_id = lf.location_id
            left join location lt on b.to_location_id = lt.location_id
            WHERE ut.role_id = :role_id
            ORDER BY b.booking_date DESC
            """
        )
        bookings = db.session.execute(booking_map, {"role_id": session["role_id"]}).fetchall()

    lf = aliased(From_adress)
    lt = aliased(From_adress)
    distance_loc_join = db.session.query(
        Distance.distance_id,
        lf.location_name.label('from_location'),
        lt.location_name.label('to_location'),
        Distance.distance_km,
        Distance.price.label('distance_price')
    ).select_from(Distance).join(lf, Distance.from_location).join(lt, Distance.to_location).all()
    
    packers = User.query.with_entities(User.first_name.label('packer_name'),User.email.label('packer_email'),User.phone_number.label('packer_phone_number')).filter_by(role_id=3).all()
    movers = User.query.with_entities(User.first_name.label('movers_name'),User.email.label('movers_email'),User.phone_number.label('movers_phone_number')).filter_by(role_id=4).all()
    return render_template('registration/dashboard.html',items=items, locations=locations, distance=distance_loc_join, packers=packers, movers=movers, bookings= bookings)

@app.route('/booking', methods=['GET','POST'])
def booking():

    user_id = session.get('user_id')
    if not user_id:
        return redirect('login')

    item_sizes = Dash_items.query.all()
    locations = From_adress.query.all()
    
    return render_template('registration/booking.html', item_sizes=item_sizes, locations= locations)

@app.route('/create-booking', methods=['POST'])
def create_booking():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    from_location_id = request.form.get('from_address_id')
    to_location_id = request.form.get('to_address_id')

    # Distance
    distance = Distance.query.filter_by(
        from_location_id=from_location_id,
        to_location_id=to_location_id
    ).first()

    if not distance:
        return "Distance not available", 400

    total_price = float(distance.price)

    product_ids = request.form.getlist('product_id[]')
    quantities = request.form.getlist('quantity[]')


    # Items (dynamic)
    items = Dash_items.query.all()
    print('items:', items)
    description_list = []


    for product_id, qty in zip(product_ids, quantities):
        print('1234')
        if not product_id or not qty:
            continue

        item = Dash_items.query.get(int(product_id))
        print('item12:',item)
        qty = int(qty)
        print('quantity12:', qty)
        total_price += float(item.item_price) * qty
        print('total12:',total_price)
        description_list.append(f"{qty} {item.item_name}")
        print('desription12:', description_list)
    booking_description = ", ".join(description_list)
                                                    

    print('booking_desc:', booking_description)

    booking = Bookings(
        user_id=user_id,
        from_location_id=from_location_id,
        to_location_id=to_location_id,
        distance_id=distance.distance_id,
        booking_cost=total_price,
        booking_description=booking_description,
        booking_status='active'
    )

    db.session.add(booking)
    db.session.commit()

    return redirect('/booking')

@app.route('/update_item', methods=['POST'])
def update_item():
    item_id = request.form.get('item_id')
    item_name = request.form.get('item_name')
    item_description = request.form.get('item_description')
    item_price = request.form.get('item_price')

    if not item_id:
        return jsonify({"status": "error", "message": "No item ID received"})

    item = Dash_items.query.filter_by(item_id=item_id).first()
    
    if item:
        item.item_name = item_name
        item.item_description = item_description
        item.item_price = item_price
        print('items_pice:', item_price)
        db.session.commit()
        print('itemss_pice:', item_price)
        return jsonify({
            'status': 'success',
            'item' : {
                'item_id': item.item_id,
                'item_name': item.item_name,
                'item_description': item.item_description,
                'item_price' : item.item_price
            }
        })
    else :
        return jsonify({'status': 'Error'})


@app.route('/update_location', methods=['POST'])
def update_location():
    location_id = request.form.get('location_id')
    location_name = request.form.get('location_name')

    if not location_id:
        return jsonify({"status": "error", "message": "No location ID received"})
    
    location = From_adress.query.filter_by(location_id=location_id).first()
    print('location:', location)

    if location:
        location.location_id = location_id
        location.location_name = location_name
        db.session.commit()
        return jsonify({
            'status': 'success',
            'location' : {
                'location_id': location.location_id,
                "location_name" : location.location_name
            }
        })
    else:
        return jsonify({"status": "error"})


@app.route('/update_distance', methods=['POST'])
def update_distance():
    distance_id = request.form.get('distance_id')
    from_location = request.form.get('from_location')
    to_location = request.form.get('to_location')
    distance_km = request.form.get('distance_in_km')
    distance_price = request.form.get('distance_price')

    if not distance_id:
        return jsonify({"status": "error", "message": "No Distance ID received"})
    
    lf = aliased(From_adress)
    lt = aliased(From_adress)
    # distance_loc_join = db.session.query(
    #     Distance.distance_id,
    #     lf.location_name.label('from_location'),
    #     lt.location_name.label('to_location'),
    #     Distance.distance_km,
    #     Distance.price.label('distance_price')
    # ).select_from(Distance).join(lf, Distance.from_location).join(lt, Distance.to_location).filter(Distance.distance_id==distance_id).first()    

    distance = Distance.query.filter(
        Distance.distance_id == distance_id
    ).first()
    

    if distance:

        from_location_obj = From_adress.query.filter_by(location_name=from_location).first()
        to_location_obj = From_adress.query.filter_by(location_name=to_location).first()

        distance.from_location_id = from_location_obj.location_id
        distance.to_location_id = to_location_obj.location_id
        distance.distance_km = int(distance_km)
        distance.price = float(distance_price)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'distance': {
                'distance_id': distance.distance_id,
                'from_location': distance.from_location_id,
                'to_location': distance.to_location_id,
                'from_location': from_location_obj.location_name,
                'to_location': to_location_obj.location_name,
                'distance_km': distance.distance_km,
                'distance_price': distance.price
            }
        })
    else :
        return jsonify({
            'status': 'error'
        })




@app.route('/add_item', methods=['POST'])
def add_item():
    name = request.form.get('item_name')
    item_description = request.form.get('item_description')
    item_price = request.form.get('item_price')

    item_size = Dash_items(
        item_name = name,
        item_description = item_description,
        item_price = item_price
    )
    db.session.add(item_size)
    db.session.commit()
    return jsonify({
        'status': 'success',
        'item' :{
            'item_name': item_size.item_name,
            'item_description': item_size.item_description,
            'item_price': item_size.item_price
        }
    })



@app.route('/add_location', methods=['POST'])
def add_location():
    name = request.form.get('location_name')
    location = From_adress(
        location_name = name
    )
    db.session.add(location)
    db.session.commit()
    return jsonify({
        'status': 'success',
        'location' :{
            'location_name': location.location_name
        }
    })




@app.route('/delete_item', methods=['POST'])
def delete_item():
    item_id = request.form.get('id')

    item_delete = Dash_items.query.get(item_id)

    try:
        db.session.delete(item_delete)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})




@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True) 