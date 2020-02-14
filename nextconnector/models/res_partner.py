# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
import requests
import json  
from . import popup_message
import logging
from . import util
_rq = util.util.request
_popup = popup_message.popup_message
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    over_credit = fields.Boolean('Permitir exceder limite de credito?')
    
    nxt_sync = fields.Selection(string="Estado de sincronización",selection=[("S","Sincronizado"),("N","No sincronizado"),("E","Error de sincronizacion")],default="N")

    def synchronize_customer(self):
        if self.nxt_sync == "S":
            return True
        
        pay_term = self.env["account.payment.term"].search([('id','=',self.property_payment_term_id.id)])

        _record = {
            "id": self.vat,
            "record_type": "customer",
            "fields": [
                {"name": "CardType","value": "2"},
                {"name": "CardCode","value": self.vat if self.vat else "" },
                {"name": "CardName","value": self.name if self.name else ""  },
                {"name": "LicTradNum","value": self.vat if self.vat else ""  },
                {"name": "E_Mail","value": self.email if self.email else "" },
                {"name": "Phone1","value": self.phone if self.phone else ""  },
                {"name": "Cellular","value": self.mobile if self.mobile else ""  },
                {"name": "Currency","value": "$"},
                {"name": "GroupNum","value": pay_term.nxt_id_erp if pay_term.nxt_id_erp else ""  }
            ]
        }

        response = _rq(self,"/nextconnector/api/records/customer",_record,"post")

        if response["status_code"] != "200":
            self.message_post(body="Error de comunicación al sincronizar registro")
        else:
            json_resp = response["response_json"]
            if json_resp["code"] != "0":
                self.write({"nxt_sync":'E'})
                self.message_post(body=json_resp["message"])
            else:   
                self.write({"nxt_sync":'S'})
                self.message_post(body="Registro sincronizado con SAP.")

    
    
