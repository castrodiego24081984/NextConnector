# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class popup_message(models.TransientModel):
    _name="nextconnector.popup.message"
    _description = "Message wizard to display warnings, alert ,success messages"      
    
    def get_default(self):
        if self.env.context.get("message",False):
            return self.env.context.get("message")
        return False 

    name=fields.Text(string="Message",readonly=True,default=get_default)
    
    def success(self, message):
        view = self.env.ref('nextconnector.nextconnector_popup_message')
        context = {}

        context['message'] = message
        return {
                'name': 'Exito!',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'nextconnector.popup.message',
                'views': [(view.id,'form')],
                'view:id': view.id,
                'target':'new',
                'context':context 
            }

    def error(self, message):
        view = self.env.ref('nextconnector.nextconnector_popup_message')
        context = {}

        context['message'] = message
        return {
                'name': 'Error! Por favor verificar',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'nextconnector.popup.message',
                'views': [(view.id,'form')],
                'view:id': view.id,
                'target':'new',
                'context':context 
            }
    