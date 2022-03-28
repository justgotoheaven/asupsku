# -*- coding: utf-8 -*-
from app import app, db
from flask_login import current_user
from models import User, Counter, Pokaz
from datetime import date, datetime
import json
import utils

@app.route('/api/get_counter_info/<int:cid>', methods=['GET'])
def counter_info(cid):
    data = {'status_code': 0}
    if current_user.is_authenticated:
        c_info = db.session.query(Counter).filter(Counter.id == cid).first()
        if not c_info:
            data['status_code'] = 404
        else:
            if c_info.owner == current_user.id:
                data['status_code'] = 200
                data['name'] = c_info.name
                data['zn'] = c_info.znomer
                data['ust_date'] = c_info.ust_data.strftime('%d.%m.%Y')
                data['pov_date'] = c_info.pov_data.strftime('%d.%m.%Y')
                data['nextpov_date'] = c_info.nextpov_data.strftime('%d.%m.%Y')
            else:
                data['status_code'] = 403
    else:
        data['status_code'] = 403    
    return json.dumps(data,default=str)

@app.route('/api/get_pkz/<int:cid>', methods=['GET','POST'])
def get_pkz(cid):
    data = {'status_code': 0}
    if current_user.is_authenticated:
        p_info = db.session.query(Pokaz).filter(Pokaz.counter == cid, Pokaz.month >= utils.now_month()-1, 
                                                Pokaz.month <= utils.now_month()+1).order_by(Pokaz.id.desc()).limit(5)
        if not p_info:
            data['status_code'] = 404
        else:
            data['status_code'] = 200
            pkz_data = []
            for p in p_info:
                current_data = {'pokaz': p.pokaz} 
                person = db.session.query(User).filter(User.id == p.person).first()
                if person:
                    current_data['person'] = person.min_name()
                else:
                    current_data['person'] = 'Неизвестно'
                current_data['month'] = p.month
                current_data['month_name'] = utils.month_name(p.month)
                current_data['pdate'] = p.date.strftime('%d.%m.%Y')
                pkz_data.append(current_data)
            data['info'] = pkz_data
    else:
        data['status_code'] = 403   
    return json.dumps(data,default=str)

def str_to_float_pkz(pkz):
    if pkz.find(',') != -1:
        pkz = pkz.replace(',','.')
    try:
        new_pkz = float(pkz)
        return new_pkz
    except ValueError:
        return -1    

@app.route('/api/set_pkz/<int:cid>/<int:month>/<pkz>', methods=['GET'])
def set_pkz(cid,month,pkz):
    data = {'status_code': 0}
    if str_to_float_pkz(pkz) == -1:
        return 500
    if current_user.is_authenticated:
        counter_info = db.session.query(Counter).filter(Counter.id == cid).first()
        if counter_info:
            if counter_info.owner == current_user.id:
                new_pkz = Pokaz(counter=counter_info.id, person=current_user.id, date=date.today(), month=month, pokaz=str_to_float_pkz(pkz))
                db.session.add(new_pkz)
                db.session.commit()
                data['status_code'] = 200
            else:
                data['status_code'] = 403
        else:
            data['status_code'] = 403
    else:
        data['status_code'] = 403    
    return json.dumps(data,default=str)