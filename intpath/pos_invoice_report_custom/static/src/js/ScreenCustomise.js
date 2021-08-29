odoo.define('pos_invoice_report_custom.ScreenCustomise', function(require) {
    "use strict";
    
    var screens = require('point_of_sale.screens');
    var PaymentScreenWidget = screens.PaymentScreenWidget;

    PaymentScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            if (self.pos.config.auto_invoice_print){
                var order = this.pos.get_order();
                order.set_to_invoice(!order.is_to_invoice());
                this.$('.js_invoice').addClass('highlight');
            }
        },
    });
});