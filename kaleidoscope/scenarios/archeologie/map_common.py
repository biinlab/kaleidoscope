# -*- coding: utf-8 -*-

from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatter import Scatter
from kivy.graphics import Color, Rectangle, Line, BorderImage
from kivy.properties import StringProperty, ListProperty, \
        NumericProperty, ObjectProperty, BooleanProperty, DictProperty
from kivy.resources import resource_add_path, resource_find
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.image import Image as CoreImage
from kivy.core.text import Label as CoreLabel
from kivy.core.audio import SoundLoader
#from kivy.cache import Cache
from json import load
from math import cos, sin, radians
from kivy.vector import Vector

from os.path import dirname, join, splitext

map_path = ('data/map-animaux-game.png', 'data/map-carpologue-game.png', 'data/map-poterie-game.png', 'data/map-animaux-game.png')
map_titre = ( 'ARCHEOZOOLOGUE', 'CARPOLOGUE', 'CERAMOLOGUE', 'INSTRUMENTOLOGUE')


class ScenarioSelectorButton(Button):
    source = StringProperty('cities.png')
    source_location = StringProperty('data/btn/')

def update_size(instance, value):
    instance.text_size = (value[0], None)

class ScenarioSelector(GridLayout):
    scenarii = ListProperty( [] )
    buttons = DictProperty( {} )

    def __init__(self, **kwargs):
        super(ScenarioSelector, self).__init__(**kwargs)
        index = 0
        for i in self.scenarii :
            text = self.scenarii[index]
            source_location = 'data/btn/'
            source = source_location + text + '.png'
            #print source, type (source)
            source = str(source)

            image = Image(source = source)
            size = image.texture_size
            self.buttons[index] = ScenarioSelectorButton(
                                          y_hint = None,
                                          height = size[1], 
                                          text = text, 
                                          source_location = source_location, 
                                          source = source
                                          )
            self.add_widget(self.buttons[index])
            index += 1

class MapEmptyPlace(Widget):
    pass

class MapAudio(FloatLayout):
    source = StringProperty('')
    sound = ObjectProperty(None)

    def play_audio(self):
        source = self.source
        if not source:
            return
        if not self.sound:
            self.sound = SoundLoader.load(source)
        self.sound.play()

    def stop(self):
        if self.sound:
            self.sound.stop()

class MapHandler(GridLayout):
    rotation = NumericProperty(0)
    last_rotation = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MapHandler, self).__init__(**kwargs)
        self.minus = Button(text = '-')
        self.add_widget(self.minus)
        self.minus.bind(on_press=self.minus_function)
        self.plus = Button(text = '+')
        self.add_widget(self.plus)
        self.plus.bind(on_press=self.plus_function)        
        
    def plus_function(self,instance):
        self.last_rotation = self.rotation
        self.rotation += 10
    
    def minus_function(self, instance):
        self.last_rotation = self.rotation
        self.rotation -= 10


class MapDescription(FloatLayout):
    item = ObjectProperty(None)
    index = NumericProperty(-1)
    layout = ObjectProperty(None)
    media = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MapDescription, self).__init__(**kwargs)


class MapThumbnail(Scatter):
    title = StringProperty('')
    filename = StringProperty('')
    origin = ListProperty([0, 0])
    imagemap = ObjectProperty(None)
    item = ObjectProperty(None)
    mapitem = StringProperty('')
    index = NumericProperty(-1)
    color = ListProperty([1, 1, 1])
    auto_color = BooleanProperty(False)
    controled = BooleanProperty(False)
    locked = BooleanProperty(False)
    right_pos = ObjectProperty((0,0))
    media_content = StringProperty('')
    media_picture = StringProperty('')
    current_country = StringProperty('')
    current_country2 = StringProperty('')
    media_picture_thumbnail = StringProperty('')

    # used by server, to know which client have this item
    client = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(MapThumbnail, self).__init__(**kwargs)
        self.media_content = self.item.get('content', '')
        self.title = self.item.get('title', '') 
        self.filename = filename = self.item.get('filename', '')
        parts = filename.rsplit('-', 1)
        filename = parts[1]
        media = mediath = splitext(filename)[0]
        media = mediath = media.replace("_active", "")
        media = mediath = media.replace("_ancrage", "")

        if media:
            media += '_casque.png'
            mediath += '_casque_thumbnail.png'
            media = join(dirname(__file__), 'data/sources', media )
            mediath = join(dirname(__file__), 'data/sources', mediath )
            mediawidget = None
            self.media_picture = media
            self.media_picture_thumbnail = mediath
    
    def pixel(self, x, y):
        # rot = self.rotation
        # self.rotation = 0

        x = int(x)
        y = self.height - int(y)

        # y = int(y) - self.height
        # x = int(x) - self.height

        # angle = radians(-self.rotation)

        # xp = x*cos(angle) - y*sin(angle)
        # yp = x*sin(angle) + y*cos(angle)

        # xp += self.width
        # yp += self.height

        # yp = self.height - yp

        # # xp = x*cos(-self.rotation) + y*sin(-self.rotation)
        # # yp = -x*sin(-self.rotation) + y*cos(-self.rotation)

        # print xp, yp
        # yp = self.height - yp

        coreimage = self.imageth._coreimage
        try:
            color = coreimage.read_pixel(x, y)
        except IndexError:
            return False
        # print self.filename, ' color : ', x,y,color

        if len(color) > 0:
            if color[-1] <= 0.003:
                return False

        return True

    def update_color(self, win):
        color = Color(71 / 360., 71 / 100., 87 / 100., mode='hsv')
        if self.auto_color == True :
            # x1,y1 = self.pos
            x1, y1 = self.center
            x2,y2 = self.right_pos
            x1 -= self.imagemap.x 
            y1 -= self.imagemap.y
            wind = Window.width + Window.height
            diff = (abs(x2-x1) + abs(y2-y1)) / wind
            # current_country = ''
            #print diff, x2 - x1, y2 - y1 
            # if self.current_country == '':
            #     print self.width/2 * self.scale
            #     # x1 += self.width/2 * self.scale
            #     # y1 += self.height/2 * self.scale
            #     country_filename = self.get_current_country(x1, y1)
            #     item = self.get_item_from_filename(country_filename)
            #     if item != None:            
            #         current_country = item["title"]
            # else:
            #     current_country = self.current_country

            if self.current_country2 == self.title and self.pos != self.origin:
                color.h = 106/360.
            # if diff < 0.05:
            #     color.h = 106 / 360.
            else:
                h = (71 - 71 * (min(2., 10*(diff - 0.01)) / 2.)) / 360.
                color.h = h
        else : 
            if win == True : 
                color.h = 106 / 360.
            else : 
                color.h = 0
        self.color = [color.rgba[0], color.rgba[1], color.rgba[2]]

    def launchAnimPanel(self, panel = None, op = True):
            # layout = self.imagemap.layout
            # width = layout.cluePanel.width
            Animation.stop_all(panel)
            if op:
                anim = Animation(x=-450, d=.2)
            else:
                anim = Animation(x=0, d=.2)
            anim.start(panel)
        
    def on_touch_down(self, touch):
        if not super(MapThumbnail, self).on_touch_down(touch):
            return
        if self.locked: return
        x,y = self.to_local(touch.x, touch.y)
        # x = touch.x - self.pos[0]
        # y = touch.y - self.pos[1]
        

        if not self.pixel(x,y):
            return
    

        layout = self.imagemap.layout
        # width = layout.cluePanel.width
        volet = layout.volet
        # clueArea = layout.clueArea
        # print self.media_picture_thumbnail
        if volet.x == 0:
            layout.anim_volet()
            # self.launchAnimPanel(volet, True)

        parent = self.parent
        if not isinstance(parent, MapClientLayout):
            parentMCL = parent.parent
            parent.remove_widget(self)
            parentMCL.add_widget(self)

        Animation.stop_all(self, 'pos')
        # self.rotation = 0
        self.controled = True
        self.scale = 1

        # self.imagemap.parent.img_description.source = self.media_picture
        # self.imagemap.parent.content_description.text = self.media_content
        # self.imagemap.layout.remove_widget(self.imagemap.layout.cluePanel)
        # self.imagemap.layout.add_widget(self.imagemap.layout.cluePanel)
        
        # self.imagemap.layout.remove_widget(self)
        # self.imagemap.layout.add_widget(self)
        return True

    def on_touch_up(self, touch):
        ''' Pose le MapThumbnail sur la carte. regarde si il est sur un mapItem.
        Si oui, enregistre le-dit mapItem, si non, le renvoi a sa place. Si on le 
        bouge sur le même mapItem, on ne fait rien'''
        ret = super(MapThumbnail, self).on_touch_up(touch)
        if not ret:
            return

        if self.locked: return
        if not self.controled: return

        layout = self.imagemap.layout
        volet = layout.volet
        if volet.x == -360:
            layout.anim_volet()
            # self.launchAnimPanel(volet, False)

        if not self._touches and ret: 
                #test if th is on a mapitem
                # x,y = self.pos

                # x += self.width / 2
                # y += self.height / 2
                # print x,y
                mapitem = self.imagemap.flag(self.index, self.center_x, self.center_y)
                if mapitem == '': 

                    parent = self.parent
                    if isinstance(parent, MapClientLayout):
                        parent.remove_widget(self)
                        parent.volet.add_widget(self)

                    self.rotation = 0
                    self.move_to_origin()
                    if self.auto_color:
                        color = Color(0 / 360., 71 / 100., 87 / 100., mode='hsv')
                        self.color = [color.rgba[0], color.rgba[1], color.rgba[2]]
                        print color.rgba
                    self.mapitem = ''
                    self.scale = 1            
                    # self.launchAnimPanel(self.imagemap.layout.cluePanel, False)
                else : 
                    # if self.mapitem!=mapitem :
                    
                    item = self.imagemap.get_child_by_filename(mapitem)
                    # posx, posy = item.right_pos
                    # posx -= self.width/2
                    # posy -= self.height/2
                    self.center = item.right_pos
                    self.rotation = item.angle
                    
                    self.mapitem = mapitem

                    self.scale = 1

                self.current_country = ''
                self.controled = False
        return ret
    
    def on_touch_move(self,touch):
        # print "Nom: ", self.title
        # print "locked: ", self.locked
        # print "controled: ", self.controled
        if self.locked: return
        if not self.controled: 
            # self._touches = []
            return

        ret = super(MapThumbnail, self).on_touch_move(touch)
        if not ret:
            return
        #mapitem = self.imagemap.flag(self.index, touch.x, touch.y)
        #print mapitem
        x,y = self.pos
        x += self.width / 2
        y += self.height / 2




        # if cluePanel.x == 1280:
        #     if clueArea.collide_point(*(x,y)):
        #         # cluePanel.x = 1280 - width
        #         self.launchAnimPanel(cluePanel, True)
        # else:
        #     if layout.clueBarPanel.collide_point(*(x,y)) or x < 1280-width:
        #         # cluePanel.x = 1280
        #         self.launchAnimPanel(cluePanel, False)

        x -= self.imagemap.x
        y -= self.imagemap.y
        ### Display current country above thumbnail
        country_filename = self.get_current_country(x, y)
        item = self.get_item_from_filename(country_filename)

        if item:
            self.current_country = item["title"]
            self.current_country2 = self.current_country
        else:
            self.current_country = ''
            self.current_country2 = ''

        # Auto correction
        if self.auto_color : 
            self.update_color(False)
        return ret
    
    def move_to_origin(self):
        Animation(pos=self.origin, t='out_elastic').start(self)

    def move_to_pos(self,pos):
        self.pos = pos
        # self.center = pos
        #Animation(pos=pos, t='out_elastic').start(self)
    
    def shake(self):
        if not self.controled:
            self.x -= 15
            anim = Animation(x = self.x + 15, t='out_elastic', d=.5).start(self)

    def get_item_from_filename(self, filename):
        for item in (data for data in self.imagemap.data):
            if item["filename"] == filename:
                return item
        return None    

    def get_current_country(self, x,y):
        country = ''
        for child in self.imagemap.children:
            # print child.filename
            if child.pixel(x,y):
                country = child.filename
        return country


class MapItem(Image):

    filename = StringProperty(None)
    active = BooleanProperty(False) #active by touch
    flagged = BooleanProperty(False) #active by flag
    flag_id = NumericProperty(-1) #MapThumbnail id 
    source_active = StringProperty(None)
    source_original = StringProperty(None)
    right_pos = ObjectProperty((0,0))
    angle = NumericProperty(0)

    def on_touch_down(self, touch):
        # if not self.collide_point(*touch.pos):
        #     return
        # return self.toggle_active(touch)
        return

    def on_touch_up(self, touch):
        # if not self.collide_point(*touch.pos):
        #     return
        # return self.toggle_active(touch)
        return

    def texture_update(self, *largs):
        if not self.source:
            self.texture = None
        else:
            filename = dirname(__file__)+"/data/sources/"+self.source
            #print filename
            image = CoreImage(filename, keep_data=True)
            texture = image.texture
            self.texture = texture
            self._coreimage = image

    def pixel(self, x, y):
        x = int(x)
        y = self.height - int(y)
        coreimage = self._coreimage
        try:
            color = coreimage.read_pixel(x, y)
        except IndexError:
            return False
        # print self.filename, ' color : ', x,y,color
        if len(color) > 0:
            if color[-1] <= 0.003:
                return False
        return True

    def toggle_active(self, touch):
        #flag wins over touch, if item is already flagged : quit
        if self.flagged : 
            return False
        x, y = touch.pos
        x -= self.x
        y -= self.y
        if self.pixel(x, y) is False : 
            return False
        self.active = not self.active
        self.source = self.source_active if self.active \
                else self.source_original
        return True

    def flag(self, flag_id, x, y):
        # print self.filename
        # #one flag at a time
        # print "self.flagged ", self.flagged
        # print "flag_id", flag_id 
        # print "self.flag_id", self.flag_id
        if self.flagged and flag_id != self.flag_id :
            # print "1" 
            return False
        if self.pixel(x, y) is False : 
            # print "2"
            # p = self.parent.unflag(flag_id)
            p = self.unflag(flag_id)
            
            #print p
            return False
        if flag_id == self.flag_id :
            # print "3"
            return True  
        if flag_id != self.flag_id : 
            # print "4"
            self.active = True
            self.flagged = True
            self.source = self.source_active
            self.flag_id = flag_id
        return True  

    def unflag(self, flag_id):
        if self.flagged == False or self.flag_id != flag_id : 
            return False
        self.active = False
        self.flagged = False
        self.flag_id = -1
        self.source = self.source_original
        return True

    def retrieve_pixels_location(self):
        if self.right_pos:
            return self.right_pos
        return (0,0)

        # OLD
        coreimage = self._coreimage
        w,h = coreimage.size
        x=0
        y=0
        alpha = 0
        #get bottom of pixel area 
        while alpha < 0.1 and y < h:
            try:
                color = coreimage.read_pixel(x, y)
            except IndexError:
                pass
            
            if len(color) > 0:
                if color[-1] >= 0.01:
                    low_pos = (x,y)
                    alpha = color[-1]
            x+=8
            if x >= w:
                x=0
                y+=8
        #get highest point
        x=0
        y+=8
        row_is_empty = False
        alpha = 0
        while row_is_empty == False and y < h:
            try:
                color = coreimage.read_pixel(x, y)
            except IndexError:
                pass
            if len(color) > 0:
                if color[-1] >= 0.01:
                    alpha = color[-1]
                    high_pos = (x,y)
            x+=8
            if x >= w:
                if alpha == 0:
                    row_is_empty == True
                x=0
                y+=8
        #get y center
        xc = min(low_pos[0],high_pos[0]) + abs(low_pos[0] - high_pos[0])/2.
        yc = low_pos[1] + (high_pos[1] - low_pos[1])/2.
        #get x (especially accurate in case of a river) 
        xc2 = 0
        alpha = 0
        while alpha == 0 and xc2 < w:
                try:
                    color = coreimage.read_pixel(xc2, yc)
                except IndexError:
                    pass
                if len(color) > 0:
                    if color[-1] >= 0.1:
                        alpha = color[-1]
                xc2 +=3    
        xc_min = xc2
        while alpha > 0.1 and xc2 < w:
                try:
                    color = coreimage.read_pixel(xc2, yc)
                except IndexError:
                    pass
                if len(color) > 0:
                    if color[-1] < 0.01:
                        alpha = color[-1]
                xc2 +=3
        xc_max = xc2
        return (xc_min + (xc_max-xc_min)/2., yc)    


class Map(FloatLayout):
    
    layout = ObjectProperty( None )
    json_filename = StringProperty('')
    data = ListProperty([])
    suffix = StringProperty('')
    layers = ListProperty([])#cities, montains, rivers or/and areas 
    active_ids = ListProperty([])
    server = BooleanProperty(False)
    color = ObjectProperty( (0,0,0,1))
    selected_items = ListProperty([])

    def __init__(self, **kwargs):
        super(Map, self).__init__(**kwargs)
        self.load()        

    def load(self):
        curdir = join(dirname(__file__), 'data')
        json_filename = join(curdir, 'scenario.json')
        resource_add_path(curdir)
        with open(json_filename, 'r') as fd:
            data = load(fd)
        self.data = data['items']

        tmp = []

        for item in self.data:
            if self.filename_match_layer(item['filename']):
                tmp.append(item)

        self.data = tmp


    def get_thumb(self, index):
        if self.thumb_index_match_layer(index): 
            item = self.data[index]
            self.selected_items.append(index)
            return MapThumbnail(item=item, imagemap=self, index=index)
        else : 
            return None

    def display_mapitem(self, filename, active, color):
            #print "display mapitem" + filename
            #if self.server :
            #    print filename, active, color
            parts = filename.rsplit('.', 1)
            if len(parts) != 2:
                return
            if self.server == False :
                if self.filename_match_layer(parts[0]) == False : 
                    return
            filename_suffix = '%s%s.%s' % (parts[0], self.suffix, parts[1])
            if active == True : 
                source = filename_suffix
            else : 
                source = filename
            #print parts[0], filename_suffix
            image = self.get_child_by_filename(filename)

            if not isinstance(image,MapItem):    
                for item in (data for data in self.data): #use a GENERATOR here
                    if filename == item["filename"]:
                        right_pos = item["rightpos"].split('x', 1)
                        right_pos =  (int(right_pos[0]), int(right_pos[1]))
                        angle = int(item["rotation"])
                image = MapItem(source=source, 
                    id = filename,
                    filename = filename,
                    right_pos = right_pos,
                    angle = angle,
                    pos_hint={'x': 0, 'y': 0},
                    source_original=filename,
                    source_active=filename_suffix) 
            image.bind(active=self.on_child_active)
            #print image.parent, self
            self.add_widget(image)        

    def hide_mapitem(self, filename):
        #print "hide mapitem" + filename
        child = self.get_child_by_filename(filename)
        if child is not None : 
            child.unbind(active=self.on_child_active)
            self.remove_widget(child) 

    def update_images(self, dt):
        #print "update_images"
        for child in self.children[:]:
            child.unbind(active=self.on_child_active)
            self.remove_widget(child)
        for item in (data for data in self.data): #use a GENERATOR here
            # if item['valide'] == oui:
            #     continue
            filename = item["filename"]

            #exclude unallowed layers (rivers etc etc)
            parts = filename.rsplit('-', 1)
            #print parts, f1(self.layers)            
            if len(parts) != 2 or parts[0] != self.f1(self.layers):
                continue
            #now display layer
            self.display_mapitem(filename, False, self.color)

    def on_child_active(self, instance, value):
        #get_id = self.get_filename_id
        self.active_ids = [x.source_original for x \
                in self.children if x.active]
        # print 'Image map "orig" changed to', self.active_ids

    def flag(self, flag_id, x,y):
        x -= self.x
        y -= self.y
        #print self.pos, x,y
        cf = ''
        # print "-----------------------------"
        for child in self.children :
            if child.flag(flag_id, x,y) : 
                #return child.filename
                cf = child.filename
        return cf           

    def unflag(self, flag_id):
        for child in self.children :
            if child.unflag(flag_id) : 
                # print "unflag"
                return child.filename
        return ''

    def retrieve_pixels_location(self, filename):
        for child in self.children :
            if child.filename == filename :
                pos = child.retrieve_pixels_location()
                return pos
        return None                      
         
    def get_child_by_filename(self, filename):
        for child in self.children : 
            if child.filename == filename :  
                return child

    def thumb_index_match_layer(self,index):
        if self.server : return True
        filename = self.data[index]['filename']
        return self.filename_match_layer(filename)

    def filename_match_layer(self,filename):
        # print self.f1(self.layers)
        parts = filename.rsplit('-', 1)

        if len(parts) != 2 or parts[0] not in self.f1(self.layers):
            return False
        else : 
            return True

    def pos2mapitem(self,x,y):
        for layer in self.children[:]:
            if not isinstance(layer, MapItem) : continue
            if layer.pixel(x,y) :
                return layer.filename
        return False

    def f1(self,list):
            string = ""
            for item in list:
                string = string + str(item)
            return string
    
class MapMenu(FloatLayout):
    time = NumericProperty(0)
    timeout = NumericProperty(1)
    color = ListProperty([1, 1, 1])
    titre = StringProperty('') 
    place = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MapMenu, self).__init__(**kwargs)
        self.titre = map_titre[self.place]

    def init_help_img(self):
        self.himg = Image(size_hint=(None,None),
            size=(1280,800),
            pos=(0,0),
            source='data/ecran-correction.png',
            opacity= 1
            )
        self.himg.on_touch_down = self.on_img_touch_down
        self.add_widget(self.himg)

    def display_help(self):
        self.toggle_help_image()

    def toggle_help_image(self):
        if not hasattr(self, 'himg'):
            self.init_help_img()
            return
        if self.himg.parent == self:
            self.remove_widget(self.himg)
            self.himg.opacity = 0
        else:
            self.init_help_img()

    def on_img_touch_down(self, touch):
        if self.himg.opacity == 1:
            self.toggle_help_image()
            return True
 

class MapClientLayout(FloatLayout):
    json_filename = StringProperty('')
    layers = ''#ListProperty( [""] )
    layer = NumericProperty(-2)
    titre = StringProperty('')
    description = StringProperty('')
    selector = ObjectProperty(None)
    imagemap = ObjectProperty(None)
    map_background = ObjectProperty(None)
    scattermap = ObjectProperty(None)
    inner_layout = ObjectProperty(None)
    logo = StringProperty('')
    color = ListProperty([1, 1, 1])
    time = NumericProperty(0)
    timelimit = NumericProperty(1)
    py = NumericProperty(None)
    mapsize = ObjectProperty( (980,484))
    mappos = ObjectProperty( (0,0) )
    mapdescription = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.items = []
        self.emptyplaces = []
        super(MapClientLayout, self).__init__(**kwargs)
        self.load()

    def load(self):
        curdir = join(dirname(__file__), 'data')
        json_filename = join(curdir, 'scenario.json')
        resource_add_path(curdir)
        with open(json_filename, 'r') as fd:
            data = load(fd)
        self.layers = data['layers']



    def create_selector(self): 
        scenarii = self.layers
        scenarii.append('all')
        pos = Window.center
        self.selector = ScenarioSelector(
                             scenarii = scenarii,
                             center = pos
                             )
        self.add_widget(self.selector)

    def remove_selector(self):
        self.remove_widget(self.selector)

    def hide_places(self):
        for child in self.children[:]:
            if isinstance(child, MapEmptyPlace):
                self.remove_widget(child)

    def create_map(self, place):
        size = self.mapsize
        #print size
        cx,cy = Window.center
        thumb_width = 0#130 #scale the map to the right 
        # pos = (cx - size[0]/2. + thumb_width,cy - size[1]/2.)
        pos = self.mappos
        #the map cannot have relative position ..

        self.titre = map_titre[place]

        self.map_background = Image(
                 source = map_path[place],
                 size_hint = (None, None), 
                 size= size,
                 pos = pos
                 )

        self.imagemap = imagemap = Map( 
                 layers = self.layers,
                 layout = self, 
                 size_hint = (None, None), 
                 size= size,
                 pos = pos
                 )

        self.add_widget(self.map_background, 15)
        self.add_widget(self.imagemap, 1)
        # self.remove_widget(self.volet)
        # self.add_widget(self.volet)

        return imagemap

    def create_emptyplace(self):
        return MapEmptyPlace()

    def create_and_add_item(self, index):
        thumb = self.imagemap.get_thumb(index)
        if thumb is None : return None
        # thumb.color = self.color
        # place = self.create_emptyplace()
        # place.size = thumb.size
        thumb.right_pos = self.imagemap.retrieve_pixels_location(thumb.item['filename'])
        # self.volet.add_widget(place)
        self.volet.add_widget(thumb)
        self.items.append(thumb)
        # self.emptyplaces.append(place)
        #self.do_layout_all()
        return thumb

    def do_layout_all(self):
        self.do_layout_items(self.emptyplaces)
        self.do_layout_items(self.items)

    def do_layout_items(self, items):
        # place correctly thumbs
        if not items:
            return
        #w, h = items[0].size
        margin = 130
        #count_in_rows = int(self.width * 0.6 / (h + margin))
        #rows_space = count_in_rows * h + (count_in_rows - 1 * margin)

        # starting point
        x = 0
        # oy = y = margin #(self.height - rows_space) / 2
        y = 500
        for item in items:
            item.pos = item.origin = x, y
            # y += item.size[1] + margin
            y -= item.size[1] - margin
            # if x > self.width - margin * 2:
            #     x = oy

            # if y > self.height - margin * 2:
            #     y = oy
            #     x += item.size[0] + margin
            
    
    def on_size(self, instance, value):
        self.do_layout_all()

    def on_pos(self, instance, value):
        self.do_layout_all()

    def hide_th(self, index):
        th = self.get_thumb_from_index(index)
        self.remove_widget(th)

    def display_th(self, index):
        th = self.get_thumb_from_index(index)
        self.add_widget(th)

    def create_map_handler(self):
        self.map_handler = MapHandler()
        self.add_widget(self.map_handler)
        return self.map_handler

    def get_thumb_from_index(self, index):
        for thumb in self.items : 
            if not isinstance(thumb, MapThumbnail):
                continue
            if thumb.index == index:
                return thumb
        return None

    def place_thumbs(self):
        for child in self.items:
            if isinstance(child, MapThumbnail):
                child.scale = 1
                pos = child.right_pos
                x,y = pos
                x += self.imagemap.x #- child.width/2.
                y += self.imagemap.y #- child.height/2
                # x -= child.width/2
                # y -= child.height/2

                #print x,y
                child.locked = True
                if pos is not None and child.current_country2 != child.title:
                    item = self.imagemap.get_child_by_filename(child.filename)
                    child.rotation = item.angle
                    child.center = (x,y)
                #convert to green 
                child.auto_color = False
                child.update_color(True)
                
        self.imagemap.update_images(1)

    def auto_color_thumbs(self):
        for child in self.items:
            if isinstance(child, MapThumbnail):
                child.auto_color = True
                child.update_color(True)

    def lock_thumbs(self, boole):
        for child in self.items:
            if isinstance(child, MapThumbnail):
                child.locked = boole
   
    def clear(self):
        self.imagemap.clear_widgets() 
        self.clear_widgets()
        self.items = []
        self.emptyplaces = []     
        #clear cache
        #Cache.remove(kv.texture)

    def anim_volet(self):
        if self.volet.x == -360:
            self.volet.x = 0
        else:
            self.volet.x = -360


from kivy.factory import Factory
Factory.register('Map', cls=Map)
Factory.register('MapHandler', cls=MapHandler)
