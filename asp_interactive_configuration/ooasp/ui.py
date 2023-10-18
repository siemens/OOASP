# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

import ipywidgets as widgets
from ipywidgets import Button, VBox, HBox, Label, Layout,GridspecLayout, HTML, Output
from IPython.display import display, Image
from PIL import Image as PImage

loader_img = Image('./img/loader.gif')
empty_img = Image("img/empty.png")
nosol_img = Image("img/nosol.png")

def basic_vbox():
    return VBox(layout=Layout(height='auto', width='auto'))

def wraped_label(text):
    return HTML(value="<style>cv{word-wrap: break-word ;color:red}</style> <p class='cv'>" + text+"</p>")

def resize(baseheight,f_name):
    baseheight = 300
    im = PImage.open(f_name)
    w, h = im.size
    if h>baseheight:
        hpercent = (baseheight/h)
        w = int((w*hpercent))
        resized = im.resize((w,h))
        resized.save(f_name)
    return w

def config_layout():
    return Layout(overflow_y='scroll',
            width='100%',
            height='300px',
            flex_flow='row',
            display='block')
         
PSTYLE = "<style>p{word-wrap: break-word; margin-right: 10px;}</style>"
class OOASPUI:
    """
    UI prototype using pywidgets
    """

    def __init__(self, iconf):
        """
        Creates the UI
        """
        self.iconf = iconf
        self.config_image = widgets.Image(format='png', width='1000px', layout=Layout(overflow = 'visible',min_width='1000px',height='300px'), unconfined=True)
        self.found_config = widgets.Image(format='png', width='1000px', layout=Layout(overflow = 'visible',min_width='1000px',height='300px'), unconfined=True)
        self.extend = basic_vbox()
        self.edit = basic_vbox()
        self.edit_object = ''
        self.browse = basic_vbox()
        self.check = basic_vbox()
        self.opts = None
        self.invalid = False
        self.update()
        self.create_structure()
        
        display(HTML("<style>div.output_scroll { height: 44em; } .container { width:100% !important; }</style>"),self.grid)

    def create_structure(self):
        """
        Crates the basic grid structure
        """
        grid = GridspecLayout(3, 6)
        grid[0, :6] = HBox(children=[self.config_image], layout=config_layout())
        grid[1, :2] = self.check
        grid[1, 2:4] = self.edit
        grid[1, 4:] = self.extend
        grid[2, 0] = self.browse
        grid[2, 1:] = HBox(children=[self.found_config], layout=config_layout())
        self.grid = grid


    def update(self):
        """
        Updates the UI based on the current interactive state
        """
        self.set_config_image()
        # self.set_history()
        self.set_edit()
        self.set_extend()
        self.set_browse()
        self.set_found_config()
        self.set_check()

    def title(self,text):
        """
        Gets a string as a title widget
        """
        return HTML(value=f'<h2>{text}</h2>')


    def call_and_update(self, f, **kwargs):
        """
        Calls a function and updates the UI
        """
        def fun(bt):
            self.found_config.value = loader_img.data
            f(bt,**kwargs)
            self.found_config.value = empty_img.data
            self.update()
        return fun

    def select_edit_object(self, change):
        if change.type != "change" or change.name != "value":
            return
        self.edit_object = change.owner.value

    def add_new_object(self,change,**kwargs):
        """
        Adds a leaf
        """
        if change.type != "change" or change.name != "value":
            return
        self.iconf.new_object(change.owner.value,**kwargs)

    def do_edit(self,change):
        """
        Used for edit dropdown menues
        """
        if change.type != "change" or change.name != "value":
            return
        opt_str = change.owner.value
        opt = self.opts[opt_str]
        call = getattr(self.iconf, opt['fun_name'])
        call(*opt['args'])

    
    def button_wrapper(self, fun_name, **kwargs):
        """
        Used for button callbacks that call the iconf
        """
        def f(bt):
            fun = getattr(self.iconf, fun_name)
            fun(**kwargs)
        return f

    def set_config_image(self):
        """
        Sets the configuration image
        """
        self.iconf.config.save_png()
        f_name = f"out/{self.iconf.config.name}.png"
        w = resize(300,f_name)
        self.config_image.layout.min_width=str(w/1)+"pt"
        self.config_image.layout.width=str(min([w,1000]))+"pt"
        image = Image(f_name,unconfined=True)
        self.config_image.value = image.data

    def set_found_config(self):
        """
        Sets the found configuration image
        """
        if self.iconf.found_config is None:
            self.found_config.layout.min_width="400pt"
            self.found_config.layout.width="400pt"
            self.found_config.value = empty_img.data
        elif self.iconf.found_config is False:
            self.found_config.layout.min_width="400pt"
            self.found_config.layout.width="400pt"
            self.found_config.value = nosol_img.data
        else:
            self.iconf.found_config.save_png("out/found/")
            f_name = f"out/found/{self.iconf.found_config.name}.png"
            w = resize(300,f_name)
            self.found_config.layout.min_width=str(w/1)+"pt"
            self.found_config.layout.width=str(min([w,1000]))+"pt"
            image = Image(f_name)
            self.found_config.value = image.data

    def set_history(self):
        """
        Sets the history list
        """
        history = []
        for i, s in enumerate(self.iconf.states):
            history.append(Label(value=f"{i}. {s.action}"))
        self.history.children= tuple([self.title('History')]+history)


    def set_browse(self):
        """
        Sets the browsing section
        """
        self.browse.children= tuple([self.title('Browse')])


    def set_extend(self):
        """
        Sets the extend domain section
        """
        domain_lbl = HTML(value=PSTYLE + "<p> <b>Domain size: "+str(self.iconf.domain_size)+"</b>  </p>") 
        config_lbl = HTML(value=PSTYLE + "<p> <b>Configuration size: "+str(self.iconf.config.size)+"</b>  </p>") 
        
        extend_domain = Button(description='Extend',button_style='info')
        extend_domain.on_click(self.call_and_update(self.button_wrapper('extend_domain')))
        dropdown = widgets.Dropdown(
            options=['']+self.iconf.kb.classes,
            value='',
            description='Add new object        ',
            disabled=False,
            style={'description_width': '170px'}
        )
        dropdown.observe(self.call_and_update(self.add_new_object))
        dropdown_propagate = widgets.Dropdown(
            options=['']+self.iconf.kb.classes,
            value='',
            description='Add new object (propagate)',
            disabled=False,
            style={'description_width': '170px'}
        )
        dropdown_propagate.observe(self.call_and_update(self.add_new_object,propagate=True))
        self.extend.children= tuple([self.title('Extend'),HBox(children=[domain_lbl,extend_domain]),config_lbl,dropdown,dropdown_propagate])

    def str_opt(self, option):
        """
        Takes an option and formats it into a human-readable string representation.
        """
        r_or_s, edit_opt = option['fun_name'].split('_',1)
        if option['fun_name']== 'remove_object_class':
            s = 'Remove'
        elif option['fun_name']== 'select_object_class':
            s = 'Select: ' + option['args'][1]
        elif option['fun_name']== 'remove_value':
            s = 'Remove: ' + option['args'][1]
        elif option['fun_name']== 'select_value':
            s = 'Select: ' +  option['args'][1] + ' as ' + str(option['args'][2])
        elif option['fun_name']== 'remove_association':
            s = f"Remove: {option['args'][0]} from {str(option['args'][1])} to  {str(option['args'][2])}" 
        elif option['fun_name']== 'select_association':
            s = f"Select: {option['args'][0]} from {str(option['args'][1])} to  {str(option['args'][2])}" 
        else:
            raise RuntimeError("Option format not expected " + str(option))
        return edit_opt, (s,option['str'])

    def set_edit(self):
        """
        Sets the edit section with the dropdowns
        """
        if self.iconf.browsing:
            self.edit.children= tuple([self.title('Edit')] + [Label(value="No options while browsing")])
            return
        if not self.iconf.brave_config:
            self.iconf._get_options()
        self.invalid = self.iconf.brave_config is None
        opts = self.iconf._brave_config_as_options()
        dropdown_object = widgets.Dropdown(
                options=['']+[o for o in opts.keys()],
                value=self.edit_object,
                description=f'Object to edit',
                disabled=False,
                style={'description_width': '100px','font_weight':'bold'}
            )
        dropdown_object.observe(self.call_and_update(self.select_edit_object))
        o = self.edit_object
        edit_dropdowns = []
        names = {'object_class':'Class','value':'Attribuite-Value','association':'Association'}
        if o!='':
            obj_opts =  opts[o]
            self.opts = {o['str']:o for o in obj_opts}
            edit_options = {'object_class':[],'value':[],'association':[]}
            for option in obj_opts:
                edit_opt, entry = self.str_opt(option)
                edit_options[edit_opt].append(entry)

            for edit, edit_o in edit_options.items():
                if len(edit_o)==0:
                    continue
                d = widgets.Dropdown(
                    options=[('','')]+edit_o,
                    value='',
                    description=names[edit],
                    disabled=False,
                    style={'description_width': '200px','font_weight':'bold'}
                )
                d.observe(self.call_and_update(self.do_edit))

                edit_dropdowns.append(d)


        self.edit.children= tuple([self.title('Edit'),dropdown_object]+edit_dropdowns)


    def set_browse(self):
        """
        Sets the browse section buttons
        """
        colora = 'danger' if self.invalid else 'primary'
        colorb = 'danger' if self.invalid else 'info'
        b_layout = Layout(height='auto', width='auto')
        incremental = Button(description='Find incrementally',button_style=colora, disabled=self.invalid, layout=b_layout)
        incremental.on_click(self.call_and_update(self.button_wrapper('extend_incrementally')))
        incrementalos = Button(description='Find incrementally (overshoot)',button_style=colora, disabled=self.invalid, layout=b_layout)
        incrementalos.on_click(self.call_and_update(self.button_wrapper('extend_incrementally',overshoot=True)))
        select_found = Button(description='Select',button_style='success',layout=b_layout)
        select_found.on_click(self.call_and_update(self.button_wrapper('select_found_configuration')))
        next_solution = Button(description='Next solution',button_style=colorb, disabled=self.invalid, layout=b_layout)
        next_solution.on_click(self.call_and_update(self.button_wrapper('next_solution')))
        end_browsing = Button(description='End browsing',syle='danger',layout=b_layout)
        end_browsing.on_click(self.call_and_update(self.button_wrapper('end_browsing')))

        self.browse.children= tuple([self.title('Browse'), incremental,incrementalos,next_solution,select_found,end_browsing])


    def set_check(self):
        """
        Sets the check section
        """
        color = 'danger' if self.invalid else 'info'
        check = Button(description='Check',button_style='success')
        check.on_click(self.call_and_update(self.button_wrapper('check')))
        clear = Button(description='Clear checks',button_style='warning')
        clear.on_click(self.call_and_update(self.button_wrapper('remove_cvs')))
        get_inferences = Button(description='Add inferences',button_style=color, disabled=self.invalid)
        get_inferences.on_click(self.call_and_update(self.button_wrapper('add_inferences')))
        create_required = Button(description='Create required',button_style=color, disabled=self.invalid)
        create_required.on_click(self.call_and_update(self.button_wrapper('create_all_required_objects')))
        elements = [check, clear, get_inferences,create_required]
        if self.invalid:
            invalid = HTML(value='<p style="color:red"><b>Invalid configuration</b></p>')
            elements = [invalid] + elements
        self.check.children= tuple([self.title('Check'),]+elements)


