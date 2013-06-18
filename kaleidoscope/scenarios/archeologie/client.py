# -*- coding: utf-8 -*-

from os.path import join, dirname
from time import time
import thread

from kaleidoscope.scenario import KalScenarioClient

from kivy.clock import Clock
from kivy.resources import resource_add_path
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Canvas

from map_common import MapClientLayout, Map, MapMenu, MapThumbnail

resource_add_path(dirname(__file__))
Builder.load_file(join(dirname(__file__), 'map.kv'))

class MapClient(KalScenarioClient):
    def __init__(self, *largs):
        super(MapClient, self).__init__(*largs)
        self.count = 0
        self.timeout = 0
        self.layout = None
        self.menu = None
        self.isPlaying = False
        #self.logo = ''
        self.color = (1,1,1,0)
        Clock.schedule_interval(self.update_graphics_timer, 1/ 100.)
        # Clock.schedule_interval(self.update_graphics_timer, 1 / 10.)
        self.index_list = []
        if self.container.couleur_auto == 'vert 1':
            self.place = 1
        elif self.container.couleur_auto == 'bleu 3':
            self.place = 3
        elif self.container.couleur_auto == 'orange 2':
            self.place = 2
        elif self.container.couleur_auto == 'violet 4':
            self.place = 4

    # RECEIVE COMMANDS FROM SERVER
    
	#TODO: a nettoyer (seule la derniere ligne doit rester)
    def handle_selector(self, args):
        # self.layout.create_selector()
        # for val in self.layout.selector.buttons.itervalues():
        #     val.bind(on_release = self.validate)
        Clock.unschedule(self.update_graphics_timer)
        Clock.schedule_interval(self.update_graphics_timer, 1.)
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
        if hasattr(self, "menu"):
            self.menu.timeout = self.timelimit

    def handle_color(self, args):
        if not self.layout:
            self.color = map(lambda x: int(x) / 255., args.split())
            return
        self.layout.color = map(lambda x: int(x) / 255., args.split())

    # def handle_logo(self, args):
    #     self.layout.logo = args

    def handle_layer(self, args):
        self.layout.layers = args


    def handle_mapsize(self, args):
        # print 'handle mapsize'
        self.layout.mapsize = map(lambda x: int(x), args.split())

    def handle_mappos(self, args):
        # print 'handle map pos'
        self.layout.mappos = map(lambda x: int(x), args.split()) #(x,y)

    def handle_game(self,args):
        pass

    def handle_menu(self, args):
        self.menu = MapMenu(color=self.color, place=(self.place-1))
        self.container.clear_widgets()
        self.container.add_widget(self.menu)  
        self.menu.launchGameButton.bind(state = self.send_launchGame)

    def handle_game_start(self, args):
        # afficher le timer et indication : la partie a demarree
        pass

    def handle_wait_game(self, args):
        self.menu.launchGameButton.opacity = 0
        self.menu.labelLaunchGame.text = 'ATTENDRE LA FIN DE PARTIE EN COURS'
        self.menu.launchGameButton.unbind(state = self.send_launchGame)
        # Changer lecran : le joueur doit attendre la prochaine partie

    def handle_game1(self, args):
        self.isPlaying = True
        self.layout = MapClientLayout(mapclient = self) 
        self.container.clear_widgets()
        self.container.add_widget(self.layout)
        self.layout.labelStatus.text = 'ASSOCIATION'
        # self.layout.exitButton.bind(state= self.send_exitgame)

    def handle_map(self, args):
        self.imagemap = imagemap = self.layout.imagemap = self.layout.create_map(self.place - 1)
        # self.imagemap.update_images(0)
        #control the main map rotation with a controler
        # self.map_handler = self.layout.create_map_handler()
        # self.map_handler.bind(rotation = self.send_rotatemap)

    def handle_game2(self, args):
        self.layout.auto_color_thumbs()
        self.layout.labelStatus.text = 'CORRECTION'
        for th in self.layout.items:
            self.send_pos(th,0)
        
    def handle_popup(self, args):
        self.layout.clear()

        label = Label(text= ' L’archéologue en déduit les modes de culture,\nd’élevage et d’alimentation sur le site de Montout\nà l’époque médiévale.',pos=(0,0), 
            size=(1280,800), 
            font_size=45, 
            font_name='data/fonts/FuturaLT-Bold.ttf',
            halign= 'center',
            valign= 'middle',
            color = self.color + [1])
        
        self.layout.add_widget(label)


        
    def handle_game3(self, args):
        self.layout.lock_thumbs(True)
        self.layout.hide_places()

    def handle_give(self, args):
        print 'handle_give'
        # create thumbnail in the gridlayout
        self.count += 1
        #print args
        index = int(args)
        #Create MapItem
        item_data = self.layout.imagemap.data[index]
        item_data["id"] = str(index)
        filename = item_data["filename"]
        item = None

        parts = filename.rsplit('-', 1)
        self.layout.imagemap.display_mapitem(filename, False, self.color)

        #Create MapThumbnail
        if item_data['valide'] == 'oui':
            item = self.layout.create_and_add_item(index)

        if item is not None :
            item.bind(mapitem = self.send_pos)

        self.index_list.append(index)
        if self.count == 5:
            tmp = []
            for idx in self.index_list:
                item = self.layout.imagemap.data[idx]
                tmp.append(item)
            self.layout.imagemap.data = tmp
            self.layout.imagemap.update_images(0)

            for mapitem in self.layout.imagemap.children[:] :
                mapitem.bind(flag_id = self.send_flag_change)

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

        for child in self.layout.volet.children[:]:
            if isinstance(child, MapThumbnail):
                self.layout.volet.remove_widget(child)
                self.layout.add_widget(child) 

        self.layout.map_background.source = self.layout.map_background.source.replace("-game", "")

        self.layout.place_thumbs()
        
        #send pos to server then
        for th in self.layout.items:
            th.locked = True
            self.send_pos(th,0)
            # self.send_color(th,th.color)

        self.layout.volet.x = -450

        self.layout.labelStatus.text = 'SOLUTION'

    def handle_clear(self, args):
        self.layout.clear()


    # SEND TO SERVER  

    def validate(self, instance):
        scenario = instance.text
        # print scenario + ' scenario was selected'
        if scenario == 'all': 
            index = -1
        else :
            index = self.layout.layers.index(scenario)
        #send index to server
        self.send('SCENARIO %d' % int(index)) 

    def send_pos(self, instance, value):
        value = instance.center
        print instance.color
        if value is None:
            value = (-1,-1)
            return
        x,y = value
        x -= self.layout.imagemap.pos[0]
        y -= self.layout.imagemap.pos[1]
        self.send('POS %d %d %d %d' % (instance.index, x, y, instance.rotation))
        self.send_color(instance, instance.color)

        # self.send_color(instance, instance.color)

        #print "CLIENT : send POS"

    def send_color(self, instance, value):
        # self.send('COLOR %d %d %d %d' % (instance.index, 255,255,255 ))
        print value
        self.send('COLOR %d %d %d %d' % (instance.index, int(value[0]*255),int(value[1]*255),int(value[2]*255) ))

    def send_flag_change(self, mapitem, flag_id):
        print 'send flagchange', flag_id
        if flag_id is None:
            flag_id = -1
        filename_index = self.filename2index(mapitem.filename) 
        self.send('FLAGCHANGE %d %d' % (filename_index,flag_id) )
        # print "CLIENT : flag change : "+str(mapitem.filename) +' '+ str(flag_id)

    def filename2index(self,filename):
        #trick to pass mapitem.filename (string) as a integer (protocol blocks strings..)
        index = 0
        for i in self.imagemap.data :
            if i['filename'] == filename :
                return int(i["id"])
                # return index
            index +=1

    def update_graphics_timer(self, dt):
        if not self.menu:
            return
        t = self.timeout - time()
        if t < 0:
            t = 0
        self.menu.time = t

        if not self.layout:
            return

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
        # print 'CLIENT : ', value
        if value == 'down':
            self.layout.clear()
            self.send('EXIT')
            


    def send_launchGame(self, instance, value):
        if value == 'down':
            self.menu.launchGameButton.opacity = 0
            self.menu.labelLaunchGame.text = ''
            self.send('WANT_TO_PLAY')

    def send_thheld(self, instance, th_index):
        pass

    def handle_thheld(self, instance, th_index):
        pass


         

    


scenario_class = MapClient
