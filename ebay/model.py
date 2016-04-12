
import web, datetime, time
#from dateutil import parser
from datetime import timedelta

db = web.database(dbn='sqlite', db='../sqlite.db')

time_format = '%Y-%m-%d %H:%M:%S'


def set_current_time(new_time):
    db.update('Time', where="1=1", current_time=new_time)


def get_current_time():
    time_string = db.select('Time')[0].current_time
    return datetime.datetime.strptime(time_string, time_format)


def get_items():
    return db.select('items', order='id DESC')


def get_select_items(category, title, description, price, open):
    if price == '':
        return db.select('items', order='id DESC', where='category like \'%' + category + '%\' and description like \'%' + description + '%\'' + ' and title like \'%' + title + '%\''  + ' and open like \'%' + open + '%\'')
    else:
        return db.select('items', order='id DESC', where='category like \'%' + category + '%\' and description like \'%' + description + '%\'' + ' and title like \'%' + title + '%\'' + ' and open like \'%' + open + '%\'' + ' and price ' + price )


def get_item(id):
    try:
        return db.select('items', where='id=$id', vars=locals())[0]
    except IndexError:
        return None


def new_item(category, title, description, price):
    db.insert('items', category=category, title=title, description=description, price=price, open=True, end_date=(get_current_time()+timedelta(days=7)).strftime(time_format))


def new_bid(id, buyer, price):
    db.insert('bids', id=id, buyer=buyer, price=price, bid_time=get_current_time().strftime(time_format))


def get_bids(id):
    if get_item(id) is None:
        return None
    else:
        return db.select('bids', where='id=$id', vars=locals(), order='bid_time DESC')


def get_highest_bid(id):
    try:
        return db.select('bids', where='id=$id', vars=locals(), order='price DESC')[0]
    except IndexError:
        return None


def del_post(id):
    db.delete('entries', where="id=$id", vars=locals())


def update_post(id, title, text):
    db.update('entries', where="id=$id", vars=locals(),
        title=title, content=text)