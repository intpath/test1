odoo.define('account_customisations.account_report', function (require) {
'use strict';

var account_report = require('account_reports.account_report');


var accountReportsWidget = account_report.include({
    init: function (parent, action) {
        this._super(parent, action);
    },

    render_searchview_buttons: function () {
        var self = this;
        this._super();
        // $('.js_account_report_bool_filter_custom', this.$searchview_buttons).each(function (i, el) {
        // });

        _.each(this.$searchview_buttons.find('.js_account_report_bool_filter_custom'), function(k) {
            $(k).toggleClass('selected', self.report_options[$(k).data('filter')]);
        });

        this.$searchview_buttons.find('.js_account_report_bool_filter_custom').click(function (event) {
            var option_value = $(this).data('filter');
            self.report_options[option_value] = !self.report_options[option_value];
            self.reload();
        });
    }
});
});
