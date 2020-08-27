from flask import Flask, jsonify, request
from flask_cors import CORS
# from flask_pymongo import PyMongo
from pymongo import MongoClient
import base64

from bson import json_util
from bson.objectid import ObjectId
import json
# from mongoflask import MongoJSONEncoder, ObjectIdConverter
from cryptography.fernet import Fernet

app = Flask(__name__)

# client = MongoClient(your mongo database connection)
db = client.sample_airbnb

CORS(app)
# mongo = PyMongo(app)


def facilities(farenId):
    facilities = db.facilities
    facils = []
    for item in db.facilities.find({ "farenId": farenId }):
        facils.append(item["title"])
    return facils


secret_key = b'CWV5t4gmiAdPpgur-GbWcLswv2BL-8b4hD1PB9N5uQY='
def coding(coding_type, msg_text):
    # secret_key = Fernet.generate_key(); # To-DO (later should use dynamic secret_key)
    keyed_fernet = Fernet(secret_key)
    if coding_type == 'encrypt':
        encoded_msg = msg_text.encode('utf-8')
        return str(keyed_fernet.encrypt(encoded_msg))
    else:
        decrypted = keyed_fernet.decrypt(msg_text.encode('utf-8'))
        return decrypted.decode('utf-8')

@app.route('/hotel', methods=['POST'])
def show_hotel():
    # setup not shown, pretend this gets us a pymongo db object
    hotel_id = request.get_json();
    if hotel_id["id"]:
        decoded = coding('decrypt', str(hotel_id["id"]))
        decrypted_Id = ObjectId(decoded)

        hotels = db.hotel
        #output = []
        row = db.hotels.find_one({'_id': decrypted_Id})

        #output.append()

        return jsonify({'result': {
                        #'id':  coding('encrypt', str(item['_id'])),
                        'name': row['name'],
                        'country': row['country'],
                        'city': row['city'],
                        'img': row['img'],
                        'facilities': facilities(decrypted_Id),
                        'desc': row['desc']} }) 
       # return json.dumps(hotel_id["id"], indent=4, default=json_util.default) 


@app.route('/hotels', methods=['GET'])
def get_sample_airbnb():
    hotels = db.hotels
    output = []

    for item in hotels.find():
        output.append({
                       'id':  coding('encrypt', str(item['_id'])),
                       'name': item['name'],
                       'country': item['country'],
                       'city': item['city'],
                       'img': item['img'],
                       'desc': item['desc']})

    return jsonify({'result': output}) 


def insert_document_booking(collection, documentToInsert):
    try:
        collection.insert_one(documentToInsert)
        return {"isInserted": True}
    except Exception as e:
        print("An exception occurred ::", e)
        return {"isInserted": False, "exactError": "An exception occurred :: " + e}

@app.route('/insertBooking', methods=['POST'])
def insertBooking():
    details = request.get_json();
    output = "";
    if details["hotelId"]:
        decoded = coding('decrypt', str(details["hotelId"]))
        post = {
            "hotelId": ObjectId(decoded),
            "startDate": details["startDate"],
            "endDate": details["endDate"],
            "FirstName": details["FirstName"],
            "LastName": details["LastName"],
            "Nationality": details["Nationality"],
            "PassportNumber": details["PassportNumber"],
            "PhoneNumber": details["PhoneNumber"],
            "Address": details["Address"]
            
        }

        insertResult = insert_document_booking(db.booking, post)
        if insertResult["isInserted"]:
            output = {"isInserted": True ,"msg": "inserted Successfully"}
        else:
            output = {"isInserted": False ,"msg": "Some Error Happened during insertion", "exactError": insertResult["exactError"]}

        return jsonify({'result': output})

@app.route('/readBooking/<string:hotelId>', methods=['GET'])
def readBooking(hotelId):
    output = [];
    if hotelId:
        decoded = coding('decrypt', hotelId)

        for item in db.booking.find({'hotelId': ObjectId(decoded)}):
            output.append({ 'startDate': item['startDate'], 'endDate': item['endDate']})

        return jsonify({'result': output}) 


if __name__ == '__main__':
    app.run(debug=True)
