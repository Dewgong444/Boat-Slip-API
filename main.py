from google.appengine.ext import ndb
import webapp2
import json

class Boat(ndb.Model):
    id = ndb.StringProperty()
    name = ndb.StringProperty()
    type = ndb.StringProperty()
    length = ndb.IntegerProperty()
    at_sea = ndb.BooleanProperty()

class Slip(ndb.Model):
    id = ndb.StringProperty()
    number = ndb.IntegerProperty(required=True)
    current_boat = ndb.StringProperty()
    arrival_date = ndb.StringProperty()

class Fish(ndb.Model):
    name = ndb.StringProperty(required=True)
    ph_min = ndb.IntegerProperty()
    ph_max = ndb.IntegerProperty()

class BoatHandler(webapp2.RequestHandler):
    def post(self):
        boat_data = json.loads(self.request.body)
        new_boat = Boat(name=boat_data['name'], type=boat_data['type'], length=boat_data['length'], at_sea=True)
        new_boat.put()
        new_boat.id = new_boat.key.urlsafe()
        new_boat.put()
        boat_dict = new_boat.to_dict()
        boat_dict['self'] = '/boat/' + new_boat.id
        self.response.write(json.dumps(boat_dict))

    def get(self):
        query1 = Boat.query()
        boatList = []
        for boat in query1:
            this_id = boat.id
            boat_dict = boat.to_dict()
            boat_dict['self'] = '/boat/' + str(this_id)
            boatList.append(boat_dict)
        self.response.write(json.dumps(boatList))

class boatIdHandler(webapp2.RequestHandler):
    def get(self, id=None):
        if id:
            b = ndb.Key(urlsafe=id).get()
            this_id = b.id
            b_dict = b.to_dict()
            b_dict['self'] = '/boat/' + str(this_id)
            self.response.write(json.dumps(b_dict))

    def delete(self, id=None):
        if id:
            boat_info = ndb.Key(urlsafe=id).get()
            boat_id = boat_info.id
            if boat_info.at_sea is False:
                this_query = Slip.query(Slip.current_boat == boat_id)
                for slip in this_query:
                    slip.current_boat = None
                    slip.put()
                    slip.arrival_date = None
                    slip.put()
            boat_info.key.delete()

    def put(self, id=None):
        if id:
            boat_data = json.loads(self.request.body)
            b = ndb.Key(urlsafe=id).get()
            b.name = boat_data['name']
            b.type = boat_data['type']
            b.length = boat_data['length']
            b.put()
            this_id = b.id
            b_dict = b.to_dict()
            b_dict['self'] = '/boat/' + str(this_id)
            self.response.write(json.dumps(b_dict))

    def patch(self, id=None):
        if id:
            boat_data = json.loads(self.request.body)
            b = ndb.Key(urlsafe=id).get()
            if 'name' in boat_data:
                b.name = boat_data['name']
                b.put()
            if 'type' in boat_data:
                b.type = boat_data['type']
                b.put()
            if 'length' in boat_data:
                b.length = boat_data['length']
                b.put()
            this_id = b.id
            b_dict = b.to_dict()
            b_dict['self'] = '/boat/' + str(this_id)
            self.response.write(json.dumps(b_dict))

class slipIdHandler(webapp2.RequestHandler):
    def get(self, id=None):
        if id:
            s = ndb.Key(urlsafe=id).get()
            this_id = s.id
            s_dict = s.to_dict()
            s_dict['self'] = '/slip/' + str(this_id)
            if s.current_boat is not None:
                boat_id = s.current_boat
                s_dict['boat_url'] = '/boat/' + str(boat_id)
            self.response.write(json.dumps(s_dict))

    def delete(self, id=None):
        if id:
            s = ndb.Key(urlsafe=id).get()
            if s.current_boat is not None:
                boat_id = s.current_boat
                boat_query = Boat.query(Boat.id == boat_id)
                for boat in boat_query:
                    boat.at_sea = True
                    boat.put()
            s.key.delete()

    def put(self, id=None):
        if id:
            slip_data = json.loads(self.request.body)
            s = ndb.Key(urlsafe=id).get()
            s.number = slip_data['number']
            s.put()
            this_id = s.id
            s_dict = s.to_dict()
            s_dict['self'] = '/slip/' + str(this_id)
            self.response.write(json.dumps(s_dict))

    def patch(self, id=None):
        if id:
            slip_data = json.loads(self.request.body)
            s = ndb.Key(urlsafe=id).get()
            s.number = slip_data['number']
            s.put()
            this_id = s.id
            s_dict = s.to_dict()
            s_dict['self'] = '/slip/' + str(this_id)
            self.response.write(json.dumps(s_dict))

class SlipHandler(webapp2.RequestHandler):
    def post(self):
        slip_data = json.loads(self.request.body)
        new_slip = Slip(number=slip_data['number'])
        new_slip.put()
        new_slip.id = new_slip.key.urlsafe()
        new_slip.put()
        slip_dict = new_slip.to_dict()
        slip_dict['self'] = '/slip/' + new_slip.id
        self.response.write(json.dumps(slip_dict))

    def get(self):
        query1 = Slip.query()
        slipList = []
        for slip in query1:
            this_id = slip.id
            slip_dict = slip.to_dict()
            slip_dict['self'] = '/slip/' + str(this_id)
            if slip.current_boat is not None:
                boat_id = slip.current_boat
                slip_dict['boat_url'] = '/boat/' + str(boat_id)
            slipList.append(slip_dict)
        self.response.write(json.dumps(slipList))

class ArrivalHandler(webapp2.RequestHandler):
    def put(self, id=None):
        if id:
            slip_data = json.loads(self.request.body)
            this_query = Slip.query(Slip.number == slip_data['number'])
            for slip in this_query:
                if slip.current_boat is None:
                    boat_info = ndb.Key(urlsafe=id).get()
                    boat_id = boat_info.id
                    boat_info.at_sea = False
                    boat_info.put()
                    slip.arrival_date = slip_data['date']
                    slip.put()
                    slip.current_boat = boat_info.id
                    slip.put()
                    slip_id = slip.id
                    slip_dict = slip.to_dict()
                    slip_dict['self'] = '/slip/' + str(slip_id)
                    slip_dict['boat_url'] = '/boat/' + str(boat_id)
                    self.response.write(json.dumps(slip_dict))
                else:
                    self.error(403)

class atSeaHandler(webapp2.RequestHandler):
    def put(self, id=None):
        if id:
            boat_info = ndb.Key(urlsafe=id).get()
            boat_info.at_sea = True
            boat_info.put()
            boat_id = boat_info.id
            this_query = Slip.query(Slip.current_boat == boat_id)
            for slip in this_query:
                slip.current_boat = None
                slip.put()
                slip.arrival_date = None
                slip.put()
            b_dict = boat_info.to_dict()
            b_dict['self'] = '/boat/' + str(boat_id)
            self.response.write(json.dumps(b_dict))

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("This is the main page for my API.")


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boat', BoatHandler),
    ('/boat/(.*)', boatIdHandler),
    ('/slip', SlipHandler),
    ('/slip/(.*)', slipIdHandler),
    ('/arrival/(.*)', ArrivalHandler),
    ('/atsea/(.*)', atSeaHandler),
], debug=True)
