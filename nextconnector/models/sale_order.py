# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning
import requests
import json  
from odoo.exceptions import UserError
from . import popup_message
import logging
from . import util

_rq = util.util.request
_popup = popup_message.popup_message
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    nxt_sync = fields.Selection(string="Estado de sincronización",selection=[("S","Sincronizado"),("N","No soncronizado"),("E","Error de sincronizacion")],default="N")

    def synchronize_record(self):

        #for rec in self:
        if self.nxt_sync == "S":
            return True

        _record = { 
            "id": self.name ,
            "record_type": "salesorder",
            "fields": [
                {"name": "CardCode","value": self.partner_id.vat},
                {"name": "CardName","value": self.partner_id.name},
                {"name": "Comments","value": self.name}
            ],
            "sublists": []
        }
        
        lines = []

        for line in self.order_line:
            lines.append({
                "line_id": "items_"+str(line.id),
                "fields": [
                    {"name": "ItemCode","value": line.product_id.default_code},
                    {"name": "Quantity","value": line.product_uom_qty,"type": "float"},
                    {"name": "Price","value": line.price_unit,"type": "float"},
                    {"name": "DiscPrcnt","value": line.discount,"type": "float"},
                    {"name": "TaxCode","value": "IVA"}
                ]
            })
        _record["sublists"].append({"sublist_id": "items", "lines": lines})

        response = _rq(self,"/nextconnector/api/records/transaction",_record,"post")

        if response["status_code"] != "200":
            self.message_post(body="Error de comunicación al sincronizar registro")
        else:
            json_resp = response["response_json"]
            if json_resp["code"] != "0":
                self.message_post(body=json_resp["message"])
            else:
                self.write({"nxt_sync":'S'})
                self.message_post(body="Registro sincronizado con SAP")
                

    #COPY FROM partner_credit_limit
    def check_limit(self):
        self.ensure_one()
        partner = self.partner_id
        user_id = self.env['res.users'].search([
            ('partner_id', '=', partner.id)], limit=1)
        if user_id and not user_id.has_group('base.group_portal') or not \
                user_id:
            moveline_obj = self.env['account.move.line']
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.id),
                 ('account_id.user_type_id.name', 'in',
                  ['Receivable', 'Payable'])]
            )
            confirm_sale_order = self.search([('partner_id', '=', partner.id),
                                              ('state', '=', 'sale')])
            debit, credit = 0.0, 0.0
            amount_total = 0.0
            for status in confirm_sale_order:
                amount_total += status.amount_total
            for line in movelines:
                credit += line.credit
                debit += line.debit
            partner_credit_limit = (partner.credit_limit - debit) + credit
            available_credit_limit = \
                ((partner_credit_limit -
                  (amount_total - debit)) + self.amount_total)

            if (amount_total - debit) > partner_credit_limit:
                if not partner.over_credit:
                    msg = ' Crédito insuficiente, ' \
                          ' monto otorgado: = %s \n' \
                           % (available_credit_limit)
                    raise UserError('No es posible confimar la orden de venta . \n' + msg)
                partner.write(
                    {'credit_limit': credit - debit + self.amount_total})
            return True

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.check_limit()
        return res

    @api.constrains('amount_total')
    def check_amount(self):
        for order in self:
            order.check_limit()

    # Onchange para codigo del cliente
    """
    @api.onchange('partner_id')
    def onchange_customer(self):
        if self.partner_id:
            state = self.nxt_district_id.code
            self.zip = state
            query =  SELECT  T1."Balance" AS "balance",  T1."CreditLine" AS "credit_limit" 
                        FROM "OCRD" T1 
                        WHERE T1."CardType" IN ('C','L') AND T1."LicTradNum" = '{id}' .format(id=self.partner_id.vat)

            record = {
                "id": "",
                "record_type": "item",
                "fields": [
                        {"name": "query","value": query}
                    ]
            }

            response = _rq(self,"/nextconnector/api/records/items",record,"get")

            if response["status_code"] != "200":
                return _popup.error(self, "Error de comunicación")
            else:
                json_resp = response["response_json"]
                if json_resp["code"] != "0":
                    return _popup.error(self, json_resp["message"])
                else:
                    for list_data in json_resp["list_data"] :
                        for row in list_data["data"] :
                            try:
                                rec = self.env['res.partner'].search([('vat','=',id)])
                                if rec :
                                    result = rec.write(row)
                                    _logger.info("Update cliente !  id:" + str(result) + " - " + str(row))
                                else:
                                    result = self.env['res.partner'].create(row)
                                    _logger.info("Create cliente !  id:" + str(result) + " - " + str(row))
                            except Exception as e:
                                _logger.info("Error al crear cliente :" + str(e))
                                raise Warning("Error al crear cliente :" + str(e))
        """