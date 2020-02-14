# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from . import popup_message
from . import util
import requests
import json 
import logging
_logger = logging.getLogger(__name__)
_rq = util.util.request
_popup = popup_message.popup_message

class process(models.TransientModel):
    _name="nextconnector.process"
    _description = "Procesos generales del conector"

    def import_items(self):
        record = {
            "id": "",
            "record_type": "items",
            "fields": [
                {"name": "query","value": "SELECT \"ItemCode\" + ' ' + \"ItemName\" AS \"name\"FROM OITM" }
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
                    #for rec in self.web_progress_iter(data, msg="Importando articulos") :
                    for row in list_data["data"] :
                        name_id = row["name"]
                        self.create_item(str(name_id))

                return _popup.success(self, "Importación culminada.")
                
    def create_item(self, id):

        query = """ SELECT  T3."ItemCode" + ' ' + T3."ItemName" as "name"
                            , T3."ItemCode" as "default_code"
                            , T3."ItemName" AS "description_sale"
                            , (T1."Price") AS "list_price" 
                            , 'product' AS "type" 
                    FROM "ITM1" T1 
                        INNER JOIN OPLN T2 ON T1."PriceList" = T2."ListNum" 
                        INNER JOIN OITM T3 ON T3."ItemCode" = T1."ItemCode"  
                    WHERE T1."PriceList" = 1 AND (T3."ItemCode" + ' ' + T3."ItemName") = '{id}' """.format(id=id)

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
                            rec = self.env['product.product'].search([('name','=',id)])
                            if rec :
                                result = rec.write(row)
                                _logger.info("Update articulo !  item_id:" + str(result) + " - " + str(row))
                            else:
                                result = self.env['product.product'].create(row)
                                _logger.info("Create articulo !  item_id:" + str(result) + " - " + str(row))
                        except Exception as e:
                            _logger.info("Error al crear articulo :" + str(e))
                            raise Warning("Error al crear articulo :" + str(e))

    def import_customers(self):

        query = """ SELECT  T1."LicTradNum" AS "name" 
                        FROM "OCRD" T1 
                    WHERE T1."CardType" = 'C' """

        record = {
            "id": "",
            "record_type": "items",
            "fields": [
                {"name": "query","value": query}
            ]
        }

        response = _rq(self,"/nextconnector/api/records/customers",record,"get")

        if response["status_code"] != "200":
            return _popup.error(self, "Error de comunicación")
        else:
            json_resp = response["response_json"]
            if json_resp["code"] != "0":
                return _popup.error(self, json_resp["message"])
            else:
                for list_data in json_resp["list_data"] :
                    #for rec in self.web_progress_iter(data, msg="Importando Clientes") :
                    for row in list_data["data"] :
                        name_id = row["name"]
                        self.create_customer(str(name_id))

                return _popup.success(self, "Importación culminada.")

    def create_customer(self, id):

        query = """ SELECT  T1."LicTradNum" AS "vat",  T1."CardName" AS "name" 
                    FROM "OCRD" T1 
                    WHERE T1."CardType" = 'C' AND T1."LicTradNum" = '{id}' """.format(id=id)

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

    def import_stock_inventory(self):

        query = """ SELECT  T0."ItemCode" + ' ' + T0."ItemName" as "product_id",
                            (T1."OnHand" - T1."IsCommited" + T1."OnOrder") as "qty_done",
                            T1."AvgPrice" 
                        FROM OITM T0 
                            INNER JOIN OITW T1 ON T0."ItemCode" = T1."ItemCode" 
                            INNER JOIN OWHS T2 On T1."WhsCode"=T2."WhsCode"
                    WHERE  T1."WhsCode" = '{id}' 
                            AND (T1."OnHand" - T1."IsCommited" + T1."OnOrder") > 0 
                    """.format(id="01")

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
                    try:
                        #CREO AJUSTE DE INVENTARIO
                        inv_ref = "AJUSTE DE INVENTARIO DESDE SAP"
                        inv_adjs = self.env['stock.inventory'].create({"accounting_date":datetime.today(), 
                                    "prefill_counted_quantity": 'zero', "company_id": 1 , "start_empty": True,
                                    "name":inv_ref
                                    })
                        lines = []
                        for row in list_data["data"] :
                            product = self.env['product.template'].search([('name','=',row["product_id"])])
                            qty_done = row["qty_done"]
                            warehouse = 8
                            lines.append({
                                    'name': inv_ref,
                                    'product_id': product.id,
                                    'product_uom': 1,
                                    'product_uom_qty': qty_done,
                                    'date': '2019-12-01',
                                    'company_id': 1,
                                    'inventory_id': inv_adjs.id,
                                    'state': 'confirmed',
                                    'location_id': 14,
                                    'location_dest_id':warehouse,
                                    'move_line_ids': [(0, 0, {
                                        'product_id': product.id,
                                        'product_uom_qty': 0,  # bypass reservation here
                                        'product_uom_id': 1,
                                        'qty_done': qty_done,
                                        'location_id': 14,
                                        'location_dest_id': warehouse
                                    })]
                                })
                        self.env['stock.move'].create(lines)
                        inv_adjs.write({'state': 'done'})
                        inv_adjs.post_inventory()
                        _logger.info("Create stock inventory :" + str(inv_adjs.id))
                        #rec.action_done()
                        return _popup.success(self, "Importación culminada.")
                    except Exception as e:
                        _logger.info("Error al crear ajuste de inventario :" + str(e))
                        raise Warning("Error al crear ajusre de inventario :" + str(e))

    
    