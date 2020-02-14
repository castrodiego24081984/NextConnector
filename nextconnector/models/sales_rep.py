from odoo import models, fields, api

#class res_users(osv.osv):
class SalesRep(models.Model): 
    _name = 'nextconnector.sales_rep'   
    nxt_id_erp = fields.Char('Codigo ERP')
    nxt_name = fields.Many2one("Nombre")
    nxt_user = fields.Many2one("res.users")
    
