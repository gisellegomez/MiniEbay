import web
import datetime
import time
from calendar import monthrange
from datetime import timedelta
from web import form

db = web.database(dbn='sqlite', db='sqlite.db')
render = web.template.render('templates/', base='base')
time_format = '%Y-%m-%d %H:%M:%S'
currentUser = ''

urls = ('/', 'Login', '/signup', 'Signup',
        '/index', 'Index', '/bid', 'Bid',
        '/bid/(\d+)', 'Bid', '/new', 'New',
        '/date', 'Date'
)
app = web.application(urls, globals())

loginForm = form.Form( 
    form.Textbox('Username', form.notnull, value=''),
    form.Password('Password', form.notnull, value='')
)
class Login: 
    def GET(self):
        form= loginForm()
        return render.login(form)

    def POST(self):
        global currentUser
        form= loginForm()
        if not form.validates():
            return render.login(form)
        else:
            item = 0
            try:
                whereString = 'user_id like \'%' + form['Username'].value + '%\''
                item = db.select('Users', where=whereString, vars=locals())[0]
                if item != 0 and item.password == form['Password'].value:
                    currentUser = form['Username'].value
                    print currentUser
                    raise web.seeother('/index')
                else:
                    return render.login(form)
            except IndexError:
                return render.login(form)


signupForm = form.Form( 
    form.Textbox('Username', form.notnull, value=''),
    form.Password('Password', form.notnull, value='')
)

class Signup: 
    def GET(self):
        form = signupForm()
        return render.signup(form)

    def POST(self):
        global currentUser
        form= signupForm()
        if not form.validates():
            return render.login(form)
        else:
            item = 0
            try:
                item = db.select('Users', where='user_id like \'%' + form['Username'].value + '%\'', vars=locals())[0]
                return render.signup(form)
            except IndexError:
                db.insert('Users', user_id=form['Username'].value, password=form['Password'].value)
                currentUser = form['Username'].value                
                raise web.seeother('/index')


months = []
days = []
hours = []
minsecs = []

for i in range (1, 13):
    months.append(str(i))
for i in range (1, 32):
    days.append(str(i))
for i in range (0, 24):
    hours.append(str(i))
for i in range (0, 60):
    minsecs.append(str(i))

dateForm = form.Form(
    form.Textbox('Year', form.regexp('\d+', 'Must be a digit')),
    form.Dropdown('Month', months),
    form.Dropdown('Day', days),
    form.Dropdown('Hour', hours),
    form.Dropdown('Minute', minsecs),
    form.Dropdown('Second', minsecs),
)

class Date:
    def __init__(self):
        self.form = dateForm()
        current_time = get_current_time()
        self.form.Year.value=current_time.year
        self.form.Month.value=current_time.month
        self.form.Day.value=current_time.day
        self.form.Hour.value=current_time.hour
        self.form.Minute.value=current_time.minute
        self.form.Second.value=current_time.second

    def GET(self):
        global currentUser
        return render.date(self.form, str(get_current_time()), currentUser)

    def RESET(self):
        global currentUser
        current_time = get_forever_time()
        self.form.Year.value=current_time.year
        self.form.Month.value=current_time.month
        self.form.Day.value=current_time.day
        self.form.Hour.value=current_time.hour
        self.form.Minute.value=current_time.minute
        self.form.Second.value=current_time.second
        parsed_time = datetime.datetime(
             int(self.form.Year.value), int(self.form.Month.value), 
                     int(self.form.Day.value),
             int(self.form.Hour.value), int(self.form.Minute.value), 
                     int(self.form.Second.value)
        )
        db.update('Time', where="1=1", current_time=parsed_time)
        return render.date(self.form, str(get_current_time()), currentUser)

    def POST(self):
        global currentUser
        if not self.form.validates():
            return render.date(self.form, str(get_current_time()), currentUser)
        else:
            parsed_time = datetime.datetime(
                int(self.form.Year.value), int(self.form.Month.value), 
                        int(self.form.Day.value),
                int(self.form.Hour.value), int(self.form.Minute.value), 
                        int(self.form.Second.value)
            )
            db.update('Time', where="1=1", current_time=parsed_time)
        return render.date(self.form, str(get_current_time()), currentUser)

options = form.Form(
    form.Textbox('ID', form.regexp('^[0-9]*$', 'Invalid text'), value=""),
    form.Dropdown('Category', ['']),
    form.Textbox('Description', form.regexp('[^\'^\"]*', 'Invalid text'), value=""),
    form.Textbox('Min Price', form.regexp('\d+', 'Must be a digit')),
    form.Textbox('Max Price', form.regexp('\d+', 'Must be a digit')),
    form.Dropdown('Status', ['', 'Open', 'Closed'])
)

class Index: 
    def GET(self):
        global currentUser
        print currentUser
        columns = options()
        categories = db.select('Categories', what='name').list()
        for category in categories:
            columns.Category.args = columns.Category.args + [category.name]
        items = get_items()
        return render.index(columns, items, currentUser)

    def POST(self):
        global currentUser
        columns = options() 
        categories = db.select('Categories', what='name').list()
        for category in categories:
            columns.Category.args = columns.Category.args + [category.name]
        if not columns.validates():
            print columns.render_css()
            raise web.seeother('/index')
        else:
            print columns.d.Status
            items = get_select_items(columns.d.ID, columns.d.Category, 
                    columns.d.Description, form['Min Price'].value, 
                    form['Max Price'].value, columns.d.Status)
            return render.index(columns, items, currentUser)        

bidForm = form.Form( 
       form.Textbox('Price', form.notnull, form.regexp('\d+', 'Must be a digit')),
       validators=[form.Validator("Price too low", lambda i: float(i.Price) > 0)]
)

class Bid:
    def __init__(self):
        self.bid = bidForm()

    def GET(self, item_id=None):
        global currentUser
        if item_id is None:
            raise web.seeother('/index')
        self.bid.d.itemID = item_id
        item = get_item(int(item_id))
        bids = get_bids(int(item_id))
        if item is None:
            raise web.seeother('/index')
        web.setcookie('item_id', item.id)
        return render.bid(item, bids, self.bid, currentUser)

    def BYNOW(self):
        global currentUser
        item_id = web.cookies().get('item_id')
        item = get_item(int(item_id))
        buy_price = item.price
        db.insert('Bids', items_id=int(item_id), item_buyer=currentUser, 
                    new_price=buy_price, 
                    b_time=get_current_time().strftime(time_format))  
        raise web.seeother('/bid/' + item_id)

    def POST(self):
        global currentUser
        item_id = web.cookies().get('item_id')
        item = get_item(int(item_id))
        bids = get_bids(int(item_id))
        if item.open == 0:
            raise web.seeother('/bid/' + item_id)
        highest_bid = get_highest_bid((int(item_id)))
        buy_price = item.price
        if highest_bid is not None:
            self.bid.validators.append(
                form.Validator("Price must be higher than highest bid (" + str(highest_bid.new_price) + " by " +
                               highest_bid.item_buyer + ")", lambda i: float(i.Price) > highest_bid.new_price))
        if not self.bid.validates():
            return render.bid(item, bids, self.bid, currentUser)
        else:
            db.insert('Bids', items_id=int(item_id), item_buyer=currentUser, 
                    new_price=self.bid['Price'].value, 
                    b_time=get_current_time().strftime(time_format))   
            raise web.seeother('/bid/' + item_id)

newForm = form.Form( 
    form.Textbox('Title', form.notnull, value=''),
    form.Dropdown('Category', []),
    form.Textbox('Description', form.notnull, value=''),
    form.Textbox('Price', form.notnull, form.regexp('\d+', 'Must be a digit')),
    form.Textbox('Days Until End', form.notnull, form.regexp('\d+', 'Must be a digit')),
    validators=[form.Validator("Price too low", lambda i: float(i.Price) > 0)]
)
class New: 
    def GET(self):
        global currentUser
        form= newForm()
        categories = db.select('Categories', what='name').list()
        form.Category.args=[]
        for category in categories:
            form.Category.args = form.Category.args + [category.name]
        return render.new(form, currentUser)

    def POST(self):
        global currentUser
        form= newForm()
        categories = db.select('Categories', what='name').list()
        form.Category.args=['']
        for category in categories:
            form.Category.args = form.Category.args + [category.name]
        if not form.validates():
            return render.new(form, currentUser)
        else:
            print form['Title'].value
            new_item(form['Category'].value, form['Title'].value, 
                form['Description'].value, form['Price'].value,
                form['Days Until End'].value) 
        raise web.seeother('/index')

def get_current_time():
    time_string = db.select('Time')[0].current_time
    return datetime.datetime.strptime(time_string, time_format)

def get_forever_time():
    time_string = db.select('Time')[0].forever_time
    return datetime.datetime.strptime(time_string, time_format)    

def get_items():
    return db.select('Items', order='id DESC')

def get_select_items(id, category, description, minPrice, maxPrice, open):
    if open == 'Open':
        open = '1'
    if open == 'Closed':
        open = '0'
    whereString = ('category like \'%' + category + '%\' and description like \'%' + 
            description + '%\'' + ' and open like \'%' + open + '%\'')
    if id != '':
        whereString += ' and id=' + id
    if minPrice != '':
        whereString += ' and price >' + minPrice
    if maxPrice != '':
        whereString += ' and price <' + maxPrice
    return db.select('Items', order='id DESC', where=whereString)

def get_item(id):
    try:
        return db.select('Items', where='id=$id', vars=locals())[0]
    except IndexError:
        return None

def new_item(category, title, description, price, daysLast):
    db.insert('items', category=category, title=title, description=description, 
        price=price, open=True, end_date=(get_current_time() + 
        timedelta(days=int(daysLast))).strftime(time_format))

def get_bids(id):
    if get_item(id) is None:
        return None
    else:
        return db.select('Bids', where='items_id=$id', vars=locals(), order='b_time DESC')

def get_highest_bid(id):
    try:
        return db.select('Bids', where='items_id=$id', vars=locals(), order='new_price DESC')[0]
    except IndexError:
        return None

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()
