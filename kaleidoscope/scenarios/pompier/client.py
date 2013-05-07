from os.path import join, dirname
from time import time
import thread

from kaleidoscope.scenario import KalScenarioClient

from kivy.clock import Clock
from kivy.resources import resource_add_path
from kivy.lang import Builder

from map_common import MapClientLayout, Map

resource_add_path(dirname(__file__))
Builder.load_file(join(dirname(__file__), 'map.kv'))

class MapClient(KalScenarioClient):
    def __init__(self, *largs):
        super(MapClient, self).__init__(*largs)
        self.count = 0
        self.timeout = 0
        self.layout = None
        #self.logo = ''
        Clock.schedule_interval(self.update_graphics_timer, 1 / 10.)

    # RECEIVE COMMANDS FROM SERVER
    
	#TODO: a nettoyer (seule la derniere ligne doit rester)
    def handle_selector(self, args):
        # self.layout.create_selector()
        # for val in self.layout.selector.buttons.itervalues():
        #     val.bind(on_release = self.validate)
        self.send('SCENARIO 0') 
        
    def handle_removeselector(self, args):
        self.layout.remove_selector()

    def handle_clear(self, args):
        pass

    def handle_waitready(self, args):
        pass

    def handle_time(self, args):
        self.timedelta, self.timeout = map(int, args.split())
        self.timedelta = time() - self.timedelta
        # apply that delta to timeout
        self.timeout += self.timedelta
        self.timelimit = self.timeout - time() 

    def handle_color(self, args):
        self.layout.color = map(lambda x: int(x) / 255., args.split())

    # def handle_logo(self, args):
    #     self.layout.logo = args

    def handle_layer(self, args):
        self.layout.layers = args

    def handle_mapsize(self, args):
        self.layout.mapsize = map(lambda x: int(x), args.split())

    def handle_mappos(self, args):
        self.layout.mappos = map(lambda x: int(x), args.split()) #(x,y)

    def handle_game(self,args):
        pass

    def handle_game1(self, args):
        self.layout = MapClientLayout(mapclient = self) 
        self.container.clear_widgets()
        self.container.add_widget(self.layout)
        self.layout.exitButton.bind(state= self.send_exitgame)

    def handle_map(self, args):
        self.imagemap = imagemap = self.layout.imagemap = self.layout.create_map()
        self.imagemap.update_images(0)
        for mapitem in imagemap.children[:] :
            mapitem.bind(flag_id = self.send_flag_change)
        #control the main map rotation with a controler
        # self.map_handler = self.layout.create_map_handler()
        # self.map_handler.bind(rotation = self.send_rotatemap)

    def handle_game2(self, args):
        self.layout.auto_color_thumbs()

    def handle_game3(self, args):
        self.layout.lock_thumbs(True)
        self.layout.hide_places()

    def handle_give(self, args):
        # create thumbnail in the gridlayout
        self.count += 1
        #print args
        index = int(args)
        item = self.layout.create_and_add_item(index)
        if item is not None :
            item.bind(mapitem = self.send_pos)

    #def handle_give2(self, args): #threaded version
    #    thread.start_new_thread(self.handle_give,(args, ))

    def handle_layoutall(self,args):
        self.layout.do_layout_all()

    def handle_thnotvalid(self, args):
        index = int(args)
        thumb = self.layout.get_thumb_from_index(index)
        if not thumb:
            return
        thumb.update_color(False)
        #shake !
        thumb.shake()

    def handle_thvalid(self, args):
        index = int(args)
        thumb = self.layout.get_thumb_from_index(index)
        if not thumb:
            return
        thumb.update_color(True)
        thumb.locked = True 

    def handle_hideth(self, args):
        return
        index = int(args)
        thumb = self.layout.get_thumb_from_index(index)
        if not thumb:
            return
        self.layout.remove_widget(thumb)

    def handle_displayth(self, args):
        index = int(args)
        thumb = self.layout.get_thumb_from_index(index)
        if not thumb:
            return
        self.layout.add_widget(thumb)

    def handle_displaymapitem(self, args):
        filename = str(args)
        self.layout.imagemap.display_mapitem(filename, True, (1,1,1,1))

    def handle_hidemapitem(self, args):
        return
        filename = str(args)
        self.layout.imagemap.hide_mapitem(filename)

    def handle_placethumbs(self, args):
        self.layout.place_thumbs()
        #send pos to server then
        for th in self.layout.items:
            th.locked = True
            self.send_pos(th,0)
            self.send_color(th,0)

    def handle_clear(self, args):
        self.layout.clear()


    # SEND TO SERVER  

    def validate(self, instance):
        scenario = instance.text
        print scenario + ' scenario was selected'
        if scenario == 'all': 
            index = -1
        else :
            index = self.layout.layers.index(scenario)
        #send index to server
        self.send('SCENARIO %d' % int(index)) 

    def send_pos(self, instance, value):
        value = instance.center
        if value is None:
            value = (-1,-1)
            return
        x,y = value
        x -= self.layout.imagemap.pos[0]
        y -= self.layout.imagemap.pos[1]
        self.send('POS %d %d %d' % (instance.index, x, y))
        #print "CLIENT : send POS"

    def send_color(self, instance, value):
        value = instance.color
        self.send('COLOR %d %d %d %d' % (instance.index, value[0]*255,value[1]*255,value[2]*255) )

    def send_flag_change(self, mapitem, flag_id):
        if flag_id is None:
            flag_id = -1
        filename_index = self.filename2index(mapitem.filename) 
        self.send('FLAGCHANGE %d %d' % (filename_index,flag_id) )
        #print "CLIENT : flag change : "+str(mapitem.filename) +' '+ str(flag_id)

    def filename2index(self,filename):
        #trick to pass mapitem.filename (string) as a integer (protocol blocks strings..)
        index = 0
        for i in self.imagemap.data :
            if i['filename'] == filename :
                return index
            index +=1

    def update_graphics_timer(self, dt):
        if not self.layout:
            return
        t = self.timeout - time()
        if t < 0:
            t = 0
        self.layout.time = t
        try:
            self.layout.timelimit = self.timelimit
        except:
            return 

    def send_rotatemap(self, instance, value):
        value = int(value)
        delta = value - self.layout.map_handler.last_rotation
        self.layout.map_handler.last_rotation = value
        if delta != 0 : 
            self.send('ROTATE %d' % delta )

    def send_exitgame(self, instance, value):
        print 'CLIENT : ', value
        if value == 'down':
            self.send('EXIT')

    def send_thheld(self, instance, th_index):
        pass

    def handle_thheld(self, instance, th_index):
        pass


         

    


scenario_class = MapClient
