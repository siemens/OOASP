# Copyright (c) 2022 Siemens AG Oesterreich
# SPDX-License-Identifier: MIT

import ipywidgets as widgets
from ipywidgets import Button, VBox, Label, Layout,GridspecLayout, HTML
from IPython.display import display, Image

def basic_layout():
    return VBox(layout=Layout(height='auto', width='auto'))

def wraped_label(text):
    return HTML(value="<style>p{word-wrap: break-word ;color:red}</style> <p>" + text+"</p>")
    

class OOASPUI:
    """
    UI prototype using pywidgets
    """

    def __init__(self, iconf):
        """
        Creates the UI
        """
        self.iconf = iconf
        self.config_image = widgets.Image(format='png')
        self.found_config = widgets.Image(format='png')

        self.history = VBox(layout=Layout(height='300ox', width='auto',overflow_y='auto'))
        self.extend = basic_layout()
        self.edit = basic_layout()
        self.browse = basic_layout()
        self.check = basic_layout()
        self.opts = None
        self.update()
        self.create_structure()
        display(HTML("<style>div.output_scroll { height: 44em; }</style>"),self.grid)

    def create_structure(self):
        """
        Crates the basic grid structure
        """
        grid = GridspecLayout(3, 6)
        grid[0, 4:] = self.history
        grid[0, :4] = self.config_image
        grid[1, :2] = self.check
        grid[1, 2:4] = self.edit
        grid[1, 4:] = self.extend
        grid[2, 0] = self.browse
        grid[2, 1:] = self.found_config
        self.grid = grid


    def update(self):
        """
        Updates the UI based on the current interactive state
        """
        self.set_config_image()
        self.set_history()
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


    def call_and_update(self, f, *args):
        """
        Calls a function and updates the UI
        """
        def fun(bt):
            f(bt,*args)
            self.update()
        return fun

    def add_leaf(self,change):
        """
        Adds a leaf
        """
        if change.type != "change" or change.name != "value":
            return
        self.iconf.new_leaf(change.owner.value)

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

    def button_wrapper(self, fun_name):
        """
        Used for button callbacks that call the iconf
        """
        def f(bt):
            fun = getattr(self.iconf, fun_name)
            fun()
        return f

    def set_config_image(self):
        """
        Sets the configuration image
        """
        self.iconf.config.save_png()
        image = Image(f"out/{self.iconf.config.name}.png")
        self.config_image.value = image.data

    def set_found_config(self):
        """
        Sets the found configuration image
        """
        if self.iconf.found_config is None:
            image = Image(f"out/empty.png")
            self.found_config.value = image.data
        else:
            self.iconf.found_config.save_png("out/found/")
            image = Image(f"out/found/{self.iconf.found_config.name}.png")
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
        extend_domain = Button(description='Add new object',button_style='info')
        extend_domain.on_click(self.call_and_update(self.button_wrapper('extend_domain')))
        dropdown = widgets.Dropdown(
            options=['']+self.iconf.kb.leafs,
            value='',
            description='Add new leaf',
            disabled=False
        )
        dropdown.observe(self.call_and_update(self.add_leaf))
        self.extend.children= tuple([self.title('Extend'), extend_domain,dropdown])


    def set_edit(self):
        """
        Sets the edit section with the dropdowns
        """
        if self.iconf.browsing:
            self.edit.children= tuple([self.title('Edit')] + [Label(value="No options while browsing")])
            return
        if not self.iconf.brave_config:
            self.iconf._get_options()
        opts = self.iconf._brave_config_as_options()
        if opts is None:
            self.edit.children= tuple([self.title('Edit')] + [Label(value="No options for conflicting configuration")])

            return
        self.opts = {o['str']:o for x in opts.values() for o in x}
        dropdowns = []
        for k,v in opts.items():
            dropdown = widgets.Dropdown(
                options=['']+[o['str'] for o in v],
                value='',
                description=f'Object {k}',
                disabled=False,
                style={'description_width': '70px','button_color':'red'}
            )
            dropdown.observe(self.call_and_update(self.do_edit))
            dropdowns.append(dropdown)
            

        self.edit.children= tuple([self.title('Edit')] + dropdowns)


    def set_browse(self):
        """
        Sets the browse section buttons
        """
        incremental = Button(description='Find incrementally',button_style='primary')
        incremental.on_click(self.call_and_update(self.button_wrapper('extend_incrementally')))
        select_found = Button(description='Select',button_style='success')
        select_found.on_click(self.call_and_update(self.button_wrapper('select_found_configuration')))
        next_solution = Button(description='Next solution',button_style='info')
        next_solution.on_click(self.call_and_update(self.button_wrapper('next_solution')))
        end_browsing = Button(description='End browsing',syle='danger')
        end_browsing.on_click(self.call_and_update(self.button_wrapper('end_browsing')))
        
        self.browse.children= tuple([self.title('Browse'), incremental,next_solution,select_found,end_browsing])


    def set_check(self):
        """
        Sets the check section
        """
        check = Button(description='Check',button_style='success')
        check.on_click(self.call_and_update(self.button_wrapper('check')))
        cvs = self.iconf.config.constraint_violations
        cvs_labels =[]
        for c in cvs:
            cvs_labels.append(wraped_label(self.iconf.config.format_cv(c)))
        if len(cvs) == 0:
            cvs_labels.append(Label(value="All checks passed!"))
        self.check.children= tuple([self.title('Check'), check] + cvs_labels)


