odoo.define('pos_products_quant.quant', function (require) {
    const pos_screens = require('point_of_sale.screens');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Dialog = require('web.Dialog');

    var _t = core._t;

    var product_quants = {}
    
    pos_screens.ProductListWidget.include({
        get_product_image_url: function(product){
            var order = this.pos.get_order();            
            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                'model': 'product.quant',
                'method': 'get_product_quant',
                'args': [product.id, order.pos_session_id],
                'kwargs': {
                    'context': {},
                }
            }).then(function (res) {
                const current_product = document.querySelector(`.product[data-product-id='${product.id}']`)
                if(current_product){
                    product_quants[`${product.display_name}`] = [parseInt(res),false];
                    current_product.querySelector(".pos_products_quant-quant_widget > span").innerHTML = res;
                    if(parseInt(res) == 0){
                        current_product.style.display = "none";
                    }
                }
            });

            return window.location.origin + '/web/image?model=product.product&field=image_128&id='+product.id;
        },
    });



    pos_screens.OrderWidget.include({
        set_value: function(val) {
            var order = this.pos.get_order();
            if (order.get_selected_orderline()) {
                var mode = this.numpad_state.get('mode');
                if( mode === 'quantity'){
                    const display_name = order.get_selected_orderline().product.display_name;
                    if(product_quants[display_name][0]>val || product_quants[display_name][1] || `${val}` == "remove"){
                        order.get_selected_orderline().set_quantity(val);
                        if(product_quants[display_name][0]>val){
                            product_quants[display_name][1] = false;
                        }
                    }else{
                        new swal({
                            title: 'Confirmation',
                            text: `You have only (${product_quants[display_name][0]}) of the (${display_name}), Are you sure you want to add more ?`,
                            type: 'warning',
                            showCancelButton: true,
                            confirmButtonColor: '#3085d6',
                            cancelButtonColor: '#d33',
                            confirmButtonText: 'Confirm'
                        }).then((result) => {
                            if(result.isConfirmed){
                                product_quants[display_name][1] = true;
                                order.get_selected_orderline().set_quantity(val);
                            }
                        })
                    }
                }else if( mode === 'discount'){
                    order.get_selected_orderline().set_discount(val);
                }else if( mode === 'price'){
                    var selected_orderline = order.get_selected_orderline();
                    selected_orderline.price_manually_set = true;
                    selected_orderline.set_unit_price(val);
                }
                if (this.pos.config.iface_customer_facing_display) {
                    this.pos.send_current_order_to_customer_facing_display();
                }
            }
        },
    });

    pos_screens.ProductScreenWidget.include({

        get_current_quant: function(display_name){
            const added_products = document.querySelectorAll('.orderlines');
            for(let i=0;i<added_products.length;i++){
                if(added_products[i].querySelector(".product-name").innerHTML.trim() == display_name){
                    return parseInt(added_products[i].querySelector(".info > em").innerHTML)
                }
            }
            return 0
        },

        click_product: function(product) {
            const display_name = product.display_name;
            const current_quant = this.get_current_quant(display_name);
            let self = this
            if(product.to_weight && this.pos.config.iface_electronic_scale){
                this.gui.show_screen('scale',{product: product});
            }else{                
                if((parseInt(product_quants[display_name][0]))==current_quant){
                    new swal({
                        title: 'Confirmation',
                        text: `You have only (${product_quants[display_name][0]}) of the (${display_name}), Are you sure you want to add more ?`,
                        type: 'warning',
                        showCancelButton: true,
                        confirmButtonColor: '#3085d6',
                        cancelButtonColor: '#d33',
                        confirmButtonText: 'Confirm'
                    }).then((result) => {
                        if(result.isConfirmed){
                            self.pos.get_order().add_product(product);
                        }
                    })
                }else{
                    this.pos.get_order().add_product(product);
                }
            }
         },
    });
});