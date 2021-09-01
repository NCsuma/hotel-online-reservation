from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from flask_restful import Api
from sqlalchemy.exc import SQLAlchemyError


app = Flask(__name__)
conn = "mysql://{0}:{1}@{2}/{3}".format('root', '', 'localhost', 'onlinereservationdb')
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

api = Api(app)

Base = automap_base()
Base.prepare(db.engine, reflect=True)
UserAccounts = Base.classes.useraccounts
Guest = Base.classes.guest
Room = Base.classes.room
RoomType = Base.classes.roomtype
Amenities = Base.classes.amenities
Reservation = Base.classes.reservation
Comments = Base.classes.comments
MessageIn = Base.classes.messagein
MessageOut = Base.classes.messageout


def get_user_name(account_username):
    try:
        user_name_result = db.session.query(UserAccounts).filter_by(ACCOUNT_USERNAME=account_username).first()
        if user_name_result:
            return jsonify({"account_id": user_name_result.ACCOUNT_ID})
        else:
            return jsonify({"account_id": ""})
    except SQLAlchemyError as e:
        return e


@app.route('/register/create', methods=['POST'])
def register():
    account_name = request.json['ACCOUNT_NAME']
    account_username = request.json['ACCOUNT_USERNAME']
    account_password = request.json['ACCOUNT_PASSWORD']
    account_type = request.json['ACCOUNT_TYPE']

    try:
        new_data = UserAccounts(ACCOUNT_NAME=account_name,
                                ACCOUNT_USERNAME=account_username, ACCOUNT_PASSWORD=account_password,
                                ACCOUNT_TYPE=account_type)
        acc_user_id = get_user_name(account_username)  # To check if emailid exists
        if not acc_user_id.json['account_id']:
            if new_data:
                db.session.add(new_data)
                db.session.commit()
                return "Data added successfully"
        else:
            return "User already exists"

    except SQLAlchemyError as e:
        return e


@app.route('/login/create', methods=['POST'])
def login():
    account_username = request.json['ACCOUNT_USERNAME']
    account_password = request.json['ACCOUNT_PASSWORD']
    try:
        login_result = db.session.query(UserAccounts).filter_by(ACCOUNT_USERNAME=account_username,
                                                                ACCOUNT_PASSWORD=account_password).all()
        if login_result:
            return jsonify(
                {"account_name": login_result[0].ACCOUNT_NAME, "account_username": login_result[0].ACCOUNT_USERNAME,
                 "account_type": login_result[0].ACCOUNT_TYPE})
        else:
            return "Credentials doesn't match"
    except SQLAlchemyError as e:
        return e


@app.route('/user_accounts/update', methods=['PUT'])
def user_update():
    account_id = request.json['ACCOUNT_ID']
    account_name = request.json['ACCOUNT_NAME']
    account_password = request.json['ACCOUNT_PASSWORD']
    try:
        result = db.session.query(UserAccounts).filter_by(ACCOUNT_ID=account_id).first()
        if account_name:
            result.ACCOUNT_NAME = account_name
        if account_password:
            result.ACCOUNT_PASSWORD = account_password
        db.session.commit()
        return "Data updated successfully"
    except SQLAlchemyError as e:
        return e


@app.route('/guest/create', methods=['POST'])
def guest():
    guest_input = request.get_json()
    if guest_input:
        guest_count = 0
        try:
            for item in guest_input:
                new_data = Guest(firstname=item["firstname"], lastname=item["lastname"], country=item["country"],
                                 city=item["city"], address=item["address"], zip=item["zip"], phone=item["phone"],
                                 email=item["email"], password=item["password"])
                if new_data:
                    db.session.add(new_data)
                    db.session.commit()
                    guest_count += 1
                    return "Data added successfully"

                else:
                    return "Data insertion unsuccessful"
        except SQLAlchemyError as e:
            return e


@app.route('/guest/update', methods=['PUT'])
def guest_update():
    guest_id = request.json['guest_id']
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    try:
        result = db.session.query(Guest).filter_by(guest_id=guest_id).first()
        if firstname:
            result.firstname = firstname
        if lastname:
            result.lastname = lastname
        db.session.commit()
        return "Data updated successfully"
    except SQLAlchemyError as e:
        return e


@app.route('/guest', methods=['GET'])
def get_all_guests():
    try:
        guest_result = db.session.query(Guest).all()
        if guest_result:
            guest_list = []
            guest_count = 0
            for item in guest_result:
                guest_list.append({"firstname": item.firstname, "lastname": item.lastname, "country": item.country,
                                   "city": item.city, "address": item.address, "zip": item.zip, "phone": item.phone,
                                   "email": item.email, "password": item.password})
                guest_count += 1
            return jsonify(guest_list)
        else:
            return "No Data Found"
    except SQLAlchemyError as e:
        return e


@app.route('/guest/<int:guest_id>', methods=['GET'])
def get_guest_by_id(guest_id=None):
    guest_id = guest_id
    try:
        guest_result = db.session.query(Guest).filter_by(guest_id=guest_id).first()
        if guest_result:
            return jsonify({"guest_id": guest_result.guest_id, "firstname": guest_result.firstname,
                            "lastname": guest_result.lastname,
                            "country": guest_result.country,
                            "city": guest_result.city, "address": guest_result.address, "zip": guest_result.zip,
                            "phone": guest_result.phone,
                            "email": guest_result.email, "password": guest_result.password})

        else:
            return "No Data Found"
    except SQLAlchemyError as e:
        return e


@app.route('/room', methods=['GET'])
def room_details():
    try:
        room_result = db.session.query(Room, RoomType).join(RoomType, Room.typeID == RoomType.typeID).all()
        if room_result:
            room_list = []
            room_count = 0
            for items in room_result:
                room_list.append(
                    {"roomNo": items.room.roomNo, "typeID": items.room.typeID, "roomName": items.room.roomName,
                     "price": items.room.price, "Adults": items.room.Adults, "Children": items.room.Children,
                     "roomImage": items.room.roomImage, "typename": items.roomtype.typename,
                     "Desp": items.roomtype.Desp})
                room_count += 1
            return jsonify({"Room": room_list})
        else:
            return "No Data Found"
    except Exception as e:
        return e


@app.route('/room/update', methods=['PUT'])
def room_details_update():
    roomNo = request.json['roomNo']
    price = request.json['price']
    try:
        result = db.session.query(Room).filter_by(roomNo=roomNo).first()
        if price:
            result.price = price
        db.session.commit()
        return "Data updated successfully"
    except SQLAlchemyError as e:
        return e


@app.route('/amenities/create', methods=['POST'])
def amenities():
    amen_input = request.get_json()
    if amen_input:
        amen_count = 0
        try:
            for item in amen_input:
                new_data = Amenities(amen_name=item['amen_name'], amen_desp=item['amen_desp'],
                                     amen_image=item['amen_image'])
                if new_data:
                    db.session.add(new_data)
                    db.session.commit()
                    amen_count += 1
                    return "Data added successfully"
                else:
                    return "Data insertion unsuccessful"

        except SQLAlchemyError as e:
            return e


@app.route('/amenities/update', methods=['PUT'])
def amenities_update():
    amen_id = request.json['amen_id']
    amen_name = request.json['amen_name']
    amen_desp = request.json['amen_desp']
    amen_image = request.json['amen_image']
    try:
        result = db.session.query(Amenities).filter_by(amen_id=amen_id).first()
        if amen_name:
            result.amen_name = amen_name
        if amen_desp:
            result.amen_desp = amen_desp
        if amen_image:
            result.amen_image = amen_image
        db.session.commit()
        return "Data updated successfully"
    except SQLAlchemyError as e:
        return e


@app.route('/amenities/delete', methods=['DELETE'])
def amenities_delete():
    amen_id = request.json['amen_id']
    try:
        result = db.session.query(Amenities).filter_by(amen_id=amen_id).first()
        db.session.delete(result)
        db.session.commit()
        return "Data deleted successfully"
    except SQLAlchemyError as e:
        return e


@app.route('/reservation/create', methods=['POST'])
def reservation():
    reserve_input = request.get_json()
    if reserve_input:
        reserve_count = 0
        try:
            for item in reserve_input:
                new_data = Reservation(roomNo=item["roomNo"], guest_id=item["guest_id"], arrival=item["arrival"],
                                       departure=item["departure"],
                                       adults=item["adults"], child=item["child"], payable=item["payable"],
                                       status=item["status"],
                                       booked=item["booked"], confirmation=item["confirmation"])
                if new_data:
                    db.session.add(new_data)
                    db.session.commit()
                    reserve_count += 1
                    return "Data added successfully"
                else:
                    return "Data insertion unsuccessful"
        except SQLAlchemyError as e:
            return e


@app.route('/reservation', methods=['GET'])
def reservation_details():
    try:
        result = db.session.query(Reservation, Room, Guest).join(Room, Reservation.roomNo == Room.roomNo).join(Guest,
                                                                                                               Reservation.guest_id == Guest.guest_id).all()
        if result:
            final_list = []
            count = 0
            for items in result:
                final_list.append(
                    {"firstname": items.guest.firstname, "lastname": items.guest.lastname, "phone": items.guest.phone,
                     "email": items.guest.email, "roomName": items.room.roomName,
                     "reservation_id": items.reservation.reservation_id,
                     "roomNo": items.reservation.roomNo, "guest_id": items.reservation.guest_id,
                     "arrival": items.reservation.arrival,
                     "departure": items.reservation.departure, "adults": items.reservation.adults,
                     "child": items.reservation.child,
                     "payable": items.reservation.payable, "status": items.reservation.status,
                     "booked": items.reservation.booked,
                     "confirmation": items.reservation.confirmation})
                count += 1
            return jsonify({"Details": final_list})
        else:
            return "No Data Found"
    except Exception as e:
        return e


@app.route('/reservation/<int:reservation_id>', methods=['GET'])
def reservation_by_id(reservation_id=None):
    reservation_id = reservation_id
    try:
        result = db.session.query(Reservation, Room, Guest).filter_by(reservation_id=reservation_id).join(Room,
                                                                                                          Reservation.roomNo == Room.roomNo).join(
            Guest, Reservation.guest_id == Guest.guest_id) \
            .first()
        if result:
            return jsonify(
                {"firstname": result.guest.firstname, "lastname": result.guest.lastname, "phone": result.guest.phone,
                 "email": result.guest.email, "roomName": result.room.roomName,
                 "reservation_id": result.reservation.reservation_id,
                 "roomNo": result.reservation.roomNo, "guest_id": result.reservation.guest_id,
                 "arrival": result.reservation.arrival,
                 "departure": result.reservation.departure, "adults": result.reservation.adults,
                 "child": result.reservation.child,
                 "payable": result.reservation.payable, "status": result.reservation.status,
                 "booked": result.reservation.booked,
                 "confirmation": result.reservation.confirmation})
        else:
            return "No Data Found"
    except Exception as e:
        return e


@app.route('/comments/create', methods=['POST'])
def comments():
    firstname = request.json["firstname"]
    lastname = request.json["lastname"]
    email = request.json["email"]
    comment = request.json["comment"]
    try:
        new_data = Comments(firstname=firstname, lastname=lastname, email=email, comment=comment)
        if new_data:
            db.session.add(new_data)
            db.session.commit()
            return "Data added successfully"
        else:
            return "Data insertion unsuccessful"
    except SQLAlchemyError as e:
        return e


@app.route('/comments/delete', methods=['DELETE'])
def comments_delete():
    comment_id = request.json['comment_id']
    try:
        result = db.session.query(Comments).filter_by(comment_id=comment_id).first()
        db.session.delete(result)
        db.session.commit()
        return "Data deleted successfully"
    except SQLAlchemyError as e:
        return e


@app.route('/messagein/create', methods=['POST'])
def messagein():
    sender = request.json["sender"]
    receiver = request.json["receiver"]
    msg = request.json["msg"]
    senttime = request.json["senttime"]
    receivedtime = request.json["receivedtime"]
    operator = request.json["operator"]
    msgtype = request.json["msgtype"]
    reference = request.json["reference"]

    try:
        new_data = MessageIn(sender=sender, receiver=receiver, msg=msg, senttime=senttime, receivedtime=receivedtime,
                             operator=operator, msgtype=msgtype, reference=reference)
        if new_data:
            db.session.add(new_data)
            db.session.commit()
            return "Data added successfully"
        else:
            return "Data insertion unsuccessful"
    except SQLAlchemyError as e:
        return e


@app.route('/messageout/create', methods=['POST'])
def messageout():
    sender = request.json["sender"]
    receiver = request.json["receiver"]
    msg = request.json["msg"]
    senttime = request.json["senttime"]
    receivedtime = request.json["receivedtime"]
    reference = request.json["reference"]
    status = request.json["status"]
    msgtype = request.json["msgtype"]
    operator = request.json["operator"]

    try:
        new_data = MessageOut(sender=sender, receiver=receiver, msg=msg, senttime=senttime, receivedtime=receivedtime,
                              reference=reference, status=status, msgtype=msgtype, operator=operator)
        if new_data:
            db.session.add(new_data)
            db.session.commit()
            return "Data added successfully"
        else:
            return "Data insertion unsuccessful"
    except SQLAlchemyError as e:
        return e


if __name__ == '__main__':
    app.run(debug=True, host='localhost', threaded=True)
