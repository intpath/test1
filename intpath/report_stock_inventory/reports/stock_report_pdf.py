# -*- coding: utf-8 -*-
import datetime

from odoo import models, api


class InventoryReportPDF(models.AbstractModel):
    _name = "report.report_stock_inventory.report_stock_pdf"

    @api.model
    def _get_report_values(self, docids, data=None):
        quantities_at_date = 0

        if data['category']:
            products = self.env['product.product'].search([('categ_id','in',data['category']),('type','=','product')])
        else:
            products = self.env['product.product'].search([('type','=','product')])
        product_dict = []


        # get the stock moves until a given string date from the wizard and store it at stock_moves_to_date.
        stock_moves = self.env['stock.move'].search([])
        stock_moves_to_date = []
        for stock_move in stock_moves:
            if stock_move.date.date() <= datetime.datetime.strptime(data['date'], '%Y-%m-%d %H:%M:%S').date():
                stock_moves_to_date.append(stock_move)
        
        # to calculate locations info
        locations_info = []
        for location in data['location']:
            location_id = self.env['stock.location'].search([('id','=',location)])
            locations_info.append({"location_id":location_id.id,"location_name":location_id.name,"total_quant":0,"line_count":0,"ref":location_id.barcode.split("-")[0]})

        total_quantity = 0
        for product in products:
            for location in data['location']:
                # calculate the quantity at location and date from stock move table.
                quantity_at_location_date = 0
                for stock_move_to_date in stock_moves_to_date:
                    if(stock_move_to_date.product_id.id == product.id and stock_move_to_date.location_id.id == location and stock_move_to_date.state == 'done'):
                        quantity_at_location_date = quantity_at_location_date - stock_move_to_date.product_qty
                    elif(stock_move_to_date.product_id.id == product.id and stock_move_to_date.location_dest_id.id == location and stock_move_to_date.state == 'done'):
                        quantity_at_location_date = quantity_at_location_date + stock_move_to_date.product_qty
                if(quantity_at_location_date > 0):
                    total_quantity = total_quantity + quantity_at_location_date
                    # to calculate total_quant and line_count
                    for index,location_2 in enumerate(locations_info):
                        if location_2["location_id"] == location:
                            locations_info[index]["total_quant"] = locations_info[index]["total_quant"] + quantity_at_location_date
                            locations_info[index]["line_count"] = locations_info[index]["line_count"] + 1
                            break
                    
                    product_dict.append(
                        {
                            'product': product,
                            'qty_available':int(quantity_at_location_date),
                            'uom_id':product.uom_id.name,
                            'location':self.env['stock.location'].search([('id','=',location)]).name,
                            'include_lines':data['include_lines'],
                        })
        
        return {
            'docs': product_dict,
            'doc_quantities': quantities_at_date,
            'loc_name': data['loc_name'],
            'categ_name': data['categ_name'],
            'report_date': datetime.date.today().strftime('%d-%m-%Y'),
            'inventory_date': data['inventory_date'],
            'locations_info':locations_info,
            'total': int(total_quantity),
        }
