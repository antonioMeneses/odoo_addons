odoo.define('smile_account_asset.create_asset', function (require) {
    "use strict";

    var core = require('web.core');
    var ListController = require('web.ListController');
    var rpc = require('web.rpc');

    function create_asset () {
        var self = this;
        rpc.query({
            model: 'account.invoice.line',
            method:'create_asset',
            args: [self.getSelectedIds(), []],
        }).then(function (asset_id) {
            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'account.asset.asset',
                res_id: asset_id,
                views: [[false, 'form']],
                target: 'current'
            });
        });
    }

    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.modelName === 'account.invoice.line' &&
                    this.getParent().action.xml_id === "smile_account_asset.action_account_invoice_line") {
                this.$buttons.on('click', '.o_list_button_create_asset', create_asset.bind(this));
            } else if (this.$buttons != undefined) {
                this.$buttons.find('.btn.btn-primary.btn-sm.o_list_button_create_asset').hide();
            }
        },
    });
});
