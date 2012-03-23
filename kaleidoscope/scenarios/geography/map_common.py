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
from json import load

from os.path import dirname, join

def update_size(instance, value):
    instance.text_size = (value[0], None)

class ScenarioSelector(GridLayout):
    scenarii = ListProperty( [] )
    buttons = DictProperty( {} )

    def __init__(self, **kwargs):
        super(ScenarioSelector, self).__init__(**kwargs)
        index = 0
        for i in self.scenarii :
            self.buttons[index] = Button(text = self.scenarii[index])
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

class MapHandler(Scatter):
    last_rotation = NumericProperty(0)

class MapDescription(FloatLayout):
    item = ObjectProperty(None)
    index = NumericProperty(-1)
    layout = ObjectProperty(None)
    media = ObjectProperty(None)

class MapThumbnail(Scatter):
    #mapclientlayout = ObjectProperty( None )
    title = StringProperty('')
    origin = ListProperty([0, 0])
    imagemap = ObjectProperty(None)
    item = ObjectProperty(None)
    mapitem = StringProperty('')
    index = NumericProperty(-1)
    #length_flag = NumericProperty(0)
    color = ListProperty([92 / 255., 145 / 255., 179 / 255.])
    auto_color = BooleanProperty(False)
    #place_correctly = BooleanProperty(False)
    controled = BooleanProperty(False)
    locked = BooleanProperty(False)
    #real_center_y = ObjectProperty(None)
    right_pos = ObjectProperty((0,0))
    #dynamic_color = BooleanProperty(True)

    # used by server, to know which client have this item
    client = ObjectProperty(None)
    """
    def on_date(self, instance, value):
        if value is None:
            self.str_date = ''
            self.date_alpha = None
            return
        months = (u'Janvier', u'Février', u'Mars', u'Avril', u'Mai', u'Juin',
                u'Juillet', u'Août', u'Septembre', u'Octobre', u'Novembre',
                u'Décembre')
        self.date_alpha = self.imagemap.get_alpha_from_realdate(value)
        y, m = self.imagemap.get_dateinfo_from_alpha(self.date_alpha)
        self.str_date = u'%s %d' % (months[m-1], y)

        if self.auto_color:
            self.update_color()
    """
    def update_color(self, win):
        """
        color = Color(71 / 360., 71 / 100., 87 / 100., mode='hsv')
        if win == True :
            color.h = 106 / 360.        
        else:
            h = 0#(71 - 71 * (min(2., (1 - 1)) / 2.)) / 360.
            color.h = h
        self.color = color.rgba
        """

        #if self.x < 2*self.width:
        #    return
        color = Color(71 / 360., 71 / 100., 87 / 100., mode='hsv')
        if self.auto_color == True :
            x1,y1 = self.pos
            x2,y2 = self.right_pos
            x1 -= self.imagemap.x 
            y1 -= self.imagemap.y
            wind = Window.width + Window.height
            diff = (abs(x2-x1) + abs(y2-y1)) / wind
            #print diff, x2 - x1, y2 - y1 
        
            if diff < 0.05:
                color.h = 106 / 360.
                #self.place_correctly = True
            else:
                h = (71 - 71 * (min(2., 10*(diff - 0.01)) / 2.)) / 360.
                color.h = h
                #self.place_correctly = False
        else : 
            if win == True : 
                color.h = 106 / 360.
            else : 
                color.h = 0
        self.color = color.rgba
        
    """
    def on_center(self, instance, value):
        if self.client is None and self.controled:
            self.date = self.imagemap.get_date_from_pos(self.center_x, self.y + 60)
        have_date = self.date is not None
        if have_date != self.have_date:
            self.have_date = have_date
    """
    def on_touch_down(self, touch):
        if not super(MapThumbnail, self).on_touch_down(touch):
            return
        Animation.stop_all(self, 'pos')
        self.controled = True
        if touch.is_double_tap:
            self.show_popup()
        return True

    def on_touch_up(self, touch):
        ret = super(MapThumbnail, self).on_touch_up(touch)
        if not self._touches : #and touch.id in self._touches.keys():
                #test if th is on a mapitem
                x,y = self.pos
                x += self.width / 2.
                mapitem = self.imagemap.flag(self.index, x, y)
                if mapitem == '': 
                    self.move_to_origin()
                    self.mapitem = ''
                else : 
                    if self.mapitem!=mapitem :
                        self.mapitem = mapitem
                """
                if self.place_correctly:
                alpha_date = self.imagemap.get_alpha_from_realdate(self.item['date'])
                self.imagemap.set_pos_by_alpha(self, alpha_date, True)
                self.do_translation = False
                """
        return ret
    
    def on_touch_move(self,touch):
        if self.locked : return
        ret = super(MapThumbnail, self).on_touch_move(touch)
        if self.auto_color : 
            self.update_color(False)
        return ret
    
    def show_popup(self):
        if self.popup is not None:
            self.popup.dismiss()
        desc = MapDescription(item=self.item)

        count = 0
        content = self.item.get('content', '')
        if content:
            label = Label(text=content)
            label.bind(size=update_size)
            desc.layout.add_widget(label)
            count += 1
        media = self.item.get('media', '')
        if media:
            ext = media.rsplit('.', 1)[-1].lower()
            media = join(dirname(__file__), 'data', media)
            mediawidget = None
            if ext in ('mp3', 'wav', 'ogg'):
                mediawidget = MapAudio(source=media)
            elif ext in ('jpg', 'png', 'jpeg', 'gif', 'bmp', 'tga'):
                mediawidget = Image(source=media)
            else:
                pass
            if mediawidget:
                count += 1
                scatter = Scatter(do_translation=False, do_rotation=False,
                        min_scale=.4, max_scale=2)
                scatter.add_widget(mediawidget)
                scatter.bind(size=mediawidget.setter('size'))
                desc.layout.add_widget(mediawidget)
                desc.media = mediawidget

        desc.layout.cols = max(1, count)
        desc.layout.height = 500

        self.popup = popup = Popup(
            title=self.item['title'],
            content=desc,
            size_hint=(.7, .7))
        self.popup.bind(on_dismiss=self.stop_media)
        popup.open()

    def move_to_origin(self):
        Animation(pos=self.origin, t='out_elastic').start(self)

    def move_to_pos(self,pos):
        self.pos = pos
        #Animation(pos=pos, t='out_elastic').start(self)

    def stop_media(self, instance):
        content = instance.content
        if not content.media:
            return
        try:
            content.media.stop()
        except Exception, e:
            print e
    """
    def control_if_right(self): 
        filename = self.item['filename']
        print filename, self.mapitem
    """
    def shake(self):
        self.x -= 15
        anim = Animation(x = self.x + 15, t='out_elastic', d=.5).start(self)
    '''         
    def refresh_color(self):
        #calculate distance from right_pos
    '''

class MapItem(Image):

    filename = StringProperty(None)
    active = BooleanProperty(False) #active by touch
    flagged = BooleanProperty(False) #active by flag
    flag_id = NumericProperty(-1) #MapThumbnail id 
    source_active = StringProperty(None)
    source_original = StringProperty(None)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return self.toggle_active(touch)

    def on_touch_up(self, touch):
        if not self.collide_point(*touch.pos):
            return
        return self.toggle_active(touch)

    def texture_update(self, *largs):
        if not self.source:
            self.texture = None
        else:
            #resource_add_path(dirname(__file__))
            #filename = resource_find(self.source)
            #print dirname(__file__)
            filename = dirname(__file__)+"/data/sources/"+self.source
            #print filename
            image = CoreImage(filename, keep_data=True)
            texture = image.texture
            self.texture = texture
            self._coreimage = image

    def pixel(self, x, y):
        #x -= self.x
        #y -= self.y
        x = int(x)
        y = int(y)
        coreimage = self._coreimage
        try:
            color = coreimage.read_pixel(x, y)
        except IndexError:
            return False
        #print x,y,color
        if color[-1] <= 0.01:
            return False
        return True

    def toggle_active(self, touch):
        #flag wins over touch, if item is already flagged : quit
        if self.flagged : 
            return False
        x, y = touch.pos
        if self.pixel(x, y) is False : 
            return False
        self.active = not self.active
        self.source = self.source_active if self.active \
                else self.source_original
        return True

    def flag(self, flag_id, x, y):
        #one flag at a time
        if self.flagged and flag_id != self.flag_id : 
            return False
        if self.pixel(x, y) is False : 
            #if flag_id == self.flag_id :
            p = self.parent.unflag(flag_id)
            #print p
            return False
        if flag_id == self.flag_id :
            return True  
        if flag_id != self.flag_id : 
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
        #self.flagged = not self.flagged
        self.source = self.source_original
        return True

    def retrieve_pixels_location(self):
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
                if color[-1] >= 0.1:
                    alpha = color[-1]
                xc2 +=3    
        xc_min = xc2
        while alpha > 0.1 and xc2 < w:
                try:
                    color = coreimage.read_pixel(xc2, yc)
                except IndexError:
                    pass
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
    #sources = ListProperty([])
    layers = ListProperty([])#cities, montains, rivers or/and areas 
    active_ids = ListProperty([])
    #flags = ListProperty([]) #List of couples (MapTHumbnail id, mapitem filename)
    server = BooleanProperty(False)
    color = ObjectProperty( (0,0,0,1) )
    #childimage_size = ObjectProperty( (100,100) )

    def __init__(self, **kwargs):
        #self._update_images = Clock.create_trigger(self.update_images, -1)
        super(Map, self).__init__(**kwargs)
        #self.size_hint = (None,None)
        """
        self.bind(pos=self._trigger_build_canvas,
                size=self._trigger_build_canvas,
                size_hint=self._trigger_build_canvas,
                pos_hint=self._trigger_build_canvas)
        """
        #self.bind(suffix=self._update_images,
        #        sources=self._update_images)
        self.load()        
        #self._update_images()
        #self.update_images(0)

    def load(self):
        curdir = join(dirname(__file__), 'data')
        json_filename = join(curdir, 'scenario.json')
        resource_add_path(curdir)
        with open(json_filename, 'r') as fd:
            data = load(fd)
        self.data = data['items']

    def get_thumb(self, index):
        if self.thumb_index_match_layer(index):
            item = self.data[index]
            return MapThumbnail(item=item, imagemap=self, index=index)
        else : 
            return None

    def display_mapitem(self, filename, active, color):
            #print "display mapitem" + filename
            parts = filename.rsplit('.', 1)
            if len(parts) != 2:
                return
            filename_suffix = '%s%s.%s' % (parts[0], self.suffix, parts[1])
            if active == True : 
                source = filename_suffix
            else : 
                source = filename
            image = self.get_child_by_filename(filename)
            if not isinstance(image,MapItem) :    
                #print source
                image = MapItem(source=source, 
                    id = filename,
                    filename = filename,
                    pos_hint={'x': 0, 'y': 0},
                    source_original=filename,
                    source_active=filename_suffix) 
            image.bind(active=self.on_child_active)
            #if not self.server :
            #    image.bind(flag_id = self.parent.flag_change_occured)
            self.add_widget(image)        

    def hide_mapitem(self, filename):
        #print "hide mapitem" + filename
        child = self.get_child_by_filename(filename)
        child.unbind(active=self.on_child_active)
        #child.unbind(flag_id = self.mapclient.send_mapitem)
        self.remove_widget(child) 

    def update_images(self, dt):
        #print "update_images"
        for child in self.children[:]:
            child.unbind(active=self.on_child_active)
            self.remove_widget(child)

        for item in self.data:
            filename = item["filename"]
            #exclude unallowed layers (rivers etc etc)
            parts = filename.rsplit('-', 1)
            #print parts, f1(self.layers)            
            if len(parts) != 2 or parts[0] != self.f1(self.layers):
                continue
            #now display layer
            self.display_mapitem(filename, False, self.color)

        #coreimage = self.children[-1]._coreimage
        #self.childimage_size = coreimage.size
    """
    def display_mapitem_from_th(self, th, active, color):
        self.display_mapitem(self, th["filename"], active, color)

    def remove_mapitem(self, filename):
        for child in self.children[:]:
            if child.id != filename :
                continue
            child.unbind(active=self.on_child_active)
            self.remove_widget(child)
            return

    def remove_mapitem_from_th(self, th):
        self.remove_mapitem( th["filename"] )         
    
    def get_filename_id(self, filename):
        return filename.rsplit(sep, 1)[-1].rsplit('.', 1)[0]
    """
    def on_child_active(self, instance, value):
        #get_id = self.get_filename_id
        self.active_ids = [x.source_original for x \
                in self.children if x.active]
        print 'Image map "orig" changed to', self.active_ids

    def flag(self, flag_id, x,y):
        """
        #get position compare to parent MapClientLayout
        w,h = self.layout.size
        delta_x = (w - self.width) / 2.
        delta_y = (h - self.height) / 2.
        if delta_x > 0:
            x -= delta_x
        if delta_y > 0:
            y -= delta_y
        print self.size,w,h,delta_x,delta_y,x,y
        """
        x -= self.x
        y -= self.y
        #print self.pos, x,y
        cf = ''
        for child in self.children :
            if child.flag(flag_id, x,y) : 
                return child.filename
        return ''           

    def unflag(self, flag_id):
        for child in self.children :
            if child.unflag(flag_id) : 
                return child.filename
        return ''

    def retrieve_pixels_location(self, filename):
        for child in self.children :
            if child.filename == filename :
                pos = child.retrieve_pixels_location()
                return pos
        return None                      
         
    """
    def unflag_all(self):
        for i in self.flags :    
            self.get_child_by_filename( i[1] ).unflag( i[0] )
    """
    def get_child_by_filename(self, filename):
        for child in self.children : 
            if child.filename == filename :  
                return child

    def thumb_index_match_layer(self,index):
        if self.server : return True
        filename = self.data[index]['filename']
        return self.filename_match_layer(filename)

    def filename_match_layer(self,filename):
        parts = filename.rsplit('-', 1)
        if len(parts) != 2 or parts[0] != self.f1(self.layers):
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
    

class MapClientLayout(FloatLayout):
    json_filename = StringProperty('')
    layers = ListProperty( ["mountains","rivers","cities","regions"] )
    layer = NumericProperty(-2)
    selector = ObjectProperty(None)
    imagemap = ObjectProperty(None)
    scattermap = ObjectProperty(None)
    inner_layout = ObjectProperty(None)
    logo = StringProperty('')
    color = ListProperty([1, 1, 1])
    time = NumericProperty(0)
    timelimit = NumericProperty(1)
    py = NumericProperty(None)
    mapsize = ObjectProperty( (702,642) )
    mappos = ObjectProperty( (200,20) )

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
    """
    def active_layers(self, layers):
        self.imagemap.layers = layers
        self.imagemap.update_images(0)        
    """
    def create_selector(self): 
        scenarii = self.layers
        scenarii.append('all')
        self.selector = ScenarioSelector(
                             cols =3,
                             scenarii = scenarii
                             )
        self.add_widget(self.selector)

    def remove_selector(self):
        self.remove_widget(self.selector)

    def hide_places(self):
        for child in self.children[:]:
            if isinstance(child, MapEmptyPlace):
                self.remove_widget(child)
        #Animation(size_hint_y=1., pos_hint={'y': 0},
        #        t='out_quad', d=.5).start(self.inner_layout)

    def create_map(self):
        size = self.mapsize
        cx,cy = Window.center
        thumb_width = 0#130 #scale the map to the right 
        pos = (cx - size[0]/2. + thumb_width,cy - size[1]/2.)
        #the map cannot have relative position .. 
        self.imagemap = imagemap = Map( 
                 layers = self.layers,
                 layout = self, 
                 size_hint = (None, None), 
                 size= size,
                 pos = pos#pos=self.mappos
                 )
        #self.scattermap = Scatter( size=imagemap.size)
        #self.scattermap.add_widget(imagemap)      
        self.map_background = Image(
                 source = 'data/map.png',
                 size_hint = (None, None), 
                 size= size,
                 pos = pos#pos=self.mappos
                 )
        self.add_widget(self.map_background)
        self.add_widget(self.imagemap)
        return imagemap
    """
    def flag_change_occured(self, mapitem, flag_id_val):
        print mapitem.filename, flag_id_val        
    """
    def create_emptyplace(self):
        return MapEmptyPlace()

    def create_and_add_item(self, index):
        thumb = self.imagemap.get_thumb(index)
        if thumb is None : return None
        thumb.color = self.color
        place = self.create_emptyplace()
        place.size = thumb.size
        thumb.right_pos = self.imagemap.retrieve_pixels_location(thumb.item['filename'])
        self.add_widget(place)
        self.add_widget(thumb)
        self.items.append(thumb)
        self.emptyplaces.append(place)
        self.do_layout_all()
        return thumb

    def do_layout_all(self):
        self.do_layout_items(self.emptyplaces)
        self.do_layout_items(self.items)
    """
    def do_layout_items(self, items):
        # place correctly thumbs
        if not items:
            return
        w, h = items[0].size
        margin = 20
        count_in_rows = int(self.width / (w + margin))
        rows_space = count_in_rows * w + (count_in_rows - 1 * margin)

        # starting point
        ox = x = (self.width - rows_space) / 2
        y = 20

        for item in items:
            item.pos = item.origin = x, y
            x += w + margin
            if x > self.width - margin * 2:
                x = ox
                y += h + margin
    """
    def do_layout_items(self, items):
        # place correctly thumbs
        if not items:
            return
        w, h = items[0].size
        margin = 10
        count_in_rows = int(self.height / (h + margin))
        rows_space = count_in_rows * h + (count_in_rows - 1 * margin)

        # starting point
        x = 20
        oy = y = margin #(self.height - rows_space) / 2

        for item in items:
            item.pos = item.origin = x, y
            y += h + margin
            
            if y > self.height - margin * 2:
                y = oy
                x += w + margin
            
    
    def on_size(self, instance, value):
        self.do_layout_all()

    def on_pos(self, instance, value):
        self.do_layout_all()
    """
    def on_inner_layout_y(self, instance, value):
        if self.py is None:
            self.py = value
            return
        diff = value - self.py
        self.py = value
        for thumb in self.children:
            if not isinstance(thumb, MapThumbnail):
                continue
            if thumb.have_date:
                thumb.center_y += diff / 2
    
    def on_inner_layout(self, instance, value):
        value.bind(y=self.on_inner_layout_y)
    """
    def hide_th(self, index):
        th = self.get_thumb_from_index(index)
        self.remove_widget(th)

    def display_th(self, index):
        th = self.get_thumb_from_index(index)
        self.add_widget(th)

    def create_map_handler(self):
        self.map_handler = MapHandler(
                pos_hint = {'x':0.44,'y':0.03}
                )
        self.add_widget(self.map_handler)
        return self.map_handler

    def get_thumb_from_index(self, index):
        for thumb in self.items : #children[:]:
            if not isinstance(thumb, MapThumbnail):
                continue
            if thumb.index == index:
                return thumb
        return None

    def place_thumbs(self):
        for child in self.items:
            if isinstance(child, MapThumbnail):
                pos = child.right_pos
                x,y = pos
                x += self.imagemap.x - child.width/2.
                y += self.imagemap.y
                if pos is not None:
                    child.move_to_pos( (x,y) )
                #convert to green 
                child.auto_color = False
                child.update_color(True)
        self.imagemap.update_images(1)

    def auto_color_thumbs(self):
        for child in self.items:
            if isinstance(child, MapThumbnail):
                child.auto_color = True

    def lock_thumbs(self, boole):
        for child in self.items:
            if isinstance(child, MapThumbnail):
                child.locked = boole
                


from kivy.factory import Factory
Factory.register('Map', cls=Map)
Factory.register('MapHandler', cls=MapHandler)
