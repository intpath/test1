odoo.define('pos_order_print.printOrder', function (require) {
    "use strict";

    var rpc = require('web.rpc');
    var show_order = require('pos_order_print.showOrder');

    var ShowOrdersWidget = show_order.ShowOrdersWidget.include({
        init: function (parent, options) {
            this._super(parent, options);
            this.pos_reference = "";
        },

        render_list: function (orders) {
            var self = this;
            this._super(orders);

            this.$('.show-order-list-lines').delegate('.print-button', 'click', function (event) {
                var pos_ref = event.currentTarget.dataset.id;
                return rpc.query({ model: 'pos.order', method: 'get_details', args: [pos_ref] }).then(function (id) {
                    self.chrome.do_action('point_of_sale.pos_invoice_report',{additional_context:{
                        active_ids:id,
                    }});
                });
            });
        }
    });

});
