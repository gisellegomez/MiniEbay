import web
import datetime
import model
from calendar import monthrange

from web import form

render = web.template.render('templates/', base='base')

urls = ('/', 'Index',
        '/bid', 'Bid',
        '/bid/(\d+)', 'Bid',
        '/new', 'New',
        '/setDate', 'setDate'
)
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), 
        initializer={'id': ''})

setDateForm = form.Form(
    form.Textbox('year', form.regexp('\d+', 'Must be a digit')),
    form.Textbox('month', form.regexp('\d+', 'Must be a digit')),
    form.Textbox('day', form.regexp('\d+', 'Must be a digit')),
    form.Textbox('hour', form.regexp('\d+', 'Must be a digit')),
    form.Textbox('minute', form.regexp('\d+', 'Must be a digit')),
    form.Textbox('second', form.regexp('\d+', 'Must be a digit')),
    validators=[
        form.Validator('year out of range', lambda i: int(i.year) 
                in range(datetime.MINYEAR, datetime.MAXYEAR)),
        form.Validator('month out of range', lambda i: int(i.month) in range(1, 13)),
        form.Validator("day out of range", lambda i: int(i.day) in range(1, 32)), ##in range(monthrange(int(i.year), int(i.month))[1] + 1)
        form.Validator('hour out of range', lambda i: int(i.hour) in range(24)),
        form.Validator('minute out of range', lambda i: int(i.minute) in range(60)),
        form.Validator('second out of range', lambda i: int(i.second) in range(60)),
    ]
    )

class setDate:
    def __init__(self):
        self.form = setDateForm()
        current_time = model.get_current_time()
        self.form.year.value=current_time.year
        self.form.month.value=current_time.month
        self.form.day.value=current_time.day
        self.form.hour.value=current_time.hour
        self.form.minute.value=current_time.minute
        self.form.second.value=current_time.second

    def GET(self):
        return render.setDate(self.form, str(model.get_current_time()))

    def POST(self):
        if not self.form.validates():
            return render.setDate(self.form, str(model.get_current_time()))
        else:
            parsed_time = datetime.datetime(
                int(self.form.year.value), int(self.form.month.value), 
                        int(self.form.day.value),
                int(self.form.hour.value), int(self.form.minute.value), 
                        int(self.form.second.value)
            )
            model.set_current_time(parsed_time)
        return render.setDate(self.form, str(model.get_current_time()))

options = form.Form(
    form.Textbox('ID', form.regexp('^[0-9]*$', 'Invalid text'), value=""),
    form.Dropdown('Category', ['']),
    form.Textbox('Description', form.regexp('[^\'^\"]*', 'Invalid text'), value=""),
    form.Textbox('Price', form.regexp('[><]?[=]?\d*', 'Must be <, >, <=, or >=, followed by digits'), value=">=0.0"),
    form.Dropdown('Open', ['', 'Open', 'Closed'])
)

class Index: 
    def GET(self):
        columns = options()
        db = web.database(dbn='sqlite', db='../sqlite.db')
        categories = db.select('Categories', what='name').list()
        for category in categories:
            columns.Category.args = columns.Category.args + [category.name]
        items = model.get_items()
        return render.index(columns, items)

    def POST(self):
        columns = options() 
        db = web.database(dbn='sqlite', db='../sqlite.db')
        categories = db.select('categories', what='name').list()
        for category in categories:
            columns.Category.args = columns.Category.args + [category.name]
        if not columns.validates():
            print columns.render_css()
            raise web.seeother('/')
        else:
            print columns.d.Open
            items = model.get_select_items(columns.d.ID, columns.d.Category, 
                    columns.d.Description, columns.d.Price, columns.d.Open)
            return render.index(columns, items)        

bidForm = form.Form( 
       form.Dropdown('User', ['']),
       form.Textbox('Price', form.notnull, form.regexp('\d+', 'Must be a digit')),
       validators=[form.Validator("Price too low", lambda i: float(i.Price) > 0)]
)

class Bid:
    def __init__(self):
        self.bid = bidForm()
        db = web.database(dbn='sqlite', db='../sqlite.db')
        users = db.select('Users', what='user_id').list()
        self.bid.User.args = []
        for user in users:
            self.bid.User.args = self.bid.User.args + [user.user_id]

    def GET(self, item_id=None):
        if item_id is None:
            raise web.seeother('/')
        self.bid.d.itemID = item_id
        item = model.get_item(int(item_id))
        bids = model.get_bids(int(item_id))
        if item is None:
            raise web.seeother('/')
        web.setcookie('item_id', item.id)
        return render.bid(item, bids, self.bid)

    def BYNOW(self):
        item_id = web.cookies().get('item_id')
        item = model.get_item(int(item_id))
        buy_price = item.price
        model.new_bid((int(item_id)), self.bid['User'].value, buy_price)
        raise web.seeother('/bid/' + item_id)

    def POST(self):
        item_id = web.cookies().get('item_id')
        item = model.get_item(int(item_id))
        bids = model.get_bids(int(item_id))
        if item.open == 0:
            raise web.seeother('/bid/' + item_id)
        highest_bid = model.get_highest_bid((int(item_id)))
        buy_price = item.price
        if highest_bid is not None:
            self.bid.validators.append(
                form.Validator("Price must be higher than highest bid (" + str(highest_bid.new_price) + " by " +
                               highest_bid.item_buyer + ")", lambda i: float(i.Price) > highest_bid.new_price))
        # self.bid.validators.append(
            # form.Validator("Price higher than item's buy price (" + str(buy_price) +
            #                ")", lambda i: float(i.Price) >= buy_price))
        if not self.bid.validates():
            return render.bid(item, bids, self.bid)
        else:
            model.new_bid((int(item_id)), self.bid['User'].value, self.bid['Price'].value)    
            raise web.seeother('/bid/' + item_id)

newForm = form.Form( 
    form.Dropdown('Category', []),
    form.Textbox('Title', form.notnull, value=''),
    form.Textbox('Description', form.notnull, value=''),
    form.Textbox('Price', form.notnull, form.regexp('\d+', 'Must be a digit')),
    validators=[form.Validator("Price too low", lambda i: float(i.Price) > 0)]
)
class New: 
    def GET(self):
        form= newForm()
        db = web.database(dbn='sqlite', db='../sqlite.db')
        categories = db.select('Categories', what='name').list()
        form.Category.args=[]
        for category in categories:
            form.Category.args = form.Category.args + [category.name]
        return render.new(form)

    def POST(self):
        db = web.database(dbn='sqlite', db='../sqlite.db')
        form= newForm()
        categories = db.select('Categories', what='name').list()
        form.Category.args=['']
        for category in categories:
            form.Category.args = form.Category.args + [category.name]
        if not form.validates():
            return render.new(form)
        else:
            model.new_item(form['Category'].value, form['Title'].value, 
                form['Description'].value, form['Price'].value) 
        raise web.seeother('/')

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()
